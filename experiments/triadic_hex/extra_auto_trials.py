import json,random,time,hashlib
from pathlib import Path
from autodepth_hex import encode
from triadic_hex import decode
root=Path(__file__).parent/'auto_work';root.mkdir(exist_ok=True)
results={}
for name,raw,depth,minleaf,mode,q in [
 ('long_repeat_18MiB',random.Random(1209).randbytes(6*1024*1024)*3,3,512*1024,'balanced',5),
 ('aligned_3MiB', random.Random(514).randbytes(1024*1024)+bytes((i%64)|(((i//16384)%4)<<6) for i in range(1024*1024))+(b'resonance'*116509)[:1024*1024],3,64*1024,'aligned',5),
]:
 s=root/(name+'.src');a=root/(name+'.uta');o=root/(name+'.out')
 s.write_bytes(raw)
 print('running',name,flush=True)
 t=time.perf_counter();m=encode(s,a,max_depth=depth,min_leaf=minleaf,boundary_mode=mode,quality=q,max_evaluations=900)
 dec=decode(a,o)
 assert o.read_bytes()==raw
 m['seconds']=round(time.perf_counter()-t,3)
 m['sha256_check']=hashlib.sha256(raw).hexdigest()==dec['sha256']
 results[name]=m
 print(name,'archive',m['archive_bytes'],'depth',m['chosen_depth'],'leaf',m['leaf_count'],'branches',m['branch_count'],'time',m['seconds'],flush=True)
 s.unlink();a.unlink();o.unlink()
 (Path(__file__).parent/'extra_auto_results.json').write_text(json.dumps(results,indent=2)+'\n')
print('DONE',flush=True)
