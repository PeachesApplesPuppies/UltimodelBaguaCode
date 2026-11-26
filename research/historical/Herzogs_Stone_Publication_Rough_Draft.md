<!-- Historical working draft recovered from the research library on 2026-11-26; text extraction, not a byte-exact original. No new verification or authorship assertion. -->

# Herzog’s Phenomenal Stone
## Reversible Representations, Relational Invariants, and a Three-Observer Verification Protocol

**A human-directed, AI-assisted working paper | Research draft v1.0 | 8 November 2026**  
**Author:** [Author name to confirm]  
**Research program:** BCE / Ultimodel’ / BaguaCode’ / Centerpoint Engine  
**Status:** Mathematical formulation and reported computational checks; independent human-observer testing not yet performed.

> “Every description is a model, not the thing itself.”

### Abstract

This paper presents a framework for distinguishing exact mathematical reversibility, observer-dependent representation, and empirical claims about the world. Its organizing method, which the author calls *full-circle transmutation*, takes an observation through definition, forward transformation, reverse reconstruction, attempted falsification, and refinement. The term “transmutation” refers here to the transformation and recovery of representations, not to physical conversion of chemical elements. Three formal components anchor the approach: reconstruction of two values from their normalized signed polarity and retained magnitude; identification of invariants under a declared family of common transformations; and separation of recurring phase from complete dynamical-state recurrence. Prior AI-assisted computational project reports describe finite-state exhaustions, exact counterexamples, and restricted Newtonian three-body integrations, including 50 reported forward and 50 reverse integrations with maximum baseline-state recovery error of approximately 8.12 × 10⁻¹³ in that numerical setup. These results are computational checks, not new physical measurements or proofs of universal cosmological propositions. To test whether prior knowledge alters human measurement or interpretation, we propose a preregistered three-condition protocol involving experienced, uninformed, and explicitly informed observers. The contribution is a transparent, falsifiable methodology that preserves both successful derivations and failed overextensions.

**Keywords:** reversibility; invariants; observer effects; AI-assisted research; preregistration; polarity; phase; numerical dynamics; falsification.

### 1. Introduction: What “full circle” means

The guiding problem is simple: when a relationship survives a transformation, is that survival a property of the underlying system, of a chosen representation, or of the observer’s knowledge? These alternatives can look identical if definitions, transformations, and measurements are allowed to shift after results are observed. They become distinguishable when each is specified beforehand.

The author describes themself as a **“full-circle transmuter.”** In this paper, that is a self-description of a method rather than a claim of exceptional authority or literal alchemy. A candidate statement is transformed from verbal description into a defined mathematical object, tested in the forward direction, reconstructed in reverse where possible, challenged with counterexamples, and then revised. A completed circle is not a guarantee that the original claim survives. A documented failure is also an outcome.

This approach grew within the BCE / Ultimodel’ / BaguaCode’ research program, which explores ratios, signed polarity, recursive processes, symbolic encodings, and comparisons between computational implementations. The broad philosophical propositions attached to that program—including “reality is monopolarity expressed over time” and the Centerpoint Engine as an observer-relative origin—remain interpretations or research questions, not established physics. The present manuscript makes a narrower, testable contribution.

### 2. Definitions and exact reconstruction

Let A and B be real quantities with nonzero total magnitude M = A + B. Define normalized signed polarity

**p = (A − B)/(A + B), with M ≠ 0.**

Then the original ordered pair is recovered exactly from *both* p and M:

**A = M(1 + p)/2;    B = M(1 − p)/2.**

Substitution verifies both equalities. This is an algebraic identity under its declared domain assumptions, not a discovery about every physical pair. The polarity p alone cannot recover the absolute magnitude: multiplying both inputs by the same nonzero factor leaves p unchanged whenever the normalized expression is defined. Conversely, M alone cannot recover their difference.

More generally, let F map an input x to a transformed representation y. If F loses distinctions, an ordinary inverse on y cannot recover every x. Reconstruction may nevertheless be possible with retained provenance h:

