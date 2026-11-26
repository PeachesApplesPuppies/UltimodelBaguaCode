"""Reciprocal cruller: exact geometric formulas and empirical contour winding.
Requires numpy, scipy, mpmath. No certified zero counts or RH claim.
"""
import numpy as np
from scipy.special import i0
import mpmath as mp

def winding(values):
    steps=np.angle(np.roll(values,-1)/values)
    return steps.sum()/(2*np.pi),np.max(np.abs(steps))

def main():
    theta=2*np.pi*np.arange(65536)/65536
    print('a | max radius | min radius | area/pi | mean radius | violation mean (r-1/r)^2 | max reciprocal error')
    for a in [0,.5,1,2,5,10]:
        r=np.exp(a*np.cos(3*theta)); reciprocal=np.exp(-a*np.cos(3*theta))
        print(f'{a:4g} {np.exp(a):.10g} {np.exp(-a):.10g} {i0(2*a):.10g} {i0(a):.10g} {2*(i0(2*a)-1):.10g} {np.max(np.abs(r*reciprocal-1)):.3g}')
        assert np.isclose(np.mean(r*r),i0(2*a),rtol=1e-13)
    print('\nOriginal time evolution a=t*sin(t):')
    for t in [0,np.pi/2,np.pi,3*np.pi/2,2*np.pi,5*np.pi/2,9*np.pi/2]:
        a=t*np.sin(t)
        print(f't={t:.8f} a={a:.8f} r(0)={np.exp(a):.9g} r(pi/3)={np.exp(-a):.9g}')
    print('\nContour scaled by .95 exp(-abs(a)), so entire curve is inside unit disk.')
    print('Synthetic conjugate symmetry is not required for this winding control; two points at angles 0 and pi/3, both radius .7.')
    roots=[.7+0j,.7*np.exp(1j*np.pi/3)]
    print('a samples actual_winding synthetic_winding product_winding actual_max_phase_step included_roots')
    mp.mp.dps=25
    for a in [0,.3,-.3,.8,-.8]:
        for n in [128,256]:
            t=np.arange(n)*2*np.pi/n
            z=.95*np.exp(a*np.cos(3*t)-abs(a)+1j*t)
            actual=[]
            for w in z:
                s=1/(1-mp.mpc(complex(w)))
                actual.append(complex((s-1)*mp.zeta(s)))
            actual=np.array(actual); syn=np.prod([1-z/root for root in roots],axis=0)
            wa,step=winding(actual); ws,_=winding(syn); wp,_=winding(actual*syn)
            inc=[i+1 for i,root in enumerate(roots) if abs(root)<.95*np.exp(a*np.cos(3*np.angle(root))-abs(a))]
            print(a,n,f'{wa:.10f}',f'{ws:.10f}',f'{wp:.10f}',f'{step:.6f}',inc,flush=True)
if __name__=='__main__':main()
