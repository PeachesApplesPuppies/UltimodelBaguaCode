# BCE — End-of-day investigation log, 2026-11-26

**Ultimodel / YanRiemann Requiem / Ryu Jingu Bang**

Status: exploratory mathematics and analogies. No proof of the Riemann hypothesis (RH), no claimed new physical law, no claim of priority. This note preserves promising ideas and failed routes together, so they can be independently checked. It supplements [the prime-energy criterion](../prime-golden-ratio-constraint-2026-11-26.md).

## Research principles and metaphors

- "Constrain the function by prime numbers themselves. By the golden ratio."
- "Look for the fastest way to lose."
- "Light speed oscillation."
- "If it has a cycle, you can recycle it."
- "Light speed distortion. The blue shift."
- "Half of it doesn't make sense."

The perfect triskelion is a metaphor for reversible three-axis projections; the Ryu Jingu Bang is a metaphor for reversible scaling; resonance, recycling, light and distortion are prompts for exploring conservation and recurrence. These metaphors are not mathematical premises. Preserve them as provenance, not as established evidence.

## 1. Exact geometry and its limits

For Cartesian coordinates $(x,y)$, take $P_1=x$, $P_2=-x/2+\sqrt3 y/2$, $P_3=-x/2-\sqrt3 y/2$. Then $P_1+P_2+P_3=0$ and $(2/3)\sum P_i^2=x^2+y^2$. Inverse: $x=P_1$, $y=(P_2-P_3)/\sqrt3$. This preserves off-axis points too.

The functional equation and conjugation symmetry allow a hypothetical quartet $1/2\pm\delta\pm it$; reflection alone cannot establish RH. The map $w=(s-1)/s$ obeys $|w|^2-1=-2\delta/|s|^2$ for $s=1/2+\delta+it$, $s\ne0$. Unit modulus detects the critical line but is not established for all transformed zeros.

Other possible directions include Li's criterion, Weil positivity, Nyman–Beurling density, the Hilbert–Pólya spectral approach, de Bruijn–Newman, and universal Jensen-polynomial hyperbolicity. These are existing research directions; listing them does not establish their required conditions.

## 2. Prime shells and recurrence

For any fixed $b>1$, let $L=b^k$, $H=b^{k+1}$ and $\psi(x)=\sum_{p^m\le x}\log p$.

$$
A_k=(\psi(L)-L)/\sqrt L,\qquad
B_k(x)=(\psi(x)-\psi(L)-(x-L))/\sqrt L.
$$

Write $B_k=B_k(H)$. Exactly,

$$
A_{k+1}=(A_k+B_k)/\sqrt b.
$$

The shell energy is $E_k=\int_L^H(\psi(x)-x)^2 dx/x^2$. As shown in the preceding note, the statement $E_k=O_\epsilon(b^{2\epsilon k})$ for every $\epsilon>0$ is equivalent to RH. The proof works for every fixed $b>1$. No proof of this bound is supplied.

For $b=\varphi=(1+\sqrt5)/2$, the carry contraction is $\varphi^{-1/2}\approx0.786151$. This does not bound the new increment. The condition $\sup_{L\le x\le H}|B_k(x)|=O_\epsilon(b^{\epsilon k})$ for every $\epsilon>0$ would suffice via the recurrence and is also implied by the standard RH prime-counting bound. It is not independently established.

An alternative Mertens target is $M(x)=\sum_{n\le x}\mu(n)=O_\epsilon(x^{1/2+\epsilon})$ for every $\epsilon>0$, another standard equivalent criterion. The local identities $\sum_{d\mid n}\mu(d)=1$ for $n=1$ and zero otherwise, and $\sum_{d\mid n}\Lambda(d)=\log n$, are exact. Local cancellation alone has not been turned into global cancellation.

## 3. Reproducible numerical experiments

Files in this directory:

- [prime_shell_experiment.py](prime_shell_experiment.py)
- [prime_shell_results.csv](prime_shell_results.csv)
- [prime_cancellation_experiment.py](prime_cancellation_experiment.py)
- [prime_cancellation_results.csv](prime_cancellation_results.csv)

