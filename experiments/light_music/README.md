# A Little Light Music — digital encoding experiment

**Status:** Reproducible computational demonstration, *not* a proof that reality is light or music.

## Aim

Use the Ultimodel / BaguaCode six-bit HEX representation and complementary provenance bits to study whether a **digitized audio signal** can be represented by an idealized **light-intensity code** and reconstructed without loss. This experiment uses numerical values for light intensity; it does **not** drive an optical emitter, measure photons, or test string theory.

## Test input and reproducibility

The source file was provided privately as `ALittleLightMusic.mp4`. **The video and extracted soundtrack are not included in this public repository.** This avoids redistributing the audiovisual work and keeps source provenance separate from the code.

Requirements:
- Python 3.10+ and `numpy`
- System `ffmpeg` on your PATH
- An accessible input video with audio at 240–242 seconds

From the repository root:

```bash
python -m pip install -r experiments/light_music/requirements.txt
python experiments/light_music/ultimodel_light_music_test.py "/path/to/ALittleLightMusic.mp4"
```

The script extracts 2 seconds of mono PCM audio at 8 kHz, 16 bits/sample, beginning at 240 seconds. It creates 16,000 samples (32,000 bytes), subject to the input containing that audio segment. It writes `run_results.json` beside the script. The exact PCM SHA-256 in the committed result identifies the tested *decoded excerpt*; a different edition/codec may give different bytes and should not be treated as an exact reproduction.

## Checks performed on this source

- **7/7 Python unittest cases passed**, locally re-executed on 2026-11-23.
- Exhaustive all-256-byte roundtrip through the `6+2` encoder/decoder.
- Exhaustive all-64-state six-bit complement and bit-reversal identities.
- All 32,000 source bytes survived normalization to idealized intensity `byte/255` and roundtrip to byte values.
- Truncating every source byte to six bits altered 19,157 byte values; keeping the additional two bits restored the original.
- The magnitude spectra of a real signal and its negation are equal; phase (and hence original sign/waveform) is not determined by magnitude-only FFT data.
- A full complex FFT and inverse FFT reproduced the exact 16-bit PCM excerpt **after rounding to integer samples**. This does not imply bit-perfect reversibility for every arbitrary floating-point FFT input or size.
- SHA-256 differed after every one of 2,500 randomly injected single-bit errors (seed 20261123). This is observed error detection for tested corruptions, **not** a mathematical guarantee that hashes can never collide.

## Interpretation and limits

1. **A digital representation can be reversible.** A number that denotes a sound sample can also denote an idealized light-intensity level; a bijective code can map it back.
2. **Coarse representations can discard information.** A six-bit output alone cannot reconstruct arbitrary eight-bit inputs; a two-bit side channel can restore them.
3. **Spectrum magnitudes discard phase.** They do not uniquely identify the waveform.
4. **Shared representation is not shared physical mechanism.** Sound is a mechanical wave in a medium. Light is an electromagnetic wave; assigning matching numbers to them is not evidence of a common ontology or that the universe is literally music.
5. **Not a full information-preservation guarantee.** If the side information or original data are destroyed, decoding may be impossible. The result concerns the stated encoding and test data.

This is an experimental extension of the project's previously documented six-bit `0x00–0x3F` ledger and provenance-preserving design philosophy, not an addition to the established native BaguaCode instruction set.

## Included files

- `ultimodel_light_music_test.py` — runnable experiment and tests
- `run_results.json` — verified result metadata (no audio)
- `requirements.txt` — Python package dependency
