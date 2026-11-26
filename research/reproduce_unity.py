import numpy as np
import scipy.special as sp
from scipy.optimize import brentq
from scipy.integrate import quad
import mpmath as mp

def kernel(nq=320, upper=1.8, nmax=8):
    nodes, weights = sp.roots_legendre(nq)
    u=(nodes+1)*upper/2
    n=np.arange(1,nmax+1)[:,None]
    a=np.pi*n*n*np.exp(4*u)
    phi=np.sum((2*np.pi**2*n**4*np.exp(9*u)-3*np.pi*n*n*np.exp(5*u))*np.exp(-a),axis=0)
    weights=weights*upper/2*phi
    def H(t,x,k=0):
        return np.dot(weights*np.exp(t*u*u)*u**k,np.cos(x*u+k*np.pi/2))
    return H

def xi(s):
    return mp.mpf('0.5')*s*mp.pi**(-s/2)*mp.gamma(s/2)*((s-1)*mp.zeta(s) if s!=1 else 1)

def li(dps, M=64):
    with mp.workdps(dps):
        r=mp.mpf('0.2'); vals=[]
        for j in range(M):
            w=r*mp.exp(2j*mp.pi*j/M)
            vals.append(mp.log(2*xi(1/(1-w))))
        return [+(k*mp.re(sum(vals[j]*mp.exp(-2j*mp.pi*j*k/M) for j in range(M)))/(M*r**k)) for k in range(1,9)]

def main():
    mp.mp.dps=40
    print('xi center',mp.nstr(xi(mp.mpf('.5')),24))
    H=kernel(); H2=kernel(480,2.0,10)
    print('kernel norm check',H(0,0),float(xi(mp.mpf('.5'))/8),H2(0,0))
    zz=[mp.zetazero(j) for j in range(1,11)]
    roots=[float(mp.im(z)) for z in zz]
    print('first ten unity maximum deviation',mp.nstr(max(abs(abs(1-1/z)-1) for z in zz),8))
    print('time, roots, gap, root change on grid refinement, residual')
    rows=[]
    for t in [-.5,-.25,0,.25,.5]:
        x=[brentq(lambda x:H(t,x),2*r-2,2*r+2,xtol=1e-11)/2 for r in roots[:2]]
        y=[brentq(lambda x:H2(t,x),2*r-2,2*r+2,xtol=1e-11)/2 for r in roots[:2]]
        rows.append(x)
        print(t,*[f'{v:.10f}' for v in x],f'{x[1]-x[0]:.10f}',max(abs(a-b) for a,b in zip(x,y)),max(abs(H(t,2*r)) for r in x))
    print('instant velocities ordinate',*[H(0,2*r,2)/H(0,2*r,1)/2 for r in roots[:2]])
    g=np.diff(np.array(rows),axis=1).ravel(); p=g/g[2]
    print('normalized gaps',p)
    for a,b in [(1,3),(0,4)]: print('opposite mean/product', (p[a]+p[b])/2,p[a]*p[b])
    print('integrated along critical axis / pi; via double precision kernel')
    for t in [1,2,np.pi,5,2*np.pi,10,*roots[:2]]:
        val=quad(lambda v:8*H(0,2*v),0,t,epsabs=1e-11)[0]/np.pi
        val2=quad(lambda v:8*H2(0,2*v),0,t,epsabs=1e-11)[0]/np.pi
        print(f'{t:.10f} {val:.12f} {2*val:.12f} grid diff {abs(val-val2):.3g}')
    print('real axis integrated / pi')
    for z in [.5,1,2,np.pi]:
        a=mp.quad(lambda v:xi(mp.mpf('.5')+v),[0,z]);print(z,mp.nstr(a,15),mp.nstr(a/mp.pi,15))
    print('Li coefficients, independent contour sampling')
    l1=li(40,64); l2=li(55,96)
    for j,(a,b) in enumerate(zip(l1,l2),1):print(j,mp.nstr(b,20),'diff',mp.nstr(abs(a-b),4))
    print('integration depth coefficient ratio')
    for N in [0,10,40,100,200]:print(N,(roots[0]/roots[1])**(N+2))
    print('synthetic off-line detector (d=.2, height first zero)')
    for d in [0,.2,-.2]:
        s=mp.mpc(mp.mpf('.5')+d,roots[0]);u=1-1/s;v=abs(u);print(d,mp.nstr(v,16),mp.nstr((v-1/v)**2,12),mp.nstr(abs(u*(1-1/(1-s))-1),5))
if __name__=='__main__':main()
