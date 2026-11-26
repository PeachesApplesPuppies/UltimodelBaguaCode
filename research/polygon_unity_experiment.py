"""Polygonal filters for xi and a controlled off-unit-circle pair.
Requires mpmath, numpy. Numerical evidence, not certified zero counts.
"""
import mpmath as mp
import numpy as np
MS=(3,4,6,12)
def xi(s):
    return mp.mpf('0.5')*s*mp.pi**(-s/2)*mp.gamma(s/2)*((s-1)*mp.zeta(s) if s!=1 else 1)
def Q(w): return 2*xi(1/(1-w))
def li(dps, M, radius, nmax=36):
    with mp.workdps(dps):
        r=mp.mpf(radius); omega=mp.exp(2j*mp.pi/M)
        vals=[mp.log(Q(r*omega**j)) for j in range(M)]
        return [+(n*mp.re(mp.fsum(vals[j]*omega**(-j*n) for j in range(M)))/(M*r**n)) for n in range(1,nmax+1)]
def wind(v): return np.angle(np.roll(v,-1)/v).sum()/(2*np.pi)
def main():
    mp.mp.dps=65
    a=1-1/mp.mpc('.7',mp.im(mp.zetazero(1)))
    print('synthetic s = 0.7 +/- i*first zero ordinate; a =',mp.nstr(a,25),'radius',mp.nstr(abs(a),25),flush=True)
    L1=li(65,128,'.2'); L2=li(75,192,'.25')
    print('max Li coefficient difference, n<=36:',mp.nstr(max(abs(x-y) for x,y in zip(L1,L2)),8),flush=True)
    print('m | L_m | L_2m/2 | L_3m/3 | synthetic radius in v=w^m | radial gap amplification',flush=True)
    for m in MS:
        print(m,*[mp.nstr(L2[m*k-1]/k,16) for k in range(1,4)],mp.nstr(abs(a)**m,17),mp.nstr((1-abs(a)**m)/(1-abs(a)),12),flush=True)
    print('check actual product vs filtered log series, v=w^m, |w|=.2',flush=True)
    w=mp.mpc('.12','.16')
    for m in MS:
        omega=mp.exp(2j*mp.pi/m)
        exact=mp.fprod(Q(w*omega**j) for j in range(m))
        approx=mp.exp(mp.fsum(L2[m*k-1]*w**(m*k)/k for k in range(1,36//m+1)))
        print(m,'error',mp.nstr(abs(exact-approx),8),flush=True)
    print('synthetic product identity, winding in original w and collapsed v planes',flush=True)
    aa=complex(a); t=np.arange(65536)*2*np.pi/65536
    for m in MS:
        omega=mp.exp(2j*mp.pi/m)
        def P(z):return (1-z/a)*(1-z/mp.conj(a))
        product=mp.fprod(P(w*omega**j) for j in range(m))
        collapsed=(1-w**m/a**m)*(1-w**m/mp.conj(a)**m)
        print(m,'identity error',mp.nstr(abs(product-collapsed),6),flush=True)
        for r in [.998,.9995]:
            z=r*np.exp(1j*t); v=r**m*np.exp(1j*t)
            fv=(1-v/aa**m)*(1-v/aa.conjugate()**m)
            fw=(1-z**m/aa**m)*(1-z**m/aa.conjugate()**m)
            print('  r',r,'v radius',r**m,'winding w',round(wind(fw)),'v',round(wind(fv)), 'J_v exact',float(2*max(0,mp.log(mp.mpf(r)**m/abs(a)**m))),flush=True)
    print('synthetic radial gap vs m; m to make |a|^m <= 0.5:',int(mp.ceil(mp.log(mp.mpf('.5'))/mp.log(abs(a)))),flush=True)
if __name__=='__main__':main()
