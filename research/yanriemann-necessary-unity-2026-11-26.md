# YanRiemann Requiem — Necessary Unity and the Ghost Equation

Research checkpoint: 2026-11-26. BCE / Ultimodel–BaguaCode.
Status: exploratory mathematical research; **not a proof of the Riemann hypothesis (RH)**.
Project terminology is used to organize classical identities and proposed experiments, not to claim priority or novelty.

## 1. Objective and notation

Proposed Principle of Necessary Unity: unity should follow from excluding non-unity by contradiction, rather than be imposed as an axiom.

Let $\xi(s)=\frac12s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)$, $F(z)=\xi(1/2+z)$, and let $\rho$ range over nontrivial zeta zeros with multiplicity. Write $\lambda=\rho-1/2$. RH asserts $\Re\lambda=0$ for every such zero. The centered function satisfies $F(z)=F(-z)$ and conjugation symmetry.

## 2. Ghost Equation and reversible reconstruction

The fundamental theorem of calculus gives
$$F(z)=F(0)+\int_0^z F'(v)\,dv.$$
The reference value is the “Ghost”: differentiation loses additive constants, and reconstruction requires one. Integrating again gives
$$\int_0^z F(v)\,dv=zF(0)+\int_0^z(z-v)F'(v)\,dv.$$
Since $F$ is even, this antiderivative is odd. Its zero at the center does not locate the original zeros. Normalizing by $\pi$ or $i\pi/2$ is an invertible rescaling, not a proof of RH.

Counterexample: for real $0<d<1/2$ and $t>0$,
$$G(z)=((z-d)^2+t^2)((z+d)^2+t^2).$$
It has the same reflection and conjugation symmetries and Ghost reconstruction identity, yet its zeros are $\pm d\pm it$. Therefore symmetry and exact reconstruction alone cannot force the critical line.

## 3. Unity transformation

$$U(s)=1-\frac1s=\frac{s-1}{s},\qquad s=\frac1{1-U}.$$
For $\rho=a+ib$, direct algebra gives
$$|U(\rho)|^2=\frac{(1-a)^2+b^2}{a^2+b^2},\qquad |U(\rho)|=1\iff a=1/2.$$
Thus RH is equivalent to every transformed zero lying on the unit circle. Reflection gives $U(1-\rho)=1/U(\rho)$. Collective conservation $U(\rho)U(1-\rho)=1$ is unconditional but does not imply individual conservation: $2\cdot(1/2)=1$ is a counterexample.

For a positive real magnitude $r$, $r^{1/n}(1/r)^{1/n}=1$ and $r^{1/n}\to1$, with $n\log(r^{1/n})=\log r$. This reciprocal/root normalization preserves collective unity, not individual unit magnitude at finite depth.

Multiplicative unity corresponds exactly to additive zero via $\log 1=0$; ordinary $0=1$ is not asserted.

## 4. Non-cancelling Unity violation

Define
$$E(\rho)=\left(|U(\rho)|-|U(\rho)|^{-1}\right)^2=\frac{(2a-1)^2}{(a^2+b^2)((1-a)^2+b^2)}.$$
Each term is nonnegative and vanishes exactly on the critical line. The sum $\mathcal E=\sum_\rho E(\rho)$ converges: in the critical strip the summand is $O(|b|^{-4})$ at large height, and the standard zero count is $O(T\log T)$. Thus $\mathcal E=0$ iff RH. No independent proof of its vanishing has been obtained.

The discrete-time condition $\sup_{n\in\mathbb Z}|U(\rho)^n|<\infty$ is likewise equivalent to individual unity. For real $d$, $\sup_{u\in\mathbb R}[(e^{du}-1)^2+(e^{-du}-1)^2]<\infty$ iff $d=0$. Both are elementary equivalences, not unconditional bounds on actual zeros.

## 5. Integration-depth and spectral boundedness