Run in this directory using Python 3 and NumPy:

    python -m pip install numpy
    python prime_shell_experiment.py --limit 30000000 --output prime_shell_results.csv
    python prime_cancellation_experiment.py --limit 30000000 --output prime_cancellation_results.csv

Both scripts use floating-point Gauss–Legendre quadrature split at prime powers; they are not certified bounds. The CSVs contain 123 rows each across four bases. Archived CSVs were transferred via a tabular text extraction, which can round the final digits; regenerate using the scripts for original precision. No raw private conversation, health details, or unrelated video is included.

Reported results: 1,857,859 primes and 1,858,718 prime powers including primes; 35 complete golden shells. Selected shell energies: k=5: .130715; 10: .028430; 15: .028001; 20: .027295; 25: .019446; 29: .021783; 30: .017664; 32: .026142; 34: .019039. Boundary increments opposed the old error in 24/35 shells, with magnitude decreasing in 15/35. A–B correlation approximately -0.2058. Finite results cannot establish an infinite bound.

## 4. Cancellation experiment

With weight $dW=L dx/x^2$ on a shell, the exact identity is

$$
E_k=P_k+C_k+Q_k,\quad P_k=\int A_k^2 dW,\quad
C_k=\int 2A_kB_k(x)dW,\quad Q_k=\int B_k(x)^2dW.
$$

Negative $C_k$ is algebraic cancellation, not a physical energy law. In 28/35 golden shells it was negative. For the 18 complete golden shells contained in [1000, 10 million], reported sums were $P=.244242$, $Q=.635720$, $C=-.466198$, $E=.413764$ (rounding); reduction $-C/(P+Q)=52.98\%$. Comparison for complete shells in that broad window: sqrt(2) 50.80%, phi 52.98%, 2 44.90%, 3 60.86%. Exact endpoints differ between bases. No unique golden-ratio advantage is demonstrated. Integral additivity makes total energy over identical endpoints independent of partition.

### Adversarial mode

Set $R_\delta(x)=x^\delta\cos(14\log x)$. For fixed $\delta$ its energy on a shell is comparable to $b^{2\delta k}$: substituting $u=\log x$ leaves an integral over a fixed-width interval of a positive exponential times cosine squared, whose minimum over starting phases is positive. Thus for $\delta>0$ the energy grows exponentially despite the exact recurrence.

Synthetic cancellation tests (k=20 through 80) reported reductions of 59.84%, 58.23%, 54.73%, 50.68% for delta 0, .05, .15, .25 respectively. The code is the authoritative reproducibility source. Cancellation percentages alone cannot rule out growth. These are synthetic signals, not actual zeta zeros.

## 5. Fastest way to lose: arithmetic perturbation

Let $N=30$ million and $H(x)=\sum_{N<p\le x}(\log p)p^{-1/4}$. Define $\psi_\pm=\psi\pm H$. The two artificial functions agree with the measured data through N, preserve prime-power jump locations and positive weights, and still satisfy $\psi_\pm(x)\sim x$. By the prime number theorem and partial summation, $H(x)\sim(4/3)x^{3/4}$. The parallelogram identity yields

$$
E_k^++E_k^-=2E_k+2\int_{b^k}^{b^{k+1}}H(x)^2\,dx/x^2
\gtrsim b^{k/2}.
$$

At least one artificial function cannot satisfy the RH-type energy bound. Neither is the genuine Chebyshev function because its von Mangoldt weights have been altered. This falsifies sufficiency of the weaker assumptions, not RH. Exact arithmetic weights must be used in any proof.

## 6. Relativity and golden ratio (exact chosen parametrization)

For collinear boosts let rapidity $\eta=\operatorname{arctanh}(v/c)$ and longitudinal approach Doppler factor $D=e^\eta$. Choose $D_n=\varphi^n$ (a modeling choice, not a physical law). Then

