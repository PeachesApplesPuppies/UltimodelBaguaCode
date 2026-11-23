# Ultimodel Triadic HEX v0.1 — reversible 1:3:9:… data tree

A working prototype that partitions byte data into a ternary tree, stores shared leaf content / identical subtrees once, and selects the smallest complete leaf encoding from eight existing methods. The encoded `.ut3` archive contains all required node references, exact lengths, checksums, compressed payloads, and metadata necessary for reconstruction **without the source file**.

**Important:** This is an experimental lossless *byte-file archiver*, not a new video codec. It doesn't recover footage from an audio soundtrack or prove that reality is light/music. Content hashes identify blocks and validate reconstruction; they do not substitute for the original unique payloads. This design reuses known deduplication, tree/DAG, compression and hashing ideas.

## Install

```bash
python -m pip install -r requirements.txt
```

## Encode and decode (source MP4 not included)

```bash
python triadic_hex.py encode ALittleLightMusic.mp4 video_depth5.ut3 --depth 5 --quality 5
python triadic_hex.py decode video_depth5.ut3 reconstructed.mp4
python -m unittest -v test_triadic_hex.py
```

A depth of 5 corresponds to at most `3^5 = 243` leaves and `364` total nodes in a full ternary tree. Actual archives may have fewer **unique** nodes due to deduplication. Leaf length differs by at most one byte when each node splits. Splitting stops early if the node has fewer than three bytes.

To verify a copy when the original remains available:

```bash
sha256sum ALittleLightMusic.mp4 reconstructed.mp4
```

Their SHA-256 values must match. The decoder also checks its internal root SHA-256 and every leaf and internal node hash before accepting an output file.

To benchmark the reference video and generate deterministic synthetic controls:

```bash
python benchmark.py /path/to/ALittleLightMusic.mp4
```

This script conducts 29 tree encode/decode runs and whole-file Brotli controls. It can take several minutes on slow hardware. It outputs `results.json` and removes all created copies/archives after verification. Run the separate long-repetition demonstration by reproducing the method in `REPORT.md`, or inspect the included recorded `long_repeat_results.json`.

## Exact archive format

- Header: `>8sBBQII32s` = magic `ULTRIAD1`, version `1`, maximum depth, original byte length, unique DAG node count, root index, original SHA-256.
- Nodes stored in topological order, one per unique byte region or unique child tuple.
- Node header: `>BQ32s` = kind (`0` leaf / `1` branch), byte length, reconstructed node SHA-256.
- Leaf: `>BBI` = transformation ID, compression ID, byte length of payload, followed by compressed bytes.
- Branch: `>III` = three earlier child IDs in original order. The same child ID may occur repeatedly, representing a deduplicated reference rather than duplicate bytes.
- Candidate leaf encodings: raw store, raw zlib6, raw Brotli quality Q, HEX 6+2 with Brotli or zlib, XOR-previous with zlib, XOR+HEX with zlib, bitshuffle with zlib.
- The HEX 6+2 transform stores all eight source bits, separating the lower six bits and upper two bits into independently packed regions.

### Losslessness argument

Every leaf method has an exact inverse on supported inputs. Every internal node combines three ordered child outputs by concatenation. Identical subtrees share stored nodes only after their reconstructed content is checked for byte equality (or established from identical children). Structural induction shows that following the root reconstructs the original byte string for a valid archive. The program additionally checks block hashes, tree depth, references, byte counts, and the original root hash. Testing cannot prove a program bug-free, and SHA-256 collision resistance is not absolute proof of accidental or adversarial correctness.

## Limits

- Maximum input size in this prototype is 256 MiB. It currently reads the input into RAM and is **not** suited to multi-GB video files.
- The archive format has a fixed maximum tree depth of 12 and node-count limit of 1 million.
- Repeated data may not help if an ordinary compressor already matches it effectively; tree metadata can make files larger.
- A tree can still expand entropy-rich data. No universal guarantee of positive compression exists.
- Treat untrusted files cautiously; this is research software, not a hardened archival standard.
- The source video and archives containing its bytes are deliberately **not distributed**.

See [REPORT.md](REPORT.md) and [results.json](results.json) for the actual measured outcomes.
