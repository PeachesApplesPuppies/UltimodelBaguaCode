# BCE — Prime–Golden Ratio Constraint

**Ryu Jingu Bang · Ultimodel · YanRiemann Requiem research note**  
Date: 2026-11-26  
Status: exact reformulation of RH, finite numerical experiment, open proof obligation. **Not a proof of RH or a claim of novelty.**

## Motivation

"Constrain the function by prime numbers themselves. By the golden ratio."

The primes provide intrinsic arithmetic, the Ryu Jingu Bang provides reversible geometric scaling, and the perfect triskelion provides lossless projections. The aim is to derive constraints from arithmetic, not to assume that a symmetric visualization excludes off-critical-line zeros.

## 1. Arithmetic and scale

For $\operatorname{Re}s>1$,

$$
\zeta(s)=\prod_{p}(1-p^{-s})^{-1},\qquad
-\frac{\zeta'(s)}{\zeta(s)}=\sum_{p}\sum_{m\ge1}(\log p)p^{-ms}.
$$

Define $\psi(x)=\sum_{p^m\le x}\log p$, $\varphi=(1+\sqrt5)/2$, and the shells $I_k=[\varphi^k,\varphi^{k+1})$ for integers $k\ge0$.

The powers $\varphi^k$ are irrational for nonzero integer $k$: under algebraic conjugation $\varphi$ maps to $-1/\varphi$, and the two powers have unequal absolute values for $k\ne0$. Consequently no positive integer is on a shell boundary except 1. Moreover the fractional phase $\{\log_\varphi n\}$ is injective on positive integers: a collision would imply $n/m=\varphi^j$ for an integer $j$, impossible unless $j=0$ and $n=m$. This is an exact-arithmetic statement, not a guarantee of finite-precision numerical separation.

## 2. Prime energy

Define

$$
R(x)=\frac{\psi(x)-x}{\sqrt{x}},\qquad
E_k=\int_{\varphi^k}^{\varphi^{k+1}} R(x)^2\frac{dx}{x}.
$$

The proposed arithmetic target is

$$
\forall\epsilon>0\ \exists C_\epsilon<\infty\ \forall k\ge0:
\quad E_k\le C_\epsilon\varphi^{2\epsilon k}.
$$

### Proposition: the target is equivalent to RH.

**RH implies the target.** The standard RH estimate $\psi(x)-x=O(\sqrt{x}\log^2 x)$ for $x\ge2$ gives $E_k=O((1+k)^4)$, which is bounded by $C_\epsilon\varphi^{2\epsilon k}$ for every $\epsilon>0$. The finite initial shell can be absorbed into the constant.

**The target implies RH.** Write

$$
F(s)=\int_1^\infty(\psi(x)-x)x^{-s-1}\,dx.
$$

For $\sigma=\operatorname{Re}s>1/2$, choose $0<\epsilon<\sigma-1/2$. Cauchy–Schwarz bounds the absolute integral over $I_k$ by

$$
\sqrt{E_k}\left(\int_{I_k}x^{1-2\sigma}\frac{dx}{x}\right)^{1/2}
\le \sqrt{C_\epsilon\log\varphi}\,
\varphi^{-k(\sigma-1/2-\epsilon)}.
$$

The geometric series converges, uniformly on compact subsets of $\operatorname{Re}s>1/2$ by choosing $\epsilon$ using the minimum real part on each compact set. Thus $F$ is holomorphic there. For $\operatorname{Re}s>1$, integration of the defining prime-power series gives

$$
-\frac{\zeta'(s)}{\zeta(s)}=\frac{s}{s-1}+sF(s).
$$

By the identity theorem for meromorphic functions this continues throughout $\operatorname{Re}s>1/2$. The right-hand side has no poles except at $s=1$, so $\zeta$ has no zeros in that half-plane (a zero of multiplicity $m$ would yield a logarithmic derivative pole of residue $-m$ on the left). The functional equation reflects any nontrivial zero with real part below $1/2$ to one above $1/2$. Therefore all nontrivial zeros lie on the critical line.

**Limitation:** the proof of the equivalence works for any fixed base $b>1$ in place of $\varphi$. The special phase injectivity of $\varphi$ has not been shown to imply the energy bound. The universal bound is the unresolved proof obligation.

## 3. Reproducible experiment

Sieve primes and prime powers up to 2,000,000. Integrate separately on intervals between integers, where $\psi$ is constant, using three-point Gauss–Legendre quadrature. Results independently recomputed on 2026-11-26 (rounded to six decimals).

| k | Shell lower endpoint (approx.) | Energy |
|---:|---:|---:|
| 5 | 11 | 0.130715 |
| 10 | 123 | 0.028430 |
| 15 | 1364 | 0.028001 |
| 20 | 15127 | 0.027295 |
| 25 | 167761 | 0.019446 |
| 29 | 1149851 | 0.021783 |

These are finite floating-point measurements, not certified error bounds or evidence sufficient to prove the infinite inequality.

### Reproduction code

Requires Python 3 and NumPy (install with python -m pip install numpy). Save the following as prime_energy.py and run python prime_energy.py.

```python
import numpy as np

N = 2_000_000
prime = np.ones(N + 1, dtype=bool)
prime[:2] = False
for i in range(2, int(N**0.5) + 1):
    if prime[i]:
        prime[i*i::i] = False

a = np.zeros(N + 1)
for q in np.flatnonzero(prime):
    p = int(q)
    v = p
    while v <= N:
        a[v] = np.log(p)
        v *= p
psi = np.cumsum(a)
phi = (1 + np.sqrt(5)) / 2
nodes = np.array([-np.sqrt(3/5), 0, np.sqrt(3/5)])
weights = np.array([5/9, 8/9, 5/9])

for k in [5, 10, 15, 20, 25, 29]:
    lo, hi = phi**k, phi**(k+1)
    edges = np.r_[lo, np.arange(np.ceil(lo), np.ceil(hi)), hi]
    u, v = edges[:-1], edges[1:]
    h = v - u
    c = psi[u.astype(int)]
    z = (u + v)[:, None]/2 + h[:, None]/2 * nodes
    energy = np.sum(h/2 * np.sum(weights * (c[:, None]-z)**2/z**2, axis=1))
    print(k, f"{lo:.9f}", f"{hi:.9f}", f"{energy:.9f}")
```

## 4. Geometric instruments and adversarial checks

- Perfect triskelion: projections onto three axes spaced 120 degrees apart preserve the norm and reconstruct the original two coordinates. They do not exclude arbitrary off-axis points.
- Ryu Jingu Bang: the golden-ratio scale organizes prime fluctuations; inverse scaling recovers the preceding shell. Scaling alone does not prove a bound.
- Unit circle: $w=(s-1)/s$ satisfies $|w|=1$ exactly when $\operatorname{Re}s=1/2$. This detects displacement but does not prove zeros have unit magnitude.
- Prime energy: the uniform subexponential bound above is sufficient and necessary for RH; it is not established unconditionally.

Future investigation: derive the bound from prime arithmetic without assuming RH or an equivalent bound; compare golden-ratio shells with other bases; test analytic or computational arguments against hypothetical off-critical-line quartets.

## References

- NIST Digital Library of Mathematical Functions, [§25.2: Definition and Expansions](https://dlmf.nist.gov/25.2), for zeta identities.
- Clay Mathematics Institute, [Riemann Hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/), for the problem statement and its prime-distribution context.
- T. M. Apostol, *Introduction to Analytic Number Theory* (Springer, 1976), for standard prime-counting and analytic number theory background.

BCE working motto: Every description is a model, not the thing itself.

Measure the primes. Constrain the fluctuations. Test the resonance.