**R(F(x), h(x)) = x.**

The additional record is part of the information boundary. This distinction matters for phase wrapping, ratios, digit encodings, normalization, and reduced dynamical coordinates. Preserving a reverse path by retaining lost information is not equivalent to proving an information-losing map was injective.

### 3. Relational invariants and observer transformations

An invariant is defined relative to a specified transformation family G. For a state space S, a quantity I is invariant under G if

**I(Tx) = I(x) for every x in S and every T in G.**

A feature may survive a common change of observer coordinates without surviving arbitrary independent changes by two observers. For three-bit states x and y, their Hamming distance d_H(x,y) is preserved when the *same* cube automorphism is applied to both. It need not be preserved when unrelated transformations are applied separately.

The BCE computational archive reports an exhaustive analysis of finite transformations and a 79-test combined Python regression suite, including rank bounds, four-state maps, and cube transformations. Those reports support defined, finite mathematical claims within their tested domains. They do not imply that an invariant exists under every possible transformation. Indeed, allowing all constant maps on a state space leaves only globally constant invariants. The allowed transformations therefore cannot be omitted from a universality claim.

This suggests a disciplined formulation of the Centerpoint Engine: rather than asserting a physically privileged point, define an observer convention, a transformation family, and a candidate invariant; then ask which features are coordinate-dependent and which are relationally stable.

### 4. Phase, winding, and recurrence

For an angular coordinate, the wrapped phase θ = Θ mod 2π does not retain the complete unwrapped angle Θ. Reconstructing Θ requires an integer winding index k or an equivalent history:

**Θ = θ + 2πk.**

Thus identical observed phase need not imply identical dynamical state. Consider the specified discrete spiral

**zₙ₊₁ = c + (i/2)(zₙ − c).**

Its exact solution is zₙ = c + (i/2)ⁿ(z₀ − c). The radius decreases by 1/2 at every step while phase repeats after four steps; the entire state does not return after four steps unless it is already at the fixed point. The attracting point c is supplied in the model definition. This example rigorously separates phase recurrence, state recurrence, and convergence to a chosen center.

The mathematical lesson is not that all of reality is a spiral. It is that repeated appearances can conceal changes in amplitude, scale, orientation, or retained history. Those omitted quantities must be audited before recurrence is asserted.

### 5. Computational evidence and an explicit counterexample

An archived BCE report titled *Herzog’s Stone — Reverse Each Function While Preserving Each Value (v1)* records five Fibonacci scale choices, five positive pentatonic scale factors, and two angular schedules, generating 50 forward Newtonian three-body numerical integrations. The report describes 50 reverse integrations from the evolved full phase-space endpoints, with maximum reported baseline recovery error of **8.120171202108395 × 10⁻¹³** and maximum scaled-final-state comparison error of about **5.45 × 10⁻¹³**. These values describe finite-precision residuals for selected collision-free numerical cases. They are not zero-error proofs, independent laboratory measurements, or a general closed-form solution of the three-body problem. Reproduction from archived code, dependencies, initial conditions, and outputs is required before journal submission.

A separate anti-proof illustrates why an elegant ratio description cannot automatically determine dynamics. Put three equal masses at identical equilateral positions qᵢ and define velocities

**vᵢ(±) = v₀[±ρqᵢ + σJqᵢ],**

where J rotates a planar vector by 90 degrees, ρ = 3/√34, and σ = 5/√34 in the reported dimensionless example. The two sets of states share initial positions, all 1:1:1 pairwise separation ratios, total energy, and signed angular momentum. Yet their radial velocities have opposite signs; the initial separation derivatives differ. Their future distance histories therefore differ. The anti-proof defeats the proposition that normalized distance ratios, even combined with those conserved scalars, uniquely fix a Newtonian trajectory. It does not defeat deterministic evolution from complete initial phase-space data.

This counterexample is a constructive success of the full-circle method: the earlier claim becomes more precise, rather than being protected from failure.

### 6. The full-circle transmutation protocol

