# Ultimodel’ — Triadic HEX 1:3:9:... Experiment

**Executed:** November 23, 2026. **Status:** tested prototype; 21/21 unit tests passed. **Source:** the user-provided `ALittleLightMusic.mp4` (not redistributed). Includes synthetic controls and whole-file compression baselines. Run data in `results.json` and `long_repeat_results.json`.

## Hypothesis and method

Recursively split each node into three ordered child blocks. At the leaf, test raw storage, zlib/Brotli, HEX 6+2, XOR, and bitshuffle methods. Select the smallest payload. Intern identical leaf blocks and identical interior subtrees so they can be referenced more than once. Preserve all node metadata, lengths, hashes, and transformation IDs in the compressed file. Decode the `.ut3` with no access to the original source. All reported archive sizes include the complete decoding metadata.

## Actual MP4 — 33,028,976 bytes

| Codec and setting | Complete bytes | Percentage saved from original | Verified |
|---|---:|---:|---|
| Whole-file Brotli q9 (reference) | **32,493,332** | **1.6217%** | Yes |
| Prior Adaptive HEX q9 (earlier report) | 32,499,550 | 1.6029% | Previously reported |
| Triadic HEX depth 0, q9 | 32,493,437 | 1.6214% | Yes |
| Triadic HEX depth 5, q9 | 32,520,892 | 1.5383% | Yes |
| Prior Adaptive HEX q5 (earlier report) | 32,514,744 | 1.5569% | Previously reported |
| Triadic HEX depth 0, q5 | 32,526,132 | 1.5224% | Yes |
| Triadic HEX depth 1, q5 | 32,526,514 | 1.5213% | Yes |
| Triadic HEX depth 2, q5 | 32,520,079 | 1.5408% | Yes |
| Triadic HEX depth 3, q5 | **32,515,322** | **1.5552%** | Yes |
| Triadic HEX depth 4, q5 | 32,521,068 | 1.5378% | Yes |
| Triadic HEX depth 5, q5 | 32,535,492 | 1.4941% | Yes |
| Triadic HEX depth 6, q5 | 32,584,422 | 1.3460% | Yes |
| Whole-file Brotli q5 | 32,598,832 | 1.3029% | Yes |

**Interpretation:** At Brotli-quality setting 5, depth 3 is the smallest tested tree archive; it beats whole-file Brotli q5 by 83,510 bytes, but the previous non-tree Adaptive HEX q5 still beats it by 578 bytes. Crucially, **the overall best verified file is ordinary whole-file Brotli q9**, smaller than our best tree archive by 21,990 bytes at q5 (or 105 bytes smaller than the tree's depth-0 q9 payload, exactly the tree wrapper overhead). We have **not** established a superior video compressor.

## 3 MiB deterministic controls

Controls were constructed using `random.Random(20261123)`; each row stores exact full `.ut3` archive sizes. The rows show whole-file Brotli q5 for comparison.

| Control | Whole Brotli q5 | Triadic depth 0 q5 | Depth 1 q5 | Depth 3 q5 | Depth 5 q5 |
|---|---:|---:|---:|---:|---:|
| Pseudorandom bytes | 3,145,737 | 3,145,833 | 3,145,980 | 3,147,744 | 3,163,620 |
| Repeated short text | 19 | 124 | 306 | 1,527 | 2,799 |
| Three repeated 1 MiB random blocks | 1,048,601 | 1,048,706 | 1,048,734 | 1,049,322 | 1,054,614 |
| 6+2 high-bit pattern | 3,145,740 | 2,361,546 | **2,359,622** | 2,362,370 | 2,388,218 |
| Random + 6+2 pattern + repetitive | 1,988,465 | 1,838,036 | **1,835,345** | 1,837,406 | 1,852,213 |

All 20 control tree archives reconstructed exactly and passed SHA-256 comparison. **Splitting helps some structured inputs, but deep trees have overhead, and repeated content alone does not automatically beat Brotli.**

## Separate long-range repetition: a conditional deduplication win

Constructed three copies of the *same* seeded 6 MiB pseudorandom block (18,874,368 bytes total). An ordinary whole-file Brotli q5 stream remained almost the original size, because the repeated sections are farther apart than its effective match window in this configuration. The ternary tree recognized all three leaf blocks as identical, stored the block once, and referenced that single leaf three times.

| Method | Size |
|---|---:|
| Raw 18 MiB input | 18,874,368 |
| Whole-file Brotli q5 | 18,874,405 |
| Triadic depth 1 archive | **6,291,614** |

The decoder used the `.ut3` alone, returned all 18,874,368 bytes exactly, and verified SHA-256 `d7f237d99df8ad21edad4f2dbaa353d1316e713ef31c8775b361b5f7a05a3b21`. This is **66.6658%** smaller than the original **for this engineered input**. A conventional deduplicating archiver or a compressor with a long enough matching window might achieve similar benefits. It is not evidence of a new universal algorithm.

## Test inventory and qualifications

- **21/21 regression methods** passed using Python `unittest`, including *all 65,536 ordered two-byte pairs*, all 256 byte values, many input lengths/depths, three-way repeated leaves, repeated subtrees, source-deleted decoding, corrupted payloads, malformed headers, truncated archives, type IDs, preservation of output when decoding fails, and source-overwrite protection.
- **29/29 benchmark tree archives** decoded byte-for-byte with matching SHA-256 (9 actual video trials + 20 synthetic control trials), plus the long-repetition trial.
- Independent ordinary Brotli baselines were fully decompressed and byte-compared.
- SHA-256 is used for practical integrity checks; it is not an unconditional logical guarantee against collisions. The encoder checks actual equality before interning duplicate leaves.
- The video was already encoded with lossy H.264/AAC. This is **lossless preservation of the existing MP4 bytes**, not recovery of information discarded by its original recording codec.
- **No physical audio/light transmission or new physical law was tested**.

## Next technical question

Could a variable-depth tree choose split/leaf boundaries jointly using dynamic programming and a fixed optimization budget? That would avoid forcing a bad depth on data and would offer a fairer comparison against established content-defined chunkers, zstd long-distance matching, and deduplicating backup formats. Include CPU, memory, and metadata costs in those comparisons.
