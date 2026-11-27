# The Almond — cumulative compensation model

Status: conditional mathematical reduction, not a proof of RH.

Let K(n)=mu(n)/sqrt(n), R(T)=sum_{n<=exp(T)}K(n). Initial unity K(1)=1 is the initial unit impulse of the distributional derivative of the causal cumulative response. For nonzero terms t=log(n), magnitude a=exp(-t/2); new coprime prime multiplication reverses polarity and delays by log(p), multiplying magnitude by p^(-1/2).

For opposite signs at t and t+d, d>=0, write a=exp(-t/2), b=a exp(-d/2). Define almond overlap as d<=a+b. Then pair cost a-b=a(1-exp(-d/2))<=ad/2<=a^2=1/n. The last inequality uses b<=a. For disjoint pairs in [2,X], summing yields at most 1+log X by harmonic comparison. Let D(T) be absolute unmatched mass excluding n=1. Triangle inequality gives |R(T)|<=1+Cpaired(T)+D(T)<=2+T+D(T), conditional on an exclusive pairing satisfying overlap. The same argument can use any subset of such pairs with all other terms counted in D.

If D(T)=O_epsilon(exp(epsilon T)) for all epsilon>0, this implies the classical RH-equivalent Mertens estimate by partial summation. Existence of a sufficiently comprehensive pairing and the unmatched bound are unproved. Local overlap alone does not imply injective matching: many positive terms may share the same negative neighbor. A normalized decaying cost is not the original fixed kernel weight; replacing it changes the observable. No conservation of additive unity follows from reciprocal weighting alone.

Initial exceptions to |R(log X)-1|<=log X at X=2,3,5 are explicit: negative terms at these primes precede first positive squarefree composite 6, while 4 contributes zero. This only explains those small cases, not all future behavior. Earlier numerical claims without saved executable logs are not treated as verified here.

Lean additions: almond_pair_cost proves the algebraic bound conditional on the overlap and decay inequalities; compensation_budget proves triangle-inequality bookkeeping; decay_step_budget proves a generic contraction-plus-forcing estimate. They do not certify an arithmetic matching, the exponential inequality itself, a debt bound, or RH.

Research protocol: find the fastest way to lose, invert and test again; require explicit hypotheses, adversarial examples, reproducible computations and proof checks without sorry or unjustified axioms. Physical light speed and geometric overlap are analogies unless an arithmetic inequality is derived independently.