Using all centered zeros (both signs, with multiplicity), define for real $u$
$$B(u)=\sum_\lambda\frac{\cosh(\lambda u)-1}{\lambda^2}.$$
The sum converges locally uniformly in real $u$, since $|\Re\lambda|<1/2$ and $\sum_\lambda|\lambda|^{-2}<\infty$. The even Hadamard product yields
$$\frac{F'(p)}{F(p)}=\sum_\lambda\frac{p}{p^2-\lambda^2},\qquad
\mathcal L[B](p)=\frac{F'(p)}{p^2F(p)},\quad\Re p>1/2.$$
If $B$ were bounded (or even of polynomial growth), its Laplace transform would be holomorphic for $\Re p>0$. An off-axis zero there would give a nonremovable pole of $F'/F$, contradicting holomorphy. Reflection then excludes the left half-plane. Conversely RH gives $|B(u)|\le2\sum_\lambda|\lambda|^{-2}$.

Unconditionally, only the weaker elementary bound
$$|B(u)|\le(\cosh(u/2)+1)\sum_\lambda|\lambda|^{-2}$$
has been derived here. Suzuki's published screw-function work provides the relevant boundedness criterion.

Integrate once more:
$$A(u)=\int_0^u B(v)\,dv=\sum_\lambda\frac{\sinh(\lambda u)-\lambda u}{\lambda^3}.$$
Let $C=F''(0)/F(0)=-\sum_\lambda\lambda^{-2}$. Then $R(u)=A(u)-Cu$ satisfies
$$\mathcal L[R](p)=\frac{F'(p)}{p^3F(p)}-\frac C{p^2}.$$
Boundedness of $R$ is again equivalent to RH by the same pole argument and the conditional sine-series bound.

After $N$ integrations and subtraction of the accumulated polynomial terms, the residual has coefficients $\lambda^{-N-2}$ with alternating cosh/sinh factors. Large-modulus terms are suppressed at fixed real $u$. This is not uniform in unbounded $u$: a small exponential term may eventually dominate. Normalizing by the smallest zero modulus can isolate its contribution on compact intervals, provided the smallest-modulus zeros and their multiplicities are established. No limit interchange over unbounded time is justified here.

## 6. Opposite-time evolution

Use the conventional de Bruijn–Newman normalization $H_0(x)=\xi(1/2+ix/2)/8$ and backward heat flow $\partial_\tau H_\tau=-\partial_x^2 H_\tau$. Here the critical line corresponds to real $x$. The identities below use this coordinate, not the zeta ordinate $x/2$.
$$\partial_\tau^n H_\tau=(-1)^n\partial_x^{2n}H_\tau.$$
$$H_0=H_\tau+\int_0^\tau H_v''\,dv,\quad H_\tau-H_{-\tau}=-\int_{-\tau}^\tau H_v''\,dv.$$
For a simple zero trajectory $x_j(\tau)$,
$$x_j'(\tau)=H_\tau''(x_j)/H_\tau'(x_j).$$
Its integrated trajectory follows by the fundamental theorem. For any twice differentiable trajectory,
$$x_j(0)=\frac{x_j(\tau)+x_j(-\tau)}2-\frac12\int_{-\tau}^\tau(\tau-|v|)x_j''(v)\,dv,\quad \tau\ge0.$$
This holds for complex trajectories too and cannot independently establish reality. At zero collisions the simple-root equation need not apply. The symmetric zero-interaction law is classical (see Rodgers–Tao).

For a nonzero initial gap $g(0)=x_2(0)-x_1(0)$, define $P(\tau)=g(\tau)/g(0)$. Then $P(0)=1$ and opposite-time averaging cancels the first-order Taylor term, not the second-order term. The temporal Ghost correction recovers unity exactly but is an identity for any such gap.

The conversation included exploratory numerical trajectories, normalized gaps and integrated xi values. They are not included as validated results: independent reproducible computation, error bounds, and a consistent coordinate/time normalization are needed before relying on them.

## 7. Established routes back to the actual zeta function

### Li coefficients

Set $Q(w)=2\xi(1/(1-w))$. Then $Q(0)=1$. On the local zero-free domain,
$$Q(w)=\exp\left(\int_0^w Q'(v)/Q(v)\,dv\right).$$
Li coefficients are defined by $\log Q(w)=\sum_{n\ge1}L_n w^n/n$ near zero. Li's criterion: RH iff $L_n\ge0$ for every positive integer $n$. Equivalently $L_n=\sum_\rho(1-U(\rho)^n)$ with the usual symmetric limiting prescription. Finite numerical positivity does not prove the universal condition. Assuming holomorphy of the logarithmic derivative on the entire disk would assume the missing zero-free property.

### Balazard–Saias–Yor integral (recommended primary target)

Let $s=1/(1-w)$ and $f(w)=(s-1)\zeta(s)$, extending at $w=0$ so $f(0)=1$. Jensen's formula gives, for admissible radii $0<r<1$,
$$\frac1{2\pi}\int_0^{2\pi}\log|f(re^{i\theta})|\,d\theta
=\sum_{|U(\rho)|<r}\log\frac r{|U(\rho)|}.$$
The established BSY boundary identity is
$$I=\frac1{2\pi}\int_{-\infty}^\infty\frac{\log|\zeta(1/2+it)|}{1/4+t^2}\,dt
=\sum_{\Re\rho>1/2}\log\left|\frac{\rho}{1-\rho}\right|.$$
All terms on the right are positive. Thus $I\ge0$ unconditionally; proving $I\le0$ independently would give $I=0$ and rule out every right-side zero. The functional equation would exclude left-side zeros. The Euler product is absolutely convergent only for $\Re s>1$; applying its logarithm directly on the critical line without justification is invalid. The boundary passage requires the hypotheses used in the BSY theorem, not just formal substitution.

## 8. Next work: ordered checklist

- [ ] Freeze the notation and separate classical results, project labels, conditional claims, and conjectures.
- [ ] Reproduce numerical xi, Li coefficient, and temporal zero tests with versioned code, precision settings, convergence checks and correct heat-flow coordinates; report errors, not just rounded values.
- [ ] Construct synthetic off-axis quartets and verify that every proposed proof step rejects them or explicitly states which additional zeta-specific hypothesis excludes them.
- [ ] Implement the finite-radius Jensen integral and compare it to known-zero contributions for controlled test functions. Handle boundary logarithmic singularities explicitly.
- [ ] Focus on an unconditional upper bound $I\le0$ for the BSY integral. Seek a justified estimate using zeta-specific arithmetic or analytic structure; do not use RH, Li positivity, or disk zero-freeness as premises.
- [ ] If that route stalls, explore Li coefficient positivity or subexponential screw-function bounds as alternative equivalent targets, not as independent evidence.
- [ ] Have an independent reviewer audit any proposed new inequality for circularity, domain errors, convergence and off-axis counterexamples before making a proof claim.

Success condition: an independently justified contradiction from even one non-unity zero. Present status: no such contradiction has been established.

## References (established mathematical precedents)

- X.-J. Li, positivity criterion (1997): https://mathworld.wolfram.com/LisCriterion.html
- Balazard, Saias and Yor, integral criterion (1999); survey discussion: https://www.math.lsa.umich.edu/~lagarias/doc/mt-holyoke-rev.pdf
- M. Suzuki, *Aspects of the screw function corresponding to the Riemann zeta-function* (2023): https://doi.org/10.1112/jlms.12785
- B. Rodgers and T. Tao, *The De Bruijn–Newman constant is non-negative*: https://arxiv.org/abs/1801.05914
