import numpy as np
import mpmath as mp
from math import pi
mp.mp.dps=23

def measure(r,n):
    # f=(s-1)zeta(s) differs from Q by a nonvanishing analytic factor in the disk.
    f=[]; radial=[]
    for j in range(n//2+1):
        w=mp.mpf(r)*mp.exp(2j*mp.pi*j/n)
        s=1/(1-w)
        z=mp.zeta(s); dz=mp.zeta(s,derivative=1)
        f.append(complex((s-1)*z))
        radial.append(float(mp.re((w/r)/(1-w)**2*(1/(s-1)+dz/z))))
    v=np.array(f+list(np.conj(f[1:-1][::-1])))
    d=np.array(radial+radial[1:-1][::-1])
    phase=np.angle(np.roll(v,-1)/v)
    return np.log(np.abs(v)).mean(), d.mean(), phase.sum()/(2*pi), np.max(np.abs(phase))

if __name__=='__main__':
    for r,ns in [(0.5,[64,128]),(0.9,[128,256]),(0.99,[256,512,1024]),(0.999,[1024,2048])]:
        for n in ns:
            print(r,n,*['%.12g'%x for x in measure(r,n)],flush=True)
    rho=0.7+14.1347251417347j
    a=1-1/rho
    print('synthetic radius',abs(a), 'angle',np.angle(a),flush=True)
    for r in [.99,.999,.9995,.9999]:
        print('synthetic',r,2*max(0,np.log(r/abs(a))), (2/r if r>abs(a) else 0),flush=True)
    for r,n in [(0.99,2048),(0.999,4096),(0.999,8192),(0.999,16384)]:
        print(r,n,*['%.12g'%x for x in measure(r,n)],flush=True)
    for r in [.999,.9995,.9999]:
        n=65536; w=r*np.exp(2j*np.pi*np.arange(n)/n)
        v=(1-w/a)*(1-w/a.conjugate())
        d=np.real(w/r*(1/(w-a)+1/(w-a.conjugate())))
        print('synthetic sampled',r,n,np.log(np.abs(v)).mean(),d.mean(),np.angle(np.roll(v,-1)/v).sum()/(2*np.pi),flush=True)
