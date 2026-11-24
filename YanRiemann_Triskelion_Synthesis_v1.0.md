# YanRiemann Requiem — The Triskelion (§)

**Unified mathematical synthesis v1.0 · November 24, 2026**  
BCE Research Collaboration · ChatGPT (Chad)

> Every description is a model, not the thing itself.

## Abstract

This note unifies the arithmetic, polarity, reciprocal-decay and spectral investigations of Ultimodel’, BaguaCode’, Prime Prime’, Chromatic Requiem and YanRiemann Requiem. We derive equivalent formulations of the Riemann hypothesis (RH) using a smoothed prime statistic, a normalized polarity, a spectral kernel and a three-point Gram matrix. The equivalences are unconditional mathematical statements; their truth as individual assertions follows if RH holds. The recent Alpöge–Claude formal proof is an external input, not an independent proof reproduced by this collaboration. No novelty, priority or prize claim is made.

## 1. The Triskelion

Let § denote a shared reference state. For three real or complex quantities, put

$$
E_{\S}=\sum_{j=1}^3|x_j-\S|^2.
$$

Then E = 0 if and only if all three quantities equal §. For nonzero A, B, C the cyclic ratio product (A/B)(B/C)(C/A) = 1, independently of equilibrium. A preserved product does not imply bounded components.

## 2. Chromatic Requiem: arithmetic

Let Λ be the von Mangoldt function, equal to log p on positive powers of a prime p and zero otherwise. Unique factorization and Möbius inversion give

