# Two-Eyed Ouroboros Engine

A standalone Python 3.10+ research prototype for exact finite-state Lens analysis. No third-party dependencies.

## Run

```sh
python ouroboros.py
python ouroboros.py --size 24 --moduli 4 6 --state 13
python ouroboros.py --size 15 --moduli 3 3 5 --state 13
python -m unittest -v
```

The CLI reports observations, surviving candidates, the minimum worst-case fixed-length supplementary code, reconstructed state, per-Lens information gain, and the smallest sufficient Lens subsets. Custom deterministic Lenses can be defined in Python with `Lens(name, observe)` and `Ouroboros(domain, lenses)`. The domain must be finite, ordered, distinct and hashable; Lens observations must be hashable. Encoder and decoder share the domain, order, and Lens definitions. Search is exhaustive within the configured Lens and work limits. Ctrl+C interrupts execution. No persistent data is modified.

## Results and mathematical basis

For modular observations with positive moduli m_i, two integers give identical observations exactly when their difference is divisible by every m_i, equivalently by L = lcm(m_i). On 0,...,N-1 the largest ambiguity fiber has ceil(N/L) members, giving ceil(log2(ceil(N/L))) supplementary bits. Full reconstruction from observations alone is possible iff N <= L. This is standard modular arithmetic, not a novelty claim.

For arbitrary Lenses the engine enumerates fibers and gives each state a zero-based rank inside its fiber. The largest fiber determines the minimum fixed-length supplementary width by counting. The trace also reports conditional entropy under a uniform source, which is a separate average information measure.

Seven test methods pass, including exhaustive tests over 2,048 configurations (two moduli 1–8, domain sizes 1–32) and 33,792 exact round trips in that grid, plus additional targeted tests for redundant Lenses, noncoprime moduli, token reconstruction, invalid codes and arbitrary custom Lenses.

See [Ouroboros Compression Theorem](../research/2026-11-27_ouroboros_compression_theorem.md).

## Limitations

No claim of net file compression: observation values, codebooks, ordering and metadata have storage costs. No proof of a universal physical invariant. Subset search is exponential in the worst case and is capped. This standalone prototype is not yet integrated into the Ultimodel browser.
