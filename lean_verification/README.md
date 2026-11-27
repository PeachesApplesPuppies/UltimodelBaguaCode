# BCE Lean Verification Department

## Windows: one click

Extract the ZIP (or download the repository ZIP), then double-click **START_LEAN.cmd** at the repository root. It uses your existing default WSL Linux installation. Internet is required for the first Lean install. It installs the pinned Lean 4.35.0 toolchain with the official elan installer if needed, without replacing your existing default toolchain. If curl or Python 3 is missing, the launcher prints the Ubuntu install command. Ctrl+C stops an active check. Keep the extracted folder on your PC. Each run writes a fresh report folder under lean_verification/results; existing reports are not overwritten.

## Cloud: no local install

Open the repository Actions tab, select **Lean verification department**, and click **Run workflow**. The workflow also runs after changes to the starter or compressor on push. Download the lean-verification-reports artifact from the completed run. A successful result means the finite 15-state modular theorem, its negative controls, and the small proof-compression fixture passed. It does not prove RH.

The local and cloud launchers run the same script. The expected fixture minimum is three supporting lemmas within the explicit tactic search space. The formal theorem statement stays fixed. Python regression tests precede the Lean checks. Full RH compilation, Mathlib installation, and comparison against the external compact proof are intentionally outside this starter. No actual Lean verification is claimed until a successful run is recorded.

References: https://lean-lang.org/install/manual/ and https://lean-lang.org/doc/reference/latest/releases/v4.35.0/
