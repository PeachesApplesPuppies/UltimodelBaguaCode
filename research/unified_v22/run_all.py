import os,sys,subprocess,shutil,json,time,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent
names=['riemann_lab','centerpoint_lab','confinement_engine','zero_boundary_engine','certified_boundary','uniqueness_engine','tiling_engine','bidirectional_engine','moment_engine','positivity_engine','multiside_engine','arithmetic_singularity','multiscale_v13','scale_v14','arithmetic_v15','operator_v16','differential_v17','coercivity_v18','correlation_v19','multiplicative_v20','distinct_v21']
def run(item):
 i,name=item; target=ROOT/'runs'/name;target.mkdir(parents=True,exist_ok=True)
 if i==1: shutil.copy2(SRC/'riemann_lab.py',target/'riemann_lab.py'); entry='riemann_lab.py'
 else:
  shutil.copytree(SRC/name,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','checkpoint.json','results.json','rerun.json','run.log'))
  entry={2:'lab.py',7:'tiling.py',10:'audit.py'}.get(i,'engine.py')
 start=time.monotonic(); status='timeout'; rc=None
 with (target/'fresh.log').open('w') as f:
  try:
   p=subprocess.run([sys.executable,'-u',entry],cwd=target,stdout=f,stderr=subprocess.STDOUT,timeout=int(os.getenv('BCE_TIMEOUT','12')),env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'});rc=p.returncode;status='pass' if rc==0 else 'fail'
  except subprocess.TimeoutExpired: pass
 return dict(version=f'{i//10}.{i%10}',name=name,status=status,returncode=rc,seconds=round(time.monotonic()-start,2))
if __name__=='__main__':
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.getenv('BCE_WORKERS','5'))) as pool:
  for fut in concurrent.futures.as_completed([pool.submit(run,item) for item in enumerate(names,1)]):
   r=fut.result();results.append(r);print(r,flush=True); p=ROOT/'status.tmp';p.write_text(json.dumps(sorted(results,key=lambda x:x['version']),indent=2));p.replace(ROOT/'status.json')
