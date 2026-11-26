# Ultimodel’ Calculator / Grapher

> Experimental local mathematical instrument, three-bit token engine, and Recognition / Resonance journal.

**Status:** research prototype. The repository separates ordinary mathematics, BCE/Ultimodel’ interface vocabulary, and hypotheses. See [`docs/RESEARCH_STATUS.md`](docs/RESEARCH_STATUS.md).

**Quick start:** Python 3.10+; standard library only. Run `python app.py --open` and execute the regression suite with `python -m unittest discover -s tests -v`.

Repository guides: [`ROADMAP.md`](ROADMAP.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md) · [`CHANGELOG.md`](CHANGELOG.md) · [`LICENSE-NOTICE.md`](LICENSE-NOTICE.md)

---

A local mathematical instrument for comparing two real quantities, changing the reference, and explicitly promoting results into named inputs for another comparison.

## Function calculator
On Windows extract the ZIP, open the project folder and double-click Start_Windows.cmd (Python 3.10+ and the Windows Python launcher required). The browser opens the calculator. From a terminal, use python app.py --open.

Type f(x)=x^2, y=sin(x), or a bare expression such as exp(-t^2) in A. The graph uses t as its horizontal axis and maps your declared function argument to it. A bare x in the input box also maps to t when neither a parameter nor a saved variable named x is supplied and the expression does not use t. The name in f(x)=... labels the input; use Define § or Promote to § to store a reusable name. Named variables can be used directly or called at another input (for example R1(t+2)). Parameters accept assignments such as k=3. Use explicit multiplication between names; 2x and 2(x+1) are accepted.

Choose Function, Derivative or Integral under Mathematical rule. Lens A or B selects the source. The slider multiplies the selected function, derivative or integral by p. Pairwise rules and Flow work as before. The integral graph shows accumulation from the lower bound to each graph coordinate. The probe gives a definite integral with that coordinate as upper bound, including reversed bounds. An elementary antiderivative with + C is shown for recognized cases. The promoted integral uses the chosen lower bound, fixing that constant. For example, integrate f(x)=x^2 from 0 to 2 for 8/3. At p=−1 the result is −8/3. Promote it and differentiate to recover the oriented integrand.

Numerical integration uses adaptive Simpson quadrature on real intervals that pass a conservative continuity check. Poles, unverified intervals, excessive work, and nested numerical integration can prevent a result. Rapid oscillations can defeat finite sampling. The parser supports arithmetic, named scalar functions and common elementary functions including inverse trig, hyperbolic trig and log10. Arbitrary Python, implicit equations, and general symbolic integration are outside this version. Expand the three-value finite-difference table to compare consecutive changes and the local return gap; one gap of zero is one observation.

## Start in VS Code
1. Extract the zip and open the **ultimodel-calculator** folder in VS Code.
2. In its terminal run `python app.py` (Windows: `py -3 app.py`; macOS/Linux: `python3 app.py`). Requires Python 3.10+. No package installation, network connection or editor extension is required.
3. Open **http://127.0.0.1:8765/** in your browser. Stop with Ctrl+C. Use `--port 8766` if the default port is busy. An optional VS Code Python debugger launch configuration is included.
4. Run the tests with `python -m unittest discover -s tests -v`.

## Polarity shifter
Choose Linear flow, then move the polarity slider. The graph shows p times the signed delta. At t=1 the outputs for p=+1, 0 and −1 are +1, 0 and −1. Intermediate values interpolate linearly. A zero output at p=0 can occur even when A differs from B. Flip Lens to reverse reference order. In shifted-delta mode the slider and Lens are independent, and undefined input expressions keep their domain boundaries.

Pick another mathematical rule to calculate and graph its result. Use the triangle presets to compare 3 arrivals with 1 second, or 3 vertices with 6 centimeters. Units in these examples are descriptive. To reuse a result, choose a name, click Promote to § and then Use as A or Use as B. Promotions of shifted delta capture the slider value.

