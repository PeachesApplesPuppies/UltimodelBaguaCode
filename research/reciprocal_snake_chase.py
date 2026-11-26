"""Numerical exploration, not a proof of RH. Requires numpy, mpmath."""
import numpy as np
import mpmath as mp

def coefficients(dps,N,r,nmax=64):
    with mp.workdps(dps):
        r=mp.mpf(r); om=mp.exp(2j*mp.pi/N)
        y=[]
        for j in range(N//2+1):
            w=r*om**j; s=(2+w)/(1-w)
            y.append(1/((2+w)*mp.zeta(s)))
        y+= [mp.conj(y[j]) for j in range(N//2-1,0,-1)]
        return [mp.re(mp.fsum(y[j]*om**(-j*n) for j in range(N)))/(N*r**n) for n in range(nmax+1)]

def mobius(N):
    mu=np.ones(N+1,dtype=np.int8); mu[0]=0
    prime=np.ones(N+1,dtype=bool); prime[:2]=False
    for p in range(2,int(N**.5)+1):
        if prime[p]: prime[p*p::p]=False
    for p in np.flatnonzero(prime):
        mu[p::p]*=-1
        if p*p<=N: mu[p*p::p*p]=0
    return mu

def main():
    mp.mp.dps=65
    c=coefficients(55,192,'.7'); d=coefficients(65,320,'.65')
    print('C(w)=1/((2+w)*zeta((2+w)/(1-w)))')
    print('n, coefficient, difference between Fourier resolutions')
    for n in [0,1,2,4,8,16,24,32,48,64]:
        print(n,mp.nstr(d[n],18),mp.nstr(abs(c[n]-d[n]),5))
    print('Max difference 0..64:',mp.nstr(max(abs(a-b) for a,b in zip(c,d)),8))
    N=1_000_000; mu=mobius(N); M=np.cumsum(mu,dtype=np.int64)
    x=np.arange(1,N,dtype=float); sq=M[1:N].astype(float)**2
    # M(x)=M(floor(x)); integrate exactly on unit intervals.
    print('X, M(X), max |M(n)|/sqrt(n), energy delta=0,.05,.2')
    energies=[]
    for delta in [0,.05,.2]:
        a=1+2*delta
        # integral from n to n+1 of t^(-2-2delta) dt
        weights=x**(-a)*(-np.expm1(-a*np.log1p(1/x)))/a
        energies.append(np.cumsum(sq*weights))
    for X in [10,100,1000,10000,100000,N]:
        print(X,M[X],float(np.max(abs(M[1:X+1])/np.sqrt(np.arange(1,X+1)))),*[float(e[X-2]) for e in energies])
    print('Synthetic controls: M(x)=x^beta, exact energy integral for delta=.05')
    for X in [100,10000,N]:
        print(X,*[(X**(2*beta-1-.1)-1)/(2*beta-1-.1) for beta in [.5,.7]])
if __name__=='__main__':main()
