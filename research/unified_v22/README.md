# BCE v2.2 — unified regression and proof audit

All 21 archived stage entrypoints were run in isolated directories. The first pass used 12-second per-stage timeouts, then incomplete stages were retried with 25 and 45 seconds. All 21 eventually exited successfully. This checks program execution, not the truth of RH or independent certification of numerical results. Later stage regressions may use archived input data, as in original source; these are not a single end-to-end pipeline.

## Run
Install Python dependencies: `python -m pip install numpy scipy sympy mpmath`. Run `python renormalization.py` for the new tests. For the full suite, obtain the original BCE_Unified_Proof_Audit_v22.zip distributed in the research conversation, extract each archive into a directory matching the corresponding name in run_all.py (archive layout varies), put the v0.1 script beside those directories, and run `python run_all.py PATH_TO_SOURCE_ROOT`. Set BCE_TIMEOUT and BCE_WORKERS environment variables to change the per-stage limit and concurrency. Ctrl+C interrupts the runner; child processes may take until their configured timeout to finish if the interrupt is received by the parent alone. Do not claim immediate global shutdown. Archived inputs are not modified.

This GitHub publication contains the consolidated audit, runner, new experiment, and final execution summary. The original binary archive containing all earlier source and fresh logs is not included in this commit.

## Joint multiplicative-path proof audit
F(x)=theta(x)-x, D_q(x)=F(qx)-F(x). For any function F, D_p(qx)+D_q(x)=D_q(px)+D_p(x)=D_pq(x). Thus all path identities are algebraic, regardless of prime arithmetic. New tests: all ten pairs of bases 2,3,5,7,11, 587875 sample points in total, maximum discrepancy 1.78e-15. Exact control F(x)=x^(2/3) on cube arguments and cube dilations passed 1000 cases despite violating the required growth. It also satisfies the identity analytically for arbitrary positive real scales. Its D_q energy from 1 to X is (q^(2/3)-1)^2 * 3/7 * (X^(7/3)-1), incompatible with O(X^(2+2 epsilon)) for epsilon<1/6.

## Sufficient bound and proof
If for a fixed q>1 and every epsilon>0, int_1^X |D_q(x)|^2 dx <= C_e X^(2+2e), telescoping gives F(x)=sum_{k>=1}D_q(x/q^k) because F(0+)=0. For terms x/q^k>=1, their L2 norm on [1,X] is <= sqrt(C_e) X^(1+e) q^(-k(1/2+e)). For the remaining tail, F(y)=-y for y<1, so it is O(1) pointwise (the sum telescopes). Minkowski then yields int_1^X |F|^2 = O_e(X^(2+2e)). Higher prime powers contribute O(sqrt(x) log x), so the same bound holds for E=psi-x. For sigma>1/2, choose e<sigma-1/2 and sum dyadic weighted energies to obtain int_1^infty |E(x)|^2 x^(-1-2sigma) dx < infinity. Cauchy-Schwarz gives holomorphy of int_1^infty E(x)x^(-s-1) dx for Re(s)>sigma. The exact identity Z'/Z=1-s times that integral, Z=(s-1)zeta(s), initially Re(s)>1, excludes zeros to the right of 1/2 by continuation. Functional symmetry excludes those to the left. Conversely RH gives E=O_e(x^(1/2+e)), hence the doubling energy bound. Reference: https://dlmf.nist.gov/25.16.

The required unconditional estimate on D_q is NOT established. All path identities hold for countermodels with forbidden growth. The earlier finite region counts, moment tests, Li coefficients, Gram positivity, and coercivity do not supply it. No RH proof or novelty claim. The artificial controls are not counterexamples to RH itself.

Research collaboration: repository owner and ChatGPT, November 23, 2026 (US Eastern time).