## First experiment
Choose **Reduction**. A=3 and B=6. Lens A shows raw 3:6, normalized 1:2, reversal of that same pair 2:1, quotient A/B=0.5, delta +3 and magnitude 3. Flip to Lens B. The raw pair is 6:3, delta −3, and normalizing the newly centered pair gives 1:0.5. The source A and B stay in their original slots.

Choose **Linear flow**, Lens A. At t=1, the inputs t and 2*t give delta 1; the derivative of delta is 1 at every t. Enter R1 as the name, choose Signed delta under Mathematical rule and click **Promote to §**. Type R1 as A and 5 as B; at t=2 the new delta is 3. To use a named C instead, define C with expression 5 first. A promotion captures both expressions, the selected quantity and orientation. Editing the original input fields cannot alter the stored definition. t and free numeric parameters remain live.

## Notation and arithmetic
- § (Eternal Variable) is the project name for a value, expression, or named result. ◯ (Eternal Function) labels explicit operations. ❂ / ⊛ (Eternal Polarity) labels complementary orientations. These names belong to the interface.
- For reference u and other v, delta = v−u; reverse delta = u−v; magnitude = abs(v−u). The raw pair is u:v. Its quotient u/v and its reverse v/u are separately displayed.
- Normalizing the first term produces **1:X**, X=v/u, provided u≠0. Reversing the *same scale* gives X:1. Renormalizing from the opposite Lens produces 1:u/v if v≠0. Their denominators differ.
- At 1:0 the quotient 1/0 is undefined. First-term normalization remains valid as 1:0. At 0:0 neither normalized scalar exists. At −1:1, normalization gives 1:−1: retain the raw pair to know which source carried the negative sign.
- Flow’ is the **rate of change of delta**, d(v−u)/dt. Ordinary derivatives and standard mathematical notation remain visible. The relation panel also compares A and B (=, <, >) at the probe. Equality compares computed real values as stored in floating point.
- Recurring structures, the value of flattening views, and “Infinite Pie” are experimental questions. Explicit promotion is the only recursive operation in this release.

## Inputs, graphs and records
Enter plain numbers, t, other named Variables’, or free symbols such as k. Use k=2 in the parameter field to evaluate expressions containing k. Python’s existing expression parser supplies precedence. Use explicit multiplication, powers ** or ^, and parentheses. Functions: sin, cos, tan, exp, log, sqrt, abs, inv, ratio and delta. Angles are radians. pi and e are constants. Vector, complex, implicit-equation and general equation-solving modes are outside v0.1.

Use the time range and probe separately. The plot uses 241 samples per selected curve; all share one scale. Toggle large ratios off to see smaller curves. Each segment is screened using an interval enclosure, including source-expression domains. A potential pole splits the line even when it falls between samples or has even multiplicity. The plot can omit valid portions when the enclosure is inconclusive. Break counts are sampling diagnostics rather than an exhaustive list of singularities.

Select **Export calculation JSON** to download source expressions, UTC timestamp, parameters, probe, range, Lens, oriented results, formula text, derived values, statuses, registry, and graph break counts. Invalid input can also be exported as an error record. Only named definitions persist in local browser storage for this origin. Use a fresh port for a fresh registry.

## Limits and implementation decisions
The default stack is Python with its built-in AST parser, a small rule table for scalar arithmetic and symbolic differentiation, a loopback HTTP server, and browser SVG. This avoids external dependencies unavailable in the build environment. It is not a general computer-algebra system. Expressions are never passed to eval. Multiplication by zero or algebraic cancellation does not silently fill holes in a promoted source expression. Domain checks for derivatives can be conservative at exceptional points such as zeros of abs or sqrt; removable cases may require separate analysis. There is no general symbolic simplification, inverse solving, one-sided limit evaluation, or arbitrary precision. Floating-point bounds and dense oscillations limit graphical resolution. Controls cap expression size and registry depth. Leave the server on localhost.

Modules: app.py serves the interface; core/mathcore.py parses, evaluates, differentiates and bounds real expressions; core/instrument.py applies Lens rules, manages the registry and builds export records; ui/index.html contains the controls and graph. All arithmetic is ordinary mathematics. No speculative physical, psychological or universal law is assumed.


