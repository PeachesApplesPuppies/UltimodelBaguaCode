# Ouroboros — finite scaling at infinity
BCE / Ultimodel / BaguaCode — 2026-11-27

**Status:** elementary established mathematical identities, targeted computational regression, and negative controls. No new RH proof, physical law, or novelty claim.

## 1. Invariant and complementary information

In the extended real numbers, for every finite real k>0, (+infinity)/k=+infinity and (-infinity)/k=-infinity. More precisely, if f(x) tends to +infinity, so does f(x)/k. The asymptotic ratio (f/k)/f=1/k wherever f is finite and nonzero. Infinity/infinity itself is undefined; its limiting ratios need not agree. Thus unboundedness survives while scale information can be lost.

A division by two does not establish recurrence, equality of finite values, or equal contributions from positive and negative domains. For example, f(x)=exp(x) has integral on [0,L] equal to exp(L)-1, while on [-L,L] it is exp(L)-exp(-L); their ratio tends to 1, not 1/2. Equal halves follow for a reflection-even integrand with well-defined nonzero symmetric-cutoff ratio. Iteration x -> x/2 has no nonzero finite periodic point; it tends to zero, not to its starting value. The limits x->infinity and n->infinity in x/2^n do not commute.

## 2. Cross-audit of prior research

- [Herzog's Convergence–Identity Principle](../docs/herzog-convergence-identity-principle.md): same limiting representation does not imply same identity. For A=x, B=2x, both diverge, but P=(A-B)/(A+B)=-1/3. For finite positive A,B, P is invariant under common positive dilation; retaining M=A+B reconstructs A=M(1+P)/2, B=M(1-P)/2. At the infinite limit, M alone no longer distinguishes scale.
- [Triskelion](../YanRiemann_Triskelion_Synthesis_v1.0.md): cyclic product (A/B)(B/C)(C/A)=1 for nonzero finite inputs, regardless of convergence. Product unity is not recurrence or a bound on individual factors.
- [BaguaCode](../README.md): XOR transition reversibility and Hamming symmetry remain separate discrete invariants; there is no natural infinity operation on the three-bit state space.
- [Golden Bang](golden_bang.md), [unified dilation audit](unified_v22/README.md), and [spectral observability](chatgiblet/phase3-plus-ultra-2026-11-23.md): constant rescaling preserves growth classes and cannot turn a divergent nonnegative integral into a convergent one. For f(x)=x^p, f(qx)/f(x)=q^p; the exponent p is retained, not forced to 1/2. A finite positive multiplier does not change a limsup nth-root growth rate. The required unconditional arithmetic energy estimates remain missing.
- [Necessary Unity / Ghost](yanriemann-necessary-unity-2026-11-26.md), [Three Infinities](three_infinities_experiment.py), [Snake Chase](reciprocal_snake_chase.py), and [light-speed xi confinement](2026-11-27_light_speed_xi_confinement.md): for s=a+it and U(s)=1-1/s,
  |U(s)|^2-1=(1-2a)/(a^2+t^2).
  For every fixed real a, |U(a+it)| tends to 1 as |t| tends to infinity, whether a=1/2 or not. For a!=1/2 the ratio of deviations at 2t and t is (a^2+t^2)/(a^2+4t^2), tending to 1/4. The exact weighted deviation (a^2+t^2)(|U|^2-1)=1-2a preserves the off-axis signal. Even t^2 times the deviation tends to 1-2a. Thus mere asymptotic unity cannot prove RH. A synthetic a=0.8 is a counterexample to that inference, not a zeta zero. The half-line symmetry of xi in a centered coordinate is independent of the infinity scaling identity. Invertible reparametrization does not exclude zeros or establish the missing uniform bound.
- Ghost reconstruction needs an additive integration constant; scale invariance cannot replace that information. Reciprocal and polygon winding tests still require domain and contour certification.

## 3. Executed reproducible regression

Python 3 standard library, exact fractions for finite arithmetic. Extended infinity checks use Python's IEEE floating infinity representation. This is a new targeted audit, not a rerun of every archived program or every prior chat; the archive itself notes some original stage source is absent. Counts are test assertions, not independent proofs.

~~~python
from fractions import Fraction as F
from itertools import product
from math import inf
from collections import Counter
c=Counter()
def check(name,expr):
    assert expr,name
    c[name]+=1
for k in [F(1,3),F(1,2),F(1),F(2),F(3),F(100)]:
    check('extended infinity',inf/float(k)==inf and -inf/float(k)==-inf)
    for n in [1,2,10,100,10**6,10**30]:
        x=F(n)
        check('finite ratio',(x/k)/x==1/k)
        for p in [1,2,3]:
            check('power scaling',(k*x)**p/x**p==k**p)
for a,b in product(range(1,21),repeat=2):
    A,B=F(a),F(b); P=(A-B)/(A+B); M=A+B
    check('polarity and recovery',((A/2-B/2)/(A/2+B/2)==P
          and M*(1+P)/2==A and M*(1-P)/2==B))
for a,b,d in product(range(1,11),repeat=3):
    A,B,C=map(F,(a,b,d))
    check('cyclic ratio',(A/B)*(B/C)*(C/A)==1)
for a,b in product(range(8),repeat=2):
    check('token XOR',(a^b)^b==a and (a^b).bit_count()==(b^a).bit_count())
for q in [F(1,2),F(2),F(3)]:
    for p in [1,2,3]:
        for n in [1,2,5,10]:
            check('dilation exponent',(q*F(n))**p/F(n)**p==q**p)
for a in [F(1,5),F(1,2),F(4,5)]:
    for t in [1,10,100,1000,10**6]:
        r=lambda b: ((1-a)**2+b*b)/(a*a+b*b)
        gap=r(t)-1
        check('Unity detects off-axis',(gap==0)==(a==F(1,2)))
        if gap:
            check('Unity gap scaling',(r(2*t)-1)/gap==(a*a+t*t)/(a*a+4*t*t))
for n in [1,2,10,100,1000]:
    check('half not recurrence',F(1,2)**n!=1)
    check('same infinite limit different finite ratio',F(2*n,n)==2)
print(dict(c)); print('total',sum(c.values()))
~~~

Observed: extended infinity 6; finite ratio 36; power scaling 108; polarity and recovery 400; cyclic ratio 1000; token XOR 64; dilation exponent 36; Unity detects off-axis 15; Unity gap scaling 10; half not recurrence 5; same infinite limit different finite ratio 5. Total 1685, all passed.

## Conclusion

Preserve the scale or weighted deviation rather than only the limiting representation. Unbounded extent is invariant under finite positive scaling; the critical-line condition is not a consequence. The next mathematical obligation remains an independent estimate that forces the actual off-axis signal to vanish, rather than merely shrink at large height.

Every description is a model, not the thing itself.
