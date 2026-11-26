"""BCE: prime-shell recurrence and adversarial test. Python 3 + numpy."""
import argparse, csv, math
import numpy as np
from pathlib import Path

PHI=(1+math.sqrt(5))/2
BASES={'sqrt2':math.sqrt(2),'phi':PHI,'2':2.,'3':3.}

def prime_powers(N):
    prime=np.ones(N+1,dtype=bool); prime[:2]=False
    for p in range(2,math.isqrt(N)+1):
        if prime[p]: prime[p*p::p]=False
    ps=np.flatnonzero(prime)
    q=[ps]; w=[np.log(ps)]
    for p in ps[ps<=math.isqrt(N)]:
        p=int(p); v=p*p
        while v<=N:
            q.append(np.array([v])); w.append(np.array([math.log(p)])); v*=p
    q=np.concatenate(q); w=np.concatenate(w); idx=np.argsort(q)
    q=q[idx]; pref=np.r_[0.,np.cumsum(w[idx])]
    return ps,q,pref

def psi(x,q,pref):
    return pref[np.searchsorted(q,x,side='right')]

def shell_energy(lo,hi,q,pref,nodes,weights):
    inner=q[np.searchsorted(q,lo,side='right'):np.searchsorted(q,hi,side='left')]
    edges=np.r_[lo,inner,hi]; left=edges[:-1]; right=edges[1:]
    c=psi(left,q,pref); h=(right-left)/2; mid=(right+left)/2
    # Integrate smooth segments, splitting at every prime power.
    result=0.
    for node,weight in zip(nodes,weights):
        z=mid+h*node
        result+=np.sum(h*weight*((c-z)/z)**2)
    return float(result)

def boundary(name,b,k):
    if name=="sqrt2" and k%2==0: return float(2**(k//2))
    return b**k

def run(N,output):
    if N<10_000_000: raise ValueError("limit must be at least 10,000,000 for the common-window comparison")
    ps,q,pref=prime_powers(N); nodes,weights=np.polynomial.legendre.leggauss(8)
    rows=[]
    print('N, primes, prime powers:',N,len(ps),len(q))
    for name,b in BASES.items():
        k=0; rs=[]
        while boundary(name,b,k+1)<=N:
            lo,hi=boundary(name,b,k),boundary(name,b,k+1); p0,p1=psi(np.array([lo,hi]),q,pref)
            A=(p0-lo)/math.sqrt(lo); B=(p1-p0-(hi-lo))/math.sqrt(lo); An=(p1-hi)/math.sqrt(hi)
            E=shell_energy(lo,hi,q,pref,nodes,weights)
            r=dict(base=name,k=k,lo=lo,hi=hi,A=A,B=B,A_next=An,E=E,E_per_log_width=E/math.log(b),recurrence_residual=An-(A+B)/math.sqrt(b))
            rs.append(r); k+=1
        rows+=rs
        print(name,'shells',len(rs),'last_hi',rs[-1]['hi'],'max residual',max(abs(r['recurrence_residual']) for r in rs))
        eligible=[r for r in rs if r['lo']>=1000 and r['hi']<=1e7]
        print('  whole shells within [1e3,1e7] count',len(eligible),'mean density',np.mean([r['E_per_log_width'] for r in eligible]),'range density',min(r['E_per_log_width'] for r in eligible),max(r['E_per_log_width'] for r in eligible))
        if name=='phi':
            print('  contraction count',sum(abs(r['A_next'])<abs(r['A']) for r in rs),'opposing increment',sum(r['A']*r['B']<0 for r in rs),'corr A,B',np.corrcoef([r['A'] for r in rs],[r['B'] for r in rs])[0,1])
            for r in rs:
                if r['k'] in [5,10,15,20,25,29,30,32,34]: print(' ',r)
    # Same endpoints; repartition cannot change total energy.
    lo,hi=1000.,1e7
    common=shell_energy(lo,hi,q,pref,nodes,weights)
    print('common interval energy',common,'density',common/math.log(hi/lo))
    for name,b in BASES.items():
        ks=range(math.ceil(math.log(lo,b)),math.floor(math.log(hi,b))+1)
        cuts=[lo]+[boundary(name,b,k) for k in ks if lo<boundary(name,b,k)<hi]+[hi]
        total=sum(shell_energy(a,z,q,pref,nodes,weights) for a,z in zip(cuts,cuts[1:]))
        print('  common partition',name,total,total-common)
    # Synthetic off-line mode: error x^(1/2+delta) cos(t log x), t=14.
    # Integral in y=log x: exp(2 delta*y) cos(t*y)^2 dy, computed analytically.
    def F(y,d,t):
        if d==0: return y/2+math.sin(2*t*y)/(4*t)
        a=2*d; b=2*t
        return math.exp(a*y)*(1/(2*a)+(a*math.cos(b*y)+b*math.sin(b*y))/(2*(a*a+b*b)))
    print('synthetic off-line tests, E_k at k=10,20,40,80, growth fit over k=20..80')
    for d in [0,.05,.15,.25]:
        es=[F((k+1)*math.log(PHI),d,14)-F(k*math.log(PHI),d,14) for k in range(81)]
        slope=np.polyfit(np.arange(20,81),np.log(es[20:]),1)[0]
        print(d,[es[k] for k in [10,20,40,80]],slope, 'expected',2*d*math.log(PHI))
    with open(output,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=30_000_000);p.add_argument('--output',default='prime_shell_results.csv');a=p.parse_args();run(a.limit,a.output)
