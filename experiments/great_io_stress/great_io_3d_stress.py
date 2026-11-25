"""3D KS close encounter validation. Run python great_io_3d.py 0 500 5.
Requires numpy scipy numba. Ctrl+C stops. Numerical tests, not proof.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np, csv,sys,signal
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from numba import njit
from fractions import Fraction
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
PAIRS=[(0,1,2),(1,2,0),(2,0,1)]
@njit(cache=True)
def mapping(u):
 a,b,c,d=u
 q=np.array([a*a-b*b-c*c+d*d,2*(a*b-c*d),2*(a*c+b*d)])
 D=2*np.array([[a,-b,-c,d],[b,a,-d,-c],[c,d,a,b]])
 return q,D
@njit(cache=True)
def ks(t,y,mu,mq,ms,al,be,H):
 u=y[:4]; s=y[4:7]; P=y[7:11]; w=y[11:14]; r=u@u; q,D=mapping(u)
 a,b,c=mu; d=s+al*q; e=s-be*q; nd=np.sqrt(d@d); ne=np.sqrt(e@e)
 U=a*c/nd+b*c/ne; gd=-a*c*d/nd**3; ge=-b*c*e/ne**3
 return np.concatenate((P/(4*mq),r*w/ms,-2*u*(w@w/(2*ms)-H-U)+r*(D.T@(al*gd-be*ge)),r*(gd+ge),np.array([r])))
@njit(cache=True)
def rel(t,y,mu):
 q=y[:3]; r=y[3:6]; d=r-q; a=np.sqrt(q@q); b=np.sqrt(r@r); c=np.sqrt(d@d)
 Q=q/a**3; S=r/b**3; D=d/c**3; U=mu[0]*mu[1]/a+mu[0]*mu[2]/b+mu[1]*mu[2]/c
 return np.concatenate((y[6:12],-(mu[0]+mu[1])*Q+mu[2]*(D-S),-(mu[0]+mu[2])*S-mu[1]*(D+Q),np.ones(1)))/U

def solve(rhs,y0,ts,tol):
 def event(t,y): return y[-1]-ts[-1]
 event.terminal=True
 s=solve_ivp(rhs,(0,np.sign(ts[-1])*1000),y0,method='DOP853',rtol=tol,atol=tol*.01,dense_output=True,events=event)
 if not s.success or not len(s.t_events[0]): raise RuntimeError(s.message)
 return [s.sol(0 if t==0 else s.t[-1] if t==ts[-1] else brentq(lambda z:s.sol(z)[-1]-t,min(0,s.t[-1]),max(0,s.t[-1]),xtol=5e-16)) for t in ts]

def chart(mu,R,V,pair,ts,tol):
 i,j,k=pair; a,b,c=mm=mu[list(pair)]; ab=a+b; al=b/ab; be=a/ab; mq=a*b/ab; ms=ab*c
 q=R[j]-R[i]; s=R[k]-be*R[i]-al*R[j]; p=mq*(V[j]-V[i]); w=ms*(V[k]-be*V[i]-al*V[j]); r=np.linalg.norm(q)
 H=p@p/(2*mq)+w@w/(2*ms)-a*b/r-a*c/np.linalg.norm(s+al*q)-b*c/np.linalg.norm(s-be*q)
 if q[0]>=0:
  x=np.sqrt((r+q[0])/2); u=np.array([x,q[1]/(2*x),q[2]/(2*x),0.])
 else:
  x=np.sqrt((r-q[0])/2); u=np.array([q[1]/(2*x),x,0.,q[2]/(2*x)])
 _,D=mapping(u); y0=np.r_[u,s,D.T@p,w,0.]
 out=[]
 for z in solve(lambda t,y:ks(t,y,mm,mq,ms,al,be,H),y0,ts,tol):
  u=z[:4]; s=z[4:7]; q,D=mapping(u); dq=D@z[7:11]/(4*(u@u)*mq); ds=z[11:14]/ms; center=-c*s; dc=-c*ds
  rr=np.zeros((3,3)); vv=rr.copy(); rr[[i,j,k]]=[center-al*q,center+be*q,center+s]; vv[[i,j,k]]=[dc-al*dq,dc+be*dq,dc+ds]; out.append(np.r_[rr.ravel(),vv.ravel()])
 return np.array(out)

def switched(mu,R,V,ts,tol):
 out=[]; switches=0; prev=None
 for start in range(0,len(ts)-1,5):
  end=min(start+5,len(ts)-1); pair=min(PAIRS,key=lambda p:np.linalg.norm(R[p[0]]-R[p[1]])); switches+=int(prev is not None and prev!=pair); prev=pair
  Y=chart(mu,R,V,pair,ts[start:end+1]-ts[start],tol); out.extend(Y if start==0 else Y[1:]); R=Y[-1,:9].reshape(3,3); V=Y[-1,9:].reshape(3,3)
 return np.array(out),switches

def reference(mu,R,V,ts,tol):
 z0=np.r_[R[1]-R[0],R[2]-R[0],V[1]-V[0],V[2]-V[0],0.]; out=[]
 for z in solve(lambda t,y:rel(t,y,mu),z0,ts,tol):
  q,r,v,w=z[:3],z[3:6],z[6:9],z[9:12]; a=-mu[1]*q-mu[2]*r; b=-mu[1]*v-mu[2]*w; out.append(np.r_[a,a+q,a+r,b,b+v,b+w])
 return np.array(out)

def initial(i):
 rng=np.random.default_rng(np.random.SeedSequence([2026112503,i])); m=rng.uniform(.3,3,3); M=m.sum(); mu=m/M
 while True:
  R=rng.normal(size=(3,3)); R-=mu@R; R/=np.sqrt(np.mean(np.sum(R*R,axis=1)))
  if min(np.linalg.norm(R[[1,2,0]]-R,axis=1))>.45: break
 V=rng.normal(size=(3,3))*rng.uniform(.2,1.4); V-=mu@V
 return mu,R,V,M

def errors(Y,Z,M):
 d=(Y-Z).reshape(-1,2,3,3); e=np.linalg.norm(d,axis=3).max(axis=(0,2)); return e[0],e[1]*np.sqrt(M)
def timeout(*args): raise TimeoutError('per-solver time cap')
def trial(arg):
 i,H=arg; signal.signal(signal.SIGALRM,timeout); mu,R,V,M=initial(i)
 row=dict(case=i,horizon=H,primary=0,refined=0,independent=0,samples=0,unity_fail=0,angular_error=0.,min_distance=np.inf,position_refined=0.,velocity_refined=0.,position_independent=0.,velocity_independent=0.,energy_drift=0.,angular_momentum_drift=0.,switches=0,errors='')
 for sign in [-1,1]:
  ts=np.linspace(0,sign*H,501)
  try:
   signal.alarm(12); Y,s=switched(mu,R,V,ts,1e-11); signal.alarm(0); row['primary']+=1; row['switches']+=s
   rr=Y[:,:9].reshape(-1,3,3); vv=Y[:,9:].reshape(-1,3,3); row['samples']+=501 if sign==-1 else 500; d=np.linalg.norm(rr[:,[1,2,0]]-rr,axis=2); row['min_distance']=min(row['min_distance'],d.min()); abc=d/np.exp(np.log(d).mean(axis=1))[:,None]
   for a,b,_ in abc:
    A,B=Fraction(float(a)),Fraction(float(b)); row['unity_fail']+=int(A*B*(1/(A*B))!=1)
   ang=[]
   for j,k,l in [(2,0,1),(0,1,2),(1,2,0)]:
    u=rr[:,k]-rr[:,j]; v=rr[:,l]-rr[:,j]; ang.append(np.arctan2(np.linalg.norm(np.cross(u,v),axis=1),np.sum(u*v,axis=1)))
   row['angular_error']=max(row['angular_error'],np.max(abs(np.sum(ang,axis=0)-np.pi)))
   E=.5*np.sum(mu[None,:]*np.sum(vv*vv,axis=2),axis=1)-np.sum((mu*mu[[1,2,0]])[None,:]/d,axis=1); L=np.sum(mu[None,:,None]*np.cross(rr,vv),axis=1)
   row['energy_drift']=max(row['energy_drift'],np.max(abs(E-E[0]))); row['angular_momentum_drift']=max(row['angular_momentum_drift'],np.max(np.linalg.norm(L-L[0],axis=1)))
  except Exception as e: row['errors']+=f'primary {sign}: {e};'; continue
  finally: signal.alarm(0)
  for kind in ['refined','independent']:
   try:
    signal.alarm(12); Z=switched(mu,R,V,ts,2.3e-14)[0] if kind=='refined' else reference(mu,R,V,ts,2.3e-14); signal.alarm(0); p,v=errors(Y,Z,M); row[kind]+=1; row['position_'+kind]=max(row['position_'+kind],p); row['velocity_'+kind]=max(row['velocity_'+kind],v)
   except Exception as e: row['errors']+=f'{kind} {sign}: {e};'
   finally: signal.alarm(0)
 for kind in ['refined','independent']: row[kind+'_pass']=row[kind]==2 and row['position_'+kind]<=1e-7 and row['velocity_'+kind]<=1e-6
 return row
if __name__=='__main__':
 from concurrent.futures import as_completed
 with Path(__file__).with_name('great_io_3d_0_500.csv').open() as f: old=list(csv.DictReader(f))
 def stress(r): return max(*(float(r[k])/1e-7 for k in ('position_independent','position_refined')),*(float(r[k])/1e-6 for k in ('velocity_independent','velocity_refined')))
 ids=[int(r['case']) for r in sorted(old,key=stress,reverse=True)[:5]]
 ids += [int(r['case']) for r in sorted((r for r in old if int(r['case']) not in ids),key=lambda r:float(r['min_distance']))[:5]]
 print('selected',ids,flush=True)
 mu,R,V,M=initial(0); chart(mu,R,V,PAIRS[0],np.array([0.,.01]),1e-11); reference(mu,R,V,np.array([0.,.01]),1e-11)
 with ProcessPoolExecutor(max_workers=5) as ex, Path(__file__).with_name('great_io_3d_stress_results.csv').open('w',newline='') as out:
  fs=[ex.submit(trial,(i,50.)) for i in ids]
  for n,f in enumerate(as_completed(fs)):
   r=f.result()
   if n==0: w=csv.DictWriter(out,fieldnames=r); w.writeheader()
   w.writerow(r); out.flush(); print(r,flush=True)