The proposed research cycle has seven accountable operations:

1. **Observation:** record an event or pattern with timestamp, instrument or source, and raw form.
2. **Definition:** specify symbols, domains, units, equivalence relations, and what counts as a complete state.
3. **Expression:** implement a forward map, equation, or explicit measurement procedure.
4. **Reversal:** determine whether the original state is recoverable, and enumerate necessary side information.
5. **Challenge:** seek counterexamples, alternative models, null explanations, and known limits.
6. **Independent comparison:** compare results across separately specified implementations or observers without silently sharing intermediate answers.
7. **Refinement:** preserve the original claim, revision history, failed cases, numerical residuals, and final bounded conclusion.

A “full circle” is completed only when the inputs, transformations, losses, and failure conditions are all visible to a reviewer. This does not require every hypothesis to be confirmed.

### 7. Proposed three-observer verification experiment

A central unresolved question is whether knowing the proposed mathematical relationship changes a person’s measurement or interpretation. We propose three observer conditions, each following one standardized protocol:

**A — Experienced:** participants who previously performed the measurement.  
**B — Uninformed:** participants new to the hypothesis who receive neutral operational instructions.  
**C — Explicitly informed:** participants new to the procedure who receive the hypothesis and predicted pattern before testing.

The word “measurement” must refer to one fixed observable and apparatus before recruitment. As a tractable first study, participants can be given a fixed set of encoded-state reconstruction tasks with objective ground-truth answers. This study would assess interpretation and expectation effects in human performance—not prove that a corresponding pattern is a law of nature. Any later physical-world study requires its own independently measurable quantity, units, instrument calibration, and competing predictions.

For the reconstruction pilot, preregister the item set, the correct answers, allowable operations, scoring rules, exclusions, and primary endpoint (for example, proportion of exact reconstructions). Secondary outcomes may include response time, confidence, and error types. Assign hypothesis-naive participants randomly to B or C; use A as an experienced comparison group, recognizing that experience cannot be randomized retrospectively. In a pilot, estimate feasibility and variance before determining a powered sample size. Analyze the preregistered contrast between B and C separately from the confounded A comparisons. No participant condition may receive hidden corrective hints during scoring. The scorer should be blinded to condition when feasible.

Possible outcomes are informative rather than self-validating. Equivalent results across conditions could indicate robustness to supplied knowledge. Differences between B and C could indicate instruction or expectation effects. Experienced participants outperforming both other groups could reflect practice rather than a deeper physical correspondence. A positive result under a predeclared rule does not, by itself, establish causality or metaphysical unity.

The study has **not yet been conducted**. It is a protocol, not a completed experimental finding. It should be preregistered before outcome data are seen.

### 8. Artificial-intelligence use, data provenance, and authorship

**AI-use disclosure.** The author used OpenAI ChatGPT as an explicitly acknowledged research assistant in the development of this work. AI assistance contributed to dialogue-based exploration, mathematical formalization, proposed computational implementations, generation or interpretation of simulated-data reports, counterexample construction, organization of research records, methodological criticism, and drafting of the present manuscript. The reported numerical values in Section 5 are transcribed from AI-assisted project reports; this manuscript does not represent them as fresh, independently rerun results or human-collected physical observations. The author supplied research directions, hypotheses, questions, revisions, and editorial decisions. Before external submission, a human investigator must inspect the referenced code and source outputs, independently rerun the computations, check citations and permissions, and verify all mathematical statements.

**Statement of intent.** The author expressly states that the purpose of documenting AI use is to make the process auditable, not to persuade readers that unperformed measurements occurred. In the author’s words: **“I’m not trying to fool anyone.”** This is a statement of intent, not a substitute for the records and independent checks by which that intent can be evaluated. No claim is made that an AI system can independently know or certify a person’s intentions.

**Accountability.** The human author retains responsibility for accuracy, originality, interpretation, disclosure, and correction. ChatGPT is acknowledged as a tool, not listed as a coauthor. The AI-assisted nature of the research should also appear in the submission cover letter and, where required, the journal’s methods or acknowledgments section. This treatment is consistent with current ICMJE and Nature Portfolio expectations on transparency and human accountability [3,4].

