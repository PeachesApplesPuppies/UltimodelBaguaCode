# AutoDepth Triadic HEX — verification and benchmark report

**Date:** November 23, 2026. **Source:** `ALittleLightMusic.mp4` supplied by the user, not redistributed. **Implementation:** bounded per-region split-or-leaf planner using the exact same archive format and decoder as Triadic HEX v0.1. **Compression level:** Brotli quality 5 except where noted.

## Executed tests

- `python -m unittest discover -s . -p 'test_*.py' -q`: **36/36 passed**, covering the existing 21 Triadic HEX tests and 15 new AutoDepth tests.
- The **65,536 ordered two-byte patterns** were exhaustively processed within a test.
- The decoder reconstructed archives **after the original inputs were deleted** in the test harness.
- Corrupt archives and invalid format/parameters were rejected; destination overwrite guard verified.
- Randomized, aligned-boundary, deterministic replay, and deduplicated-node accounting tests passed.
- Actual MP4 archive was reconstructed using the *unchanged* Triadic HEX decoder, with complete byte equality and matching SHA-256.

## Actual video test (Brotli quality 5)

| Method | Entire archive bytes | Notes |
|---|---:|---|
| Original MP4 | 33,028,976 | already H.264/AAC-encoded |
| Fixed Triadic HEX depth 0 | 32,526,132 | best leaf codec |
| Fixed Triadic HEX depth 3 | 32,515,322 | best fixed depth among 0..6 in prior full depth scan |
| Earlier Adaptive HEX v0.1 | 32,514,744 | earlier q5 report |
| **AutoDepth max depth 4** | **32,513,441** | min leaf 131072, balanced, split budget 1000 |
| Whole-file Brotli q5 | 32,598,832 | simple one-stream reference |
| Whole-file Brotli q9 | **32,493,332** | **still beats all of the above** |

The AutoDepth result saves **1,881 bytes** relative to the best tested fixed-depth tree at q5, or **1,303 bytes** relative to the previously recorded block-adaptive q5 archive. It used **19 unique stored leaves and 9 unique internal branch nodes**; the selected tree reaches depth 4, but not all branches reach that depth. It was produced in approximately 23 seconds in this sandbox (not a formal performance guarantee). The MP4 data was read only as raw bytes; no video frames were decoded by this compressor.

## Structured controls

| Case | AutoDepth archive | Chosen depth | Outcome |
|---|---:|---:|---|
| Three copies of 2 MiB seeded random data (6 MiB) | 2,097,286 bytes | 0 | Brotli already exploited repetition; branching added no value |
| Mixed 3 MiB random/HEX-structured/text | 1,835,194 bytes | 0 | chose leaf; transforms already exposed redundancy |
| Three copies of 6 MiB seeded random data (18 MiB) | **6,291,614 bytes** | 1 | one unique shared leaf; exactly reconstructed 18 MiB |
| Aligned-boundary 3 MiB synthetic case | 1,048,879 bytes | 0 | tested extra alignment candidates; they were not beneficial |

These synthetic controls were selected to test specific representations. The 18 MiB repetition case illustrates content deduplication, which is existing computer-science technology; no claim of originality or universal superiority follows.

## Interpretation

This is a **real improvement** in a narrowly specified benchmark: automatic depth decisions choose a better `.ut3` size on the supplied MP4 at the same compression quality. The gain is small (~0.006% of the original video). It does **not** outperform the stronger whole-file Brotli q9 setting, and a fair comparison across compressors must consider speed, memory and equalized search budget as well as archive size.

The planner is a bounded local optimizer, not an optimal global ternary partitioning theorem. More sophisticated search, content-defined chunking, arithmetic coding and established deduplicating compressors are legitimate future baselines.
