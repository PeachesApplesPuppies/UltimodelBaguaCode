"""Ultimodel Adaptive HEX v0.1: exact, self-describing block-wise file compression.

Tries conventional and reversible HEX/XOR/bitshuffle views PER BLOCK, stores
whichever entire encoded payload is smallest. Encodes *existing bytes*, not
video pixels. Does not guarantee that compressed output is smaller than input.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile
import zlib

from transforms import TRANSFORMS
try:
    import brotli
except ImportError:
    brotli = None

MAGIC = b'ULTADP01'
VERSION = 1
HEADER = struct.Struct('>8sBIIQ32s')   # magic, version, block bytes, block count, source length, SHA-256
BLOCK = struct.Struct('>BBII32s')       # transform, compressor, original len, encoded len, block SHA-256
MAX_BLOCK = 8 * 1024 * 1024
MAX_BLOCKS = 1_000_000
READ = 1 << 20
TRANS = {'raw':0, 'hex6+2':1, 'xor':2, 'xor+hex6+2':3, 'bitshuffle':4}
CODEC = {'store':0, 'zlib':1, 'brotli':2}
TRANS_BACK = {v:k for k,v in TRANS.items()}
CODEC_BACK = {v:k for k,v in CODEC.items()}
CANDIDATES = (('raw','store'), ('raw','zlib'), ('raw','brotli'),
              ('hex6+2','zlib'), ('hex6+2','brotli'),
              ('xor','zlib'), ('xor+hex6+2','zlib'), ('bitshuffle','zlib'))


def file_hash(path: Path) -> bytes:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(READ), b''):
            h.update(part)
    return h.digest()


def compress(data: bytes, codec: str, quality: int):
    if codec == 'store': return data
    if codec == 'zlib': return zlib.compress(data, 6)
    if codec == 'brotli':
        if brotli is None: raise ValueError('Install brotli to encode this method')
        return brotli.compress(data, quality=quality)
    raise ValueError('Unknown codec')


def decompress(data: bytes, codec: str, limit: int) -> bytes:
    if codec == 'store': out = data
    elif codec == 'zlib':
        z = zlib.decompressobj()
        out = z.decompress(data, limit + 1)
        if len(out) > limit or z.unconsumed_tail or not z.eof or z.unused_data:
            raise ValueError('Invalid, oversized, or trailing zlib data')
        out += z.flush()
    elif codec == 'brotli':
        if brotli is None: raise ValueError('Install brotli to decode this method')
        decoder = brotli.Decompressor()
        parts = []
        size = 0
        for i in range(0, len(data), 4096):
            part = decoder.process(data[i:i+4096])
            parts.append(part)
            size += len(part)
            if size > limit:
                raise ValueError('Decoded block exceeds declared limit')
        if not decoder.is_finished(): raise ValueError('Incomplete Brotli stream')
        out = b''.join(parts)
    else:
        raise ValueError('Unknown compressor')
    if len(out) > limit: raise ValueError('Decoded block exceeds declared limit')
    return out


def best_block(data: bytes, quality: int = 5, candidates=CANDIDATES):
    """Return selected transform, codec and payload, deterministic on equal sizes."""
    if not 0 <= quality <= 11: raise ValueError('Brotli quality must be 0..11')
    best = ('raw', 'store', data)
    views = {'raw': data}
    for transform, codec in candidates:
        if codec == 'brotli' and brotli is None: continue
        if transform not in TRANS or codec not in CODEC: raise ValueError('Invalid candidate')
        if transform not in views:
            views[transform] = TRANSFORMS[transform][0](data)
        encoded = compress(views[transform], codec, quality)
        if len(encoded) < len(best[2]):
            best = (transform, codec, encoded)
    return best


def encode(source: Path, destination: Path, *, block_size: int = 1<<20,
           brotli_quality: int = 5) -> dict:
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Input and output must be different files')
    if not (1 <= block_size <= MAX_BLOCK): raise ValueError('Block size out of range')
    if not (0 <= brotli_quality <= 11): raise ValueError('Brotli quality out of range')
    if brotli is None: raise ValueError('Brotli package required for identical candidate selection')
    size = source.stat().st_size
    count = (size + block_size - 1) // block_size
    if count > MAX_BLOCKS: raise ValueError('Too many blocks')
    digest = file_hash(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    choices = Counter()
    try:
        with tempfile.NamedTemporaryFile(prefix='.uhx-', dir=destination.parent, delete=False) as o:
            tmp = Path(o.name)
            o.write(HEADER.pack(MAGIC, VERSION, block_size, count, size, digest))
            reread = hashlib.sha256()
            with source.open('rb') as f:
                for index in range(count):
                    raw = f.read(min(block_size, size - index*block_size))
                    if len(raw) != min(block_size, size - index*block_size):
                        raise ValueError('Source changed while encoding')
                    reread.update(raw)
                    transform, codec, encoded = best_block(raw, brotli_quality)
                    o.write(BLOCK.pack(TRANS[transform], CODEC[codec],len(raw),len(encoded),hashlib.sha256(raw).digest()))
                    o.write(encoded)
                    choices[f'{transform}/{codec}'] += 1
                if f.read(1) or reread.digest() != digest:
                    raise ValueError('Source changed while encoding')
        archive_size = tmp.stat().st_size
        os.replace(tmp, destination)
        tmp = None
    finally:
        if tmp is not None: tmp.unlink(missing_ok=True)
    return {'source_bytes':size, 'archive_bytes':archive_size,
            'saved_percent':round(100*(1-archive_size/size),4) if size else None,
            'sha256':digest.hex(),'blocks':count,'block_size':block_size,
            'brotli_quality':brotli_quality,'selection_counts':dict(choices),'verified':False}


def decode(archive: Path, destination: Path) -> dict:
    archive, destination = Path(archive), Path(destination)
    if archive.resolve() == destination.resolve():
        raise ValueError('Input and output must be different files')
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    with archive.open('rb') as f:
        header = f.read(HEADER.size)
        if len(header) != HEADER.size: raise ValueError('Archive header truncated')
        magic, version, block_size, count, size, digest = HEADER.unpack(header)
        if magic != MAGIC or version != VERSION:
            raise ValueError('Wrong archive magic/version')
        if not 1 <= block_size <= MAX_BLOCK:
            raise ValueError('Unsupported block size')
        expected_count = (size + block_size - 1) // block_size
        if count != expected_count or count > MAX_BLOCKS:
            raise ValueError('Invalid block count')
        sha = hashlib.sha256()
        choices = Counter()
        remaining = size
        try:
            with tempfile.NamedTemporaryFile(prefix='.uhx-', dir=destination.parent, delete=False) as o:
                tmp = Path(o.name)
                for index in range(count):
                    h = f.read(BLOCK.size)
                    if len(h) != BLOCK.size: raise ValueError('Truncated block header')
                    t, c, raw_length, packed_length, expected_hash = BLOCK.unpack(h)
                    length = min(block_size, remaining)
                    if t not in TRANS_BACK or c not in CODEC_BACK:
                        raise ValueError('Unsupported transform/codec ID')
                    if raw_length != length or packed_length > length or packed_length < 0:
                        raise ValueError('Invalid block length')
                    compressed = f.read(packed_length)
                    if len(compressed) != packed_length: raise ValueError('Truncated block payload')
                    transformed_limit = 8 * ((length+7)//8)  # max padding from bitshuffle
                    transformed = decompress(compressed, CODEC_BACK[c], transformed_limit)
                    restored = TRANSFORMS[TRANS_BACK[t]][1](transformed, length)
                    if len(restored) != length:
                        raise ValueError('Incorrect reconstructed block length')
                    if hashlib.sha256(restored).digest() != expected_hash:
                        raise ValueError('Block SHA-256 mismatch')
                    o.write(restored)
                    sha.update(restored)
                    remaining -= length
                    choices[f'{TRANS_BACK[t]}/{CODEC_BACK[c]}'] += 1
                if remaining or f.read(1): raise ValueError('Unexpected trailing bytes or missing data')
                if sha.digest() != digest: raise ValueError('Whole-file SHA-256 mismatch')
            os.replace(tmp, destination)
            tmp = None
        finally:
            if tmp is not None: tmp.unlink(missing_ok=True)
    return {'recovered_bytes':size,'sha256':digest.hex(), 'blocks':count,
            'selection_counts':dict(choices),'verified':True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    for name in ('encode','decode'):
        q = sub.add_parser(name)
        q.add_argument('input', type=Path)
        q.add_argument('output', type=Path)
        if name == 'encode':
            q.add_argument('--block-size', type=int, default=1<<20)
            q.add_argument('--brotli-quality', type=int, default=5)
    args = p.parse_args()
    result = encode(args.input,args.output,block_size=args.block_size,brotli_quality=args.brotli_quality) if args.action=='encode' else decode(args.input,args.output)
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()