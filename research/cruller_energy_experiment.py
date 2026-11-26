"""Three Infinities reciprocal energy. Empirical quadrature, not certified.
Run: python cruller_energy_experiment.py
Requires numpy, scipy, mpmath. Ctrl-C interrupts; no inputs are modified.
"""
import numpy as np
import mpmath as mp
from scipy.special import roots_legendre
from math import pi, log
from functools import lru_cache
A=.2
@lru_cache(None)
def base(n): return roots_legendre(n)
def nodes(a,b,n):
    x,w=base(n)
    return (a+b)/2+(b-a)/2*x,(b-a)/2*w

def energy(w):
    s=1/(1-mp.mpc(complex(w)))
    f=(s-1)*mp.zeta(s) if w else mp.mpf(1)
    return float(1/abs(f)**2)

def radial(theta,lo,hi,n):
    if hi<=lo:return 0.
    rr,weights=nodes(lo,hi,n)
    return sum(q*t*energy(t*np.exp(1j*theta)) for t,q in zip(rr,weights))

def regional(r,n,dps):
    mp.mp.dps=dps
    inner=0.; outer=[]
    for j in (0,1):
        start=0 if j==0 else -pi/3
        end=pi/3
        ti=to=0.
        cuts=np.linspace(start,end,5)
        for aa,bb in zip(cuts[:-1],cuts[1:]):
            angles,weights=nodes(aa,bb,n)
            for phi,q in zip(angles,weights):
                theta=phi+2*pi*j/3
                b=min(r,A/np.cos(phi))
                ti+=q*radial(theta,0,b,n)
                to+=q*radial(theta,b,r,n)
        if j==0:ti*=2;to*=2
        else:ti*=2
        inner+=ti;outer.append(to)
    return np.array([inner,outer[0],outer[1],outer[1]])

def main():
    print('Actual F(w)=(s-1)zeta(s), s=1/(1-w). Integral dA/|F|^2.',flush=True)
    print('Triangle inradius .2. R2=R3 by conjugation (computed once).',flush=True)
    print('r n dps T R1 R2 R3 TOTAL (n Gauss nodes per panel / radial interval)',flush=True)
    for r in [.4,.75,.9,.95,.99]:
        for n,dps in [(6,20),(12,30)]:
            v=regional(r,n,dps)
            print(f'{r} {n} {dps}',*(f'{x:.10f}' for x in v),f'{sum(v):.10f}',flush=True)
    print('Synthetic normalized simple and double poles: F(w)=(1-w/a)^m, a=.7; integrate epsilon<|w-a|<.1.',flush=True)
    print('epsilon simple_numeric simple_exact double_numeric double_exact',flush=True)
    for e in [1e-2,1e-3,1e-4,1e-5,1e-6]:
        u,ww=nodes(log(e),log(.1),64); a=.7
        sim=2*pi*a*a*sum(ww)
        dou=2*pi*a**4*sum(ww*np.exp(-2*u))
        print(f'{e:g} {sim:.10g} {2*pi*a*a*log(.1/e):.10g} {dou:.10g} {pi*a**4*(e**-2-.1**-2):.10g}',flush=True)
    print('Analytic lower bound |F| >= (1-2r)/(1-r) for r<1/2; energy upper bound:',flush=True)
    for r in [.1,.25,.4,.49]:
        print(r,pi*r*r*((1-r)/(1-2*r))**2,flush=True)
if __name__=='__main__':main()
