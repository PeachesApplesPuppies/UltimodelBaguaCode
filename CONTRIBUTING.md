# Contributing to Ultimodel’ Calculator / Grapher

This repository is an experimental mathematical instrument. Contributions should preserve a strict separation between:

1. ordinary mathematics and software behavior;
2. BCE/Ultimodel’ interface vocabulary;
3. proposed interpretations or hypotheses.

## Before changing code

Run the full regression suite:

```bash
python -m unittest discover -s tests -v
```

A change should not silently alter existing arithmetic, token semantics, provenance, or stored recognition history.

## Preferred contribution types

- reproducible bugs;
- additional tests and counterexamples;
- clearer domain/singularity handling;
- deterministic comparison methods;
- import/export and provenance improvements;
- narrowly scoped experimental features with explicit assumptions.

## Hypothesis contributions

A proposed relationship should state:

- the objects being compared;
- the Lens’ or reference frame;
- the exact transformation or normalization used;
- what is preserved;
- what is discarded;
- what would falsify the proposal.

Do not promote a resemblance to a scientific law merely because it is numerically or visually suggestive.

## Pull requests

Include:

- a concise description of the change;
- tests added or changed;
- assumptions introduced;
- known failure cases;
- whether the change affects stored data or exports.
