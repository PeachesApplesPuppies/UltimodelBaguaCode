"""Benchmarks automatic depth against fixed-depth triadic and whole-file Brotli."""
import hashlib,json,random,time,sys
from pathlib import Path
import brotli
from autodepth_hex import encode as auto_encode
from triadic_hex import encode as fixed_encode, decode

ROOT=Path(__file__).parent
OUT=ROOT/'auto_work'
OUT.mkdir(exist_ok=True)
VIDEO=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/ALittleLightMusic.mp4')

def trial(name,data,*,max_depth, min_leaf, mode='balanced',quality=5, fixed_depths=(0,1,3)):
    s=OUT/(name+'.src'); a=OUT/(name+'.uta'); rec=OUT/(name+'.recovered')
    s.write_bytes(data)
    sha=hashlib.sha256(data).hexdigest()
    z= {'input_bytes':len(data),'input_sha256':sha}
    print('running',name,'bytes',len(data),'auto depth',max_depth,'mode',mode,flush=True)
    start=time.perf_counter()
    z['auto']=auto_encode(s,a,max_depth=max_depth,min_leaf=min_leaf,boundary_mode=mode,quality=quality,max_evaluations=1000)
    z['auto']['seconds']=round(time.perf_counter()-start,3)
    z['auto']['decoded']=decode(a,rec)
    assert rec.read_bytes()==data
    print('auto done',name,z['auto']['archive_bytes'],z['auto']['chosen_depth'],z['auto']['seconds'],flush=True)
    z['fixed']={}
    for d in fixed_depths:
        start=time.perf_counter()
        result=fixed_encode(s,a,depth=d,quality=quality)
        v=decode(a,rec)
        assert rec.read_bytes()==data
        z['fixed'][str(d)]={'archive_bytes':result['archive_bytes'],
          'seconds':round(time.perf_counter()-start,3),'leaf_count':result['leaf_count'],
          'verified':v['byte_exact_verified_against_root_hash']}
        print('fixed depth',d, z['fixed'][str(d)]['archive_bytes'],flush=True)
    t=time.perf_counter(); comp=brotli.compress(data,quality=quality)
    assert brotli.decompress(comp)==data
    z['whole_brotli']={'archive_bytes':len(comp),'seconds':round(time.perf_counter()-t,3)}
    print('whole Brotli',name,len(comp),flush=True)
    (ROOT/'autodepth_results.json').write_text(json.dumps({**(json.loads((ROOT/'autodepth_results.json').read_text()) if (ROOT/'autodepth_results.json').exists() else {}),name:z},indent=2)+'\n')
    s.unlink(missing_ok=True);a.unlink(missing_ok=True);rec.unlink(missing_ok=True)
    return z

if __name__=='__main__':
    rng=random.Random(20261123)
    rep=rng.randbytes(2*1024*1024)*3
    trial('long_repeat_6MiB',rep,max_depth=4,min_leaf=65536,quality=5,fixed_depths=(0,1,3))
    random_blob=rng.randbytes(1024*1024)
    structured=bytes((rng.randrange(64) | ((i//256)%4<<6)) for i in range(1024*1024))
    trial('mixed_3MiB',random_blob+structured+((b'RESONANCE' * (1024*1024//9+1))[:1024*1024]),max_depth=4,min_leaf=32768,quality=5,fixed_depths=(0,1,3))
    if VIDEO.exists():
        trial('ALittleLightMusic_mp4',VIDEO.read_bytes(),max_depth=4,min_leaf=131072,quality=5,fixed_depths=(0,3))
    print('ALL COMPLETE',flush=True)
