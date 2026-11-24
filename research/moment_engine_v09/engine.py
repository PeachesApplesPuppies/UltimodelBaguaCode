"""Exact Hermite moment criterion; exploratory zeta contour moments."""
import json, os, tempfile
from pathlib import Path
import sympy as S
import mpmath as mp

def moments(poly):
    p=S.Poly(poly).monic(); n=p.degree(); a=p.all_coeffs(); m=[S.Integer(n)]
    for k in range(1,2*n-1):
        m.append(-sum(a[j]*m[k-j] for j in range(1,min(k-1,n)+1))-(k*a[k] if k<=n else 0))
    return m

def classify(m):
    n=int(m[0]); H=S.Matrix(n,n,lambda i,j:m[i+j]); A=H.copy(); piv=[]
    while A.rows:
        if any(A[i,i]<0 for i in range(A.rows)): return 'nonreal',H.rank(),piv
        i=next((i for i in range(A.rows) if A[i,i]>0),None)
        if i is None: return ('all_real' if A.is_zero_matrix else 'nonreal'),H.rank(),piv
        A.row_swap(0,i); A.col_swap(0,i); d=A[0,0]; piv.append(str(d)); b=A[1:,0]; A=A[1:,1:]-b*b.T/d
    return 'all_real',H.rank(),piv

def save(data):
    fd,p=tempfile.mkstemp(dir='.',prefix='.checkpoint-');
    try:
        with os.fdopen(fd,'w') as f: json.dump(data,f,indent=2); f.flush();os.fsync(f.fileno())
        os.replace(p,'results.json')
    finally:
        if os.path.exists(p):os.unlink(p)

def main():
    x=S.symbols('x'); q=S.Rational; state={}; cases=[]
    for name,p,want in [('off_line_pair',(x-2)**2+q(1,16),'nonreal'),('repeated_on_line',(x-2)**2,'all_real'),('two_simple',(x-1)*(x-2),'all_real'),('mixed',(x-1)*(x*x+1),'nonreal'),('higher_multiplicity',(x-1)**4*(x+2)**2,'all_real')]:
        m=moments(p); got,rank,piv=classify(m); assert got==want; cases.append(dict(name=name,result=got,rank=rank,moments=list(map(str,m)),pivots=piv))
    for t in [q(0),q(1,5),q(1,4),q(2,5)]:
        got,rank,piv=classify(moments(x**4-12*t*x*x+1+12*t*t)); assert (got=='all_real')==(24*t*t>=1);cases.append(dict(name='heat '+str(t),result=got,rank=rank))
    for k in range(1,41):
        a=q(k,7); e=q(1,10**k); p=(x-a)**2*(x+1)*(x-3)
        for sign in [-1,0,1]:
            f=p*((x-a)**2+sign*e**2); got,_,_=classify(moments(f)); assert (got=='all_real')==(sign<=0)
    state['exact_cases']=cases; state['family_tests']=120
    old=json.loads(Path('v08_reference.json').read_text()); assert old['zeta']['summary']['confined_singleton']==5
    state['previous_zeta_result']=old['zeta']['summary'];state['previous_zeta_note']='Read archived result; not a rerun or independent certification.';save(state)
    print('129 exact tests passed; archived v0.8 classification checked',flush=True)
    # Numerical contour quadrature in centered coordinates w=-i(s-1/2).
    # No known zero locations used. Composite midpoint; NOT validated.
    mp.mp.dps=25
    corners=[mp.mpc(0,20),mp.mpc(1,20),mp.mpc(1,26),mp.mpc(0,26),mp.mpc(0,20)]
    rows=[]
    for n in (24,48,96):
        m=[mp.mpc(0) for _ in range(3)]
        for a,b in zip(corners,corners[1:]):
            h=(b-a)/n
            for j in range(n):
                s=a+(j+mp.mpf('.5'))*h; w=-1j*(s-mp.mpf('.5')); v=mp.zeta(s,derivative=1)/mp.zeta(s)*h/(2j*mp.pi)
                for k in range(3):m[k]+=w**k*v
        d=2*m[2]-m[1]**2
        rows.append(dict(samples_per_edge=n,moments=[str(z) for z in m],centered_discriminant=str(d)));state['exploratory_zeta']=rows;save(state);print(n,mp.nstr(m[0],10),mp.nstr(d,10),flush=True)
if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:raise SystemExit(130)
