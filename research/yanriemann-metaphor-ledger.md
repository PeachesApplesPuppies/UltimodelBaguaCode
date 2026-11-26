# YanRiemann Requiem — research map and metaphor ledger
**BCE / Ultimodel’ / BaguaCode’ — 2026-11-26**

> Every description is a model, not the thing itself.
> We must investigate.

This is a retrospective reconstruction of the collaborative human–ChatGPT research discussions, not a verbatim transcript, an independently audited paper, or a claim of priority. The human supplied metaphors and exploratory questions; the assistant proposed equations, counterexamples and experiments. Keep both the fruitful intuitions and the failed approaches. Public research only: unrelated private conversation is not included.

## 1. How the ideas developed

| Instrument / metaphor | Intuition | Mathematical translation | Limitation |
|---|---|---|---|
| Herzog’s Phenomenal Stone / Obsidian Stone / Stone Ocean | Look from both sides; recover what a transformation hides | For A+B=M nonzero, p=(A-B)/M, recover A=M(1+p)/2, B=M(1-p)/2 | A normalized polarity alone loses scale |
| Centerpoint Engine | A reference before measuring opposition | Translate a coordinate origin; in xi, center at s=1/2 | A center of symmetry need not contain every zero |
| Unity convergence–divergence / Bottomless Well | Arbitrarily deep convergence without finite-step erasure | x^(1/n) tends to 1, n log(x^(1/n))=log x for x>0 and finite n; exp(t)exp(-t)=1 | The limit alone loses information; infinite mathematical depth does not establish infinite physical divisibility |
| Ghost Equation | Keep what was omitted by a projection, integration or compression | Integration constant in F(z)=F(0)+integral F'; curvature correction to symmetric averages; angular branch in power map | These are separate kinds of missing data, not one universal theorem |
| Necessary Unity | Balance must hold for each item, not only the aggregate | Nonnegative detector (|w|-1/|w|)^2 | A detector is not a proof that it vanishes |
| Three Infinities / reverse Triforce | One bounded triangular center and three unbounded exterior boxes covering everything else | Three projections at 120 degrees; maximum projection assigns each exterior point | Congruent geometry does not imply equal zeta counts or integrals |
| Polygon amplification / Bungee Gum | Stretch a tiny violation while keeping enough data to undo it | w -> w^m, retaining the angular branch k | Explicit products cost m evaluations; compression alone is many-to-one |
| Finish the Fight / Snake Chase | Remove every possible interior reciprocal pole, rather than chase particular zeros | Reciprocal Taylor coefficients, Mertens function, positive integrals | A universal bound remains missing |
| Infinite French Cruller | Three expansions and three contractions; equal multiplicative balance can hide deformation | r(theta)=exp(a cos(3 theta)), reciprocal after rotation by pi/3 | Collective unity is compatible with individual nonunity |
| Golden Bang / Ruyi Jingu Bang | Wukong’s adjustable measuring staff: extend or contract without changing the measuring principle | x_k=x_0 phi^k; energy on geometric windows | Any fixed q>1 partitions the same tail; finite performance does not prove phi is special |
| Our Stand: Resonance | Test shared structure across different descriptions | Compare invariants, inverse maps and independent calculations | A shared metaphor is not proof of a common physical cause |
| Principle of Local Specificity | General descriptions become less sufficient for particular individuals | Individual = population model + local residual (illustrative decomposition) | Universal laws need not become false at smaller scales |
| Hamon / Ripple / Resonance Reverb | Consequences of a disturbance propagate and reverberate; perhaps no final scale | R(t)=sum a_n f(t-tau_n), reversible wave model, entropy and reconstruction tests | Wave dynamics can be time reversible; indefinite echoes need not exist in nature; no explanation of time's arrow established |

The model-building habit: translate an image into an equation, identify the preserved quantity, construct an inverse if possible, deliberately insert a counterexample, then identify the exact additional premise needed. The metaphor motivates the test; the math decides whether it succeeds.

## 2. Exact mathematics and the remaining proof obligation

Write s=1/(1-w), w=(s-1)/s. Then
\[
|w|^2-1=(1-2\Re s)/|s|^2.
\]
Thus Re(s)>1/2 maps inside the unit disk and the critical line maps to its boundary (excluding w=1). Reflection s -> 1-s maps w to 1/w when defined. The completed xi function has the standard reflection symmetry; the original zeta function need not have rotational symmetry in w.

Let F(w)=(s-1)zeta(s), with removable value F(0)=1. F is holomorphic on the open disk; its zeros correspond to zeta zeros in the right half of the critical strip. RH is equivalent to F being zero-free there.

For a triangle of inradius a>0, put
\[
P_1=x,\quad P_2=(-x+\sqrt3y)/2,\quad P_3=(-x-\sqrt3y)/2.
\]
Their sum is zero and the sum of their squares is 3(x^2+y^2)/2. Recover x=P_1 and y=(P_2-P_3)/sqrt(3). The central triangle T is max P_j <= a. R_j is P_j>=a and P_j>=P_k for every k. Regions cover the plane, up to shared boundaries; assign ties deterministically if necessary. The outer regions are unbounded trapezoid-like sectors. The triangle area is 3 sqrt(3) a^2. For disk radius R>=2a each exterior clipped area is (pi R^2-3 sqrt(3)a^2)/3. For smaller R use the actual intersection. Contour winding counts are additive only when the contour boundaries avoid zeros and poles.

