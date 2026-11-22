"""Anchored real integrals. Use quadrature only on intervals with a checked domain."""
import math
from .mathcore import quadrature_samples, Boundary, interval, scalar, names, num, node, simp, var

def primitive(x):
    """Return one elementary primitive where this rule table applies."""
    t = var("t")
    if "t" not in names(x):
        return simp("*", x, t)
    op, args = x.op, x.args
    if x == t:
        return node("/", node("**", t, num(2)), num(2))
    if op == "neg":
        a = primitive(args[0])
        return None if a is None else node("neg", a)
    if op in ("+", "-"):
        a, b = map(primitive, args)
        return None if a is None or b is None else node(op, a, b)
    if op == "*":
        for a, b in (args, args[::-1]):
            if "t" not in names(a):
                q = primitive(b)
                return None if q is None else simp("*", a, q)
    if op == "**" and args[0] == t and args[1].op == "num":
        n = args[1].args[0] + 1
        if n == 0:
            return node("log", node("abs", t))
        return node("/", node("**", t, num(n)), num(n))
    if op == "/" and args[1] == t and "t" not in names(args[0]):
        return simp("*", args[0], node("log", node("abs", t)))
    if args == (t,):
        return {"sin":node("neg",node("cos",t)), "cos":node("sin",t),
                "exp":node("exp",t)}.get(op)
    return None

def enclosure(f, start, end, env):
    lo,hi=sorted((start,end))
    try:
        low,high=interval(f,lo,hi,env)
        if not all(map(math.isfinite,(low,high))):
            raise Boundary("nonfinite bounds")
        return low,high
    except (ArithmeticError,ValueError) as exc:
        raise Boundary("Integral domain unverified across this interval: "+str(exc)) from exc

def integrate(f, start, end, env):
    enclosure(f,start,end,env)
    if start==end:
        return 0.
    def sample(t):
        remaining=quadrature_samples.get()
        if remaining is not None:
            if remaining<=0:raise ValueError("Integral sampling budget reached; shorten the graph range.")
            quadrature_samples.set(remaining-1)
        return scalar(f,{**env,"t":t})
    def sim(a,b,fa,fm,fb):
        return (b-a)*(fa+4*fm+fb)/6
    def refine(a,b,fa,fm,fb,estimate,tol,depth):
        m=(a+b)/2
        fl,fr=sample((a+m)/2),sample((b+m)/2)
        l,r=sim(a,m,fa,fl,fm),sim(m,b,fm,fr,fb)
        err=l+r-estimate
        if abs(err)<=15*tol:
            return l+r+err/15
        if depth==0:
            raise Boundary("Integral accuracy unresolved; shorten the interval.")
        return refine(a,m,fa,fl,fm,l,tol/2,depth-1)+refine(m,b,fm,fr,fb,r,tol/2,depth-1)
    # Several initial panels reduce single-panel aliasing.
    total=0.
    for i in range(4):
        a=start+(end-start)*i/4
        b=start+(end-start)*(i+1)/4
        fa,fm,fb=sample(a),sample((a+b)/2),sample(b)
        s=sim(a,b,fa,fm,fb)
        total+=refine(a,b,fa,fm,fb,s,1e-8*(1+abs(s))/4,9)
    if not math.isfinite(total):
        raise Boundary("Integral exceeds numeric range")
    return total
