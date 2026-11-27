# Light-speed coordinate and xi-function confinement
BCE / Ultimodel research note — 2026-11-27

**Status: exploratory reformulation and numerical evidence, not a proof of RH.**

## Physical inspiration
For a photon in vacuum, rest mass is zero, E=hf, p=hf/c, and E/c² is an energy-equivalent mass, not invariant mass. A longitudinal change of momentum in a specified frame satisfies dp/dt=(h/c) df/dt. Freely propagating photons in flat vacuum have constant frequency in an inertial frame. The speed c is constant locally. A physical law linking photon frequency to zeta zeros has not been established.

## Coordinate model
Let beta=v/c in (0,1), x=log(beta/(1-beta)), beta=1/(1+exp(-x)). This is a bijection from (0,1) onto the real line. Reflection beta -> 1-beta corresponds to x -> -x. Let t>=0 and optionally u=t/(1+t) in [0,1). Negative t is covered by conjugation. The velocity identification is an analogy, not a derivation from relativity, and t is a mathematical zero-height coordinate, not necessarily physical time.

Define xi(s)=s(s-1) pi^(-s/2) Gamma(s/2) zeta(s)/2 and G(x,t)=xi(beta+it). Its functional equation and conjugation give |G(-x,t)|=|G(x,t)|.

A reflection-invariant disk containing exactly one zero counted with multiplicity must have its zero on the critical line: otherwise rho and 1-conj(rho) are distinct zeros in that disk. This is a conditional local argument; covering all zeros by such disks has not been established.

## Exact derivative and proof target
At nonzero G,
Q(x,t)=d/dx log |G(x,t)|² = 2 beta(1-beta) Re(xi'(s)/xi(s)).
Since beta(1-beta)>0, positivity of Q is equivalent to positivity of the real logarithmic derivative. A sufficient global condition is d/dx |G(x,t)|²>0 for every x>0 and t>=0, which rules out a zero there because a differentiable nonnegative function at an interior zero has derivative zero. Reflection excludes x<0. For the log-derivative criterion one must either prove zero-freeness or prove positivity on the punctured domain and exclude poles: near any hypothetical off-line zero of order m, xi'/xi=m/(s-rho)+O(1), which has negative real part immediately to its left at the same height. This contradicts positivity.

Horizontal monotonicity is an established equivalent formulation of RH: Jonathan Sondow and Cristian Dumitrescu, *A monotonicity property of Riemann's xi function and a reformulation of the Riemann Hypothesis*, Periodica Mathematica Hungarica 60 (2010), 37–40. https://arxiv.org/abs/1005.1104 ; DOI 10.1007/s10998-010-1037-3. No claim of novelty for that criterion.

## Reproducible numerical check
The following independent reduced grid was run in Python with mpmath at 30 decimal digits. It gave 208 positive values out of 208, minimum 2.09670649111701e-6. No interval certification or coverage of continuous or unbounded domains. Earlier conversational reports of 3,802 samples and five local interval certificates are not independently reproduced here and are not relied upon.

Install mpmath with python -m pip install mpmath, then run:

```python
import mpmath as m
m.mp.dps = 30
xs = list(map(m.mpf, ['.001','.01','.1','.5','1','2','5','10']))
ts = [m.mpf(i) for i in range(0,201,10)] + [
    m.im(m.zetazero(i)) for i in range(1,6)]
vals = []
for x in xs:
    b = 1/(1+m.exp(-x))
    for t in ts:
        s = m.mpc(b,t)
        d = (1/s + 1/(s-1) - m.log(m.pi)/2
             + m.digamma(s/2)/2
             + m.zeta(s,derivative=1)/m.zeta(s))
        vals.append(2*b*(1-b)*m.re(d))
print(len(vals), sum(v>0 for v in vals), m.nstr(min(vals),15))
```

## Open problem
An independent uniform positivity argument for the entire domain is missing. Compactifying coordinates does not establish uniform bounds, exclude zeros, or prove RH. Frequency/momentum/energy conservation currently supplies inspiration only. This note closes the current exploratory session with the unresolved step clearly identified.
