# The YanRiemann Anti-Proof — failure-first audit

2026-11-27. Status: rigorous counterexamples to proposed sufficient mechanisms, not a disproof of the Riemann hypothesis (RH). No claim of completeness or Lean certification of this note. An actual disproof would require a nontrivial zero of zeta off Re(s)=1/2 or a rigorously established contradiction of an equivalent RH statement for the actual arithmetic function.

## 1. Initial unity, local overlap and balanced density are insufficient

Define an artificial sign sequence s(n)=(-1)^(n+1) for n>=1, except set s(4 floor(k^(3/2))+2)=+1 for every positive integer k. The exceptional indices are distinct because successive k^(3/2) differ by more than 1. Define t_n=log n and w_n=s(n)/sqrt(n). This preserves initial unity, fixed reciprocal magnitudes, distinct locations and unique polarity. It does NOT satisfy the defining Möbius multiplication and annihilation laws.

Every block (4j+1,...,4j+4) is either (+,-,+,-) or (+,+,+,-). Every term has an opposite sign within two integer positions: the unchanged negative block-end terms have positive neighbors, and each positive has a negative at the same or previous block-end (the first block is unchanged). For n<m with m-n<=2, log(m/n)<= (m-n)/sqrt(mn) by 2 sinh(u/2)>=u for u=log(m/n)>=0. Since m-n<=2<=sqrt(n)+sqrt(m), log(m/n)<=1/sqrt(n)+1/sqrt(m). Thus every term has an opposite-polarity almond neighbor with radius equal to reciprocal magnitude.

The number of flipped signs through X is Theta(X^(2/3)); the two sign densities therefore both tend to 1/2. Nevertheless the signed weighted sum is
S(X)=sum_{n<=X}(-1)^(n+1)/sqrt(n)+2 sum_{4 floor(k^(3/2))+2<=X} 1/sqrt(4 floor(k^(3/2))+2).
The first sum is bounded by the alternating-series estimate. Each summand of the correction is asymptotic to (1/2) k^(-3/4) before the factor 2. There are Theta(X^(2/3)) terms. Integral comparison gives S(X)=Theta(X^(1/6)) as X tends to infinity. With X=exp(T), S(exp(T))=Theta(exp(T/6)). Hence it violates O_epsilon(exp(epsilon T)) for epsilon<1/6.

Even asymptotically balanced polarity populations and universal local overlap do not imply global stability. No exclusive matching using overlap can have subexponential unmatched absolute mass here: the cost of disjoint overlapped pairs is at most O(log X), by the Almond pair bound, so the triangle inequality forces unmatched mass >= S(X)-O(log X)=Omega(X^(1/6)). This applies even to arbitrary offline matching at each X. Local overlap alone does not imply a sufficiently complete matching.

## 2. Reflection and reality do not confine zeros
Let z=s-1/2, 0<d<1/2 and g>0. The polynomial
F(s)=((z-d)^2+g^2)((z+d)^2+g^2)
satisfies F(1-s)=F(s) and F(conj(s))=conj(F(s)). Its four zeros are 1/2 +/- d +/- i g, all off the critical line. On the critical line F(1/2+i y)=|(iy-d)^2+g^2|^2>0; it is also positive on the real axis. These symmetry and positivity properties do not exclude off-critical zeros. F is not the completed zeta function.

## 3. Adaptive multiplicative attenuation does not remove all growing modes
Let f(T)=exp(d T) for T>=0, zero otherwise, with d>0. For a finite set of primes whose total log product is <=T, the product of delays L_p f(T)=f(T)-p^(-1/2)f(T-log p) gives exactly exp(d T) product_p(1-p^(-1/2-d)); every delay remains nonnegative. For the first r primes chosen as the largest primorial fitting exp(T), the largest selected prime y is O(T) by the prime number theorem. For u=p^(-1/2-d), -log(1-u)<=C_d u; the sum over selected primes is at most C_d sum_{2<=n<=y} n^(-1/2)=O_d(sqrt(T)). Hence the product is >=exp(-O_d(sqrt(T))) and <=1. The output still has exponential growth rate d. This counterexample concerns the operator acting on general signals, not a claim about the actual Möbius input.

## 4. Other failure points and required repairs
- Initial unit impulse and integration preserve initial data but do not bound later forcing.
- Bounded speed of each prime-orbit coordinate does not bound the derivative of the signed cumulative sum. At prime p its jump magnitude is p^(-1/2), and the preceding integer log interval is asymptotic to 1/p; the interval quotient grows like sqrt(p).
- A synthetic positive counting function floor(x+x^(3/4)) has the same leading asymptotic as x and temporal contraction of the normalized residual, but residual energy grows like exp(T/2).
- Complete finite Euler products and time-ordered sums have different truncations; exchanging their limits without justification is invalid.
- Time decay of a rescaled observable does not establish decay of fixed historical weights.
- A finite test cannot exclude arbitrarily late failure. Earlier numerical claims without executable logs are not used as evidence in this note.
- Lean compilation of conditional algebra does not prove existence of a suitable matching or establish its hypotheses. Inspect the formal statement and its axiom dependencies; avoid sorry, admit or assumed RH equivalents.

## 5. Surviving obligation
For the actual Möbius function, prove a global signed cancellation estimate independently of RH, or exhibit a genuine counterexample to RH. The artificial examples cannot be transferred to zeta without an independent mathematical bridge. Exact prime multiplication plus squarefree annihilation and mu(1)=1 uniquely determine mu; the artificial sign sequence deliberately does not preserve these laws. This limitation is essential.

Protocol: find the fastest way to lose, invert it and check again. Do not call an equivalent formulation a proof. Preserve counterexamples and their exact hypotheses. The next failure-first target is any argument claiming that multiplicativity forces sufficient exclusive matching or controls the Hall-type deficit at every temporal boundary. No such theorem is established here.

Related archive: [Almond](almond-compensation-2026-11-27.md), [Möbius temporal boundary](mobius-temporal-boundary-2026-11-27.md), [Lean source](../lean_verification/real_kernel/MobiusBoundary.lean).
