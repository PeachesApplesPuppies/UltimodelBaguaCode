# Ouroboros Proof Compressor v0.1

A conservative, bounded Lean 4 proof-search assistant for Ultimodel / BaguaCode. It reduces an explicitly supplied pool of candidate lemmas while retaining the same theorem source, and only saves an accepted candidate when a configured checker reports success and the target's axiom policy passes.

**Status:** Python implementation tested; actual Lean execution and RH proof integration have not been verified in the build environment. This tool does not prove RH, automatically rewrite arbitrary proofs, or establish that a proof is globally minimal.

## Quick start

Requires Python 3.10 or later, no third-party Python packages. Actual proof checks require Lean 4 (and Lake for an existing Lean project). Use the toolchain pinned by the project. Run from this directory:

```sh
python -m unittest discover -s tests -v
python proof_compressor.py --project . --command lean --target ouroboros_chain --out chain_result reduce examples/Chain.lean --lemmas hP hPQ hQR hUnused hDuplicate --mode exact
```

Windows: substitute `py -3` for `python` if appropriate. The output directory must not already exist. Use a fresh output directory for each run. The example theorem is an implication chain; two alternative hypotheses can supply P, and the True hypothesis is irrelevant. A three-lemma solution is expected, **not a Lean-verified result from this build**. If Lean is unavailable, the program records `unavailable` and does not create `accepted.lean`.

## Apply to an existing Lean project

1. Obtain and build a trusted checkout of the desired Lean project using its pinned toolchain. For RH, independently verify that the exact named theorem is the intended mathematical statement and inspect its allowed axioms. No RH repository is bundled here.
2. Audit a built module and a fully qualified theorem name. Replace the illustrative paths and identifiers with actual project values:

```sh
python proof_compressor.py --project /path/to/project --target Namespace.target --out audit_result audit Project.Module
```

This generates a small Lean probe using `getUsedConstants` for direct references in the declaration's type and (when accessible) proof body, and `#print axioms` for transitive axioms. Imported opaque proof bodies may be unavailable; that is not evidence that a theorem has no dependencies. The probe API has not been compiled in this build and may need adaptation to the project's Lean version. Output is bounded to the final 16,000 characters, so large dependency lists can be incomplete; the JSON flags possible truncation. Direct references are not a complete transitive theorem graph or a minimal lemma set.

3. Select a small target proof or subgoal. In a **copy** of its source, retain the theorem statement, imports, namespace and surrounding context. Replace the selected tactic body with the standalone line `-- OUROBOROS: LEMMAS` at the appropriate indentation. Supply the candidate lemma identifiers in their original order. Use a fully qualified target name for auditing. The reducer fills the marker with Lean's `solve_by_elim only [...]` tactic. The tactic must be appropriate to the subgoal. Arbitrary long tactic scripts or theorems cannot be automatically reduced by this version.

```sh
python proof_compressor.py --project /path/to/project --target Namespace.target --out reduced_result --timeout 120 reduce /path/to/template.lean --lemmas lemmaA lemmaB lemmaC --budget 32 --mode greedy
```

The default checker command is `lake env lean`; set `--command lean` for standalone files. The command is executed without a shell. Only use trusted source files, projects, toolchains and commands: Lean elaborators can execute code. This tool is not a sandbox and cannot protect against a malicious checker or project. It checks a fixed source template, not equivalence to some separately supplied original theorem; the template and theorem identity must be reviewed by the operator. For independent statement comparison and extra kernel checks, consider Lake comparator where available.

## Search strategies

- `greedy`: repeatedly try removing one candidate. If every final one-deletion trial is rejected, the set is single-deletion minimal for this configured search/checker. It need not be globally smallest.
- `exact`: test subsets in increasing cardinality, subject to the trial budget. If every smaller subset is rejected, the first accepted set is minimum among the sets accepted by this configured tactic/checker. It does not rule out a different proof strategy. Worst-case subset search is exponential.
- A timeout, missing checker, unrecognized axiom report, or exhausted budget cannot certify minimality. A rejected trial means the configured checker did not accept the candidate; it is not a mathematical impossibility proof.

The full candidate pool must pass before reduction begins. Each accepted candidate must use no axiom outside the configured allowance (default: `propext`, `Classical.choice`, `Quot.sound`), and no additional axioms relative to the accepted baseline. `sorryAx` is prohibited and incomplete-proof diagnostics are rejected. Extra axioms explicitly allowed by the user remain assumptions, not unconditional proofs.

## Outputs and safe operation

- `report.json`: trial status, source SHA-256, elapsed time, reported axioms, bounded checker log, selected lemma names, and scoped minimality claim.
- `accepted.lean`: generated only when the configured checker accepts a candidate and its axiom audit passes. It includes the `#print axioms` check.
- `audit.lean`: generated in audit mode for reproducing the inspection.

Original source is not overwritten. Each trial uses a temporary scratch directory and is removed afterward. A new report directory is required. Ctrl+C interrupts a live trial; on POSIX the spawned process group is terminated, on Windows only the immediate process is explicitly terminated (children may outlive it). A per-trial timeout and maximum trial count bound the search under ordinary process behavior. The tool does not prevent a trusted checker from writing to its own project/cache. For important proofs, run in a disposable checkout.

## Tests actually run

`test_results.txt` records eight passing Python unit tests, including 64 simulated search cases, exact-versus-greedy counterexamples, malformed source, failed baselines, timeouts, axiom safeguards, and subprocess behavior. Simulated checker output is not Lean validation. `unavailable_demo/report.json` records the real attempt to launch Lean, which failed because Lean was not installed. No accepted Lean proof was produced here.

References:
- Lean 4 tactic reference: https://lean-lang.org/doc/reference/latest/Tactic-Proofs/Tactic-Reference
- Lean proof validation: https://lean-lang.org/doc/reference/latest/ValidatingProofs/
- Lake comparator: https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/

Discard redundancy. Preserve the statement. Let the kernel judge validity.
