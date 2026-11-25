"""The Great Io: asymmetric planar Newtonian three-body experiment.
BCE / UltimodelBaguaCode, 2026-11-25.

Run: python -m pip install numpy scipy
     python great_io_gravity_test.py
Stop at any time with Ctrl+C. No files are written.
Compares Cartesian and log-polar Jacobi-coordinate integrations with DOP853.
ABC=1 is a normalization identity, not a new gravitational conservation law.
The tighter baseline run reproduced a maximum sampled position disagreement
of 1.78e-9, unity residual 1.11e-15, and minimum sampled separation 0.0095056.
Changing initial velocity gave final position difference 3.70087 despite
identical initial normalized shape. Exact collisions are not handled.
This is a numerical coordinate-equivalence test, not a general analytical
solution to the three-body problem. No speed advantage was observed.
"""

import numpy as np
from scipy.integrate import solve_ivp
m=np.array([1.,1.7,.6]); M=m.sum(); M12=sum(m[:2]); alpha=m[1]/M12; beta=m[0]/M12
r=np.array([[-1.,.2],[.7,-.6],[.3,1.2]])
v=np.array([[.25,.45],[-.55,.1],[.12,-.38]])
r-=m@r/M; v-=m@v/M

def newton(t,y):
    R,V=y[:6].reshape(3,2),y[6:].reshape(3,2)
    d=R[None,:,:]-R[:,None,:]; d2=(d*d).sum(axis=2); np.fill_diagonal(d2,np.inf)
    acc=np.sum(d*m[None,:,None]/d2[:,:,None]**1.5,axis=1)
    return np.r_[V.ravel(),acc.ravel()]

def polar(q,dq):
    return np.log(np.linalg.norm(q)), np.arctan2(q[1],q[0]), q@dq/(q@q), (q[0]*dq[1]-q[1]*dq[0])/(q@q)

def encode(R,V):
    return np.r_[polar(R[1]-R[0],V[1]-V[0]),polar(R[2]-beta*R[0]-alpha*R[1],V[2]-beta*V[0]-alpha*V[1])]

def unpolar(z):
    u,a,du,da=z; e=np.array([np.cos(a),np.sin(a)]); j=np.array([-e[1],e[0]]); rho=np.exp(u)
    return rho*e,rho*(du*e+da*j),e,j,rho

def decode(z):
    q,dq,*_=unpolar(z[:4]); s,ds,*_=unpolar(z[4:]); c=-m[2]/M*s; dc=-m[2]/M*ds
    return np.r_[np.array([c-alpha*q,c+beta*q,c+s]).ravel(),np.array([dc-alpha*dq,dc+beta*dq,dc+ds]).ravel()]

def transformed(t,z):
    q,dq,e1,j1,r1=unpolar(z[:4]); s,ds,e2,j2,r2=unpolar(z[4:]); d13=s+alpha*q; d23=s-beta*q
    a13=d13/np.linalg.norm(d13)**3; a23=d23/np.linalg.norm(d23)**3
    ddq=-M12*q/r1**3+m[2]*(a23-a13); dds=-M/M12*(m[0]*a13+m[1]*a23)
    def rhs(z,e,j,r,dd):
        u,a,du,da=z
        return [du,da,dd@e/r-du**2+da**2,dd@j/r-2*du*da]
    return np.r_[rhs(z[:4],e1,j1,r1,ddq),rhs(z[4:],e2,j2,r2,dds)]

def dist(R):
    return np.linalg.norm(R[:,[1,2,0]]-R[:,[0,1,2]],axis=2)

def invariants(Y):
    R=Y[:,:6].reshape(-1,3,2); V=Y[:,6:].reshape(-1,3,2); d=dist(R)
    energy=.5*np.sum(m[None,:]*np.sum(V*V,axis=2),axis=1)-np.sum((m[[0,1,2]]*m[[1,2,0]])[None,:]/d,axis=1)
    ang=np.sum(m[None,:]*(R[:,:,0]*V[:,:,1]-R[:,:,1]*V[:,:,0]),axis=1)
    scale=np.exp(np.mean(np.log(d),axis=1)); abc=d/scale[:,None]
    return energy,ang,d,abc,scale

def run(R,V,horizon=8.,tol=1e-11):
    ts=np.linspace(0,horizon,2001); opt=dict(t_eval=ts,method='DOP853',rtol=tol,atol=tol*.01)
    a=solve_ivp(newton,[0,horizon],np.r_[R.ravel(),V.ravel()],**opt)
    b=solve_ivp(transformed,[0,horizon],encode(R,V),**opt)
    assert a.success and b.success,(a.message,b.message)
    Y=a.y.T; Z=np.array([decode(z) for z in b.y.T]); E,L,d,abc,scale=invariants(Y); E2,L2,d2,abc2,_=invariants(Z)
    print('horizon',horizon,'tol',tol,'samples',len(ts),'nfev',a.nfev,b.nfev)
    print('max_pos',np.max(np.linalg.norm((Y[:,:6]-Z[:,:6]).reshape(-1,3,2),axis=2)),'max_vel',np.max(np.linalg.norm((Y[:,6:]-Z[:,6:]).reshape(-1,3,2),axis=2)))
    print('min separation',d.min(),'max ABC error',np.max(np.abs(np.prod(abc,axis=1)-1)),np.max(np.abs(np.prod(abc2,axis=1)-1)))
    print('energy',E[0], 'drifts',np.max(abs(E-E[0])),np.max(abs(E2-E2[0])),'L',L[0],'drifts',np.max(abs(L-L[0])),np.max(abs(L2-L2[0])))
    for i in [0,500,1000,1500,2000]: print('sample',ts[i],*abc[i], 'scale',scale[i], 'pos',Y[i,:6].tolist())
    return ts,Y,Z,abc
if __name__=='__main__':
    print('initial R',r,'initial V',v)
    t,Y,Z,abc=run(r,v)
    run(r,v,tol=1e-13)
    vv=v.copy(); vv[0]+=[.05,-.03]; vv-=m@vv/M
    print('velocity counterexample'); _,Y2,_,abc2=run(r,vv)
    print('counterexample same initial shape',np.max(abs(abc[0]-abc2[0])),'final shape diff',np.linalg.norm(abc[-1]-abc2[-1]),'final position diff',np.max(np.linalg.norm((Y[-1,:6]-Y2[-1,:6]).reshape(3,2),axis=1)))
    print('cycle initial abc',abc[0], 'at t=8/3 approx',abc[667], 'cyclic permutation',np.roll(abc[0],-1))
