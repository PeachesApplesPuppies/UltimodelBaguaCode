from datetime import datetime,timezone
import colorsys
import math,re
from .mathcore import *

LIMIT=1800
def budget(x):
    left=[x];n=0
    while left:
        v=left.pop();n+=1
        if n>LIMIT:raise ValueError("Expression expansion limit reached (1800 nodes).")
        left.extend(i for i in v.args if isinstance(i,Expr))
    return x

def relation(a,b,lens,polarity=1):
    polarity=number(polarity)
    if not -1 <= polarity <= 1:
        raise ValueError("Polarity must be between −1 and +1.")
    if lens not in ("A","B"):raise ValueError("Lens must be A or B.")
    u,v=(a,b) if lens=="A" else (b,a)
    delta=node("-",v,u)
    flow=node("on",budget(diff(delta)),delta)
    return {"shifted":node("*",num(polarity),delta),"sum":node("+",u,v),"product":node("*",u,v),"A":a,"B":b,"delta":delta,"oppositeDelta":node("-",u,v),"magnitude":node("abs",delta),
            "quotient":node("/",u,v),"inverseQuotient":node("/",v,u),
            "X":node("/",v,u),"inverseX":node("/",u,v),"flow":flow}

CALCULUS={"function","derivative","integral"}

def calculus_result(a,b,lens,p,key,anchor):
    source=a if lens=="A" else b
    if key=="derivative":
        source=node("on",budget(diff(source)),source)
    elif key=="integral":
        pending=[source]
        while pending:
            item=pending.pop()
            if item.op=="integral":
                raise ValueError("Nested numerical integrals exceed this version’s evaluation budget.")
            pending.extend(v for v in item.args if isinstance(v,Expr))
        source=node("integral",source,num(number(anchor)))
    return budget(simp("*",num(p),source) if p!=0 else node("*",num(0),source))

def bindings(records):
    previous={};reserved=set()
    if not isinstance(records,list) or len(records)>24:raise ValueError("Limit: 24 named Variables’.")
    for r in records:
        name=r["name"]
        if (not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}",name) or name in previous or name in reserved or
            name in FUNCS|{"e","pi","t","A","B"}):raise ValueError("Choose an unused, non-reserved variable name.")
        if r["kind"]=="variable":x=parse(r["expression"],previous)
        elif r["kind"]=="promotion":
            a=budget(parse(r["A"],previous));b=budget(parse(r["B"],previous))
            orientation=r["lens"]
            polar=number(r.get("polarity",1))
            pair=relation(a,b,orientation,polar)
            key=r["result"]
            x=(calculus_result(a,b,orientation,polar,key,r.get("anchor",0))
               if key in CALCULUS else pair[key])
        else:raise ValueError("Unknown variable record kind.")
        budget(x)
        if name in names(x):raise ValueError("A variable cannot reference itself.")
        reserved.update(names(x)-{"t"});previous[name]=x
    return previous

def probe(expr,env):
    missing=sorted(names(expr)-env.keys())
    label=show(expr.args[0]) if expr.op=="on" else show(expr)
    if missing:
        # A known invalid subexpression remains invalid even in a symbolic result.
        def check(q):
            if not names(q)-env.keys():
                scalar(q,env)
                return
            for child in q.args:
                if isinstance(child,Expr):check(child)
            if q.op=="/" and not names(q.args[1])-env.keys() and scalar(q.args[1],env)==0:
                raise Boundary("zero denominator")
        try:check(expr)
        except Boundary as e:return dict(expr=label,value=None,status="Undefined / relational boundary",detail=str(e))
        return dict(expr=label,value=None,status="symbolic",detail="Set "+", ".join(missing))
    try:return dict(expr=label,value=scalar(expr,env),status="valid",detail="")
    except Boundary as e:return dict(expr=label,value=None,status="Undefined / relational boundary",detail=str(e))

def number(x):
    v=float(x)
    if not math.isfinite(v) or abs(v)>1e100:raise ValueError("Enter a finite number with magnitude ≤ 1e100.")
    return v

