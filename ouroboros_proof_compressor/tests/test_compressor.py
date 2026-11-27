import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from itertools import combinations
from proof_compressor import (LeanChecker, Verdict, minimize, parse_axioms, render, dependency_probe, STANDARD)

TEMPLATE = 'theorem demo : True := by\n  -- OUROBOROS: LEMMAS\n'
POOL = ('a','b','c','d','e')

class Oracle:
    """Simulated checker, not Lean: acceptance iff a chosen subset meets a rule."""
    def __init__(self, rule): self.rule = rule
    def check(self, source):
        m = re.search(r'solve_by_elim only \[(.*?)\]',source)
        names = frozenset(filter(None,m[1].split(', ')))
        result = self.rule(names)
        return result if isinstance(result,Verdict) else Verdict('accepted' if result else 'rejected')

class Tests(unittest.TestCase):
    def test_render(self):
        self.assertEqual(render(TEMPLATE,['a','b']), 'theorem demo : True := by\n  solve_by_elim only [a, b]\n')
        self.assertEqual(render(TEMPLATE,[]), 'theorem demo : True := by\n  solve_by_elim only []\n')
        for bad in ['',TEMPLATE+TEMPLATE]:
            with self.assertRaises(ValueError): render(bad,['a'])
        with self.assertRaises(ValueError): render(TEMPLATE,['a]; sorry'])

    def test_greedy(self):
        r=minimize(TEMPLATE,POOL,Oracle(lambda x: {'b','c'} <= x))
        self.assertEqual(r['retained_lemmas'],['b','c'])
        self.assertTrue(r['search_complete_for_configured_checker'])
        self.assertEqual(r['removed_count'],3)

    def test_exact_vs_greedy(self):
        check=Oracle(lambda x: 'a' in x or {'b','c','d'} <= x)
        g=minimize(TEMPLATE,POOL,check)
        e=minimize(TEMPLATE,POOL,check,mode='exact')
        self.assertEqual(g['retained_lemmas'],['b','c','d'])
        self.assertEqual(e['retained_lemmas'],['a'])
        self.assertTrue(e['search_complete_for_configured_checker'])

    def test_exhaustive_monotone_oracles(self):
        n=0
        for size in range(6):
            for req in combinations(POOL,size):
                for mode in ['greedy','exact']:
                    r=minimize(TEMPLATE,POOL,Oracle(lambda x:set(req)<=x),mode=mode)
                    self.assertEqual(r['retained_lemmas'],list(req))
                    self.assertTrue(r['search_complete_for_configured_checker'])
                    n+=1
        self.assertEqual(n,64)

    def test_budget_timeout_and_failed_baseline(self):
        for status in ('timeout','unavailable','unconfirmed','rejected'):
            r=minimize(TEMPLATE,POOL,Oracle(lambda x:Verdict(status)))
            self.assertIsNone(r['accepted_source'])
            self.assertFalse(r['search_complete_for_configured_checker'])
        for mode in ['greedy','exact']:
            r=minimize(TEMPLATE,POOL,Oracle(lambda x:True),budget=1,mode=mode)
            self.assertEqual(r['retained_lemmas'],list(POOL))
            self.assertFalse(r['search_complete_for_configured_checker'])
        r=minimize(TEMPLATE,POOL,Oracle(lambda x:Verdict('timeout') if not x else True),mode='exact')
        self.assertEqual(len(r['retained_lemmas']),1)
        self.assertFalse(r['search_complete_for_configured_checker'])

    def test_axiom_policy(self):
        r=minimize(TEMPLATE,POOL,Oracle(lambda x:Verdict('accepted',axioms=() if len(x)==5 else ('Classical.choice',))))
        self.assertEqual(r['retained_lemmas'],list(POOL))
        self.assertTrue(all(t['status']=='rejected' for t in r['trials'][1:]))
        self.assertEqual(parse_axioms("'demo' does not depend on any axioms",'demo'),())
        self.assertEqual(parse_axioms("'demo' depends on axioms: [propext,\n Classical.choice]",'demo'),('Classical.choice','propext'))
        for bad in ['','\'other\' does not depend on any axioms',"'demo' does not depend on any axioms\n'demo' does not depend on any axioms"]:
            with self.assertRaises(ValueError): parse_axioms(bad,'demo')

    def test_subprocess_gate(self):
        cases=[("print(\"'demo' does not depend on any axioms\")",'accepted'),
               ("print(\"'demo' depends on axioms: [sorryAx]\")",'rejected'),
               ("print(\"'demo' depends on axioms: [Untrusted.ax]\")",'rejected'),
               ("print(\"warning: declaration uses 'sorry'\"); print(\"'demo' does not depend on any axioms\")",'rejected'),
               ("print(\"'demo' does not depend on any axioms\"); raise SystemExit(1)",'rejected'),
               ("print('hello')",'unconfirmed'), ("import time; time.sleep(5)",'timeout')]
        with tempfile.TemporaryDirectory() as d:
            for code,expected in cases:
                checker=LeanChecker(d,[sys.executable,'-c',code],'demo',timeout=.3 if expected=='timeout' else 5)
                self.assertEqual(checker.check('theorem demo : True := by trivial').status,expected)
            self.assertEqual(LeanChecker(d,['missing_checker_123456'],'demo').check('test').status,'unavailable')
            self.assertEqual(list(Path(d).iterdir()),[])

    def test_dependency_source(self):
        s=dependency_probe('Mathlib','Namespace.target')
        self.assertIn('import Mathlib',s)
        self.assertIn('env.find? `Namespace.target',s)
        with self.assertRaises(ValueError):dependency_probe('Mathlib\n#eval 1','x')

if __name__=='__main__':unittest.main()
