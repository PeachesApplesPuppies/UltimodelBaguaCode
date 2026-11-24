"""Herzog's Chromatic Requiem: reversible ratios, finite arithmetic tests."""
import argparse, csv, json, math
from fractions import Fraction
from pathlib import Path
import numpy as np


def encode(value, reference=1):
    """Exact R:B:G ratio (for exact inputs); a fixed positive reference is retained."""
    v, g = Fraction(value), Fraction(reference)
    if g <= 0:
        raise ValueError('reference must be positive')
    return max(v, 0), max(-v, 0), g


def decode(ratio):
    r,b,g = map(Fraction, ratio)
    if min(r,b)<0 or g<=0 or (r and b):
        raise ValueError('not a signed reference ratio')
    return (r-b)/g


def swatch(ratio):
    r,b,g = map(Fraction, ratio)
    decode(ratio)
    m=max(r,b,g)
    return '#'+''.join(f'{round(255*v/m):02X}' for v in (r,g,b))


def primitive_palette(max_sum):
    for s in range(1,max_sum+1):
        for r in range(s,-1,-1):
            for b in range(s-r,-1,-1):
                g=s-r-b
                if math.gcd(math.gcd(r,b),g)==1:
                    yield r,b,g


class Requiem:
    def __init__(self, limit=1_000_000):
        if limit<2: raise ValueError('limit must be >=2')
        self.limit=limit
        self.T=math.log(limit)
        self.p=np.ones(limit+1,dtype=bool); self.p[:2]=False
        for k in range(2,math.isqrt(limit)+1):
            if self.p[k]: self.p[k*k::k]=False
        lam=np.zeros(limit+1,dtype=np.longdouble)
        for k in np.flatnonzero(self.p):
            n=int(k)
            while n<=limit:
                lam[n]=np.log(np.longdouble(k)); n*=int(k)
        self.ps=np.cumsum(lam)
        self.w=np.zeros(limit+1,dtype=np.longdouble)
        self.w[1:]=np.cumsum(lam[1:]/np.arange(1,limit+1,dtype=np.longdouble))
        self.gamma=np.longdouble('0.577215664901532860606512090082402431')
        self.pi=np.longdouble('3.141592653589793238462643383279502884')
        self.c0=float(self(0))

    def __call__(self,t):
        t=np.abs(np.asarray(t,dtype=np.longdouble)); x=np.exp(t)
        if np.any(~np.isfinite(x)) or np.any(x>self.limit*(1+1e-15)):
            raise ValueError('out of sieve range')
        n=np.minimum(x.astype(int),self.limit); z=1/x
        G=x*self.w[n]-self.ps[n]-x*t+(1+self.gamma)*x
        # Stable small-z evaluation; series has positive terms.
        a=(1+z)*np.log1p(z); b=np.zeros_like(z); mask=z<1
        b[mask]=(1-z[mask])*np.log1p(-z[mask])
        correction=1-(a-b)/(2*z)
        small=z<0.01
        correction=np.where(small,z*z/6+z**4/20+z**6/42+z**8/72,correction)
        return np.asarray((G-np.log(2*self.pi)+correction)/np.sqrt(x),float)


def run(limit, samples, out):
    if samples<2: raise ValueError('samples must be >=2')
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    C=Requiem(limit); t=np.linspace(0,C.T-1e-9,samples); y=C(t); q=y/C.c0
    rng=np.random.default_rng(42); mins=[]
    for _ in range(100):
        u=np.sort(rng.uniform(0,C.T,12))
        mins.append(float(np.linalg.eigvalsh(C(u[:,None]-u[None,:])/C.c0)[0]))
    for i in range(-500,501):
        v=Fraction(i,137); g=Fraction(7,3); z=encode(v,g)
        assert decode(z)==v/g and decode(tuple(11*a for a in z))==v/g
    # A lossy 8-bit swatch must not replace the exact ratio.
    assert swatch(encode(Fraction(1,10000)))==swatch(encode(0))
    assert decode(encode(Fraction(1,10000)))!=decode(encode(0))
    # Synthetic symmetric growing quartet proxy, not zeta zeros.
    controls=[]
    for d in (0,.01,.05,.15,.25):
        u=np.arange(201)*2*np.pi/14
        v=np.cosh(d*u)*np.cos(14*u)
        # At exact phase returns the cosh envelope is observable.
        measured=float(np.arccosh(max(1.,v[-1]))/u[-1])
        assert abs(measured-d)<1e-8
        controls.append({'delta':d,'recovered':measured,'max_ratio':float(max(abs(v))), 'violations':int(np.count_nonzero(abs(v)>1+1e-10))})
    palette=list(primitive_palette(25)); assert len(palette)==len(set(palette))
    # Atomic CSV replacement protects an existing complete output on interrupt.
    tmp=out/'chromatic.csv.tmp'
    with tmp.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['t','kernel','R','B','G','normalized','hex_preview'])
        for a,b in zip(t,y):
            ratio=encode(float(b),C.c0)
            w.writerow([a,b,*map(str,ratio),float(decode(ratio)),swatch(ratio)])
    tmp.replace(out/'chromatic.csv')
    summary={'limit':limit,'primes':int(C.p.sum()),'samples':samples,'max_t':float(t[-1]),'C0':C.c0,'max_abs_ratio':float(max(abs(q))), 'sample_violations':int(np.count_nonzero(abs(q)>1+1e-10)),'PSD_passes':sum(v>=-1e-10 for v in mins),'min_normalized_eigenvalue':min(mins),'exact_ratio_checks':1001,'primitive_palette_count':len(palette),'synthetic_controls':controls}
    tmp=out/'results.json.tmp'; tmp.write_text(json.dumps(summary,indent=2)); tmp.replace(out/'results.json')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--limit',type=int,default=1_000_000); p.add_argument('--samples',type=int,default=20001); p.add_argument('--out',default='output'); a=p.parse_args()
    run(a.limit,a.samples,a.out)