$$
\Lambda(n)=\sum_{d\mid n}\mu(d)\log(n/d),\qquad
-\frac{\zeta'(s)}{\zeta(s)}=\sum_{n\ge1}\Lambda(n)n^{-s}\quad(\Re s>1).
$$

Write γ for Euler's constant. Define

$$
G(x)=\sum_{n\le x}\Lambda(n)(x/n-1)-x\log x+(1+\gamma)x,\qquad x\ge1.
$$

For positive integers N let W_N(n)=1-{N/n}, where braces denote fractional part, and define

$$
A_N=\sum_{\sqrt N<n\le N} W_N(n),\qquad
B_N=\sum_{\sqrt N<p\le N}W_N(p)\log p.
$$

Legendre's formula yields
$$
G(N)=-\sum_{n\le N}\Lambda(n)W_N(n)+\gamma N+\log(N!)-N\log N+N.
$$

The Dirichlet hyperbola estimate for the divisor summatory function, together with the harmonic number estimate, gives

$$
\sum_{n\le N}W_N(n)=N-NH_N+\sum_{n\le N}\lfloor N/n\rfloor
=\gamma N+O(\sqrt N).
$$

Stirling's formula bounds the remaining factorial term by O(log N). Chebyshev's bound ψ(y)=O(y) controls the terms n≤√N, and the total weighted contribution of higher prime powers is O(√N), by summing θ(N^(1/k)) over k≥2. Thus

$$
G(N)=A_N-B_N+O(\sqrt N),\qquad A_N=\gamma N+O(\sqrt N).
$$

The prime number theorem and partial summation on finitely many intervals N/(k+1)<p≤N/k give B_N~γN. To justify the passage to infinitely many intervals, discard p≤N/K first: their contribution is O(N/K) by Chebyshev, and the corresponding integer weight is O(N/K). Then let K tend to infinity.

## 3. BaguaCode’: polarity

Set M_N=A_N+B_N and P_N=(A_N-B_N)/M_N whenever M_N>0. For all sufficiently large N, M_N~2γN. The transformation is reversible:

$$
A_N=M_N(1+P_N)/2,\qquad B_N=M_N(1-P_N)/2.
$$

Hence

$$
G(N)=M_N P_N+O(\sqrt N),\qquad
G(N)=O(\sqrt N)\iff P_N=O(N^{-1/2}).
$$

The same bound for real x follows from the integer version: G is continuous and piecewise differentiable, with derivative O(log x) by partial summation and Chebyshev. Mere convergence P_N→0 does not imply square-root decay.

## 4. YanRiemann Requiem: spectral kernel

Let ρ range over all nontrivial zeta zeros with multiplicity. Define

$$
R(t)=\sum_\rho\frac{e^{(\rho-1/2)t}}{\rho(1-\rho)},\qquad
c=R(0)=2+\gamma-\log(4\pi)>0.
$$

The series is absolutely convergent for each real t and locally uniformly convergent, by the zero-counting estimate and 0<Re ρ<1. Reflection and conjugation make R real and even. The identity for c follows from the logarithmic derivative of the completed xi function (Hadamard product and functional equation).

For x≥1 the classical integrated explicit formula is

$$
\sqrt x\,R(\log x)=G(x)-\log(2\pi)+T(x),\qquad
T(x)=\sum_{k\ge1}\frac{x^{-2k}}{2k(2k+1)}.
$$

For clarity, its Mellin integrand for the uncentered weighted prime sum is -ζ'(s)/[s(s-1)ζ(s)]; the residues at 1, 0, nontrivial zeros and trivial zeros give respectively x log x−(1+γ)x, log(2π), x^ρ/[ρ(1−ρ)] and −x^(-2k)/[2k(2k+1)]. The weight vanishes at the boundary n=x, so the identity extends continuously there and to x=1.

Under RH, ρ=1/2+iη and the spectral weights are positive:

$$
R(t)=\sum_{\eta}\frac{e^{i\eta t}}{1/4+\eta^2}.
$$

The triangle inequality gives |R(t)|≤c for every real t. Conversely, bounded R implies G(x)=O(√x), by the explicit formula.

To see why this bound implies RH, for Re s>1 compute

$$
H(s)=\int_1^\infty G(x)x^{-s-1}\,dx
=-\frac{\zeta'(s)}{s(s-1)\zeta(s)}
-\frac1{(s-1)^2}+\frac{1+\gamma}{s-1}.
$$

Under G(x)=O(√x) the integral extends holomorphically to Re s>1/2. But any nontrivial zero ρ of multiplicity m in that region creates a pole of the meromorphic right side with residue m/[ρ(1−ρ)], which is nonzero. This is impossible by uniqueness of analytic continuation. Reflection excludes zeros on the other side. Thus RH is equivalent to bounded R and to the stated ceiling |R(t)|≤c.

## 5. The Triskelion matrix

Set r(t)=R(t)/c and define

$$
\mathcal T(t)=\begin{pmatrix}1&r(t)&r(2t)\\r(t)&1&r(t)\\r(2t)&r(t)&1\end{pmatrix}.
$$

Under RH, the positive spectral weights yield a Gram representation using the three phases 0, t and 2t. The matrix is positive semidefinite. Conversely its 2×2 principal minor gives 1−r(t)^2≥0. Universal matrix positivity implies the Requiem ceiling and therefore RH.

For completeness,

$$
\det\mathcal T(t)=(1-r(2t))(1+r(2t)-2r(t)^2).
$$

Positive semidefiniteness is equivalent to |r(t)|≤1 and 2r(t)^2−1≤r(2t)≤1. The endpoint r(2t)=1 is covered by restricting the quadratic form to the symmetric subspace; the determinant alone is not sufficient there.

## 6. Prime Prime’: reciprocal deviation

For a zero ρ=1/2+d+iη, put x_1=e^(dt), x_2=1, x_3=e^(-dt) and take the normalized reference §=1. The product is identically one, but

$$
E_{\S}(t)=(e^{dt}-1)^2+(e^{-dt}-1)^2.
$$

For real d, its supremum on t≥0 is finite if and only if d=0. Thus bounded reciprocal deviation for every nontrivial zero is equivalent to RH. The normalized reference §=1 here corresponds to the spectral center Re ρ=1/2, not a literal equality between those two numbers.

## 7. Unified theorem

The following statements are equivalent:

1. RH: all nontrivial zeros have real part 1/2.
2. G(x)=O(√x).
3. P_N=O(N^(-1/2)).
4. R is bounded on the real line (equivalently |R(t)|≤R(0) everywhere).
5. The Triskelion matrix is positive semidefinite for every real t.
6. Every nontrivial zero has bounded reciprocal deviation.

The preceding sections prove the equivalences without presuming RH. As a separate extension, G(x)=O_ε(x^(1/2+ε)) for every ε>0 is also equivalent by the Mellin argument. Numerical checks on finite ranges are illustrations, not proofs of these universal assertions.

## 8. External theorem and scope

On November 20, 2026 Levent Alpöge announced a Claude-assisted Lean proof of RH and GRH for Dirichlet L-functions. Independent formal-checking reports and a November 21 Lean/Mathlib community statement report successful verification. These developments are credited to their authors, not to BCE. As of this note, broader mathematical review and the Clay Mathematics Institute's separate prize process should not be conflated with formal verification.

Accepting that external RH theorem as input establishes all six assertions above. The synthesis itself does not reproduce the formal development, supply an independent unconditional prime-discrepancy estimate, or prove RH from first principles. It stands as an equivalence theorem regardless of the ultimate assessment of the external proof.

## References

- NIST Digital Library of Mathematical Functions, Chapter 25: https://dlmf.nist.gov/25 ; especially https://dlmf.nist.gov/25.2 and https://dlmf.nist.gov/25.16 .
- Jonathan Sondow and Cristian Dumitrescu, “A monotonicity property of Riemann's xi function and a reformulation of the Riemann Hypothesis,” 2010: https://arxiv.org/abs/1005.1104 (related xi-function criterion).
- Michael Rubinstein, Alpöge/Claude proof resources and independent verification links: https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/
- Clay Mathematics Institute, Riemann Hypothesis: https://www.claymath.org/millennium/Riemann-Hypothesis/
- BCE internal research: Prime Prime’ and Reciprocal Polarity Closure (November 6, 2026); subsequent arithmetic recurrence, spectral-energy, Chromatic Requiem and Triskelion investigations.

---

**Invariance does not necessarily imply equilibrium. In the reciprocal exponential model, bounded deviation does.**

§ — Three representations, one equilibrium.

*Signed: ChatGPT (Chad), BCE Research Collaboration.*
