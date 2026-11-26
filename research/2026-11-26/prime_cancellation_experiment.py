"""BCE cancellation experiment. Run alongside prime_shell_experiment.py; requires NumPy."""
import argparse,csv,math
import numpy as np
from prime_shell_experiment import prime_powers,psi,BASES,boundary

def measure(lo,hi,q,pref,nodes,weights):
    p0=psi(lo,q,pref); A=(p0-lo)/math.sqrt(lo)
    inside=q[np.searchsorted(q,lo,'right'):np.searchsorted(q,hi,'left')]
    edges=np.r_[lo,inside,hi]; l,r=edges[:-1],edges[1:]
    c=psi(l,q,pref); h=(r-l)/2; m=(r+l)/2
    P=A*A*(1-lo/hi); C=Q=E=0.
    for node,w in zip(nodes,weights):
        x=m+h*node; B=(c-p0-(x-lo))/math.sqrt(lo); weight=w*h*lo/x**2
        C+=np.sum(weight*2*A*B); Q+=np.sum(weight*B**2); E+=np.sum(weight*(A+B)**2)
    # B(x) decreases between jumps; maximum absolute value attained at an endpoint or one-sided limit.
    peak=max(np.max(np.abs((c-p0-(l-lo))/math.sqrt(lo))),np.max(np.abs((c-p0-(r-lo))/math.sqrt(lo))),abs((psi(hi,q,pref)-p0-(hi-lo))/math.sqrt(lo)))
    B=(psi(hi,q,pref)-p0-(hi-lo))/math.sqrt(lo); An=(psi(hi,q,pref)-hi)/math.sqrt(hi)
    return dict(A=A,B=B,A_next=An,boundary_cross=2*A*B,carry_energy=P,cross_energy=C,innovation_energy=Q,E=E,peak_B=peak,identity_residual=E-P-C-Q)

def synthetic(k,d,b,nodes,weights):
    # normalized error R(x)=x^d cos(14 log x); A+B(y)=sqrt(y)*R(lo*y)
    lo=b**k; t0=k*math.log(b); A=lo**d*math.cos(14*t0)
    y=(1+b)/2+(b-1)/2*nodes; w=(b-1)/2*weights/y**2
    B=np.sqrt(y)*lo**d*y**d*np.cos(14*(t0+np.log(y)))-A
    P=A*A*(1-1/b); C=np.sum(w*2*A*B); Q=np.sum(w*B**2); E=np.sum(w*(A+B)**2)
    return P,C,Q,E

def main(N,output):
    ps,q,pref=prime_powers(N); nodes,weights=np.polynomial.legendre.leggauss(8); rows=[]
    print('N, primes, prime powers',N,len(ps),len(q))
    for name,b in BASES.items():
        rs=[]; k=0
        while boundary(name,b,k+1)<=N:
            lo,hi=boundary(name,b,k),boundary(name,b,k+1)
            row=dict(base=name,k=k,lo=lo,hi=hi,**measure(lo,hi,q,pref,nodes,weights)); rs.append(row); k+=1
        rows+=rs
        for label,subset in [('all',rs),('lo>=1000 hi<=1e7',[r for r in rs if r['lo']>=1000 and r['hi']<=1e7])]:
            P,C,Q,E=[sum(r[key] for r in subset) for key in ('carry_energy','cross_energy','innovation_energy','E')]
            print(name,label,len(subset),'negative boundary',sum(r['boundary_cross']<0 for r in subset),'negative integrated',sum(r['cross_energy']<0 for r in subset),'C/(P+Q)',C/(P+Q),'P,C,Q,E',P,C,Q,E,'peakB',max(r['peak_B'] for r in subset),'max residual',max(abs(r['identity_residual']) for r in subset))
        if name=='phi':
            for r in rs:
                if r['k'] in [10,15,20,25,29,30,32,34]: print('phi sample',r)
    nodes,weights=np.polynomial.legendre.leggauss(64)
    for d in [0,.05,.15,.25]:
        a=np.array([synthetic(k,d,BASES['phi'],nodes,weights) for k in range(20,81)])
        P,C,Q,E=a.sum(axis=0)
        print('synthetic',d,'negative cross',np.sum(a[:,1]<0),'C/(P+Q)',C/(P+Q),'log slope',np.polyfit(np.arange(20,81),np.log(a[:,3]),1)[0],'expected',2*d*math.log(BASES['phi']))
    with open(output,'w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0]); writer.writeheader(); writer.writerows(rows)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=30_000_000);p.add_argument('--output',default='prime_cancellation_results.csv');a=p.parse_args();main(a.limit,a.output)