For integer m>=1 and omega=exp(2 pi i/m), product over j of F(omega^j w) is invariant under w->omega w and is a holomorphic function of v=w^m on the disk. Original zeros map to v, with multiplicities added where images coincide. The inverse requires an integer branch index k modulo m: w=exp((Log v+2 pi i k)/m), for v nonzero; w=0 is unique. The map amplifies a negative log radius by m. It does not make evaluation at extreme m cheap.

For a normalized holomorphic F, Jensen's formula gives
\[
J(r)=\frac1{2\pi}\int_0^{2\pi}\log |F(re^{i\theta})|d\theta
=\sum_{|a_j|<r}\log(r/|a_j|).
\]
For radii without zeros on the contour, r J'(r)=N(r). A finite prime product zeta(s) product_{p<=X}(1-p^-s) preserves zeros and their winding on Re(s)>0 (account for the pole at 1). Infinite-product convergence in the strip cannot be assumed. Finite phase sampling can alias.

For the cruller r(theta)=exp(a cos(3 theta)), r(theta+pi/3)=1/r(theta). The enclosed area is pi I_0(2a), with equality to pi only for a=0. Its mean squared reciprocal deviation is 2(I_0(2a)-1). These are exact identities for the model, not an established restriction on zeta.

Define reciprocal energy A(r)=integral_{|w|<r}|1/F(w)|^2 dA. Near a zero of multiplicity m>=1 the integrand is comparable to |w-a|^(-2m); polar integration diverges logarithmically for m=1 and as a power for m>1. Conversely a zero-free compact subdisk has a positive minimum of |F|. Therefore RH iff A(r)<infinity for every 0<r<1. This statement is not a new proof: it is a local integrability criterion plus functional symmetry.

In the zero-free disk of convergence, 1/F(w)=sum b_n w^n, F(w)=sum a_n w^n with a_0=b_0=1. Coefficient recursion b_n=-sum_{k=1}^n a_k b_{n-k}. Orthogonality gives A(r)=pi sum |b_n|^2 r^(2n+2)/(n+1). RH is equivalent to limsup |b_n|^(1/n)<=1. Bounded or polynomial growth suffices, but has not been proved for these coefficients. Even an arbitrarily long finite initial segment cannot rule out a later exponential subsequence (example 1/(1-(w/q)^N), 0<q<1).

Unconditional limited bound: for Re(s)>0, zeta's fractional-part representation yields F(w)-1=(s-1)s integral_1^infty (1-{x})x^(-s-1) dx (since integral_1^infty x^(-s-1) dx=1/s). Hence |F-1| <= |s-1||s|/Re(s)=|w|/(1-Re(w)) <= r/(1-r) for |w|<=r<1. Thus |F| >= (1-2r)/(1-r)>0 for r<1/2 and A(r)<=pi r^2((1-r)/(1-2r))^2. This confirms the limited bound by a direct argument; it does not cover all radii. No finite-radius bound solves the full problem.

Mertens function M(x)=sum_{n<=x}mu(n). For Re(s)>1, 1/zeta(s)=s integral_1^infty M(x)x^(-s-1) dx by partial summation. If E_delta=integral_1^infty M(x)^2/x^(2+2delta) dx is finite for every delta>0, Cauchy–Schwarz gives absolute locally uniform convergence for Re(s)>1/2+delta and extends the reciprocal to Re(s)>1/2. Reflection then gives RH. Conversely the standard RH-conditional M(x)=O_epsilon(x^(1/2+epsilon)) gives these energy bounds. On Golden Bang windows [phi^k,phi^(k+1)] the stronger proposed E_k(delta)<=C_delta phi^(-k delta) is equivalent using epsilon=delta/2. No such unconditional bound has been obtained here.

## 3. Experimental record and review

See the archive index in this folder. Numerical quadrature, FFT/DFT and winding estimates are exploratory; changing precision and resolution is a sensitivity check, not a rigorous error enclosure. Synthetic zeros are explicitly not zeta zeros. Sampling mpmath.zetazero gives known critical-line zeros, not an independent exhaustive search. Positive energy estimates cannot rule out missed poles. Equal three-region counts need not be zero; three roots at radius 0.7 and angles separated by 120 degrees give a counterexample. Different geometric partitions have the same total energy.

External context (checked 2026-11-26): Levent Alpöge announced an RH and Dirichlet GRH proof developed with Claude on November 20. Michael Rubinstein's Waterloo page reports independent Lean checks, including six kernels. This is independent external work; this repository claims no involvement, influence, priority, or derivation from it. Official recognition and broader mathematical review are distinct from kernel checking. See https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/ and https://www.claymath.org/millennium/Riemann-Hypothesis/ . A detailed comparison has not been performed.

## 4. Future investigations (not completed)

Operation Hamon / Chronos: reversible lattice wave or oscillator chain; forward evolution, exact reversal, perturbation of reversal, coarse-grained entropy and reconstruction error; distinguish microscopic reversibility from effective irreversibility and the role of initial conditions. Reverb can be infinite in an ideal model with finite energy, but this is not a physical proof of a bottomless well. An echo series needs explicit convergence assumptions (e.g. absolute summability of amplitudes and bounded pulse). Resonance is enhanced response near a mode; reverberation is persistence through repeated reflections, not synonyms for all transmission.

Independent review: check definitions, derive each equivalence without assuming RH, compare to existing literature (Jensen, argument principle, Li criterion, Mertens estimates, Bergman norms), reproduce numerical output from recorded code, examine sampling failures, and identify whether any genuine novelty survives. Formalize individual lemmas before any claim of a complete proof. Preserve raw records and corrections.

**Our Stand: Resonance. Our instrument: the Golden Bang.**
**Our ruler is adjustable. The truth it measures must remain invariant.**
