# Ouroboros Compression Theorem
BCE / Ultimodel / BaguaCode — 2026-11-27

> Discard redundancy. Preserve distinction. Recover identity.

**Status:** exact finite-state counting theorem and exhaustive computational examples. The project name and synthesis are proposed terminology; the counting argument is standard. No claim of novel information theory, universal file compression, or proof of RH.

## 1. Minimum complementary information

Let X be a nonempty finite state space and T:X→Y any deterministic representation. Assume T(x) is retained and the encoder and decoder share X, T, and the agreed ordering of each fiber. Write m = max over y in T(X) of |T^(-1)(y)|.

The minimum worst-case fixed-length number of supplementary binary digits required for exact reconstruction is

    b_min = ceil(log2(m)).

More explicitly, there exists an encoder I:X→{0,1}^b and decoder D on the encoded image such that D(T(x), I(x))=x for every x in X if and only if b≥b_min.

**Necessity:** a fiber of size m has the same retained representation for all its elements. The supplementary code must distinguish them. There are 2^b available codewords, so 2^b≥m.

**Sufficiency:** give each fiber a shared deterministic ordering. Encode the zero-based rank of x within its own fiber using b bits, padded with leading zeros. Given T(x) and that rank, the decoder looks up the original x. Unused ranks can be rejected. If m=1, the empty supplementary string suffices.

This is the finite quantitative version of [Herzog's Convergence–Identity Principle](../docs/herzog-convergence-identity-principle.md). It also formalizes the recovery constraint in the [Ouroboros scaling note](2026-11-27_ouroboros_scaling_invariant.md).

## 2. Exact exhaustive results

The pair domain is ordered pairs (A,B) with A,B in {1,...,16}, including equal pairs. Ratios are exact reduced positive integer pairs. Signed difference is B-A. Absolute magnitude here means |B-A|. Zero polarity means the calculator's shifted difference at multiplier zero, not normalized polarity. Ratio plus scale uses A+B. Token domains are ordered pairs of three-bit states, encoded as integers 0,...,7. The byte domain is 0,...,255.

| Retained representation | Domain size | Distinct outputs | Largest fiber | Minimum extra bits |
|---|---:|---:|---:|---:|
| Relative magnitude A:B | 256 | 159 | 16 | 4 |
| Signed difference B-A | 256 | 31 | 16 | 4 |
| Absolute magnitude | 256 | 16 | 30 | 5 |
| Zero shifted polarity | 256 | 1 | 256 | 8 |
| Ratio and original scale | 256 | 256 | 1 | 0 |
| BaguaCode XOR transition | 64 | 8 | 8 | 3 |
| BaguaCode Hamming distance | 64 | 4 | 24 | 5 |
| HEX lower six bits | 256 | 64 | 4 | 2 |

All eight expected minimum widths matched in the executed JavaScript enumeration. Every encoded state was reconstructed from its retained value and fiber rank: 1,664/1,664 round trips across the eight domains. The following standard-library Python reproduction implements the same algorithm and checks both round trips and the counting lower bound.

~~~python
from collections import defaultdict
from itertools import product
from math import gcd

pairs = list(product(range(1, 17), repeat=2))
tokens = list(product(range(8), repeat=2))
bytes_ = list(range(256))

def ratio(x):
    a, b = x
    g = gcd(a, b)
    return a // g, b // g

cases = [
    ("Relative magnitude", pairs, ratio, 16, 4),
    ("Signed difference", pairs, lambda x: x[1]-x[0], 16, 4),
    ("Absolute magnitude", pairs, lambda x: abs(x[1]-x[0]), 30, 5),
    ("Zero shifted polarity", pairs, lambda x: 0, 256, 8),
    ("Ratio and original scale", pairs,
     lambda x: (ratio(x), sum(x)), 1, 0),
    ("XOR transition", tokens, lambda x: x[0]^x[1], 8, 3),
    ("Hamming distance", tokens,
     lambda x: (x[0]^x[1]).bit_count(), 24, 5),
    ("HEX low six bits", bytes_, lambda x: x & 63, 4, 2),
]

total = 0
for name, domain, transform, expected_m, expected_b in cases:
    fibers = defaultdict(list)
    for x in domain:
        fibers[transform(x)].append(x)
    m = max(map(len, fibers.values()))
    b = (m-1).bit_length()
    assert (m,b) == (expected_m,expected_b)
    assert m <= 2**b and (b == 0 or m > 2**(b-1))
    for y, group in fibers.items():
        for rank, x in enumerate(group):
            code = format(rank, f"0{b}b") if b else ""
            assert len(code) == b
            recovered = fibers[y][int(code,2) if code else 0]
            assert recovered == x
            total += 1
    print(name, len(domain), len(fibers), m, b)
assert total == 1664
print("Round trips:", total)
~~~

## 3. Boundaries and application

- These are supplementary bits given the representation, not compressed file sizes. Encoding the representation, shared tables, framing and metadata may cost more than the original.
- A different domain or representation changes the fiber sizes. The result is worst-case and fixed-length; expected length with a known probability distribution and variable-length codes is a different question.
- No injective fixed-length encoder can represent all n-bit strings using fewer than n bits. A practical compressor must exploit source structure or a distribution, and account for every byte of overhead.
- Infinite domains with unbounded finite fibers, or an infinite fiber, admit no finite uniform bound of this form. The formula here is specifically for finite X.
- Recoverability is not necessarily preservation of a numerical magnitude, physical energy, or a periodic orbit. The decoder supplies a mathematical return to the original state.
- A practical next step for the instrument is an optional finite-domain fiber analyzer: report the largest ambiguity, supplementary width, and round-trip test separately from actual encoded storage. It is not implemented by this research note.

**Magnitude is the measurement. Relationship is the information. Recoverability is the constraint.**
