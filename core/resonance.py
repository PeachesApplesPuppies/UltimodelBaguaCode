"""Deterministic comparisons of manually supplied evidence."""
from collections import Counter
from fractions import Fraction
import math
import re
from typing import TypedDict
from .tokens import State, transition, hamming_distance, change_ratio, flow

GEOMETRY = ("line","angle","triangle","rectangle","square","circle","spiral","polygon",
            "ratio between lengths","ratio between areas","symmetry","rotation","reflection")
STATUSES = ("Unexamined","Surface Similarity","Structurally Similar","Normalized Match",
            "Partial Match","Broken Rhyme","Validated Under Current Model")
PHI = (1+math.sqrt(5))/2


class RhymeCandidate(TypedDict, total=False):
    object_A: str
    object_B: str
    lens_A: str
    lens_B: str
    normalized_A: dict | None
    normalized_B: dict | None
    candidate_invariant: str
    similarity_score: dict
    status: str


def ratio(raw, lens):
    if not raw.strip():
        return None
    parts = re.split(r"[:×]",raw)
    if len(parts)!=2 or any(len(s)>40 or not re.fullmatch(r"\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)\s*",s) for s in parts):
        raise ValueError("Use two decimal measurements separated by : or ×.")
    a,b = map(Fraction,parts)
    if lens=="Reverse":
        a,b=b,a
    return dict(raw_ratio=raw,lens=lens,oriented_terms=[str(a),str(b)],
                normalized_ratio=f"1:{b/a}" if a else None,
                normalization_operation="divide both oriented terms by first" if a else "undefined: zero first term",
                quotient=float(a/b) if b else None)


def sequence(raw):
    values=[s.strip() for s in re.split(r"[,\n]",raw) if s.strip()]
    if len(values)>256:
        raise ValueError("Use at most 256 sequence entries.")
    if not values:
        return None
    motifs={}
    for width in (2,3):
        for motif,n in Counter(tuple(values[i:i+width]) for i in range(len(values)-width+1)).items():
            if n>1:
                motifs[str(motif)]=n
    period=next((p for p in range(1,len(values)//2+1)
                 if all(a==b for a,b in zip(values,values[p:]))),None)
    return dict(sequence=values,frequency=dict(Counter(values)),repeated_motifs=motifs,
                observed_period=period,inversion=list(reversed(values)),mirror_symmetry=values==values[::-1])


def analyze(form, observation, reference) -> RhymeCandidate:
    candidates=[]
    for side in "AB":
        get=lambda field: form.get(field+"_"+side,"")
        lens=get("lens") or "Forward"
        if lens not in ("Forward","Reverse"):
            raise ValueError("Unknown orientation.")
        geometry=get("geometry")
        if geometry and geometry not in GEOMETRY:
            raise ValueError("Unknown geometry.")
        token=get("token")
        confidence=get("token_confidence")
        if token:
            State.parse(token)
            if not get("token_lens").strip() or not confidence or not 0<=float(confidence)<=1:
                raise ValueError("Each token needs its Lens’ and a confidence from 0 to 1.")
        candidates.append(dict(ratio=ratio(get("ratio"),lens),sequence=sequence(get("sequence")),
                               token=token,token_lens=get("token_lens"),token_confidence=confidence,
                               geometry=geometry,topology=get("topology"),operator=get("operator"),lens=lens))
    a,b=candidates
    ra,rb=a["ratio"],b["ratio"]
    tests={}
    if ra and rb:
        tests["normalized_pair"]=(ra["normalized_ratio"]==rb["normalized_ratio"]
                                  if None not in (ra["normalized_ratio"],rb["normalized_ratio"]) else None)
    tolerance=form.get("tolerance","")
    tol=float(tolerance) if tolerance!="" else None
    if tol is not None and not (math.isfinite(tol) and 0<=tol<=100):
        raise ValueError("Relative tolerance must be 0–100 percent.")
    for side,obj in zip("AB",candidates):
        r=obj["ratio"]
        if r and r["quotient"] is not None:
            err=abs(r["quotient"]-PHI)
            obj["phi_test"]=dict(measured_ratio=r["quotient"],phi=PHI,absolute_error=err,
                                 relative_error=err/PHI,percent_error=100*err/PHI,tolerance_percent=tol)
            if form.get("hypothesis")=="Phi" and side=="A":
                tests["A_within_phi_tolerance"]=None if tol is None else 100*err/PHI<=tol
    scores={k:None for k in ("ratio","topological","operator","sequence","token","semantic")}
    if tests.get("normalized_pair") is not None:
        scores["ratio"]=int(tests["normalized_pair"])
    for key,field in (("topological","topology"),("operator","operator")):
        if a[field] and b[field]:
            scores[key]=int(a[field].strip().casefold()==b[field].strip().casefold())
    if a["sequence"] and b["sequence"]:
        x,y=(v["sequence"]["sequence"] for v in candidates)
        scores["sequence"]=sum(i==j for i,j in zip(x,y))/max(len(x),len(y))
    token_comparison=None
    if a["token"] and b["token"]:
        x,y=map(State.parse,(a["token"],b["token"]))
        d=hamming_distance(x,y).value
        token_comparison=dict(xor=str(transition(x,y)),distance=d,change_ratio=str(change_ratio(x,y)),
                              flow=flow(x,y,form["elapsed"]).value if form.get("elapsed") else None,
                              same_lens=a["token_lens"]==b["token_lens"])
        if token_comparison["same_lens"]:
            scores["token"]=1-d/3
    focus=form.get("hypothesis","Pair")
    decisive=tests.get("A_within_phi_tolerance" if focus=="Phi" else "normalized_pair")
    suggested="Unexamined" if decisive is None else ("Normalized Match" if decisive else "Broken Rhyme")
    if focus=="Phi" and decisive:
        suggested="Structurally Similar"
    return dict(object_A=observation,object_B=reference,lens_A=a["lens"],lens_B=b["lens"],
                normalized_A=ra,normalized_B=rb,A=a,B=b,tests=tests,token_comparison=token_comparison,
                preserved_features=form.get("preserved",""),different_features=form.get("different",""),
                unknown_features=form.get("unknown",""),candidate_invariant=form.get("invariant",""),
                comparison_method=focus,similarity_score=scores,suggested_status=suggested,
                status=form.get("status") or suggested)


def stress(form):
    def pair(first,second):
        vals=[ratio(form.get("ratio_"+side,""),lens) for side,lens in zip("AB",(first,second))]
        if any(not v or v["normalized_ratio"] is None for v in vals):
            return None
        return vals[0]["normalized_ratio"]==vals[1]["normalized_ratio"]
    la,lb=(form.get("lens_"+s) or "Forward" for s in "AB")
    flip={"Forward":"Reverse","Reverse":"Forward"}
    a=ratio(form.get("ratio_A",""),la)
    b=ratio(form.get("ratio_B",""),lb)
    scale=baseline=None
    if a and a["normalized_ratio"] is not None:
        u,v=map(Fraction,a["oriented_terms"])
        baseline=dict(matches=sum(Fraction(y,x)==v/u for x in range(1,11) for y in range(1,11)),
                      possible=100,model="uniform ordered integer pairs 1..10; exact aspect match to A")
        if b and b["normalized_ratio"] is not None:
            w,z=map(Fraction,b["oriented_terms"])
            scale=(2*v)/(2*u)==(3*z)/(3*w)
    return dict(scope="pair aspect ratios",current=pair(la,lb),both_inverted=pair(flip[la],flip[lb]),
                only_B_inverted=pair(la,flip[lb]),independently_scaled=scale,baseline=baseline)
