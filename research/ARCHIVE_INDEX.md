# BCE research archive — public reading guide
**Snapshot: 2026-11-26.** Human-directed, AI-assisted exploratory research. Not peer reviewed or an independent proof of RH.

Start with [YanRiemann Requiem: research map and metaphor ledger](yanriemann-metaphor-ledger.md). This preserves the thought process, equations, counterexamples and unresolved proof obligation. The [earlier Necessary Unity notes](yanriemann-necessary-unity-2026-11-26.md) and [Golden Bang specification](golden_bang.md) are companion documents, not independent confirmations.

## Research lineage

1. [Herzog’s Phenomenal Stone, November 8 working draft](historical/Herzogs_Stone_Publication_Rough_Draft.md): exact reversibility, observer invariance, finite-state models, phase versus full-state recurrence, proposed three-observer protocol. Historical claims are reported, not newly certified.
2. [BCE / Ultimodel’ progress report, November 20](historical/PROGRESS_REPORT_2026-11-20.md): BaguaCode virtual machine, symbolic bridge, address book, emulator matrix and development checkpoints.
3. [YanRiemann metaphor ledger](yanriemann-metaphor-ledger.md): from Unity and Ghost to polygon, triangle, reciprocal, cruller and golden staff; Hamon and Resonance Reverb as future physical-model hypotheses.
4. [Metaphors and research vocabulary](metaphors-and-method.md): a reading guide to how the images generated concrete tests.

See also the [repository README](../README.md) and [research status](../docs/RESEARCH_STATUS.md) for the broader software program.

## Experiments and recorded output

| Experiment | Source | Recorded output |
|---|---|---|
| Unity, heat-deformed xi kernel, Li coefficients | [reproduce_unity.py](reproduce_unity.py); [verify_ghost_extra.py](verify_ghost_extra.py) | [results](reproduce_unity_results.txt) |
| Finite prime-factor elimination / phase aliasing | [ghost_winding_experiment.py](ghost_winding_experiment.py) | [results](ghost_winding_results.txt) |
| Radial Jensen / winding | [radial_unity_experiment.py](radial_unity_experiment.py) | [results](radial_unity_results.txt) |
| Polygon amplification | [polygon_unity_experiment.py](polygon_unity_experiment.py) | [results](polygon_unity_results.txt) |
| Three Infinities | [three_infinities_experiment.py](three_infinities_experiment.py) | [results](three_infinities_results.txt) |
| Snake Chase / Mertens energy | [reciprocal_snake_chase.py](reciprocal_snake_chase.py) | [results](reciprocal_snake_chase_results.txt) |
| French Cruller | [cruller_experiment.py](cruller_experiment.py) | [results](cruller_results.txt) |
| Cruller reciprocal energy | [cruller_energy_experiment.py](cruller_energy_experiment.py) | [results](cruller_energy_results.txt) |
| Golden ratio windows | [golden_ratio_windows.py](golden_ratio_windows.py) | [results](golden_ratio_results.txt) |

## Reproduction

Install Python 3 and the packages numpy, scipy and mpmath in an isolated environment. From this folder, run a script with python, e.g. python three_infinities_experiment.py. To reproduce both parts of the first combined log, run reproduce_unity.py followed by verify_ghost_extra.py. For the last cross-check in the ghost winding log, repeat the nonzero critical-line control with N=1024 instead of 256. The scripts are exploratory and can require substantial compute time; Ctrl-C interrupts them. They do not need to modify input files. Use local environment/package records for exact numerical reproducibility; historic dependency versions were not systematically captured. Some result transcripts omit wrappers or trailing whitespace; this is not a byte-identical archival claim.

## Audit checkpoints

- The published phase-alias example is especially important: a sampled contour reported winding 40 for a nonzero control when the true count was zero. Removing the known prime-factor phase or increasing sampling resolution restored zero. Thus apparent integer winding alone is not certification.
- The reciprocal Snake Chase script uses C(w)=1/((2+w)zeta((2+w)/(1-w))), a different coordinate map and normalization from B(w)=1/[(s-1)zeta(s)] with s=1/(1-w) in the Golden Bang and Cruller Energy scripts. Do not combine their Taylor coefficients or treat them as identical functions. C is holomorphic wherever the displayed denominator is nonzero; its pole-detection region differs from B's.
- All mpmath, numpy and scipy results are numerical, not interval-certified or exhaustive. Some functions convert high-precision values to double precision. Synthetic examples are controls, not claimed zeros of zeta.
- The central obstruction remains unproved: a zero-free disk, finite reciprocal energy on every compact subdisk, subexponential reciprocal coefficient growth, or equivalent arithmetic tail control. These are equivalent formulations of RH, not four independent proofs.
- Historical draft records and reconstructed notes preserve original wording or interpretations where practical; read with the status labels and latest corrected derivations. No claim that every earlier chat, unpublished artifact, or external result has been recovered. Private life, private conversation logs and unrelated personal material are excluded.
- Verification on GitHub is file-content readback, not a mathematical audit. No external verification submission, endorsement, or accepted priority is claimed.

## Independent review requested

Start with definitions, check the algebra and analytic domains, rerun the controls, then look for a missing assumption or counterexample. A negative result is welcome. Compare against established mathematical literature before making a novelty claim. The external Alpöge–Claude announcement and Waterloo Lean checks are independent work, not evidence that this repository proved RH.

**Every description is a model, not the thing itself. We must investigate.**
