# Equal-budget adversarial comparison: single direction vs three-lens

**Date:** 2026-11-23 · **Result:** useful for the tested sign-loss cases, but mathematically breakable.

## Protocol

Treat each function as a black box (no formula accessible). Compare exactly **five observed inputs**:

| Method | Samples, R=10 |
| --- | --- |
| Both Sides + Middle | -10, -0.1, 0, 0.1, 10 |
| Positive-only | 0, 0.1, 5, 10, 20 |
| Negative-only | 0, -0.1, -5, -10, -20 |

A **collision witness** is two different observed inputs with equal outputs. It proves non-injectivity, but no witnessed collision does **not** prove injectivity. The sampling design is fixed and not a universal optimum.

## Constructed benchmark: 275 functions

| Family | Cases | Three-lens | Positive-only | Negative-only |
| --- | ---: | ---: | ---: | ---: |
| Even / sign-erasing | 100 | 100 | 0 | 0 |
| Sign / plateau | 25 | 25 | 25 | 25 |
| Positive-interior collision | 25 | 0 | 25 | 0 |
| Negative-interior collision | 25 | 0 | 0 | 25 |
| Injective controls | 100 | 0 | 0 | 0 |
| **Witnesses (175 non-injective)** | | **125** | **50** | **50** |

All 100 injective controls returned zero collision witnesses. Dataset is deliberately constructed, **not** a representative sampling of mathematical functions. Results cannot be generalized into an unconditional superiority claim.

## Counterexample that breaks sampled inference

Let f(x)=x² and g(x)=x²+x(x²−100)(x²−0.01).

The two functions have equal outputs at **all five three-lens probe points**. Yet f(5)=25 and g(5)=−9346.25, and g(5) differs from g(−5). Thus equality at these points cannot prove global equivalence or even symmetry. An adversarial perturbation can be constructed to vanish on *any finite set of probes*.

## Implementation stress and fix

A local mirror of the three-lens module was checked over **10,000 seeded random rational radii × six named transformations × six probe positions = 360,000 point comparisons**, using exact rational oracle calculations; no discrepancies found. Seed: 21023. JSON serialization and reconstruction of each defined output from sign and magnitude also passed.

Found and fixed an input-handling defect: non-string cardinality selections (e.g. empty lists and objects) previously produced Python TypeError instead of an explicit validation ValueError.

**116 local regression methods passed:** 105 existing equation-family package tests plus 11 new adversarial comparison tests. This is not a complete full-repository integration or GitHub CI run; the separate 18-test triad suite was not executed by this local mirror.

## Decision and follow-up

Three-lens sampling is preferable in this *specific tested black-box task* when looking for symmetric-wing sign loss, but loses within-wing resolution relative to a one-direction design. Recommended next step: add held-out/adaptive interior probes plus negative counterparts for symmetry, and clearly separate **matched samples**, **verified symbolic identity**, and **unknown beyond samples**. No fixed number of samples establishes a general proof without assumptions about the function class.
