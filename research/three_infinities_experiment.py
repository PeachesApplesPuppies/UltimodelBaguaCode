"""Regional winding experiment. Requires numpy and mpmath. Empirical, not certified."""
import numpy as np
import mpmath as mp
from functools import lru_cache
A=0.2
ROOTS=np.array([.08+.03j,.65+.08j,.73*np.exp(1j*(2*np.pi/3+.12)),.81*np.exp(-1j*(2*np.pi/3+.19))])
OMEGA=np.exp(2j*np.pi/3)
def segment(a,b,n): return a+(b-a)*np.arange(n)/n
def contours(r,n):
    lo,hi=np.exp(-1j*np.pi/3),np.exp(1j*np.pi/3)
    a,b=2*A*lo,2*A*hi
    arc=r*np.exp(1j*np.linspace(-np.pi/3,np.pi/3,n,endpoint=False))
    region=np.concatenate([segment(a,r*lo,n),arc,segment(r*hi,b,n),segment(b,a,n)])
    triangle=np.concatenate([segment(a,b,n)*OMEGA**k for k in range(3)])
    whole=r*np.exp(2j*np.pi*np.arange(3*n)/(3*n))
    return [triangle]+[region*OMEGA**k for k in range(3)]+[whole]
@lru_cache(maxsize=100000)
def f_cached(x,y,dps):
    with mp.workdps(dps):
        w=mp.mpc(x,y); s=1/(1-w)
        return complex((s-1)*mp.zeta(s)) if w else 1+0j
def f(w,dps):
    return np.array([f_cached(round(z.real,15),round(abs(z.imag),15),dps).conjugate() if z.imag<0 else f_cached(round(z.real,15),round(abs(z.imag),15),dps) for z in w])
def synthetic(w): return np.prod(1-w[:,None]/ROOTS[None,:],axis=1)
def winding(values):
    phases=np.angle(np.roll(values,-1)/values)
    return phases.sum()/(2*np.pi),max(abs(phases))
def region_of(w):
    p=np.array([w.real,(-w.real+np.sqrt(3)*w.imag)/2,(-w.real-np.sqrt(3)*w.imag)/2])
    return 'T' if max(p)<A else 'R'+str(1+np.argmax(p))
def main():
    print('Triangle inradius',A,'circumradius',2*A,flush=True)
    print('Synthetic roots:',[(region_of(w),complex(w),abs(w)) for w in ROOTS],flush=True)
    print('Columns: radius, samples per segment, precision, model, counts [T,R1,R2,R3,disk], maximum sampled phase step (radians)',flush=True)
    for r in [.75,.95,.99]:
        for n,dps in [(64,25),(128,35)]:
            cs=contours(r,n); actual=[f(c,dps) for c in cs]
            for name,vals in [('actual',actual),('synthetic',[synthetic(c) for c in cs]),('actual*synthetic',[v*synthetic(c) for c,v in zip(cs,actual)])]:
                res=[winding(v) for v in vals]
                print(r,n,dps,name,[round(t[0],10) for t in res],round(max(t[1] for t in res),6),flush=True)
    print('Projection recovery and power-map recovery with retained branch index:',flush=True)
    with mp.workdps(65):
        rho=mp.mpc('.7',mp.im(mp.zetazero(1))); w=1-1/rho
        x,y=mp.re(w),mp.im(w)
        p1=x;p2=(-x+mp.sqrt(3)*y)/2;p3=(-x-mp.sqrt(3)*y)/2
        recovered=mp.mpc(p1,(p2-p3)/mp.sqrt(3))
        print('projection reconstruction error',mp.nstr(abs(w-recovered),8),flush=True)
        print('m, radius, retained branch, absolute original s reconstruction error',flush=True)
        for m in [1,3,4,6,12,144,1728,20736]:
            v=w**m; j=int(mp.nint((m*mp.arg(w)-mp.arg(v))/(2*mp.pi)))
            back=mp.exp((mp.log(v)+2j*mp.pi*j)/m)
            print(m,mp.nstr(abs(v),17),j,mp.nstr(abs(1/(1-back)-rho),8),flush=True)
        print('Without branch index, m-th root is ambiguous; compression does not preserve direction by itself.',flush=True)
        print('High-height example: s=.7+3e12 i (synthetic, not a zeta zero).',flush=True)
        w=1-1/mp.mpc('.7','3e12'); gap=-mp.log(abs(w))
        print('negative log radius',mp.nstr(gap,18),'degree to halve radius',mp.ceil(mp.log(2)/gap),flush=True)
        for depth in [12,24,25]:
            m=12**depth
            print('depth',depth,'degree',m,'radius',mp.nstr(mp.exp(-m*gap),18),flush=True)
if __name__=='__main__':main()

# Additional compressed polygon tests on the actual function and controls.
def compressed_tests():
    print('Compressed polygon tests: radius in v=0.5, count actual / synthetic / product, max actual phase step',flush=True)
    for m in [3,4,6,12]:
        for n in [64,128]:
            t=2*np.pi*np.arange(n)/n
            v=.5*np.exp(1j*t)
            w=.5**(1/m)*np.exp(1j*t/m)
            vals=np.prod([f(w*np.exp(2j*np.pi*k/m),25) for k in range(m)],axis=0)
            syn=np.prod(1-v[:,None]/(ROOTS[None,:]**m),axis=1)
            print(m,n,[round(winding(z)[0],10) for z in [vals,syn,vals*syn]],round(winding(vals)[1],6), 'expected synthetic',sum(abs(ROOTS)**m<.5),flush=True)
    print('Equal-count counterexample: one orbit of three interior roots at modulus 0.7.',flush=True)
    roots=.7*np.exp(.1j)*OMEGA**np.arange(3)
    print('regions',[region_of(w) for w in roots], 'radii',abs(roots),flush=True)
    print('winding',[round(winding(np.prod(1-c[:,None]/roots[None,:],axis=1))[0],10) for c in contours(.95,128)],flush=True)
if __name__=='__main__':compressed_tests()