## Saved periodic-table data
Open Periodic table under Select inputs. Choose an element and property, then use it in A or B. In a formula, use e.g. 2*element(H,Ar)+element(O,Ar) for the relative molecular mass of water using abridged central values. Z is a proton count. Ar and its published uncertainty are dimensionless. The calculator handles uncertainties as separate scalars; it does not propagate them automatically. Missing weights are null and unavailable for arithmetic. All 118 records ship offline in data/elements.json, from CIAAW’s Abridged Standard Atomic Weights 2024 (https://ciaaw.org/abridged-atomic-weights.htm).

## Zero Spin
Click Run 1 : 1 : 0 for three observed readings. The panel compares A→B, B→C and C→A. Lens B reverses the cycle. A zero reading has neutral sign; its local rate is undetermined without a function. Switch to Use source functions to treat numeric literals as constant functions, or enter t, -t and 0 at probe 0 to see rates +1, -1 and 0. The panel examines the original inputs, independently of the polarity slider. All three steps and the evidence mode are included in Export calculation JSON.

### Color / contrast code

Enter independent F (frequency) and M (magnitude) expressions. The calculator evaluates both at the probe and exports each expression, value and status alongside the experimental BCE quantity C = F × M. Empty inputs stay unentered. FM-2 assigns hue from polarity times the signed product and shade from absolute magnitude. Its arrow points along (F,M) and becomes a dot at the origin. The exported visual record includes HEX, marker ink, luminance contrast ratio, and angle in degrees. Nearby inputs can look alike at screen resolution.
 With both color inputs blank, the interface supplies the A and B expressions. Select a property and target A or B before clicking an element. Missing property values are disabled.

## Token engine v0.1

Run the existing launcher, then choose **Token engine** at the top of the calculator, or open http://127.0.0.1:8765/tokens. Python 3.10+ is sufficient. In pair mode enter two three-bit strings and an elapsed time. In Sequence mode enter one state per line. Select Manual to enter one timestamp per line in the same order. Set a clock unit or type a custom name.

The editable Lens’ gives each L/F/M bit two labels. The neutral Lens’ displays literal bits. Calculate to inspect the history, inverses, transition table and five time plots. Export JSON for the full active history or CSV for one row per interval. When opening CSV in Excel, import the five token columns as text to preserve leading zeroes.

See ENGINEERING_REPORT.md for verification, conventions and limits.

In **Compare two states**, choose **Append target to sequence** to record the pair. A fresh history starts with the source at time zero. Otherwise the current state must match the last sequence entry. The button adds one target at the previous timestamp plus the pair's elapsed time, then opens Sequence so you can inspect or export the result. Switch back to Compare to enter the next target. History lives in the open page until exported.

## Recognition / Resonance Engine v0.1

From the calculator choose **Recognition** (or open /recognition on the local server). Write what you noticed and what it reminded you of, then press **RECOGNITION WAVE · Save**. The original account receives a UTC timestamp and stable ID immediately. Reopen a wave to add an investigation, an observed stage or a challenge. Use **Save investigation** to keep edits before switching events. Review revisions remain available in the timeline. Export the selected event as JSON or CSV.

For the rectangle experiment enter 10:6.18 in A and 5:3.09 in B. Select Pair and save to compare exact aspects. Choose Phi and enter 0.01 for a tolerance of 0.01 percent before testing A against φ. Press **TRY TO BREAK THIS** to record the pair stress tests. To test the bad example, start a second wave with A = 10:4 and the same Phi tolerance.

The local journal persists across restarts in ~/.bce-ultimodel/recognitions.sqlite3. Set BCE_RECOGNITION_DB to choose another file. See RECOGNITION_REPORT.md for the comparison methods and their limitations.

## Public research archive — YanRiemann Requiem / Golden Bang (2026-11-26)

Start with the [research archive index](research/ARCHIVE_INDEX.md), the [metaphor ledger](research/yanriemann-metaphor-ledger.md), and [Metaphors as a research instrument](research/metaphors-and-method.md). Includes historical drafts, executable numerical experiments, recorded results, negative controls, and open proof obligations. Human-directed, AI-assisted research; not an independently audited proof of the Riemann hypothesis.
