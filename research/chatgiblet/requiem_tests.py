"""Finite numerical illustrations, not a proof of RH or of positivity for all t."""
import numpy as np
N = 1_000_000
prime = np.ones(N+1, dtype=bool); prime[:2] = False
for k in range(2, int(N**.5)+1):
    if prime[k]: prime[k*k::k] = False
lam = np.zeros(N+1, dtype=np.longdouble)
for k in np.flatnonzero(prime):
    n = int(k)
    while n <= N:
        lam[n] = np.log(np.longdouble(k)); n *= int(k)
ps = np.cumsum(lam)
w = np.zeros(N+1, dtype=np.longdouble)
w[1:] = np.cumsum(lam[1:]/np.arange(1,N+1,dtype=np.longdouble))
gamma = np.longdouble('0.577215664901532860606512090082402431')
pi = np.longdouble('3.141592653589793238462643383279502884')

def requiem(t):
    t = np.abs(np.asarray(t,dtype=np.longdouble)); x = np.exp(t)
    if np.any(x > N+1e-8): raise ValueError('out of sieve range')
    n = np.minimum(x.astype(int),N); z = 1/x
    G = x*w[n]-ps[n]-x*t+(1+gamma)*x
    # sum_{n>=1} z^(2n)/(2n(2n+1)) in closed form, continuous at z=1
    a=(1+z)*np.log1p(z); b=np.zeros_like(z); mask=z<1
    b[mask]=(1-z[mask])*np.log1p(-z[mask])
    correction=1-(a-b)/(2*z)
    return np.asarray((G-np.log(2*pi)+correction)/np.sqrt(x),float)

if __name__ == '__main__':
    T=float(np.log(N)); rng=np.random.default_rng(42); mins=[]
    for i in range(100):
        t=np.sort(rng.uniform(0,T,12))
        mins.append(np.linalg.eigvalsh(requiem(t[:,None]-t[None,:]))[0])
    t=np.linspace(0,T-1e-6,200001); y=requiem(t)
    print('C(0)',requiem(0),'sample maximum abs',np.max(np.abs(y)))
    print('PSD checks',sum(v>=-1e-10 for v in mins),'/100; min eig',min(mins))
    for g in [14.1347251417347,21.0220396387716,25.0108575801457]:
        v=np.trapezoid(y*np.exp(-1j*g*t),t)/t[-1]; pred=1/(g*g+.25)
        print('omega',g,'coefficient',v,'simple-zero prediction',pred,'abs error',abs(v-pred))
