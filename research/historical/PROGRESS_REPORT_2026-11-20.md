<!-- Historical working draft recovered from the research library on 2026-11-26; text extraction, not a byte-exact original. No new verification or authorship assertion. -->

# BCE / Ultimodel’ — Progress report and advancement guide
**Date:** 20 November 2026  
**Focus:** Herzog's Stone, BaguaCode’, four-emulator matrix, Roman alphabet + mathematical-expression bridge, provenance address book

## Executive status

The earlier project reached a genuine software-checkpoint: an integrated native BaguaCode 26-instruction virtual machine, two independently implemented execution runtimes (Python and JavaScript), finite symmetry/ratio experiments, and limited Python/C# semantics comparison. The archived README reports previously run test suites. This report does **not** imply those older source archives were rerun today.

This delivery adds **BCE Symbolic Bridge v0.1**: a small Python-only reversible source encoding and exact arithmetic interpreter, with a content-addressable record index and automated tests. It is an add-on candidate, **not** a replacement of the canonical VM.

## Historical components and evidence

| Component | Status from historical artifacts | Limits |
|---|---|---|
| Early calculator and three-bit L/F/M Token Engine | Implemented with automated Python tests | Separate from the canonical 26-opcode VM |
| Native BaguaCode v1 26-instruction VM | Python and independently written browser JS reportedly passed trace parity | Archive was not fully rerun in this session |
| H/R/C/W four-operation experiment | All 4! = 24 operation orders represented | Finite declared model, not a general physical law |
| Three-bit signed-coordinate symmetry | 48 invertible transformations tested | Transformations of model representations only |
| OCEAN lexical graph | Constructed graph/cycle relationships | Closure is a mathematical artifact of selected edge potentials |
| Four emulator matrix | Python-host Python-semantics and C#-semantics cells executed | Both C#-host cells still require .NET SDK execution |
| Python/C# general-language frontends | Not implemented | Python and C# language semantics include types, errors, effects and runtime details |
| Historical A1Z26 lexical bridge | Python `four_words.py` recovered from Library | Experimental word encoding; not Bagua-native opcode grammar |
| This release: Symbolic Bridge v0.1 | Python tests executed locally in this turn | No Bagua-native lowering, C#, or JavaScript integration yet |

**Archived run commands** in original integrated package: `python run.py --all`, `python run.py --test`, and `python verify_js_parity.py`. C# archive commands: `dotnet run --project csharp/HerzogFourByFive.csproj -- --output-dir results --radius 2`, then `python compare.py --output-dir results --radius 2` in the four-directions baseline folder. The archive documents that its .NET stage was not run.

## New bridge architecture

```
Roman text and mathematical source
        │
        ▼
lossless ASCII token stream (LETTER, DIGIT, SYMBOL, WHITESPACE)
        │                      │
        │                       └──> exact text reconstruction
        ▼
restricted arithmetic parser → JSON AST
        │
        ▼
exact-rational Python reference evaluator → ordered execution trace
        │
        ▼
content address + parent links + source SHA-256 → finite address book
        │
        ▼
[FUTURE] documented native BaguaCode v1 compiler/adapter
        │
        ▼
[FUTURE] independent Python/JS/C# parity and mismatch ledger
```

### Roman alphabet convention

For a letter `L` take its uppercase one-based position `n∈[1,26]`, then `a,b=divmod(n,8)`. Each component fits in a three-bit register. Record case independently. `E=5 → (0,5) → 000 101`; `Z=26 → (3,2) → 011 010`. This is injective for the 26 uppercase letters; merely taking `n mod 8` is lossy. The separate `LETTER` namespace prevents instruction/number collisions.

### Math syntax

Supported: integer literals, alphabetic variables, `+ - * / ^ ( )`, unary signs, assignment `NAME=expression`. Exact rational values are represented by `Fraction` objects and emitted in `n/d` notation. An undefined ratio raises an error, never an invented infinity. No arbitrary code execution.

Example `P=(A-B)/(A+B)`, A=6, B=3, evaluates to exactly `1/3` and records each operation. Exact reconstruction from the pair's polarity alone is impossible without retaining magnitude: `M=A+B`, `p=(A-B)/M`, `A=M(1+p)/2`, `B=M(1-p)/2`, provided `M≠0`.

## The address-book hypothesis

A finite rule set may describe an open-ended generative process. The address book stores **versioned objects, parent references, code/parameter digests, derivations and counterexamples**, permitting selective replay and deduplication. It does not establish a lossless compression of arbitrary data into fewer bits or imply an actual spacetime wormhole. A fixed program can generate arbitrarily many outputs over unbounded time and memory; at any finite point, only finitely many outputs have been materialized.

## Advancement priorities and acceptance gates

| Priority | Deliverable | Pass / fail gate |
|---|---|---|
| P0 | Preserve canonical archives and version numbers | Archived Bagua VM, original tests, and proof debts retained unchanged |
| P1 | Install and run .NET 10 SDK for existing C# implementations | Both C# host cells execute; output/type/error parity report records mismatches rather than hiding them |
| P2 | Freeze exact Bagua source grammar and observable trace schema | Versioned grammar, value tags, opcode names, error taxonomy, test vector registry |
| P3 | Integrate the new lexical/mathematical bridge | Token stream round-trips exactly; well-typed AST lowers to native Bagua operations or reports unsupported constructs |
| P4 | Build independent C# evaluator/parser for bridge | Same chosen test vectors run under .NET with exact rational output and meaningful error parity |
| P5 | Add source-language subset frontends | Explicitly supported Python/C# arithmetic subset agrees with its native runtime, preserving integer vs floating division |
| P6 | Make address book navigable | Hash-based lookup, child/parent graph, immutable snapshot export, replay from declared seeds and environment |
| P7 | Validate against fresh holdout inputs | Randomized/property-based tests, cross-language disagreements, intentionally lossy encodings, undefined operations documented |

**Practical stack:** Python 3.10+ (stdlib-only for the new bridge), existing offline browser/JS Bagua VM, optional Node.js for parity, .NET 10 SDK for C#, local JSON output now; SQLite later if the address book outgrows simple files. Retain original `Herzog_Stone_Full_Emulator` distribution separately.

## Next concrete action

Execute the new bridge tests, and separately confirm that the original full emulator archives are intact. Then run the pending .NET verification **before adding more speculative language features**. After the baseline is reproducible, implement a documented AST → Bagua-native instruction lowering pass for `+,-,*,/` with exact rational values. One passing example is not enough: require known counterexamples and full roundtrip records.

## What is and is not proved

- **Established in this new bridge:** exact reversible letter/ASCII-token encoding for its declared character set; exact rational evaluation for its small grammar; deterministic finite parent-linked records; local Python regression tests.
- **Historical results reported, not rerun here:** integrated Bagua virtual computer, Python↔JS parity, 24 operation-order tests, 48 symmetry calculations.
- **Unverified:** C# independent execution, general-language equivalence, arbitrary infinite compression, and any universal physical resonance law.

*Every description is a model, not the thing itself.*
