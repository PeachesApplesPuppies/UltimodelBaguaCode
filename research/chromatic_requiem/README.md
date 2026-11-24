# Herzog's Chromatic Requiem — v1.0

BCE / UltimodelBaguaCode research. Ratio first; addition secondary. This is an exploratory representation of the YanRiemann Requiem, not a proof of RH.

## Run

Python 3.10+ with NumPy: `python -m pip install -r requirements.txt`

`python engine.py --limit 1000000 --samples 20001 --out output`

Outputs `chromatic.csv` (time, kernel, exact rational representation of the computed floats, normalized value, and lossy RGB hex preview) and `results.json`. Ctrl+C interrupts the calculation; the CSV and JSON are individually replaced only after their temporary files are fully written. An interrupted run may leave temporary files or outputs from different runs. The output is numerical, not interval-certified. Increasing limit increases memory use approximately linearly.

## Ratio algebra

For real C(t), with fixed C(0)>0, encode R:B:G = max(C(t),0):max(-C(t),0):C(0). Decode q=(R-B)/G. Common positive scaling leaves q unchanged. A ratio is confined precisely when R+B <= G; this is a necessary condition of positive definiteness, not a general sufficient condition for it. Addition of kernel values is optional; it is not needed to encode or change ratios. The symbolic primitive palette enumerates nonnegative integer triples with gcd 1, a countably infinite set (e.g. (n,1,0)). This does not establish prime factorization under ratio changes or infinitely many perceptible colors. Hex previews use RGB order (R,G,B), maximum-channel scaling and 8-bit rounding; they are deliberately lossy. Exact rational encodings preserve the input float, not an unknown exact transcendental kernel value.

## Arithmetic and proof audit

For x=exp(|t|), let H(x) = sum_{n<=x} Lambda(n)(x/n-1) - x log x + (1+EulerGamma)x - log(2pi) + sum_{k>=1} x^(-2k)/(2k(2k+1)). The arithmetic kernel is C(t)=H(x)/sqrt(x), as in the earlier Requiem test. C(0)=2+EulerGamma-log(4pi)>0. The classical integrated explicit formula identifies C(t) with sum over nontrivial zeros of exp((rho-1/2)|t|)/(rho(1-rho)), counting multiplicities. The zero series converges absolutely on compact t intervals by the classical zero counting estimate. Under RH these are positive coefficients on real frequencies, so C is positive definite and |C(t)|<=C(0).

Conversely, assume |C(t)|<=C(0) for all real t. Then int_1^infty H(x)x^(-s-1)dx is holomorphic for Re(s)>1/2 by domination. Initially Re(s)>1, the prime sum contributes -(zeta'/zeta)(s)/(s(s-1)), by absolute convergence and integrating x/n-1 from n to infinity. The remaining elementary terms contribute meromorphic terms with poles only at 1, 0, and negative even integers; these have no pole at a right-side nontrivial zero rho. Such a zero of multiplicity m contributes the nonzero residue m/[rho(1-rho)], impossible in the holomorphic region. Reflection excludes left-side zeros. Thus for this specific kernel, global color confinement is equivalent to RH. It is not established by the ratio encoding or finite tests. No novelty claim.

References: classical explicit formula and zero counts, https://dlmf.nist.gov/25.16 ; https://dlmf.nist.gov/25.10 . Previous YanRiemann arithmetic implementation: requiem_tests.py (prior research). Related formulation: research/ChatGiblet_Hypothesis.md.

## Tests

A seeded random test of 100 matrices of size 12 checks numerical positive semidefiniteness, not global positivity. Exact rational round trips and common scaling check 1,001 values. The synthetic cosh(delta*t)cos(14*t) proxy at phase returns tests five growth rates including zero; these are not actual zeta zeros. A hex collision explicitly shows loss of ratio information. The finite palette through sum 25 is enumerated without duplicates. See results.json for the executed default run.