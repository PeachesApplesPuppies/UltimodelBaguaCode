# Cancer and temporal feedback — exploratory functional model

This is a literature-based classification, not a genomic sequence analysis, clinical model, experimental cancer result, or proof of RH. No patient data used.

## Gene panel
| Gene | Regulatory role | Example cancer-associated alteration |
|---|---|---|
| KRAS | growth drive | activation |
| BRAF | growth drive | activation |
| EGFR | growth drive | activation |
| MYC | growth drive | activation |
| TP53 | checkpoint/death | impaired regulation |
| RB1 | checkpoint | loss |
| APC | growth restraint | loss |
| PTEN | growth restraint | loss |
| BRCA1 | repair | loss |
| BRCA2 | repair | loss |
| MLH1 | repair | loss |
| MSH2 | repair | loss |
| BCL2 | death restraint | increased activity |
| TERT | replicative maintenance | reactivation |

Genes can have multiple roles; alterations are variant- and tissue-dependent. Normal versions are not intrinsically cancerous. Cancer can involve growth activation, loss of restraints, impaired repair, survival, replicative maintenance, immune evasion and tissue invasion. A single alteration is not necessarily sufficient.

## Model
A scalar illustrative recurrence x_(t+1)=a*x_t+b_t distinguishes feedback retention from forcing, but cannot capture actual cancer heterogeneity. For a toy constant coefficient, x_t=x_0*a^t: a<1 decays, a=1 persists, a>1 grows. This is a mathematical example, not fitted gene effect sizes. Repair defects are not equivalent to increased proliferation; they can change the distribution of future alterations. No Möbius law is known for genes.

## Arithmetic research continuation
For square-free primorial P and gcd(m,P)=1, family members are md for d|P. Define H_P(u)=sum_{d|P,log d<=u} mu(d)/sqrt(d). For coprime square-free A,B, H_AB(u)=sum_{d|B}mu(d)/sqrt(d)*H_A(u-log d). Local completion occurs when u-log d>=log A. Full completion deficit Delta=log(mP)-T. Missing signed family weight is mu(mP)/sqrt(mP) times sum_{q|P,q<exp(Delta)} mu(q)*sqrt(q). Absolute bound O(exp(-T/2+Delta)); summing families with 0<Delta<=D gives O(exp(-T/2+L+2D)), L=T-log P. For largest primorial <= exp(T), L=O(log T) by PNT and Bertrand, so D=eta*T with eta<1/4 yields vanishing near-completion missing weight. This is not a bound on all current family contributions.

Completed families together tend to zero for maximal primorial depth: p_r~T, product_{p<=p_r}(1-p^(-1/2))=exp(-(2+o(1))*sqrt(T)/log(T)), while restricted base sum is at most 2 exp(L/2). However primes q in (X/2,X] outside selected blocks have no arrived nontrivial partners. Their absolute weight is asymptotic to (2-sqrt(2))*sqrt(X)/log(X). Cross-family cancellation remains essential and unproved. No RH claim. These are analytical derivations, not new Lean-checked results. Earlier unlogged numerical claims are not treated as verified data.

## Sources
https://www.cancer.gov/about-cancer/understanding/what-is-cancer
https://www.cancer.gov/about-cancer/causes-prevention/genetics
https://pmc.ncbi.nlm.nih.gov/articles/PMC4526158/
https://pmc.ncbi.nlm.nih.gov/articles/PMC5916814/
https://pmc.ncbi.nlm.nih.gov/articles/PMC6008968/
https://www.merckmanuals.com/professional/oncology/overview-of-cancer/cellular-and-molecular-basis-of-cancer
