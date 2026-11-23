# Adaptive HEX v0.1 — reversible, block-wise file compression

**Status: experimental research codec; not a new general-purpose video codec or a universal compression breakthrough.**

The encoder splits a file into blocks. It tries eight candidates per block: store raw, zlib, Brotli, HEX 6+2 split with zlib/Brotli, previous-byte XOR with zlib, XOR then 6+2 with zlib, and 8-bit-plane transpose with zlib. It stores whichever encoded candidate is smallest, recording the transform and compressor IDs. A 32-byte SHA-256 for each original block and a file-wide SHA-256 are included in the archive. A separate decoder reconstructs the original file **from the `.uhx` archive alone**.

The 6+2 transformation is the project's earlier lossless split of every byte into six low bits plus two retained high bits. It is not compression by itself. The adaptive selector and its container metadata add overhead. The design does not guarantee smaller output, especially for short or high-entropy files.

## Installation

Python 3.10+:

```bash
python -m pip install -r experiments/adaptive_hex/requirements.txt
python experiments/adaptive_hex/adaptive_hex.py encode myvideo.mp4 myvideo.uhx
python experiments/adaptive_hex/adaptive_hex.py decode myvideo.uhx recovered.mp4
python -m unittest discover -s experiments/adaptive_hex -p 'test_*.py' -v
```

Use `--brotli-quality 9` for the tested higher-effort setting, or `--block-size 65536` to explore smaller blocks. Default block size is 1 MiB and Brotli quality 5. All encoding choices are deterministic with the same software version, library versions and settings. The codec operates on the **existing file bytes**, so it does not reconstruct video or sound lost by H.264/AAC encoding.

Benchmark, if you have a local video file:

```bash
python experiments/adaptive_hex/benchmark.py /path/to/ALittleLightMusic.mp4
```

This benchmark includes several deterministic synthetic controls. Its files are temporary and removed after each trial. The resulting JSON records all archive sizes and exact-byte verification results. The original video file is **not included** in the repository.

## Format and validity

The archive is `ULTADP01` plus version, block size, block count, original size, full-file SHA-256, followed by each block's transform ID, codec ID, original bytes count, compressed bytes count, original-block SHA-256, and payload. Everything needed for reconstruction is inside the archive.

Decoder checks format, block count/lengths, known operations, payload length, block hashes, whole-file hash and absence of trailing bytes. The output is written into a same-directory temporary file and moved into place only after successful verification. Input and output paths must differ. Encoding also writes atomically and detects changes to the source during its two passes.

Limits: maximum block size 8 MiB, maximum 1 million blocks. This prototype is **not hardened for untrusted attacker-crafted archives** and uses ordinary SHA-256 rather than an authenticated signature. It has no self-repair, encryption, or resilience to the loss of its only complete archive. Brotli decoding uses bounded blocks but decompression of adversarial payloads can still consume substantial resources. Compare byte-exact recovery and total archive sizes, not merely the compressed payload lengths.

## Scope of the verified claim

We established that this implementation **reconstructs its accepted inputs exactly** in the regression suite and the tested files. The benchmark is a measurement of existing codec combinations chosen adaptively. No novel entropy-coding theorem or universal space advantage is claimed. The test report separates wins on deliberately structured controls from the results on the supplied H.264/AAC MP4.
