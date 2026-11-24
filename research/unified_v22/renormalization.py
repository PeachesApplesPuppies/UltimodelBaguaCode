import numpy as np, json, itertools
from pathlib import Path
from fractions import Fraction as Q
N=1_000_000
p=np.ones(N+1,dtype=bool);p[:2]=False
for k in range(2,int(N**.5)+1):
 if p[k]:p[k*k::k]=False
pr=np.flatnonzero(p); theta=np.cumsum(np.where(p,np.log(np.maximum(1,np.arange(N+1))),0));F=theta-np.arange(N+1)
rows=[]
for a,b in itertools.combinations([2,3,5,7,11],2):
 x=np.arange(1,N//(a*b)+1); da=F[a*x]-F[x]; db=F[b*x]-F[x]; ab=F[a*b*x]-F[x]
 left=(F[a*b*x]-F[b*x])+db;right=(F[a*b*x]-F[a*x])+da
 err=max(np.max(np.abs(left-ab)),np.max(np.abs(right-ab)))
 assert err<1e-7
 rows.append(dict(p=a,q=b,samples=len(x),max_error=float(err)))
energy=[]
for q in [2,3,5,7,11]:
 for X in [100,1000,10000,100000]:
  if q*X>N:continue
  x=np.arange(1,X+1); d=F[q*x]-F[x];energy.append(dict(q=q,X=X,normalized_energy=float(d@d/X**2)))
# Exact growing-mode control: rational scale factors are cubes, F(x)=x^(2/3) on perfect cubes.
# This exceeds square-root scale but satisfies every composition identity exactly.
controls=0
for x,a,b in itertools.product(range(1,11),range(2,12),range(2,12)):
 f=lambda k:Q(k*k); D=lambda q,k:f(q*k)-f(k)
 assert D(a*b,x)==D(a,b*x)+D(b,x)==D(b,a*x)+D(a,x)
 controls+=1
out=dict(primes=len(pr),cocycle=rows,energy=energy,exact_growing_mode_controls=controls,mode='F(x)=x^(2/3), restricted to x and scales that are perfect cubes; identity holds on all positive reals too')
Path('renormalization.json').write_text(json.dumps(out,indent=2));print('cocycle pairs',len(rows),'points',sum(r['samples'] for r in rows),'max error',max(r['max_error'] for r in rows),'controls',controls);print(energy)
