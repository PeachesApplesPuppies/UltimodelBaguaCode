"""Real scalar expression trees. Python's AST parses input; nothing is eval'd."""
import ast
import math
import operator
from contextvars import ContextVar

# Per-request work budget for numerical quadrature.
quadrature_samples=ContextVar("quadrature_samples",default=None)
import re
from dataclasses import dataclass

class Boundary(ValueError):
    pass

@dataclass(frozen=True)
class Expr:
    op: str
    args: tuple

def node(op, *args):
    return Expr(op, args)

def num(v):
    return node("num", v)

def var(name):
    return node("var", name)

FUNCS = {"sin", "cos", "tan", "exp", "log", "sqrt", "abs", "inv", "ratio", "delta",
         "on", "signnz", "ln", "atan", "asin", "acos", "sinh", "cosh", "tanh", "log10"}
BINARY = {ast.Add:"+", ast.Sub:"-", ast.Mult:"*", ast.Div:"/", ast.Pow:"**"}
def parse(text, bindings=None):
    if not isinstance(text,str) or not 0 < len(text.strip()) <= 400:
        raise ValueError("Use 1 to 400 characters per expression.")
    text=text.strip().replace("−","-").replace("×","*").replace("÷","/").replace("π","pi")
    scope=dict(bindings or {})
    signature=re.fullmatch(r"[A-Za-z]\w*\(\s*([A-Za-z]\w*)\s*\)\s*=\s*(.+)",text)
    if signature:
        axis,text=signature.groups()
        if axis in FUNCS|{"pi","e"}:raise ValueError("Choose a variable name for the function argument.")
        scope[axis]=var("t")
    # Python's tokenizer distinguishes 2x from k2x and recognizes 1e-3.
    import tokenize, io
    try:
        toks=list(tokenize.generate_tokens(io.StringIO(text).readline))
        pieces=[]
        for i,tok in enumerate(toks):
            if i and ((toks[i-1].type==tokenize.NUMBER and
                       (tok.type==tokenize.NAME or tok.string=="(")) or
                      (toks[i-1].string==")" and tok.string=="(")):
                pieces.append((tokenize.OP,"*"))
            pieces.append((tok.type,tok.string))
        text=tokenize.untokenize(pieces)
    except (tokenize.TokenError,IndentationError) as exc:
        raise ValueError("Incomplete expression or unmatched parentheses.") from exc
    try:
        tree = ast.parse(text.strip().replace("^","**").replace("−","-").replace("×","*"), mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("Invalid expression syntax.") from exc
    if len(list(ast.walk(tree))) > 130:
        raise ValueError("Expression is too large.")
    def read(n):
        if isinstance(n,ast.Constant) and type(n.value) in (int,float) and abs(n.value)<=1e100:
            return num(n.value)
        if isinstance(n,ast.Name) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}",n.id):
            if n.id in ("pi","e"):
                return num(math.pi if n.id=="pi" else math.e)
            if n.id in FUNCS: raise ValueError("Function requires parentheses.")
            return scope.get(n.id,var(n.id))
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.UAdd,ast.USub)):
            a=read(n.operand)
            return a if isinstance(n.op,ast.UAdd) else node("neg",a)
        if isinstance(n,ast.BinOp) and type(n.op) in BINARY:
            return node(BINARY[type(n.op)],read(n.left),read(n.right))
        if (isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="element"
                and len(n.args)==2 and not n.keywords and all(isinstance(arg,ast.Name) for arg in n.args)):
            from .elements import element_value
            return num(element_value(n.args[0].id,n.args[1].id))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in scope and len(n.args)==1 and not n.keywords:
            return node("at",scope[n.func.id],read(n.args[0]))
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in FUNCS and not n.keywords:
            f=n.func.id
            k=2 if f in ("delta","ratio","on") else 1
            if len(n.args)!=k: raise ValueError(f"{f} requires {k} argument(s).")
            a=[read(x) for x in n.args]
            if f=="ln":return node("log",a[0])
            if f=="log10":return node("/",node("log",a[0]),num(math.log(10)))
            if f=="delta": return node("-",a[1],a[0])
            if f=="ratio": return node("/",*a)
            if f=="inv": return node("/",num(1),a[0])
            return node(f,*a)
        raise ValueError("Use numbers, names, arithmetic and the listed functions only.")
    return read(tree.body)

