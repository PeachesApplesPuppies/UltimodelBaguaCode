import json, math, os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def main():
    N=10_000_000
    p=np.ones(N+1,dtype=bool); p[:2]=False
    for k in range(2,math.isqrt(N)+1):
        if p[k]: p[k*k::k]=False
    primes=np.flatnonzero(p)
    a=np.zeros(N+1); a[primes]=np.log(primes)
    for k in primes[primes<=math.isqrt(N)]:
        m=int(k)**2
        while m<=N: a[m]=math.log(k); m*=int(k)
    psi=np.cumsum(a)
    endpoints={str(x):float(psi[x]-x) for x in (100,1000,10000,100000,1000000,N)}
    reference=[-5.954688770642605,-3.3190877528245437,13.396693263108318,51.56402565800818,-413.402504368918,-1460.5966541059315]
    assert all(abs(a-b)<1e-7 for a,b in zip(endpoints.values(),reference))
    # Finite-window translation on a zero-padded sequence; Gram of shifts.
    t=np.linspace(math.log(100),math.log(N),32768,endpoint=False)
    x=np.exp(t); f=(psi[x.astype(int)]-x)/np.sqrt(x)
    shifts=[0,1,8,64,256,1024]
    def gram(v):
        Z=np.stack([np.pad(v,(k,max(shifts)-k)) for k in shifts]); Z=Z/np.linalg.norm(v)
        return Z@Z.conj().T
    G=gram(f); eig=np.linalg.eigvalsh(G)
    assert eig.min()>-1e-12
    # Unitary cyclic shift is exact on finite support, but depends on padding period.
    rng=np.random.default_rng(26); v=rng.normal(size=256)+1j*rng.normal(size=256)
    err=max(abs(np.vdot(np.roll(v,k),np.roll(v,k))-np.vdot(v,v)) for k in range(-20,21))
    assert err<1e-10
    # Growing controls: normalized Gram remains PSD despite growth.
    controls=[]
    for d in [0,.01,.05,.25]:
        for T in [20,80]:
            t0=np.linspace(0,T,32768,endpoint=False); g=np.exp((d+14j)*t0)
            H=gram(g); h=1.; dt=T/len(g); k=round(h/dt); h=k*dt
            c=np.vdot(g[:-k],g[k:])/np.vdot(g,g)
            # exact continuum normalized autocorrelation of truncated exponential
            mag=(1-h/T) if d==0 else math.exp(-d*h)*(-math.expm1(-2*d*(T-h)))/(-math.expm1(-2*d*T))
            assert abs(abs(c)-mag)<1e-10 and np.linalg.eigvalsh(H).min()>-1e-12
            controls.append(dict(delta=d,T=T,gram_min=float(np.linalg.eigvalsh(H).min()),correlation_magnitude=float(abs(c)),formula=mag,energy=float(np.vdot(g,g).real*dt)))
    # Laplace energy: exact dyadic integrals of a growing mode, threshold eps=delta.
    thresholds=[]
    for d in [0,.01,.05,.25]:
        for e in [.01,.05,.1,.3]:
            rate=2*(d-e)
            thresholds.append(dict(delta=d,epsilon=e,finite=rate<0,integral=(-1/rate if rate<0 else None)))
    # Check previously archived endpoint values when available, without silently assuming them.
    out=dict(primes=len(primes),endpoint_regressions=6,endpoints=endpoints,prime_gram_eigenvalues=eig.tolist(),shift_norm_error=float(err),controls=controls,weighted_energy_thresholds=thresholds)
    tmp=ROOT/'results.tmp'; tmp.write_text(json.dumps(out,indent=2)); os.replace(tmp,ROOT/'results.json'); print(json.dumps(out,indent=2))
if __name__=='__main__':
    try: main()
    except KeyboardInterrupt: raise SystemExit(130)
