# Ouroboros — Unity/Riemann diagnostic and proof-compression notes
Date: 2026-11-27
Status: exact algebraic identity, previously reported exploratory tests (not independently audited here), open verification tasks.

## Exact identity
For s = beta + it, with real beta and t and s != 0, define U(s) = 1 - 1/s.
Then

    |U(s)|^2 = ((beta-1)^2+t^2)/(beta^2+t^2)
    |s|^2 (|U(s)|^2-1) = 1-2*beta.

This follows directly by subtracting the denominator from the numerator. Thus |U(s)| = 1 iff beta = 1/2. For fixed beta, |U(s)| tends to 1 as |t| tends to infinity even when beta differs from 1/2. Rounded unity is not sufficient evidence of exact critical-line membership. The weighted expression retains the real-coordinate deviation; for numerical stability evaluate the simplified expression where beta is known. This is an identity for all nonzero s, not a proof that zeta zeros satisfy it with zero deviation.

If both t and the exact weighted deviation d are retained, beta = (1-d)/2 reconstructs s. This is complementary-coordinate reconstruction, not a proof of RH.

## Previously reported exploratory tests
The conversation reported 30 synthetic coordinates (24 off the critical line), 210 exact reconstruction checks, six-decimal rounding producing apparent unit magnitude for 14 of those 24 off-line controls, and evaluation of 20 known critical-line zeros at 40-digit working precision. The exact original test grid, raw outputs and executable script are not available in this publication session. These figures are archived as reported, not independently reproduced. They cannot establish RH. Testing zeros already selected on the critical line is only a consistency check.

## Reproducible future tests
- Specify exact rational beta and t grids and rounding conventions before testing.
- Compare direct rational arithmetic with floating-point evaluation of the unweighted and weighted deviations.
- Include synthetic off-axis points and symmetric off-axis zero-set controls; do not label synthetic points as actual zeta zeros.
- Distinguish a finite verified range of zeros from the universal RH statement.
- Independently audit the formal theorem statement, dependencies, permitted axioms and toolchain of any external Lean proof claim before relying on it. This note does not authenticate any claimed recent RH or GRH proof.

## Infrastructure
The repository already contains:
- [Proof compressor](../ouroboros_proof_compressor/README.md): bounded search over supplied lemma candidates, not arbitrary proof reduction.
- [Lean verification department](../lean_verification/README.md): lightweight starter and cloud workflow.

Actual verification of a full RH proof has not been performed by this project. Acceptance of a finite starter theorem would not prove RH. Proof text reduction, preservation of a formal theorem statement, mathematical validity under stated axioms and exact reconstruction of original proof text are distinct objectives.

**Preserve the distinction that the measurement can hide.**