def show(x):
    op,a=x.op,x.args
    if op in ("num","var"): return str(a[0])
    if op=="integral":return "∫["+show(a[1])+", t] "+show(a[0])+" dt"
    if op=="at":return "("+show(a[0])+") at t="+show(a[1])
    if op=="neg":return "(-"+show(a[0])+")"
    if op in BINARY.values():return "("+show(a[0])+" "+op+" "+show(a[1])+")"
    return op+"("+", ".join(map(show,a))+")"

def names(x):
    if x.op=="integral":return {"t"} | names(x.args[0])
    if x.op=="at":return (names(x.args[0])-{"t"}) | names(x.args[1])
    if x.op=="var":return {x.args[0]}
    return set().union(*(names(v) for v in x.args if isinstance(v,Expr)))

def safe_pow(a,b):
    if a==0 and b<=0: raise Boundary("zero base with nonpositive exponent")
    if a<0 and not float(b).is_integer(): raise Boundary("nonreal power")
    return math.pow(a,b)

def scalar(x,env):
    op,a=x.op,x.args
    if op=="num":return float(a[0])
    if op=="var":return env[a[0]]
    if op=="at":return scalar(a[0],{**env,"t":scalar(a[1],env)})
    if op=="integral":
        from .calculus import integrate
        return integrate(a[0],a[1].args[0],env["t"],env)
    vals=[scalar(v,env) for v in a]
    f={"+":operator.add,"-":operator.sub,"*":operator.mul,"/":operator.truediv,"**":safe_pow,
       "neg":operator.neg,"sin":math.sin,"cos":math.cos,"exp":math.exp,"log":math.log,
       "sqrt":math.sqrt,"abs":abs,"on":lambda value,domain:value}
    try:
        if op=="signnz":
            if vals[0]==0:raise Boundary("absolute-value derivative at zero requires a separate check")
            z=math.copysign(1,vals[0])
        elif op=="tan":
            if abs(math.cos(vals[0]))<1e-14:raise Boundary("tangent pole")
            z=math.tan(vals[0])
        elif op in ("atan","asin","acos","sinh","cosh","tanh"):z=getattr(math,op)(*vals)
        else:z=f[op](*vals)
        if not math.isfinite(z):raise Boundary("numeric range exceeded")
        return z
    except (ArithmeticError,ValueError) as exc:
        raise Boundary(str(exc)) from exc

def simp(op,*a):
    # Only simplify the display/derivative. Flow retains the original domain separately.
    if op=="-" and a[0]==a[1]:return num(0)
    if op in ("+","-") and a[1]==num(0):return a[0]
    if op=="+" and a[0]==num(0):return a[1]
    if op=="*" and num(0) in a:return num(0)
    if op=="*" and num(1) in a:return a[1] if a[0]==num(1) else a[0]
    q=node(op,*a)
    if all(v.op=="num" for v in a):
        try:
            z=scalar(q,{})
            return num(int(z) if abs(z)<1e12 and z.is_integer() else z)
        except Boundary:pass
    return q

