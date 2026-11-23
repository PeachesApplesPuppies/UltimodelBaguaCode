# Ultimodel AutoDepth Triadic HEX — v0.2 experimental extension

**Status:** working, locally tested branch calculator, built on the previously published Triadic HEX v0.1. Uses the **same `.ut3` format and decoder**. This is a reversible byte archiver, not an MP4 video codec or a universal information compressor.

## What was already implemented?

A repository audit on November 23, 2026 found:

- **Adaptive HEX v0.1 (PR #4):** picks raw/zlib/Brotli/HEX/XOR/bitshuffle transformations separately per **fixed-size block**. It does not have a tree or optimize split depth.
- **Triadic HEX v0.1 (PR #5):** builds fixed-depth 1:3:9… ternary trees, interns identical leaves/subtrees, and picks a reversible leaf codec. All nontrivial branches are forced to the same requested depth unless they contain fewer than three bytes.
- **AutoDepth v0.2 (this change):** reuses Triadic HEX code and on-disk format, but *locally* compares stopping at a node against subdividing that node into three children. Different branches can stop at different depths.

This is **adaptive splitting + deduplication**, not something we can claim nobody has invented: chunking, dynamic programming, Merkle-DAG-like structures and deduplication have substantial prior art.

## The calculator

For each candidate region of the input:

1. Compute the smallest supported reversible leaf representation using the existing `best_leaf` method (raw/store, zlib, Brotli, reversible HEX 6+2, XOR and bitshuffle options).
2. If within the maximum depth, minimum child-size and split-exploration budget, try dividing into three consecutive children.
3. Recursively obtain the locally best child plans.
4. Count **complete archive bytes**, including unique payloads, node metadata and deduplicated references, for the leaf option and the split option.
5. Keep the cheaper plan. Internal nodes can share identical leaves or entire subtrees; the serialized DAG includes exact child order and full source hashes.
6. Optionally test block-aligned split points (4 KiB and 64 KiB) in addition to balanced thirds.

**Important optimization boundary:** This is a deterministic bounded *greedy bottom-up planner*, not a proof of the globally smallest possible encoding. It optimizes among the candidate splits visited under the child plans already selected. Changing a child plan could sometimes enable more deduplication with a distant sibling. It does not examine arbitrary split positions, all transformation orders, or all encoding schemes.

### Usage

Install from the repository root:

```bash
python -m pip install -r experiments/triadic_hex/requirements.txt
```

Preview branch choices **without keeping an archive**:

```bash
python experiments/triadic_hex/autodepth_hex.py plan video.mp4 --max-depth 4 --min-leaf 131072 --quality 5
```

Create an actual archive and restore it using the unchanged Triadic HEX decoder:

```bash
python experiments/triadic_hex/autodepth_hex.py encode video.mp4 video.ut3 --max-depth 4 --min-leaf 131072 --quality 5
python experiments/triadic_hex/triadic_hex.py decode video.ut3 recovered.mp4
```

Try two alternative boundary alignments:

```bash
python experiments/triadic_hex/autodepth_hex.py plan video.mp4 --max-depth 3 --min-leaf 131072 --quality 5 --boundary-mode aligned
```

`plan` creates an ephemeral candidate archive to measure its exact size, then discards it. It performs the same expensive compression exploration as `encode`.

Flags:

- `--max-depth`: maximum *possible* ternary levels; each branch may stop sooner (0–12).
- `--min-leaf`: minimum allowed bytes in each child for a split (default 65,536).
- `--quality`: Brotli quality for **each candidate leaf**, default 5 (0–11).
- `--boundary-mode`: `balanced` (one candidate pair of thirds) or `aligned` (also try 4 KiB/64 KiB-aligned positions).
- `--max-evaluations`: maximum *split expansions* (default 500), not an absolute upper bound on leaf compressor invocations, elapsed seconds, or total memory. The output reports both expanded and evaluated regions.

The JSON output includes `chosen_depth`, `logical_leaves_by_depth`, `branch_trace` (first 128 logical decisions and their root.0.1-style addresses), source offsets, coding method, node counts, and full-file SHA-256.

## Reproducibility

```bash
python -m unittest discover -s experiments/triadic_hex -p "test_*.py" -v
```

36/36 regression test methods passed locally (21 original triadic + 15 new AutoDepth). The new tests cover exhaustive two-byte input combinations, various lengths and deterministic random inputs, source-deleted recovery, exact hash checks, incorrect parameters, corrupted archives, overwrite protection, depth limits, aligned boundary candidate generation, dedup cost accounting, and strict split-exploration limits.

The real-video benchmark source `ALittleLightMusic.mp4` was supplied by the user and is **not** distributed. The public `autodepth_results.json`, `extra_auto_results.json`, and `final_video_results.json` contain reproducible metrics and hashes, not audiovisual content.

## Safety and scientific boundaries

- Original data bytes or a losslessly equivalent representation must be preserved somewhere; **hashes alone cannot restore data**.
- Decoder must receive an unmodified `.ut3` archive. Full SHA-256 checks detect practically relevant corruption; they are not logical guarantees against all cryptographic collisions.
- Source files are loaded into memory; v0.1 limits source size to 256 MiB. Very deep and high-quality searches can be costly.
- AutoDepth does **not** guarantee the archive is smaller than its input or smaller than the best standard compressor.
- Results are for already encoded MP4 *bytes*, not a new lossless encoding of raw video frames.
- The historical HEX naming is project vocabulary. Reversible transforms and DAGs are familiar established mathematics/computer science.
