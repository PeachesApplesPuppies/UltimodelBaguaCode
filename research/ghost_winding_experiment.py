"""Numerical winding test for finite prime elimination (not a proof of RH).
Python 3, numpy, mpmath. Run: python ghost_winding_experiment.py
"""
import numpy as np
import mpmath as mp

mp.mp.dps = 30
N=256
X=1_000_000
sieve=np.ones(X+1,dtype=bool); sieve[:2]=False
for p in range(2,int(X**.5)+1):
    if sieve[p]: sieve[p*p::p]=False
primes=np.flatnonzero(sieve)
logs=np.log(primes)
t=float(mp.im(mp.zetazero(1)))

def winding(phases):
    # Nearest-angle increments; can alias on undersampled curves.
    return np.angle(np.exp(1j*np.diff(np.r_[phases, phases[0]]))).sum()/(2*np.pi)

def test(name,center,r,synthetic=False):
    s=center+r*np.exp(2j*np.pi*np.arange(N)/N)
    if synthetic:
        f=np.prod([s-(.5+a*.2+b*1j*t) for a in (-1,1) for b in (-1,1)],axis=0)
    else:
        f=np.array([complex(mp.zeta(complex(v))) for v in s])
    phase=np.angle(f)
    print(f'\n{name}: center={center}, radius={r}; original winding={winding(phase):.9f}')
    for cutoff in (100,10000,1000000):
        l=logs[primes<=cutoff]
        # Each log(1-p^-s) is single-valued on Re(s)>0.
        ghost=np.array([np.log1p(-np.exp(-v*l)).sum() for v in s])
        reduced_logmag=np.log(np.abs(f))+ghost.real
        reduced_phase=phase+ghost.imag
        print(f'  X={cutoff:7d} primes={len(l):5d}: log10|reduced| range [{reduced_logmag.min()/np.log(10):.3f}, {reduced_logmag.max()/np.log(10):.3f}]; raw winding={winding(reduced_phase):.9f}; corrected winding={winding(reduced_phase-ghost.imag):.9f}; max ghost phase step={np.max(np.abs(np.diff(np.r_[ghost.imag,ghost.imag[0]]))):.3f} rad')

if __name__=='__main__':
    test('Actual first zero',.5+1j*t,.1)
    test('Displaced control',.7+1j*t,.1)
    test('Nonzero critical-line control',.5+1j,.1)
    test('Synthetic off-line zero',.7+1j*t,.1,True)
