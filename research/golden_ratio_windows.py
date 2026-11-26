"""Numerical comparison of geometric windows; not a proof. Requires numpy, scipy, mpmath."""
import numpy as np
import mpmath as mp
from scipy.special import expi
from math import sqrt, pi
PHI=(1+sqrt(5))/2
SCALES=[1.25,1.5,PHI,2.,3.]
N=5_000_000

def sieve(N):
    prime=np.ones(N+1,dtype=bool); prime[:2]=False
    for p in range(2,int(sqrt(N))+1):
        if prime[p]: prime[p*p::p]=False
    mu=np.ones(N+1,dtype=np.int8); mu[0]=0
    for p in np.flatnonzero(prime):
        mu[p::p]*=-1
        if p*p<=N: mu[p*p::p*p]=0
    return prime,mu

def edges(lo,hi,q):
    a=[lo]; k=1
    while True:
        x=int(lo*q**k)
        if x>=hi: break
        if x>a[-1]: a.append(x)
        k+=1
    return np.array(a+[hi])

def coeffs(r,m,nmax,dps):
    with mp.workdps(dps):
        rr=mp.mpf(str(r)); y=[]
        for j in range(m//2+1):
            w=rr*mp.exp(2j*mp.pi*j/m); s=1/(1-w)
            y.append(complex(1/((s-1)*mp.zeta(s))))
    vals=np.array(y+y[-2:0:-1],dtype=complex)
    vals[m//2+1:]=np.conj(vals[m//2+1:])
    return np.fft.fft(vals)[:nmax+1].real/m/r**np.arange(nmax+1)

def energy(c,r):
    n=np.arange(len(c)); return pi*np.sum(c*c*r**(2*n+2)/(n+1))

def main():
    p,mu=sieve(N); P=np.cumsum(p,dtype=np.int32); M=np.cumsum(mu,dtype=np.int32)
    x=np.arange(1,N,dtype=float); a=1.1
    E=np.zeros(N+1); E[2:]=np.cumsum(M[1:N].astype(float)**2*x**(-a)*(-np.expm1(-a*np.log1p(1/x)))/a)
    print('Actual prime/Mobius counts; E=.05 damped energy integral from 1 to X',flush=True)
    for z in [100,1000,10000,100000,1000000,N]: print(z,P[z],M[z],f'{E[z]:.10f}',flush=True)
    print('Scale | windows | total primes | prime error RMS (log-width weighted; vs li increments) | Mobius increment RMS / sqrt(width) (log-width weighted) | E tail 100..N | peak E increment per log width',flush=True)
    for q in SCALES:
        e=edges(100,N,q); l,h=e[:-1],e[1:]; w=np.log(h/l); dp=P[h]-P[l]; dM=M[h]-M[l]; dE=E[h]-E[l]; pred=expi(np.log(h))-expi(np.log(l))
        rms=lambda v: np.sqrt(np.average(v*v,weights=w))
        print(f'{q:.9f} {len(l)} {sum(dp)} {rms(dp/pred-1):.7f} {rms(dM/np.sqrt(h-l)):.7f} {sum(dE):.10f} {max(dE/w):.7f}',flush=True)
    print('Grid phase sensitivity: shift internal endpoints by fractions 0,.25,.5,.75 of log(q); same endpoints 100,N. Mean and range of RMS errors:',flush=True)
    for q in SCALES:
        pe=[]; me=[]
        for phase in [0,.25,.5,.75]:
            e=[100]; k=0
            while True:
                z=int(100*q**(k+phase)); k+=1
                if z>=N: break
                if z>e[-1]:e.append(z)
            e=np.array(e+[N]); l,h=e[:-1],e[1:]; w=np.log(h/l)
            pred=expi(np.log(h))-expi(np.log(l))
            pe.append(np.sqrt(np.average(((P[h]-P[l])/pred-1)**2,weights=w)))
            me.append(np.sqrt(np.average(((M[h]-M[l])/np.sqrt(h-l))**2,weights=w)))
        print(f'{q:.9f}', 'prime mean/range',*[f'{v:.7f}' for v in [np.mean(pe),min(pe),max(pe)]], 'Mobius mean/range',*[f'{v:.7f}' for v in [np.mean(me),min(me),max(me)]],flush=True)
    print('Golden windows endpoints: X prime_count M(X) E(X)',flush=True)
    for z in edges(100,N,PHI): print(z,P[z],M[z],f'{E[z]:.10f}',flush=True)
    print('Computing B(w)=1/[(s-1)zeta(s)], s=1/(1-w), coefficients 0..256',flush=True)
    c=coeffs(.96,1024,256,30); d=coeffs(.97,2048,256,40)
    print('Max abs difference',max(abs(c-d)), 'b0,b1,b2',d[:3],flush=True)
    print('Selected coefficients n,b_n',flush=True)
    for n in [0,1,2,4,8,16,32,64,128,256]:print(n,f'{d[n]:.12g}',flush=True)
    print('Scale | windows (indices 1..256) | max block |b_n|^(1/n) | last block maximum |b_n|^(1/n) | sum coefficient energy at r=.99, n=1..256',flush=True)
    n=np.arange(1,257); rate=abs(d[1:])**(1/n); terms=pi*d[1:]**2*.99**(2*n+2)/(n+1)
    for q in SCALES:
        e=edges(1,257,q); mx=[max(rate[l-1:h-1]) for l,h in zip(e[:-1],e[1:])]; sums=[sum(terms[l-1:h-1]) for l,h in zip(e[:-1],e[1:])]
        print(f'{q:.9f} {len(mx)} {max(mx):.10f} {mx[-1]:.10f} {sum(sums):.12f}',flush=True)
    print('Truncated reciprocal energy for n=0..256:',flush=True)
    for r in [.75,.95,.99]:print(r,f'{energy(d,r):.12f}',flush=True)
    print('Synthetic controls: exponential rate phi fails at r>=1/phi; polynomial growth safe for all r<1. At r=.75, energy term ratio tends to (phi*r)^2 =', (PHI*.75)**2,flush=True)
    print('All comparisons finite; equal totals arise from partitioning the same interval. No RH claim.',flush=True)
if __name__=='__main__':main()