def visual_code(frequency, magnitude, product, polarity=1):
    if None in (frequency, magnitude, product):
        return None
    # Compress wide numeric ranges while keeping the mapping continuous at zero.
    oriented = product * polarity
    signed_product = math.copysign(math.log1p(abs(oriented)), oriented)
    hue = 270 + 85 * (2 / math.pi) * math.atan(signed_product)
    shade = 0.28 + 0.50 * (2 / math.pi) * math.atan(math.log1p(abs(magnitude)))
    rgb = [round(255 * c) for c in colorsys.hls_to_rgb(hue / 360, shade, 0.72 * abs(polarity))]
    channels = [c / 255 for c in rgb]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055)**2.4 for c in channels]
    lum = sum(c * w for c, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    black, white = (lum + 0.05) / 0.05, 1.05 / (lum + 0.05)
    angle = math.degrees(math.atan2(magnitude, frequency)) % 360 if frequency or magnitude else None
    return {"mapping": "FM-2", "display_product": oriented, "polarity": polarity, "hex": "#{:02X}{:02X}{:02X}".format(*rgb),
            "ink": "#000000" if black >= white else "#FFFFFF",
            "contrast_ratio": max(black, white), "angle_degrees": angle}


def color_contrast(request, bank, env):
    factors = {}
    expressions = []
    for key in ("frequency", "magnitude"):
        source = request.get(key, "").strip()
        if source:
            expr = budget(parse(source, bank))
            expressions.append(expr)
            reading = probe(expr, env)
        else:
            reading = {"value": None, "status": "unentered"}
        factors[key] = {"source": source, **reading}
    product = (probe(node("*", *expressions), env) if len(expressions) == 2
               else {"value": None, "status": "awaiting both factors"})
    visual = visual_code(factors["frequency"]["value"], factors["magnitude"]["value"], product["value"], number(request.get("polarity", 1)))
    return {**factors, "product": product, "visual": visual}


def zero_spin(a,b,c,env,lens,reading_only):
    sources={"A":a,"B":b,"C":c}
    points={}
    for name,expr in sources.items():
        value=probe(expr,env)
        v=value["value"]
        sign=(value["status"] if v is None else "neutral" if v==0 else "positive" if v>0 else "negative")
        rate=(dict(value=None,status="undetermined from a reading",detail="")
              if reading_only else probe(node("on",budget(diff(expr)),expr),env))
        points[name]=dict(value=value,sign=sign,rate=rate)
    order="ABCA" if lens=="A" else "BACB"
    steps=[]
    for left,right in zip(order,order[1:]):
        u,v=sources[left],sources[right]
        numerator=points[left]["value"]["value"]
        denominator=points[right]["value"]["value"]
        quotient=probe(node("/",u,v),env)
        reason=quotient["status"]
        if denominator==0 and numerator is not None:
            reason=("Undefined 0/0 · every real q solves 0q=0" if numerator==0 else
                    "Undefined · no real q solves 0q="+str(numerator))
        steps.append(dict(pair=left+" → "+right,delta=probe(node("-",v,u),env),
                          quotient=quotient,reason=reason))
    return dict(points=points,steps=steps,reading_only=reading_only)

def compute(p):
    token=quadrature_samples.set(160000)
    try:
        return _compute(p)
    finally:
        quadrature_samples.reset(token)

def _compute(p):
    env={k:number(v) for k,v in p.get("parameters",{}).items()}
    if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}",k) or k in FUNCS|{"e","pi","t"} for k in env):
        raise ValueError("Invalid parameter name.")
    reg=p.get("variables",[]);bank=bindings(reg)
    if env.keys() & bank.keys():raise ValueError("A parameter and a named Variable’ cannot share a name.")
    a=budget(parse(p["A"],bank));b=budget(parse(p["B"],bank));lens=p.get("lens","A")
    lo,hi,t=map(number,[p.get("lo",-5),p.get("hi",5),p.get("t",0)])
    if not lo<hi:raise ValueError("Range start must be less than end.")
    env["t"]=t
    exprs=relation(a,b,lens,p.get("polarity",1))
    selected=p.get("plots",["A","B","delta","magnitude","X","inverseX","flow"])
    anchor=number(p.get("anchor",0))
    rule=p.get("rule","shifted")
    for key in CALCULUS & (set(selected)|{rule}):
        exprs[key]=calculus_result(a,b,lens,number(p.get("polarity",1)),key,anchor)
    rows={k:probe(v,env) for k,v in exprs.items()}
    primitive_text=None
    if "integral" in exprs:
        from .calculus import primitive
        prim=primitive(a if lens=="A" else b)
        if prim is not None:
            primitive_text=show(simp("*",num(number(p.get("polarity",1))),prim))+" + C"
    comparison="symbolic"
    va,vb=rows["A"]["value"],rows["B"]["value"]
    if va is not None and vb is not None:comparison="A = B" if va==vb else "A < B" if va<vb else "A > B"
    elif any(rows[k]["status"].startswith("Undefined") for k in ("A","B")):comparison="undefined"
    selected=p.get("plots",["A","B","delta","magnitude","X","inverseX","flow"])
    plots={};gaps={};n=241
    for k in dict.fromkeys(selected):
        x=exprs[k];segments=[];seg=[];gap=0;prev=None
        if not names(x)-env.keys():
            for j in range(n):
                at=lo+(hi-lo)*j/(n-1)
                try:val=scalar(x,{**env,"t":at})
                except (ArithmeticError,ValueError):val=None
                join=False
                if val is not None and seg:
                    try:
                        bounds=interval(x,prev,at,env)
                        join=all(math.isfinite(z) for z in bounds)
                    except (ArithmeticError,ValueError):pass
                if seg and not join:segments.append(seg);seg=[];gap+=1
                if val is not None:seg.append([at,val])
                prev=at
            if seg:segments.append(seg)
        plots[k]=segments;gaps[k]=gap
    table=None
    if p.get("sample_step") is not None:
        h=number(p["sample_step"])
        if h<=0:raise ValueError("Sample step must be positive.")
        source=a if lens=="A" else b
        values=[probe(source,{**env,"t":t+i*h})["value"] for i in range(3)]
        def subtract(new,old):
            return None if new is None or old is None else new-old
        left,right=(subtract(values[i+1],values[i]) for i in (0,1))
        table=dict(step=h,values=values,first=[left,right],second=subtract(right,left),
                   return_gap=subtract(values[2],values[0]))
    spin=None
    if "spin_C" in p and p["spin_C"] is not None:
        spin=zero_spin(a,b,budget(parse(p["spin_C"],bank)),env,lens,p.get("reading_only",False))
        spin["C"]=p["spin_C"]
    return {"color_contrast":color_contrast(p, bank, env),"zero_spin":spin,"timestamp":datetime.now(timezone.utc).isoformat(),"A":p["A"],"B":p["B"],"lens":lens,"probe_t":t,"polarity":number(p.get("polarity",1)),
            "difference_table":table,"anchor":anchor,"rule":rule,"antiderivative":primitive_text,"range":[lo,hi],"parameters":p.get("parameters",{}),"quantities":rows,"comparison":comparison,
            "variables":reg,"singularities_or_errors":{k:v["detail"] for k,v in rows.items() if v["status"].startswith("Undefined")},
            "graph_breaks":gaps,"plots":plots}

