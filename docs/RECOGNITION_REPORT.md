# Recognition / Resonance Engine v0.1

## Implemented

Two text fields create a RecognitionEvent. SQLite stores the literal capture, its UUID, UTC creation time and a monotonically ordered journal entry. The capture records a first sensation and association together when both are entered together. An optional later stage records when the stage was entered. A remembered earlier onset can be described in the note. Entry timestamps should be interpreted as recording times.

Each investigation stores a new RhymeCandidate snapshot containing the source descriptions, both ratio orientations, original measurements, exact normalized ratios, method, evidence, objections, classification and Lens’ information. B can reference another saved observation by ID. All manual geometry categories are available. Files and media can be named as references. The operator enters measurements. Review history, including changes of mind, is immutable through the interface. JSON contains the entire event journal. CSV has one timestamped row per entry with a JSON payload to retain nested evidence and verbatim multiline text.

TRY TO BREAK THIS records tests and answers alongside the review. Broken Rhymes indexes failed primary tests and explicit broken classifications, including failures later superseded. Relationships enter families only by user action. A family stores separate source IDs and review numbers. Each member requires a passed primary test, a supported classification, a shared named invariant, both domains, prompt, active capture Lens’ and discarded information. The observer supplies the independence rationale. Source objects retain their identities.

## Similarity and tests

| Component | Implemented comparison |
|---|---|
| Ratio | Exact normalized aspect equality, scored 0 or 1. Normalize oriented a:b to 1:(b/a) using rational arithmetic. Separately, the measured quotient for φ is a/b. |
| Topological | Case-insensitive equality of manually declared topology labels (0 or 1). Geometry labels alone supply no proof of topology. |
| Operator | Case-insensitive equality of supplied operator names (0 or 1). |
| Sequence | Equal positions divided by the longer sequence length. Each sequence also stores symbol counts, repeated overlapping motifs of length 2 and 3, reversal and palindrome symmetry. The smallest lag matching every overlap, with at least two periods' worth of data, is reported as a finite observed period. |
| Token | For supplied three-bit tokens with the same declared Lens’, 1 minus Hamming distance divided by three. Raw XOR, changed ratio and optional changes per elapsed tick reuse the token engine. |
| Semantic | Unassessed. The observer can describe a semantic resemblance and record supporting or conflicting evidence. |

Missing evidence produces an unassessed component. The program does not aggregate the six components. The Pair primary test concerns aspect equality. The Phi primary test concerns A's oriented quotient at the relative tolerance explicitly entered by the user. A passing test supports only that stated comparison. Users can record a partial or broken judgment separately from the automatic result. “Validated Under Current Model” requires a passing primary comparison and entered evidence.

The stress test compares the pair under simultaneous inversion, inversion of B alone and independent positive scaling by 2 and 3. Its chance baseline enumerates all 100 ordered integer pairs with terms 1–10, reporting the fraction that exactly matches A. This selected baseline is an illustration. It cannot estimate real-world coincidence rates without a sampling model appropriate to the observation.

## Required examples

| Measurements | Observed quotient | Absolute error from φ | Relative error (%) | At 0.01% tolerance |
|---|---:|---:|---:|---|
| 10 × 6.18 | 1.6181229773 | 0.0000889886 | 0.00549980 | Within tolerance |
| 5 × 3.09 | 1.6181229773 | 0.0000889886 | 0.00549980 | Within tolerance |
| 10 × 4 | 2.5 | 0.8819660113 | 54.5084972 | Broken golden-ratio rhyme |

The first two raw pairs have different absolute scales. Both normalize to 1:309/500. After reversal both normalize to 1:500/309. Inverting only one breaks the pair match. Reversing both preserves their mutual correspondence even though their inverted quotients are now near 1/φ.

## Subjective inputs and limits

Immediate sensation, salience, perceived similarity, chosen Lens’, declared topology, candidate invariant, confidence, source independence and assessment of counterevidence are human reports. Identical declared labels can describe different structures. Exact decimal-ratio comparison treats entered values as exact; it does not model instrument uncertainty. Finite recurrence cannot establish an infinite period. Unknown references, singular ratios and absent measurements stay distinguishable from failed tests. Earlier events cannot establish how often recognition was experienced but went unrecorded.

Only saved edits survive closing the browser. Concurrent stale reviews are rejected before any write. Retry with the same operation ID is idempotent. The journal is local to the user account that starts the calculator.

## Verification and next feature

The automated suite checks the two geometric examples, singularities, scale and Lens’ tests, a repeated but aperiodic sample, token comparisons, exact capture text, UTC journal ordering, append-only failures, CSV round-trip, concurrent edit guard, idempotence and family provenance. The existing calculator and token tests are included. The local HTTP capture, challenge, reopen and export workflow was checked separately. A native Windows launcher and visual browser interaction were not exercised.

Smallest useful next feature: add optional ± measurement uncertainty so the observer can distinguish rounding differences from a genuine failure of aspect-ratio agreement.
