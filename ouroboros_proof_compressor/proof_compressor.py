#!/usr/bin/env python3
"""Conservative, bounded search over explicit Lean 4 lemma pools."""
import argparse
from dataclasses import asdict, dataclass
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import tempfile
import time

MARKER = re.compile(r'^([ \t]*)-- OUROBOROS: LEMMAS[ \t]*$', re.M)
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_']*(?:\.[A-Za-z_][A-Za-z0-9_']*)*\Z")
STANDARD = frozenset(('propext', 'Classical.choice', 'Quot.sound'))


def ident(s):
    if not isinstance(s, str) or not IDENT.fullmatch(s):
        raise ValueError(f'Unsupported Lean identifier: {s!r}')
    return s


def sha(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def render(template, lemmas):
    if len(list(MARKER.finditer(template))) != 1:
        raise ValueError('Expected exactly one standalone -- OUROBOROS: LEMMAS marker')
    return MARKER.sub(lambda m: m[1] + 'solve_by_elim only [' + ', '.join(map(ident, lemmas)) + ']', template)


def audit_source(source, target):
    return source.rstrip() + '\n\n#print axioms ' + ident(target) + '\n'


def parse_axioms(output, target):
    prefix = re.escape("'" + target + "'")
    matches = list(re.finditer(prefix + r"\s+(?:does not depend on any axioms|depends on axioms:\s*\[([^\]]*)\])", output))
    if len(matches) != 1:
        raise ValueError('Expected exactly one recognizable axiom report for the target')
    raw = matches[0].group(1)
    return tuple(sorted(set(x.strip() for x in raw.split(',') if x.strip()))) if raw else ()


@dataclass
class Verdict:
    status: str
    detail: str = ''
    axioms: tuple = ()
    seconds: float = 0.0
    output: str = ''


class LeanChecker:
    def __init__(self, project, command, target, timeout=30, allowed=STANDARD):
        self.project = Path(project).resolve()
        self.command = tuple(command)
        self.target = ident(target)
        self.timeout = timeout
        self.allowed = frozenset(allowed)
        if not self.project.is_dir() or not self.command or timeout <= 0:
            raise ValueError('Invalid project directory, command, or timeout')

    def check(self, source):
        # A fresh scratch file inside the project preserves Lake import resolution.
        start = time.monotonic()
        with tempfile.TemporaryDirectory(prefix='ouroboros_trial_', dir=self.project) as d:
            path = Path(d) / 'Trial.lean'
            path.write_text(audit_source(source, self.target), encoding='utf-8')
            try:
                proc = subprocess.Popen([*self.command, str(path)], cwd=self.project,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    encoding='utf-8', errors='replace', start_new_session=(os.name == 'posix'))
            except OSError as e:
                return Verdict('unavailable', str(e))
            def stop():
                if os.name == 'posix':
                    try: os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                else:
                    proc.kill()
            try:
                out, _ = proc.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                stop(); out, _ = proc.communicate()
                return Verdict('timeout', 'Checker exceeded trial budget', seconds=time.monotonic()-start, output=out[-16000:])
            except KeyboardInterrupt:
                stop(); proc.communicate(); raise
        elapsed = time.monotonic()-start
        def result(status, detail='', axioms=()):
            return Verdict(status, detail, axioms, elapsed, out[-16000:])
        if proc.returncode != 0:
            return result('rejected', f'Checker exit code {proc.returncode}')
        # Refuse incomplete proofs anywhere in the trial source, including warnings.
        if re.search(r'declaration uses [\'`‘]?sorry|\bsorryAx\b', out, re.I):
            return result('rejected', 'Incomplete proof diagnostic')
        try:
            axioms = parse_axioms(out, self.target)
        except ValueError as e:
            return result('unconfirmed', str(e))
        extra = set(axioms) - self.allowed
        if extra:
            return result('rejected', 'Unapproved axioms: ' + ', '.join(sorted(extra)), axioms)
        return result('accepted', 'Checker accepted and axiom policy passed', axioms)


def minimize(template, candidates, checker, budget=64, mode='greedy'):
    pool = tuple(map(ident, candidates))
    if len(set(pool)) != len(pool) or not pool or not 1 <= budget or mode not in ('greedy','exact'):
        raise ValueError('Use a nonempty unique lemma pool, positive budget, and valid search mode')
    render(template, pool)
    trials, cache = [], {}
    baseline_axioms = None
    def trial(subset):
        nonlocal baseline_axioms
        if subset in cache: return cache[subset]
        if len(trials) >= budget: return None
        source = render(template, subset)
        v = checker.check(source)
        if v.status == 'accepted':
            if baseline_axioms is None: baseline_axioms = set(v.axioms)
            elif set(v.axioms) - baseline_axioms:
                v = Verdict('rejected', 'Introduces axioms absent from baseline', v.axioms, v.seconds, v.output)
        cache[subset] = v.status
        trials.append({'lemmas': list(subset), 'source_sha256': sha(source), **asdict(v)})
        return v.status
    baseline = trial(pool)
    best = pool if baseline == 'accepted' else None
    complete = False
    if best is not None and mode == 'greedy':
        while True:
            changed = False
            for i in range(len(best)):
                smaller = best[:i]+best[i+1:]
                if trial(smaller) == 'accepted':
                    best = smaller; changed = True; break
            if not changed:
                complete = all(cache.get(best[:i]+best[i+1:]) == 'rejected' for i in range(len(best)))
                break
    elif best is not None:
        # Search in cardinality order. A timeout or unconfirmed result at a
        # smaller cardinality prevents a claim of a certified minimum.
        inconclusive = False
        found = False
        for size in range(len(pool)):
            for subset in combinations(pool, size):
                status = trial(subset)
                if status is None:
                    inconclusive = True; break
                if status == 'accepted':
                    best = subset; found = True; break
                if status != 'rejected': inconclusive = True
            if found or len(trials) >= budget: break
        complete = not inconclusive and (found or all(s in cache for n in range(len(pool)) for s in combinations(pool,n)))
    # 'rejected' means this search tactic/checker configuration did not accept,
    # not that a theorem cannot be proved from those lemmas in another way.
    return {'baseline': baseline, 'mode': mode, 'budget': budget, 'trials': trials,
            'original_lemmas': list(pool), 'retained_lemmas': list(best) if best is not None else None,
            'removed_count': len(pool)-len(best) if best is not None else None,
            'search_complete_for_configured_checker': complete,
            'claim': ('minimum accepted cardinality in tested search space' if mode=='exact' else 'single-deletion minimal for configured checker') if complete else 'best accepted candidate only; no minimality claim',
            'template_sha256': sha(template), 'accepted_source': render(template,best) if best is not None else None}


def dependency_probe(module, target):
    # Optional direct constant references. Imported opaque bodies may not be
    # available in some Lean versions; the report distinguishes that case.
    ident(module); ident(target)
    return f'''import Lean
import {module}

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let some ci := env.find? `{target} | throwError "Target not found"
  for dep in ci.type.getUsedConstants do
    logInfo m!"OUROBOROS_TYPE_DEP: {{dep}}"
  match ci.value? true with
  | none => logInfo "OUROBOROS_BODY_UNAVAILABLE"
  | some value =>
    logInfo "OUROBOROS_BODY_AVAILABLE"
    for dep in value.getUsedConstants do
      logInfo m!"OUROBOROS_BODY_DEP: {{dep}}"
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', default='.', help='Trusted Lean/Lake project root')
    p.add_argument('--command', default='lake env lean', help='Lean checker command (no shell)')
    p.add_argument('--timeout', type=float, default=30)
    p.add_argument('--target', required=True, help='Fully qualified target theorem name')
    p.add_argument('--out', required=True, help='New report directory; never overwrite existing files')
    p.add_argument('--allow-axiom', action='append', default=[], help='Explicit additional axiom (not sorryAx)')
    sub = p.add_subparsers(dest='action', required=True)
    q = sub.add_parser('reduce'); q.add_argument('template'); q.add_argument('--lemmas', nargs='+', required=True); q.add_argument('--budget', type=int, default=64); q.add_argument('--mode', choices=['greedy','exact'], default='greedy')
    q = sub.add_parser('audit'); q.add_argument('module', help='Built Lean module to inspect')
    a = p.parse_args()
    if 'sorryAx' in a.allow_axiom: p.error('sorryAx cannot be approved')
    output = Path(a.out).resolve()
    output.mkdir(parents=True, exist_ok=False)
    checker = LeanChecker(a.project, shlex.split(a.command, posix=True), a.target, a.timeout, STANDARD|set(a.allow_axiom))
    if a.action == 'reduce':
        template = Path(a.template).read_text(encoding='utf-8')
        report = minimize(template, a.lemmas, checker, a.budget, a.mode)
        accepted = report.pop('accepted_source')
        if accepted is not None:
            (output/'accepted.lean').write_text(audit_source(accepted,a.target),encoding='utf-8')
        success = accepted is not None
    else:
        source = dependency_probe(a.module,a.target)
        verdict = checker.check(source)
        report = asdict(verdict)
        report['source_sha256'] = sha(source)
        report['type_dependencies'] = re.findall(r'OUROBOROS_TYPE_DEP: ([^\r\n]+)', verdict.output)
        report['body_dependencies'] = re.findall(r'OUROBOROS_BODY_DEP: ([^\r\n]+)', verdict.output)
        report['body_available'] = 'OUROBOROS_BODY_AVAILABLE' in verdict.output
        report['dependencies_may_be_truncated'] = len(verdict.output) >= 16000
        (output/'audit.lean').write_text(audit_source(source,a.target),encoding='utf-8')
        success = verdict.status == 'accepted'
    report['checker'] = {'command': list(checker.command), 'project': str(checker.project), 'target': checker.target, 'allowed_axioms': sorted(checker.allowed), 'timeout_seconds': checker.timeout}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f'Report: {output / "report.json"}')
    return 0 if success else 1

if __name__ == '__main__':
    raise SystemExit(main())
