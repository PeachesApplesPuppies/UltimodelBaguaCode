# The Great Io — extended 3D stress test

Research date: 2026-11-25. Numerical research, not an analytical solution to the general three-body problem.

## Archived results
Ten cases selected from the 500-case spatial dataset: five largest normalized trajectory disagreements, then five closest sampled separations among the remaining cases. Both time directions, normalized horizon 50 each. All ten completed; only cases 74 and 362 passed both comparison tolerances (position 1e-7, velocity 1e-6). Eight failed. Case 39 had maximum position disagreement 0.0035158146028697 and velocity disagreement 0.1542752915857476. Exact unity closure by construction and small energy/angular momentum drift do not guarantee accurate trajectories.

## Reproduce
Use Python on Linux/macOS or WSL (the script uses Unix SIGALRM timeouts).
```sh
python -m pip install numpy scipy numba
python great_io_3d_stress.py
```
Run in this directory. The script reads great_io_3d_0_500.csv and overwrites great_io_3d_stress_results.csv incrementally; preserve a copy of the archived results before rerunning. Ctrl+C interrupts the parent; active worker processes may take time to stop (per-solver alarms are configured). A partial output is not a completed test.

CSV files were recovered from the conversation's parsed file contents, with the added row-index column removed. Script archived from recovered text; its opening docstring names an earlier command, so use the command above. No fresh numerical rerun was performed during publication. The selection is deliberately biased toward hard cases. Results are finite-time numerical comparisons, not certified error bounds. Exact collisions and infinite-time behavior remain untested.