$$
v_n=c\tanh(n\log\varphi)
=c\frac{\varphi^{2n}-1}{\varphi^{2n}+1},
\quad v_1=c/\sqrt5.
$$

For light-cone coordinates $u=ct+x$, $w=ct-x$, the transformation $u'=\varphi u,\ w'=\varphi^{-1}w$ preserves $uw$. This is a Lorentz boost up to sign convention. With continuously increasing rapidity at rate $\log\varphi/T$ per proper time, constant collinear proper acceleration is $a=c\log\varphi/T$. This describes a massive observer, not photon acceleration.

A separate chosen direction rule is the golden angle $\theta_g=2\pi/\varphi^2$, with successive directions $n\theta_g\bmod 2\pi$. Irrational rotation is dense and never repeats exactly. Direction changes may create coordinate centripetal acceleration $v^2/r$ for a curved path. Noncollinear relativistic boosts cannot be combined by simply adding scalar rapidities; these direction and boost prescriptions are not yet one dynamical system.

Blueshift: $f_n=f_0\varphi^n$, $\lambda_n=\lambda_0\varphi^{-n}$ and $f_n\lambda_n=c$ in vacuum. Frequency, wavelength and observer-measured photon energy change, not the local speed of light. An invariant product permits reciprocal unbounded growth; it does not enforce constant amplitude. There is no demonstrated link to prime arithmetic or reason for nature to select phi.

## 7. Oscillation, conservation, and recycling

In the explicit formula for prime counting, a zero $\rho=1/2+\delta+i\omega$ contributes a term proportional to $x^\rho/\rho$ (with sign and conventions as appropriate). After normalizing by $\sqrt x$ and writing $u=\log x$, this gives $e^{\delta u}e^{i\omega u}$ up to a constant. This is a formal individual zero contribution, not a justified decomposition into independent normalizable modes in an established Hilbert space.

The golden step multiplier is $q=\varphi^\delta e^{i\omega\log\varphi}$, so $|q|=1$ exactly when $\delta=0$. This is a detector, not an independently established constraint.

A hypothetical operator $U$ preserving a positive-definite norm, with nonzero eigenvectors $Uf=qf$ for every relevant zero, would force $|q|=1$. Constructing it and proving spectral correspondence without assuming RH are missing steps.

Light-speed propagation is insufficient: $F(x,t)=e^{a(x-ct)}$ solves $F_{tt}=c^2F_{xx}$ but has an exponential spatial profile (not a finite-energy wave on the whole line). A wave equation or invariant speed alone does not supply the desired arithmetic norm conservation.

**Recycling / recurrence:** For a nonzero mode $f$, exact recurrence $U^Nf=f$ with positive integer N gives $q^N=1$ and hence $\delta=0$. Even approximate recurrence $U^{n_j}f\to f$ in norm along integers $n_j\to\infty$ gives $|q|=1$. Exact finite closure additionally constrains the phase and is stronger than needed, so it should not be presumed for all zeta-zero frequencies. Reversibility is weaker than recurrence. Phase recurrence alone can coexist with an expanding or contracting radius. Full-state recurrence has not been shown for an arithmetic evolution representing the zeros.

## 8. Open obligations and review

The next step is to derive a genuine unconditional estimate or positive conservation law from exact arithmetic. An equivalent RH statement is not progress toward its proof unless the new condition is independently proved or makes a specific lemma tractable. Test counterexamples first. Do not assume randomness/independence of Mobius signs, or assume a conserved norm that silently encodes the desired spectrum.

Audit checklist: exact definitions and domains; independent premises; justify analytic continuation and interchange of sums/integrals; universal quantifiers; adversarial examples; independent mathematical review. Code and finite data are supporting material only.

**Conclusion:** the work provides reformulations, exact algebraic identities, reproducible finite experiments, negative results for several proof strategies, and physical analogies. RH is not proved. The physics analogies have not been established as mechanisms in arithmetic.

Every description is a model, not the thing itself.