**Reproducibility requirement.** The release package should include executable code, dependency versions, raw numerical outputs, seeds if applicable, test fixtures, instrument specifications for future human measurements, time-stamped revision history, preregistration, and a concise record of which reasoning steps were AI-assisted. Any missing element must be identified as missing, not silently reconstructed.

### 9. Limits and falsification conditions

Four boundaries govern the conclusions. First, an exact identity remains exact only within its mathematical domain; for example, polarity reconstruction requires M ≠ 0. Second, numerical accuracy in selected trajectories is evidence about an implementation and setup, not a universal theorem. Third, a representation-invariant pattern is not necessarily a physical invariant. Fourth, observer agreement may reflect common training, shared instructions, or analytic choices.

The framework therefore invites its own disproof: find a pair for which a claimed inverse fails despite all recorded side information; identify a transformation within the declared family that changes the asserted invariant; reproduce a computational residual outside the reported tolerance; or show that preregistered observer predictions fail under blinded scoring. A failed test narrows or rejects the specified claim and must remain in the published record.

The project does not currently establish a new law of gravity, physical conversion of lead to gold, a universal center of time, or a general solution to the gravitational three-body problem. Such larger claims require independent governing equations, calibrated physical observables, and evidence capable of distinguishing them from established alternatives.

### 10. Conclusion

The full-circle method proposes that a mathematical description earns strength not by escaping criticism, but by returning to its inputs, identifying what was lost, and surviving independent attempts to break it. Reversibility with retained provenance, relational invariants under specified transformations, and separation of phase from full-state recurrence are exact and useful concepts. Archived computational checks suggest concrete routes for further independent reproduction. The next decisive step is not an additional analogy: it is an openly disclosed, preregistered measurement with inexperienced and informed participants, a defined observable, and an analysis plan set in advance.

The author’s phrase **“full-circle transmuter”** names this commitment to repeated transformation, reversal, correction, and disclosure. The result sought is not a perfect story. It is a model whose successful and failed predictions can be checked by people who were never asked to believe it.

### Acknowledgments

The author acknowledges the use of OpenAI ChatGPT in ideation, mathematical and computational assistance, critical review, synthesis of project reports, and manuscript drafting. The author also acknowledges the value of independent critics and future blinded participants, whose disagreement is essential to evaluating the proposed claims. No external participants are represented as having contributed data to this draft.

### References and research materials

1. BCE research archive (7–8 November 2026). *Herzog’s Stone — Reverse Each Function While Preserving Each Value (v1).* Internal computational report; raw output and code verification pending for publication.
2. BCE research archive (7–8 November 2026). *Ultimodel’ v0.8 — Nine-Point (Inverse Enneagram) Anti-Proof*; and *The Infinite Local Spiral and the Centerpoint Engine.* Internal reports; claims limited to the documented mathematical and computational settings.
3. International Committee of Medical Journal Editors (ICMJE). *Recommendations: Use of AI by Authors* (accessed 8 November 2026). https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html
4. Nature Portfolio. *Editorial Policies: Artificial Intelligence (AI)* (accessed 8 November 2026). https://www.nature.com/nature-portfolio/editorial-policies/ai
5. Center for Open Science / OSF Support. *Welcome to Registrations & Preregistrations!* (accessed 8 November 2026). https://help.osf.io/article/330-welcome-to-registrations

### Submission readiness note (remove before publication)

This is a publication-oriented **rough draft**, not a peer-reviewed or submission-verified article. Before sending it to a journal or posting as a research preprint: replace the author placeholder; verify every cited computational result from source files; archive reproducible code and outputs; obtain independent mathematical review; decide whether to publish the mathematical paper and the human-observer protocol separately; preregister the human study; and adapt the AI-use statement to the receiving venue’s policy. No three-observer measurement has yet been run.
