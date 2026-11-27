# Möbius temporal boundary — 2026-11-27

Status: analytical reduction, not a proof of RH. No numerical results are asserted here without reproducible logs.

Let X = exp(T), R(T) = sum_{n<=X} mu(n)/sqrt(n), and R_p(T) be the same sum restricted to p not dividing n, for a fixed prime p. Extend both by zero for T<0. Put h=log(p), a=1/sqrt(p).

By unique factorization, mu(pn)=-mu(n) if p does not divide n, and zero otherwise. Thus R(T)=R_p(T)-a R_p(T-h). Define U_p(T)=R_p(T)-R_p(T-h), the unmatched signed weight over X/p<n<=X, p not dividing n. Then R(T)=(1-a)R_p(T-h)+U_p(T).

Absolute bound: |U_p(T)| <= 2(1-p^(-1/2)) exp(T/2)+O_p(exp(-T/2)) as T tends to infinity, by integral comparison. This does not establish subexponential growth.

Boundary equivalence: if for every epsilon>0, U_p(T)=O_{p,epsilon}(exp(epsilon T)), telescoping over j=0,...,floor(T/h) bounds R_p(T) by a constant times exp(epsilon T)/(1-p^(-epsilon)); hence R has subexponential growth. Conversely R_p(T)=sum_{j=0}^{floor(T/h)} a^j R(T-jh), so subexponential growth of R implies that of R_p and U_p. Partial summation in both directions relates the bound on R to M(X)=O_epsilon(X^(1/2+epsilon)), the classical RH-equivalent Mertens bound. Thus the signed boundary estimate for even one fixed prime is equivalent to RH, not a proof of it.

For p=2 the open sum contains only odd integers in (X/2,X]. Recursively pairing by 3,5,... is a candidate investigation, not a demonstrated bound. Complete finite prime families factor as product(1-1/sqrt(p)); time truncation prevents passing from that product to the ordinary ordered sum without justification.

Earlier context: the normalized Chebyshev residual A(t)=exp(-t/2)(psi(exp(t))-exp(t)) has exact temporal contraction with arithmetic forcing; this alone does not bound the forcing. The Möbius delay kernel has transfer function 1/zeta(1/2+z) initially for Re(z)>1/2. Absence of positive-real-part poles of its meromorphic continuation is equivalent to RH by symmetry. Absolute kernel summability fails. The energy and boundary approaches remain conditional.

Lean scope: the starter checks elementary finite algebra/telescoping only. The real-valued weighted arithmetic identity, analytic RH equivalence, and signed boundary bound are not formalized by those checks. No RH certification is claimed.
