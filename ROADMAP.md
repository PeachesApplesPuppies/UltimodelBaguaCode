# Roadmap

This roadmap is intentionally conservative. The project should become more testable before it becomes more general.

## v0.6 — Measurement uncertainty

- Optional ± uncertainty on entered measurements.
- Distinguish exact disagreement from overlap within uncertainty.
- Preserve raw measurement, uncertainty, and comparison method in provenance.

## v0.7 — Temporal resonance

- Compute elapsed time between recognition events.
- Detect clustering and repeated intervals without inferring causation.
- Keep temporal similarity separate from structural similarity.

## v0.8 — Domain adapters

Define adapters that translate domain-native data into the existing relational grammar without rewriting the core engine.

Candidate adapters:

- music: frequency, interval, duration, phase, recurrence;
- language: tokens, dependency relations, clause structure, rhythm;
- narrative/game: state, action, alternatives, consequence, provenance;
- chemistry: species, stoichiometry, phase, rate, transition;
- physics: vectors, frequency, phase, angular momentum, orbital ratios.

## v0.9 — External mathematical verification

- Optional Wolfram-backed verification path.
- Keep local deterministic calculations and external verification visibly separate.

## v1.0 candidate — Provenance graph / Periodic Mycelium

- Represent observations, candidate rhymes, tests, failures, and relationship families as a graph.
- Store both preserved and non-preserved relations.
- No automatic promotion of a rhyme to a law.
