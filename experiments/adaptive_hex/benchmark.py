"""Actual-source and deterministic synthetic controls (full-file verification)."""
from pathlib import Path
from time import perf_counter
import hashlib,json,random,sys,zlib
import brotli
from adaptive_hex import encode,decode,HEADER,BLOCK

ROOT=Path(__file__).resolve().parent
INPUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/ALittleLightMusic.mp4')
OUT=ROOT/'bench_temp'
OUT.mkdir(exist_ok=True)

def trial(label,content_path,block=1<<20,q=5):
    archive=OUT/(label+'.uhx')
    decoded=OUT/(label+'.recovered')
    start=perf_counter()
    result=encode(content_path,archive,block_size=block,brotli_quality=q)
    encode_seconds=perf_counter()-start
    start=perf_counter()
    recovered=decode(archive,decoded)
    decode_seconds=perf_counter()-start
    assert content_path.read_bytes()==decoded.read_bytes()
    assert recovered['sha256']==result['sha256']
    row={'case':label,**result,'encode_seconds':round(encode_seconds,3),
         'decode_seconds':round(decode_seconds,3),'byte_exact_verified':True,
         'sha_match_verified':True}
    print(json.dumps(row),flush=True)
    decoded.unlink()
    archive.unlink()
    return row

rows=[trial('original_mp4_adaptive',INPUT)]
raw=INPUT.read_bytes()
for method,data in [('brotli5',brotli.compress(raw,quality=5)),('brotli9',brotli.compress(raw,quality=9)),('zlib6',zlib.compress(raw,6))]:
    if method.startswith('brotli'):
        assert brotli.decompress(data)==raw
    else: assert zlib.decompress(data)==raw
    rows.append({'case':'original_mp4_'+method,'source_bytes':len(raw),'archive_bytes':len(data),
                 'saved_percent':round(100*(1-len(data)/len(raw)),4),
                 'byte_exact_verified':True,'note':'bare compressor payload; no format header'})
rng=random.Random(20261123)
block=1<<20
cases={
'control_random':rng.randbytes(3*block),
'control_repetitive':(b'ULTIMODEL!\n'*(3*block//11+2))[:3*block],
'control_six_plus_two':bytes(rng.randrange(64) | ((i%4)<<6) for i in range(3*block)),
'control_mixed':rng.randbytes(block) + bytes(rng.randrange(64) | ((i%4)<<6) for i in range(block)) + (b'ABCD'* (block//4))
}
for name,b in cases.items():
    input_path=OUT/(name+'.bin')
    input_path.write_bytes(b)
    rows.append(trial(name,input_path))
    input_path.unlink()
(ROOT/'benchmark_results.json').write_text(json.dumps({'description':'Full, counted archive sizes; synthetic controls seeded 20261123','video_original_sha256':hashlib.sha256(raw).hexdigest(),'tests':rows},indent=2)+'\n')