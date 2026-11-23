#!/usr/bin/env python3
"""Reversibly encode ANY file into PCM16 WAV and decode using WAV alone.

The WAV contains data-as-audio, not the soundtrack. Versioned file header and
SHA-256 are embedded as encoded PCM samples. This is a lossless *container*
encoding, not codec compression or regeneration of video from sound.
"""
import argparse
import hashlib
import os
import struct
import tempfile
import wave
from pathlib import Path

import numpy as np

MAGIC = b'ULHXLWAV'  # 8 bytes
VERSION = 1
HEADER = struct.Struct('<8sBQ32s')  # 8 magic, 1 version, 8 len, 32 sha
SAMPLE_RATE = 48_000
CHUNK = 1 << 20


def to_pcm16(data: bytes) -> bytes:
    x = np.frombuffer(data, dtype=np.uint8).astype(np.int16)
    return ((x - 128) * 256).astype('<i2').tobytes()


def from_pcm16(data: bytes) -> bytes:
    samples = np.frombuffer(data, dtype='<i2')
    if np.any(samples % 256 != 0):
        raise ValueError('Invalid WAV sample: not a canonical reversible 8->16 code')
    return ((samples // 256) + 128).astype('u1').tobytes()


def sha256(path: Path) -> bytes:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(CHUNK), b''):
            h.update(chunk)
    return h.digest()


def encode(source: Path, dst: Path) -> dict:
    if source.resolve() == dst.resolve():
        raise ValueError('Input and output paths must differ')
    src_size = source.stat().st_size
    if src_size >= (1 << 64):
        raise ValueError('Source too large')
    header = HEADER.pack(MAGIC, VERSION, src_size, sha256(source))
    dst.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dst), 'wb') as wav, source.open('rb') as f:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframesraw(to_pcm16(header))
        for chunk in iter(lambda: f.read(CHUNK), b''):
            wav.writeframesraw(to_pcm16(chunk))
    return {'source_bytes': src_size, 'wav_bytes': dst.stat().st_size,
            'source_sha256': sha256(source).hex(), 'container_frames': src_size + len(header),
            'wav_seconds': (src_size + len(header)) / SAMPLE_RATE}


def decode(wavpath: Path, dst: Path) -> dict:
    """Read only the WAV: no original source path required or accessed."""
    if wavpath.resolve() == dst.resolve():
        raise ValueError('Input and output paths must differ')
    dst.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wavpath), 'rb') as wav:
        if (wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getcomptype()) != (1, 2, SAMPLE_RATE, 'NONE'):
            raise ValueError('Not a supported lossless data WAV')
        if wav.getnframes() < HEADER.size:
            raise ValueError('Truncated header')
        h = from_pcm16(wav.readframes(HEADER.size))
        magic, version, wanted_length, wanted_hash = HEADER.unpack(h)
        if magic != MAGIC or version != VERSION:
            raise ValueError('Wrong container magic/version')
        if wav.getnframes() != HEADER.size + wanted_length:
            raise ValueError('Frame count does not equal declared payload length')
        hasher = hashlib.sha256()
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=dst.parent, prefix='.hexroundtrip-', delete=False) as out:
                temp_path = Path(out.name)
                remaining = wanted_length
                while remaining:
                    raw = wav.readframes(min(CHUNK, remaining))
                    if not raw:
                        raise ValueError('Unexpected end of WAV data')
                    original = from_pcm16(raw)
                    if len(original) > remaining:
                        raise ValueError('WAV payload longer than declared')
                    out.write(original)
                    hasher.update(original)
                    remaining -= len(original)
            if hasher.digest() != wanted_hash:
                raise ValueError('SHA-256 mismatch: WAV content was modified or corrupted')
            os.replace(temp_path, dst)
            temp_path = None
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
    return {'recovered_bytes': wanted_length,
            'recovered_sha256': hasher.hexdigest(), 'hash_verified': True}


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('encode', 'decode'):
        p = sub.add_parser(action)
        p.add_argument('input', type=Path)
        p.add_argument('output', type=Path)
    args = parser.parse_args()
    import json
    print(json.dumps(encode(args.input, args.output) if args.action=='encode' else decode(args.input, args.output), indent=2))

if __name__ == '__main__':
    cli()
