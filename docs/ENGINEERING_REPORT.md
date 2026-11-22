# Ultimodel Token Engine v0.1 · engineering report

## Delivered

The local calculator opens the new engine at /tokens. The engine has eight three-bit states in L/F/M order. A separate transition type holds the XOR mask. The Python core distinguishes states, masks, structural ratios, Hamming magnitudes, rates, Lens’ configurations and timestamps.

Pair and sequence modes use the same evaluator. Each interval has source and target times, raw tokens and their complements, the transition mask, Hamming distance, changed-to-unchanged ratio, changed fraction and Flow’ per chosen time unit. The Lens’ editor provides separate names for each quality and each of its bit values. Five time plots track the raw bits and the two interval measurements. JSON exports the active clock, Lens’, state history and intervals. CSV exports the intervals and embeds the full Lens’ metadata in each row.

## Verification

32 automated tests passed (24 existing and 8 new), including exhaustive checks of all 64 ordered state pairs. The example history yields masks 001, 100 and 010. For 000 → 111, the rate falls from 3 to 1 when elapsed time increases from one to three units. Tests cover inversion twice, type misuse, invalid bits, invalid clocks, a one-state history, Lens’ relabeling, CSV round-trip and live HTTP routes for the page, validation and exports. Browser JavaScript passed syntax checking. Browser rendering and a native Windows launch were not manually verified.

## Conventions and edge cases

- Time starts at zero for an automatic clock. A manual clock may start anywhere, with strictly increasing finite times. Every timestamp marks an observation. The interval row uses its source time and also records its target time.
- State plots hold the last observed bit until the next timestamp. The distance and rate appear across the interval they summarize. This convention does not locate a change within the interval.
- Hamming distance counts differing endpoint bits. Intervening switches that cancel are unobservable. Token Flow’ means state-change rate for this discrete grammar. The calculator’s continuous derivative of delta is a separate operation.
- The M bit is a state coordinate. Transition magnitude is a count from 0 to 3. The ratio 3:0 records three changed and zero unchanged. The normalized fraction uses three as its denominator.
- Custom unit names label the time axis. The user supplies time values in that unit. The engine accepts up to 2,000 observations per history and uses finite floating-point timestamps. If the clock loses precision enough to repeat a timestamp or overflow an interval or rate, the calculation reports a validation error.
- A single observation has no intervals. Its JSON retains the state and Lens’. Its CSV contains headers only. Spreadsheet importers sometimes strip leading zeros; import token columns as text.
- Each export captures the currently entered comparison or sequence. The calculator lets the user download it explicitly.

## Append target to sequence

Pair mode now extends the active sequence after validation. Prior observations retain their timestamps, including irregular intervals. A repeated target records a later observation with zero endpoint change. The initial sample sequence is shown as a placeholder so a fresh history begins with the user's first pair.
