# Three-lens infinity investigations

**Research status:** implemented deterministic probe and reference examples; not a general theorem prover, limit solver, or model of physical resonance.

## Three distinct mathematical subjects

1. **Signed real numbers:** For every real x, x = sign(x) × abs(x), with sign(0)=0. The magnitude alone cannot distinguish x from -x except at zero. Probe -R, 0, and +R together.
2. **Limits and unbounded growth:** A limit of f(x) as x approaches ±infinity or 0± describes a process, not an ordinary real input. The six supported transformations have pre-established limit labels; they are *not inferred* from a finite probe. Evaluating f(0), when defined, is not the same as taking a two-sided limit.
3. **Infinite cardinality:** |N|=|Z|=|Q|=aleph_0; |R|=|P(N)|=2^aleph_0; |P(R)|=2^(2^aleph_0). Cantor's theorem proves |P(S)|>|S| for any set S. Cardinality is the size of a set, **not** the absolute value of a signed scalar. These cardinalities have no positive/negative orientation.

## Investigate opposite wings and the middle simultaneously

For R>1, the local inspector evaluates each supported f at -R, 0, R, and -1/R, 0, 1/R using exact rational arithmetic. It reports input and output polarities, output magnitude, whether f(0) is defined, and whether the opposite-wing outputs coincide.

For example, f(x)=abs(x) maps -R and +R to the same number: a loss of polarity information. The pair (sign(x), abs(x)) can reconstruct x. For f(x)=1/x, zero is excluded from the domain; no value at zero may be invented from one-sided limits. For f(x)=sign(x), different positive magnitudes all map to +1, so magnitude information is lost.

A sample table also compares four sequences at every finite n:

- negative: -n -> -infinity;
- middle: 0 -> 0;
- positive: +n -> +infinity;
- alternating: (-1)^n n has **no extended-real limit**, while its magnitude is n -> +infinity.

The alternating claim is justified by the even subsequence 2k -> +infinity and the odd subsequence -(2k-1) -> -infinity. Both cannot share the same extended-real limit. Plotting eight samples only illustrates the already-proved result.

## Implementation

- Python standard library: core/infinity_triad.py
- Browser interface: ui/infinity_triad.html
- Routes: GET /triad and POST /api/triad
- Regression suite: tests/test_infinity_triad.py

To run: python app.py --open, then follow Both Sides + Middle; to test: python -m unittest discover -s tests -v.

Boundaries: only six explicitly implemented transformations; a positive rational R in (1, 1,000,000]; known set-cardinality comparisons, not arbitrary infinite-set inference; no direct proof of any cross-domain physical equivalence; undefined expressions such as infinity - infinity are never computed as ordinary scalar arithmetic.
