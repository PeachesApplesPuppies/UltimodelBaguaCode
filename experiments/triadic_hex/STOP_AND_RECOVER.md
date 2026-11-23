# AutoDepth Live v0.4 — STOP, BREAK, and recover

**Read this before running a long operation.** Ultimodel AutoDepth Live is experimental software. It aims to stop work safely and restore declared output files to their last verified closed state. **BREAK is not a guaranteed zero-latency kill switch**, and no recovery system can restore an unavailable or corrupt only copy.

This guide applies to **PR #7 / branch `feature/live-closed-state-v0.4`** of [UltimodelBaguaCode](https://github.com/PeachesApplesPuppies/UltimodelBaguaCode/pull/7). It is not necessarily present in `main` yet.

## Setup — one time

From the repository root:

```bash
cd experiments/triadic_hex
python -m pip install -r requirements.txt
python build_zipapp.py
```

You now have `AutoDepthLive_v0.4.pyz` in this directory. The zipapp needs Python 3.10+ and installed dependencies (Brotli/NumPy). Playback with `play` also requires system FFplay.

If you used GitHub **Code → Download ZIP**, select the **`feature/live-closed-state-v0.4` branch first**. You may instead run the equivalent `.py` files directly; those examples are at the bottom of this guide.

## A. Immediate close while streaming or playing

Terminal A:

```bash
python AutoDepthLive_v0.4.pyz play movie.ut3 --port 8766
```

Use `serve` instead of `play` to supply a local `http://127.0.0.1:8766/video.mp4` stream without starting FFplay.

**Option 1 — simplest:** press **Ctrl+C** in Terminal A. The first signal requests cooperative cancellation. If the process is unresponsive, a second Ctrl+C forces Python interruption; this is less graceful.

**Option 2 — out-of-band STOP:** keep Terminal A visible long enough to copy its printed session token. In Terminal B run:

```bash
python AutoDepthLive_v0.4.pyz break --port 8766 --token PASTE_THE_PRINTED_TOKEN
```

- Use the **actual port and fresh session token** from Terminal A. Using `--port 0` when starting chooses an available port automatically; copy the one printed.
- `BREAK acknowledged` means the stop request was accepted. Wait until the stream/player exits before starting recovery or replacing files.
- `play` supervises its FFplay child and requests that playback close. `serve` only controls the stream service; separately launched media players are not owned by the stream.
- The control server binds to local loopback and requires the token. Do not post the token publicly or expose the service beyond your own machine.

## B. Immediate close for compression / arbitrary programs

The bundled encoder's normal Ctrl+C handler requests cancellation and protects its declared output:

```bash
python AutoDepthLive_v0.4.pyz encode input.mp4 output.ut3 --max-depth 4
```

For an **independent BREAK control that can forcibly terminate an unresponsive child**, launch the job under the supervisor:

```bash
# Terminal A: supervise the built-in encoder
python AutoDepthLive_v0.4.pyz runner run --port 8777 -- python AutoDepthLive_v0.4.pyz encode input.mp4 output.ut3 --max-depth 4
```

```bash
# Terminal B: stop this supervisor (use its newly printed token)
python AutoDepthLive_v0.4.pyz runner break --port 8777 --token PASTE_THE_PRINTED_TOKEN
```

**Do not add `--protect output.ut3` to this specific built-in-encoder example.** The encoder already owns a closed-state checkpoint/lock for its output; a second wrapper checkpoint for the same output can block waiting on that lock. If the runner forcibly kills the child, manually recover the built-in checkpoint before trusting the output.

For a different, external writer that does **not** use the built-in checkpoint system, explicitly name every output to protect:

```bash
python AutoDepthLive_v0.4.pyz runner run --port 8777 --protect result.dat -- python your_writer.py result.dat
```

Then stop it using the same `runner break` command above with the new session's token.

- Only specified `--protect` output paths receive rollback protection; repeat the flag to protect more than one file.
- The supervisor first requests termination, then escalates when the child does not respond. It does **not** stop unrelated applications.
- On Windows, stopping a child's own grandchildren is not yet fully validated. If a writer survives, stop it **before** restoring files.
- If you do not control or trust the program you are executing, do not treat the supervisor as a sandbox.

## C. Recover from an unexpected close

1. **Confirm the old writer and its children are stopped.** Do not restore while anything is still writing to the output.
2. Inspect the journal:

   ```bash
   python AutoDepthLive_v0.4.pyz checkpoint status --output output.ut3
   ```

3. Restore a prior incomplete `pending` transaction:

   ```bash
   python AutoDepthLive_v0.4.pyz checkpoint recover --output output.ut3
   ```

4. Run archive verification (when the file is a complete `.ut3` archive):

   ```bash
   python AutoDepthLive_v0.4.pyz verify output.ut3
   ```

- Recovery uses a SHA-256-verified pre-run snapshot. If no pending job exists, `recover` reports that and does not rewrite a completed state.
- If the protected output was nonexistent before the job, failed-job rollback **removes** that unfinished output rather than inventing earlier contents.
- If you used `--state-dir PATH` with the supervisor, use the **same** `--state-dir PATH` with `checkpoint status/recover`. For multiple protected outputs, repeat `--output` for each.
- Keep the nearby hidden `.ultimodel-closed-<id>/` folder and its `blobs/` intact; backups can require storage equal to another full copy of an output. Do not delete them until recovery is no longer needed.
- If a backup is missing or fails validation, recovery **refuses to overwrite** the current file. Do not assume that indicates successful recovery.
- Checkpoints preserve declared local output-file contents and some metadata, **not** active memory, network requests, other files, or external side effects. No software can guarantee recovery from every OS/power failure.

## D. No zipapp? Run source scripts instead

From `experiments/triadic_hex`:

```bash
python autodepth_live.py play movie.ut3 --port 8766
python autodepth_live.py break --port 8766 --token PASTE_THE_PRINTED_TOKEN

python breakable_runner.py run --port 8777 --protect result.dat -- python your_writer.py result.dat
python breakable_runner.py break --port 8777 --token PASTE_THE_PRINTED_TOKEN

python closed_state.py status --output result.dat
python closed_state.py recover --output result.dat
```

For more examples, technical restrictions, and regression tests, return to the [README](README.md).

## If BREAK is not responding

- Confirm the correct port/token and that the process is still active.
- Use Ctrl+C in the original terminal where possible.
- If the process is hung beyond the supervisor's control, stop it using your operating system's process controls, then **check that no writer remains** before running `checkpoint recover`.
- The supervisor uses POSIX process groups where supported; its Windows process-tree cleanup needs further validation. There is no hard real-time termination guarantee.
