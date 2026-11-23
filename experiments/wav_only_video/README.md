# Lossless MP4 → data-WAV → identical MP4

**Purpose:** reproduce the November 23, 2026 Ultimodel experiment in which a complete 33 MB MP4 was encoded into a PCM WAV and then reconstructed **from the WAV alone**, byte-for-byte.

## Critical distinction

There are **two different WAVs** one could make from a video:

1. **Audio soundtrack WAV:** contains only the sound. The original visual frames and video metadata are absent. The exact MP4 cannot generally be recovered.
2. **Data-carrying WAV (this experiment):** stores **every original MP4 byte** as one canonical PCM16 audio sample, plus a version, original length, and SHA-256 header. Reversing that encoding recovers the entire original file. This WAV is *not* the soundtrack; if played through speakers, it is data-as-audio.

The second encoding is like wrapping bytes in a WAV container, not synthesizing visuals from acoustic waves. It is **not compression**: the 33,028,976-byte input becomes a 66,058,094-byte WAV (approximately double the size).

## Files

- `lossless_video_wav.py`: standalone streaming encoder and decoder (uses NumPy).
- `test_lossless_video_wav.py`: 15 regression methods; synthetic fixtures only, no copyrighted footage.
- `verification.json`: original experiment's file sizes, hashes, and locally executed checks.
- `requirements.txt`: NumPy dependency.

The original/reconstructed MP4, extracted soundtrack WAV, and 63 MB data-WAV are deliberately **not included** in this public repository because the redistribution rights of the source video have not been established. No video is needed to run the synthetic tests; the original source video is required to reproduce the exact **same** media experiment.

## Run on your machine

From the root of the GitHub repository:

```bash
python -m pip install -r experiments/wav_only_video/requirements.txt
python experiments/wav_only_video/lossless_video_wav.py encode ALittleLightMusic.mp4 video_data.wav
python experiments/wav_only_video/lossless_video_wav.py decode video_data.wav recovered.mp4
python -m unittest discover -s experiments/wav_only_video -p "test_*.py" -v
```

The decoder accepts the data-WAV as its **only input**. For a stricter experiment, first move or remove the original MP4 after the encoding completes, then decode the WAV into a new filename. The code accesses no original-video path while decoding.

To verify equality on a system with SHA-256 tools:

```bash
sha256sum ALittleLightMusic.mp4 recovered.mp4
```

Both should read:

```
615a72af951d8c4833bca80dc7a569340abdfca2b4574af9b1e72302f580b8ca
```

## Protocol details

Container convention v1:

- WAV: RIFF/WAVE, PCM16, mono, 48,000 frames/s.
- A source byte `b` in 0..255 maps to signed sample `(b - 128) * 256`. This is one-to-one.
- Each original source byte consumes two bytes of WAV PCM storage.
- The first 49 PCM samples represent the packed header `<8sBQ32s`: magic `ULHXLWAV`, version `1`, little-endian unsigned original byte length, and 32-byte SHA-256 digest.
- The decoding path checks WAV format, header, canonical sample encoding, exact payload frame count, and SHA-256 before atomically moving a temporary output into place.
- Both encoding and decoding reject identical input/output paths to protect against accidentally destroying the only remaining copy.
- The WAV RIFF format imposes practical size limits; this v1 prototype does not support arbitrary-size files over those limits. This format is not a secured or error-correcting communication protocol.

## Verified results and boundaries

In the original local run:

- Original source: **33,028,976 bytes**.
- Encoded data WAV: **66,058,094 bytes**.
- Recovered MP4: **33,028,976 bytes**, identical to original on a complete byte comparison.
- Original and recovered SHA-256: **615a72af951d8c4833bca80dc7a569340abdfca2b4574af9b1e72302f580b8ca**.
- WAV-only decoder rerun in a separate temporary destination produced the same byte count and hash.
- **15/15 regression methods passed**, including exhaustive two-byte fixture coverage (all 65,536 pairs), source-deleted reconstruction, random sizes, exact byte roundtrips, corruption detection, truncated data, Unicode paths, and accidental-overwrite protection.

**What this proves:** this particular mapping is lossless for accepted data when the data-WAV survives unmodified, and the tested MP4 was reconstructed exactly.

**What it does not prove:** that the audio soundtrack contains the lost video; that light and music are physically identical; or that a generic lossy audio edit or transcoding will preserve the data-WAV. Recompressing, volume-adjusting, normalizing, resampling, or converting the data-WAV to MP3 will generally destroy its encoded information.

The checksum detects the tested corruption; it is not a guarantee against adversarial substitution or all conceivable hash collisions.