def diff(x):
    op,a=x.op,x.args
    if "t" not in names(x):return num(0)
    if op=="var":return num(1)
    if op=="integral":return a[0]
    if op=="at":return simp("*",node("at",diff(a[0]),a[1]),diff(a[1]))
    u=a[0]; du=diff(u); m=lambda p,q:simp("*",p,q)
    if op=="on":return node("on",du,a[1])
    if op in ("+","-"):return simp(op,du,diff(a[1]))
    if op=="neg":return simp("neg",du)
    if op in ("*","/","**"):
        v=a[1];dv=diff(v)
        if op=="*":return simp("+",m(du,v),m(u,dv))
        if op=="/":return simp("/",simp("-",m(du,v),m(u,dv)),simp("**",v,num(2)))
        if dv==num(0):
            if v==num(1):return du
            return m(m(v,simp("**",u,simp("-",v,num(1)))),du)
        return m(x,simp("+",m(dv,node("log",u)),simp("/",m(v,du),u)))
    if op=="signnz":return node("on",num(0),x)
    factor={"sin":lambda:node("cos",u),"cos":lambda:simp("neg",node("sin",u)),
            "tan":lambda:simp("/",num(1),simp("**",node("cos",u),num(2))),
            "exp":lambda:x,"log":lambda:simp("/",num(1),u),
            "sqrt":lambda:simp("/",num(1),m(num(2),x)),"abs":lambda:node("signnz",u)}
    square=simp("**",u,num(2))
    factor.update({"sinh":lambda:node("cosh",u),"cosh":lambda:node("sinh",u),
                   "tanh":lambda:node("-",num(1),node("**",x,num(2))),
                   "atan":lambda:node("/",num(1),node("+",num(1),square)),
                   "asin":lambda:node("/",num(1),node("sqrt",node("-",num(1),square))),
                   "acos":lambda:node("/",num(-1),node("sqrt",node("-",num(1),square)))})
    return m(factor[op](),du)

def interval(x,lo,hi,env):
    """Conservative enclosure: only draw a segment if its whole t interval passes."""
    op,a=x.op,x.args
    if op=="num":return (float(a[0]),)*2
    if op=="var":return (lo,hi) if a[0]=="t" else (env[a[0]],)*2
    if op=="at":
        l,h=interval(a[1],lo,hi,env)
        return interval(a[0],l,h,env)
    if op=="integral":
        from .calculus import enclosure
        start=a[1].args[0]
        l,h=enclosure(a[0],min(lo,start),max(hi,start),env)
        # Bound all signed integrals from the anchor through this window.
        bound=max(abs(lo-start),abs(hi-start))*max(abs(l),abs(h))
        return -bound,bound
    b=[interval(q,lo,hi,env) for q in a];l,h=b[0]
    if op=="on":return b[0]
    if op in ("+","-","*","/","**"):
        c,d=b[1]
        if op=="+":return l+c,h+d
        if op=="-":return l-d,h-c
        if op=="/":
            if c<=0<=d:raise Boundary("possible zero denominator")
            c,d=1/d,1/c
        if op in ("*","/"):
            vs=[l*c,l*d,h*c,h*d];return min(vs),max(vs)
        if c==d:
            vs=[safe_pow(l,c),safe_pow(h,c)]
            if l<=0<=h:vs.append(safe_pow(0,c))
        else:
            if l<=0:raise Boundary("unverified power domain")
            vs=[safe_pow(i,j) for i in (l,h) for j in (c,d)]
        return min(vs),max(vs)
    if op=="neg":return -h,-l
    if op=="abs":return (0 if l<=0<=h else min(abs(l),abs(h))),max(abs(l),abs(h))
    if op=="signnz":
        if l<=0<=h:raise Boundary("derivative branch")
        return (math.copysign(1,l),)*2
    if op in ("sin","cos"):
        shift=math.pi/2 if op=="sin" else 0
        f=getattr(math,op);vs=[f(l),f(h)]
        for k in (0,1):
            a0=shift+k*math.pi
            if math.ceil((l-a0)/(2*math.pi))<=math.floor((h-a0)/(2*math.pi)):vs.append((-1)**k)
        return min(vs),max(vs)
    if op=="tan":
        if math.ceil((l-math.pi/2)/math.pi)<=math.floor((h-math.pi/2)/math.pi):raise Boundary("tangent pole")
    f=getattr(math,op)
    values=[f(l),f(h)]
    if op=="cosh" and l<=0<=h:values.append(1.)
    return min(values),max(values)

