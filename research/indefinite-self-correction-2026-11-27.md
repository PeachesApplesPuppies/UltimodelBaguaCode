# The Principle of Indefinite Self-Correction
2026-11-27

## Original statement
"Problem doesn't equal no problem, but no problem equals problem."

The author describes a process where failures may be discovered late, repairs may introduce new failures, and the history of revisions must be retained. The conjecture is that relative failure frequency decreases as the system improves, by analogy with prime density.

## Interpretation and scope
The second equality is operational, not literal Boolean equality: a failure calls for diagnosis and repair; an absence of detected failure calls for scrutiny of the test and its scope. A proved invariant on a specified domain does not need to be doubted indefinitely within that domain; new questions concern its assumptions, applicability or extensions.

## Proposition 1 — Zero residual is not zero underlying magnitude
Let R=a+b and D=|a|+|b|. The triangle inequality gives |R|<=D, not the converse. Take a=1, b=-1. Then R=0 and D=2. Thus R=0 does not imply D=0. This is an exact instance of cancellation in the existing compensation budget. It demonstrates loss of information in the projection (a,b) -> a+b; it does not imply that every cancellation is an error.

## Proposition 2 — Finite clean observation does not exclude later failure
For any natural number N, define bad(n) iff n=N. For every n<N, bad(n) is false, while bad(N) is true. Therefore unrestricted finite clean observations cannot entail a universally clean sequence. A proof based on extra structural assumptions may establish correctness; finite testing alone does not.

## Proposition 3 — Preserve provenance by construction
Let H_0=[s_0] and H_(k+1)=H_k ++ [s_(k+1)] for state s_k. By induction H_k is a prefix of H_j whenever j>=k, and every recorded earlier state can be recovered by its index. This preserves recorded revision order, provided the log is retained losslessly. It does not recover unrecorded information, and is not a guarantee that arbitrary implementations preserve history.

## Failure-first transition rule
At step k record the model, test, outcome, scope, and change. A detected failure motivates diagnosis and a proposed correction; a clean result motivates checking the limits of the test or seeking a distinct falsification target. Rerun prior relevant tests after changes, and distinguish repeated known failures from newly introduced ones. A new correction is not presumed sound. This defines an ongoing protocol, not a theorem that all problems can be detected or solved.

## Attack against convergence
Even diminishing relative failure frequency does not imply diminishing absolute failure count or weighted failure debt. Let failure indices be n=k^2, k>=1. Through N there are floor(sqrt(N)) failures, so density tends to zero while the count diverges. The earlier YanRiemann anti-proof gives a stronger weighted example: exceptional indices 4 floor(k^(3/2))+2 have vanishing density yet produce a signed correction of order N^(1/6). Prime density is another example of a vanishing relative frequency, but no mapping from prime indices to actual model failures has been established.

If testing is to measure convergence, specify a reproducible distribution of tasks and a fixed or calibrated severity metric. Track failures per test, their severity, unresolved debt, detection delay and regressions. Changing the task population can change the observed rate without actual improvement.

## Status
Established: cancellation hides component information; finite clean testing alone does not exclude later failure; an intact append-only record preserves recorded order. Proposed: indefinite detectability and repairability, decreasing failure rate, or convergence of the correction process. None follows from these elementary propositions. No claim of an RH proof or of unlimited automatic repair.

Related: [Almond compensation](almond-compensation-2026-11-27.md), [YanRiemann anti-proof](yanriemann-anti-proof-2026-11-27.md), [Lean source](../lean_verification/real_kernel/MobiusBoundary.lean).

Protocol: find the fastest way to lose, invert it, check again; retain the evidence.
