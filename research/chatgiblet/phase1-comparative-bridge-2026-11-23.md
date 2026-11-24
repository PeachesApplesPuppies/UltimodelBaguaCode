# ChatGiblet Phase I — comparative analytical bridge
2026-11-23. Research note; not an independent proof of RH, not a Lean-certified development, no novelty claim.

Sources: Alpöge's announcement https://alpo.ge/remark.pdf ; Waterloo working draft v2 (22 November) https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/zeta-paper_v2.pdf , sections I.1 and II.1; Yan Ru Pei's roadmap https://peabrane.github.io/post/riemann-hypothesis-lean-roadmap/ . Full credit for the arithmetic argument belongs to Alpöge and Claude. The Waterloo draft quotes its main inequality (M) from the formal development and does not prove it outright.

## Exact identity
Let E(x)=psi(x)-x and G(x)=sum_{n<=x} Lambda(n)(x/n-1)-x log x+(1+gamma)x. Partial summation gives G(x)=x integral_1^x E(u)/u^2 du +(1+gamma)x. Hence x G'(x)-G(x)=E(x) almost everywhere (or using right derivatives). For A(t)=exp(-t/2) G(exp t), B(t)=exp(-t/2) E(exp t), B=A'-A/2 almost everywhere. Bounded A does not imply bounded B: A=sin(exp(t/4)). Nor does a one-sided estimate bound |A|, nor do sparse windows bound a generic function globally.

## Windowed positive-energy criterion (conditional on classical oscillation theorem)
Define U_j=int_j^{j+1} exp(-t) max(G(exp t),0)^2 dt. Consider the property: for every eps>0 and arbitrarily large T, U_j<=exp(2 eps j) for every integer j whose unit interval is contained in [T,3T/2]. The arithmetic window bound in the Waterloo draft implies this with harmless constants or a smaller epsilon. Conversely, set H(x)=int_0^1 G(x exp u) du. Cauchy-Schwarz on at most two integer blocks shows H(exp t)<=C_eps exp((1/2+eps)t) for t in [T+1,3T/2-2]. Its Mellin transform equals (exp(s)-1)/s times the transform of G, minus an entire boundary term. This multiplier has no zeros in Re(s)>0; therefore the nontrivial poles of G in that half-plane survive, and H has no poles on the positive real axis. The windowed sign-change theorem of Kaczorowski and Pintz (as cited in Waterloo I.1) applies to H(x)-2 x^theta for theta>1/2+eps, if a pole exists to the right of theta. Its sign-change intervals [X^(1-alpha),X] fit strictly inside the above windows for, e.g., X=exp(1.4 T), alpha=0.2. Contradiction. Thus the windowed positive-energy property excludes all poles to the right of 1/2. Conversely the classical explicit formula for G under RH gives G=O(sqrt x), implying the property. This is an alternative criterion derived using classical machinery, not a replacement for the difficult arithmetic argument. The use of the sign-change theorem remains a cited input.

## Global original energy
Let Theta=sup Re(rho) over nontrivial zeros, V_j=int_j^{j+1} exp(-t)|E(exp t)|^2 dt. Standard truncated explicit formula gives E(x)=O(x^Theta log^2 x) (choose truncation height comparable to x at half-integers and extend; for Theta=1 Chebyshev suffices). Hence limsup V_j^(1/j)<=exp(2 Theta-1). Conversely if this inequality were strict, Cauchy-Schwarz on unit blocks would extend integral_1^infty E(x)x^(-s-1) dx holomorphically to a half-plane containing a zero with real part arbitrarily close to Theta. Its meromorphic identity -zeta'(s)/(s zeta(s))-1/(s-1) has a nonzero residue -m/rho at that zero, contradiction. Therefore limsup V_j^(1/j)=exp(2 Theta-1). A windowed arithmetic bound, via pole exclusion, forces Theta=1/2 and gives the original energy criterion, without assuming RH. This still uses an equivalent zero-exclusion step; no direct derivative-norm bound was obtained.

## Numerical replication
Python/NumPy, sieve through 2,000,000. The four G values were 1.7493152448, 3.6714618625, 11.0404360839, -12.2678007288 at x=10000,100000,1000000,2000000 respectively. Right derivative identity residual max 2.6e-9. Tests establish neither asymptotics nor proof correctness.

Reproduce:
```python
import numpy as np
N=2_000_000
prime=np.ones(N+1,dtype=bool); prime[:2]=False
for p in range(2,int(N**.5)+1):
    if prime[p]: prime[p*p::p]=False
lam=np.zeros(N+1)
for p in np.flatnonzero(prime):
    q=int(p)
    while q<=N:
        lam[q]=np.log(p); q*=int(p)
psi=np.cumsum(lam)
w=np.cumsum(lam[1:]/np.arange(1,N+1))
for x in [10000,100000,1000000,2000000]:
    G=x*w[x-1]-psi[x]-x*np.log(x)+(1+np.euler_gamma)*x
    dG=w[x-1]-np.log(x)+np.euler_gamma
    E=psi[x]-x
    print(x,G,x*dG-G-E)
```
## Status
Analytical identities and conditional reduction written out; numerical replication executed. Lean compilation not performed (no Lean toolchain available). Independent mathematical review and novelty search remain necessary. Do not describe this as a new proof of RH.
