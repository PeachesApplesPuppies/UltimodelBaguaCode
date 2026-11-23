"""Triadic tree vs whole-file Brotli and previous Adaptive HEX. Writes results.json."""
import hashlib,json,random,sys,time
from pathlib import Path
import brotli
from triadic_hex import encode,decode

HOME=Path(__file__).resolve().parent
VIDEO=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/ALittleLightMusic.mp4')
RESULTS=HOME/'results.json'
SCRATCH=HOME/'work'
SCRATCH.mkdir(exist_ok=True)
original=VIDEO.read_bytes()
master_hash=hashlib.sha256(original).hexdigest()
results={'experiment':'Triadic HEX exact byte compression','source':VIDEO.name,
         'original_size':len(original),'original_sha256':master_hash,
         'date':'2026-11-23','runs':[]}

def save():RESULTS.write_text(json.dumps(results,indent=2)+'\n')

def trial(name,source,depth,q):
    a=SCRATCH/(name+f'-d{depth}-q{q}.ut3')
    b=SCRATCH/(name+f'-d{depth}-q{q}.out')
    t=time.perf_counter(); report=encode(source,a,depth=depth,quality=q); encode_secs=time.perf_counter()-t
    t=time.perf_counter();verification=decode(a,b); decode_secs=time.perf_counter()-t
    s=source.read_bytes()
    assert b.read_bytes()==s
    assert verification['sha256']==hashlib.sha256(s).hexdigest()
    row={'name':name,'depth':depth,'brotli_quality':q,**report,
         'encode_seconds':round(encode_secs,3),'decode_seconds':round(decode_secs,3),
         'bytewise_identical':True,'sha256_match':True}
    print('RUN',name,'depth',depth,'q',q,'bytes',row['archive_bytes'],'nodes',row['node_count'],'seconds',round(encode_secs,2),flush=True)
    results['runs'].append(row)
    save()
    b.unlink();a.unlink()
    return row

for quality in (5,9):
    t=time.perf_counter()
    compressed=brotli.compress(original,quality=quality)
    assert brotli.decompress(compressed)==original
    results.setdefault('baselines',[]).append({'method':f'whole_file_brotli_q{quality}',
        'bytes':len(compressed),'encode_seconds':round(time.perf_counter()-t,3),
        'bytewise_identical':True})
    print('BASE',quality,len(compressed),flush=True)
    del compressed
save()

for depth in (0,1,2,3,4,5,6):
    trial('video',VIDEO,depth,5)
for depth in (0,5):trial('video',VIDEO,depth,9)

rng=random.Random(20261123)
unit=rng.randbytes(1<<20)
structured=bytes(rng.randrange(64) | ((i%4)<<6) for i in range(3*(1<<20)))
cases={
    'random':rng.randbytes(3*(1<<20)),
    'repeated_bytes':b'ABCDEF'*((3*(1<<20))//6),
    'repeated_block':unit*3,
    'hex62_structured':structured,
    'mixed_three':rng.randbytes(1<<20) + structured[:(1<<20)] + b'XYZ!'*((1<<20)//4)
}
for name,data in cases.items():
    path=SCRATCH/(name+'.bin');path.write_bytes(data)
    bro=brotli.compress(data,quality=5)
    assert brotli.decompress(bro)==data
    results.setdefault('control_baselines',[]).append({'case':name,'whole_brotli5_bytes':len(bro),
        'input_bytes':len(data),'bytewise_identical':True})
    del bro
    for depth in (0,1,3,5):trial(name,path,depth,5)
    path.unlink()
results['overall_all_reconstructed']=all(x['bytewise_identical'] and x['sha256_match'] for x in results['runs'])
save()
print('DONE',str(RESULTS),flush=True)
