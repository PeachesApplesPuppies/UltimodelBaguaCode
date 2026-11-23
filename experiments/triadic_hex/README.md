# Ultimodel AutoDepth Live v0.4 — BREAK + last-known-good recovery

This experimental source package extends the existing Triadic HEX (`.ut3`) v1
format without changing its on-disk specification. `autodepth_hex.py` selects
per-branch tree depth; `autodepth_live.py` provides a seekable virtual file and
loopback HTTP byte ranges; `live_player.py` owns and stops a child player;
`breakable_runner.py` can supervise any **child command it launches** and
terminate its process group if it is not responding.

> **EMERGENCY STOP / IMMEDIATE CLOSE:** Press **Ctrl+C** in the running terminal. For a stream or supervised task, use the **separate-terminal, token-protected BREAK command** printed at startup. BREAK is a stop request, not a hard real-time guarantee. See [STOP_AND_RECOVER.md](STOP_AND_RECOVER.md) for copy-and-paste commands, fallback steps, and restoring the last known-good state.

## Install

Python 3.10+ required. System FFmpeg/FFplay is optional (needed only for
playback). On a desktop, extract the ZIP and run:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s . -p "test*.py" -v
```

Alternatively the `AutoDepthLive_v0.4.pyz` is a **compressed zipapp** of the
Python program source, not the third-party dependency binaries. Install the
requirements first; this zipapp uses the installed Python interpreter as its
uncompressed bootstrap. Nothing here self-bootstraps without an interpreter.

## Stream a compressed video without full extraction

```bash
python AutoDepthLive_v0.4.pyz serve video.ut3 --port 8766
```

Then open `http://127.0.0.1:8766/video.mp4` in a media player that supports
HTTP range requests. Alternatively, to launch and supervise FFplay:

```bash
python AutoDepthLive_v0.4.pyz play video.ut3 --port 8766
```

The stream prints a session-specific stop token:

```text
BREAK command: python autodepth_live.py break --port 8766 --token <token>
```

To stop from another terminal with the **zipapp**:

```bash
python AutoDepthLive_v0.4.pyz break --port 8766 --token YOUR_PRINTED_TOKEN
```

Or **Ctrl+C** in the running terminal. A second Ctrl+C force-interrupts the
cooperative signal handler. The stop endpoint binds locally, checks the
session token, declines further data reads and releases the decoded cache.

## Last-known-good closed-state checkpoints (v0.4)

**For every bundled Triadic/AutoDepth encode/decode operation**, before any
output changes, the program copies its prior output into a separate,
content-hashed local snapshot and atomically writes a `pending` journal.

- Success: fsync output and record a `closed` journal with a new output hash.
- BREAK, error, or nonzero exit: stop the child first, then restore the prior
  snapshot into place, leaving a `restored` journal.
- Abrupt process death: a `pending` journal remains, and the **next invocation**
  with that output auto-restores before it starts. A manual recovery command is
  also provided. Do not restore while an orphaned writer still runs.
- A previously committed file whose bytes change outside the managed runner
  causes an error, rather than being silently treated as safe baseline.
- For an output that did not exist before the run, recovery removes the
  uncommitted output file.
- Snapshots preserve exact bytes, POSIX permission mode, and modification time;
  no hardlinks are used, because the child might modify the output in place.

Run bundled encode/decode directly (automatic protection):

```bash
python AutoDepthLive_v0.4.pyz encode video.mp4 video.ut3 --max-depth 4
python AutoDepthLive_v0.4.pyz decode video.ut3 restored.mp4
```

For **arbitrary external commands**, tell the supervisor which files may be
changed. Only the declared output paths receive rollback protection:

```bash
python AutoDepthLive_v0.4.pyz runner run --port 8777 \
  --protect output.ut3 -- python some_writer.py output.ut3
```

A multi-output command may repeat `--protect`. An optional stable `--state-dir`
controls where backups live. It must be supplied again to recover that job.

Inspect or recover a prior interrupted operation, without starting a new one:

```bash
python AutoDepthLive_v0.4.pyz checkpoint status --output output.ut3
python AutoDepthLive_v0.4.pyz checkpoint recover --output output.ut3
```

Backups are stored in a hidden `.ultimodel-closed-<id>/` directory adjacent to
the protected output. They consume disk space; plan for a complete extra copy
of the previous output. Existing snapshots are retained for the latest job,
while older blob generations may accumulate until an explicit cleanup policy
is implemented. Preserve this directory for crash recovery. **Do not delete
its blobs unless you have verified that you no longer need to recover.**

### Important recovery limits

This safeguards only declared local output files, not arbitrary process memory,
remote databases, undeclared paths or a multi-file atomic transaction. Programs
that ignore the supervisor and write elsewhere are not protected. The supervisor
can be forcibly killed, potentially leaving a child process still running;
stop that child before manually recovering. Power-loss durability depends on
filesystem guarantees. Corrupt/missing snapshots cause a *safe refusal*, not
fabricated recovery. No method can recover data whose only surviving copy has
been destroyed. Read-only streaming does not write or require file checkpoints.

## Break any subprocess launched through our supervisor

For compression and arbitrary child commands, use an independent control
process. This remains responsive even when the child is blocked inside a
native compression library and cannot check a cooperative cancellation flag.

Terminal A:

```bash
python AutoDepthLive_v0.4.pyz runner run --port 8777 -- \
  python autodepth_hex.py encode video.mp4 output.ut3 --max-depth 4
```

Terminal B (using the printed token):

```bash
python AutoDepthLive_v0.4.pyz runner break --port 8777 --token YOUR_PRINTED_TOKEN
```

The supervisor requests termination, then escalates to forcible termination
when necessary. On POSIX platforms it creates a separate process group and
terminates that group. On Windows it stops the direct child; complete cleanup
of all grandchildren requires additional OS-specific job-object support.

**Safety limits:** Neither application code nor operating systems can guarantee
physically instantaneous termination under every imaginable failure. Tests
measure observed stop latency, not a real-time bound. A force-killed process
may leave temporary scratch files, though output archive creation uses an
atomic replace and existing completed archives are not overwritten until a
new one is fully constructed. Do not use the supervisor as a sandbox for
untrusted executable code. The package intentionally does not launch or
terminate unrelated user processes.

## Compressed source and actual video experiments

- The 33,028,976-byte video was stored in an AutoDepth `.ut3` archive.
- FFprobe/FFmpeg successfully read the stream through HTTP ranges; no entire
  MP4 was extracted to disk during the playback check.
- In the BREAK test using FFmpeg (`-re`) on the real `.ut3` archive, 89 HTTP
  range requests were observed before BREAK. The run ended ~0.176 s after the
  BREAK request, and the archive's SHA-256 was unchanged.
- 26/26 live and BREAK regression tests passed; 36/36 earlier fixed-depth and
  AutoDepth tests passed when run separately.
- The test archive, original MP4, and decoded media are **not** distributed in
  the source package.

## Differences from prior releases

- Cooperative `BreakController` checkpoints in index scans, random reads,
  full verification, encoding, decoding, planner recursion and archive writes.
- Transactional file commits preserved; interrupted operations do not commit
  an incomplete final archive.
- Authorized `POST /__break` stop control and Ctrl+C/SIGTERM handling.
- FFplay child-process lifecycle supervised; stop ends playback and server.
- Independent process-group supervisor for stubborn child processes.

These changes do not alter the existing `.ut3` file format and are intended to
be reviewed separately from the earlier Triadic HEX and AutoDepth PRs.

## First-time download guide: run, stop, and recover

**Important: v0.4 currently lives on the `feature/live-closed-state-v0.4` branch / [PR #7](https://github.com/PeachesApplesPuppies/UltimodelBaguaCode/pull/7), not necessarily the default `main` branch.** To download this specific version using Git:

```bash
git clone --branch feature/live-closed-state-v0.4 https://github.com/PeachesApplesPuppies/UltimodelBaguaCode.git
cd UltimodelBaguaCode/experiments/triadic_hex
python -m pip install -r requirements.txt
python build_zipapp.py
```

Alternatively, select that branch on GitHub, choose **Code → Download ZIP**, extract it, then open a terminal in `experiments/triadic_hex`. Use `python` or your platform's equivalent (for example, `py` on Windows). Building the `.pyz` requires Python; the archive does **not** include Python, Brotli, or NumPy.

**Basic archive lifecycle** (the encode and decode commands automatically create closed-state checkpoints for their output files):

```bash
python AutoDepthLive_v0.4.pyz plan input.mp4 --max-depth 4
python AutoDepthLive_v0.4.pyz encode input.mp4 input.ut3 --max-depth 4
python AutoDepthLive_v0.4.pyz verify input.ut3
python AutoDepthLive_v0.4.pyz decode input.ut3 recovered.mp4
```

**Playback without extracting the full MP4:**

```bash
python AutoDepthLive_v0.4.pyz play input.ut3 --port 8766
```

`play` requires FFplay on your PATH. For an external HTTP-range-capable player, use `serve` instead and open the printed `http://127.0.0.1:PORT/video.mp4` URL. If port 8766 is occupied, use `--port 0` and copy the actual port printed on startup.

### STOP NOW: three controls

1. **Terminal A still accessible?** Press **Ctrl+C** in that same terminal. The first signal requests cooperative cancellation; a second signal forces Python interruption. Allow rollback/recovery to finish if possible.
2. **Streaming or playback running, but Terminal A is blocked?** Open Terminal B and run the following with the *actual* port and session token printed by Terminal A:

   ```bash
   python AutoDepthLive_v0.4.pyz break --port 8766 --token YOUR_PRINTED_TOKEN
   ```

   This requests that the HTTP stream stop and, for `play`, that the supervised FFplay process close. An acknowledgement means the **request was accepted**, not proof every process has already exited.
3. **A supervised compressor or other child command is stuck?** Start external work under the independent runner, then send its own BREAK from Terminal B:

   ```bash
   # Terminal A — example external writer; only declared outputs can be rolled back
   python AutoDepthLive_v0.4.pyz runner run --port 8777 --protect output.bin -- python writer.py output.bin

   # Terminal B — use the token printed by this runner session
   python AutoDepthLive_v0.4.pyz runner break --port 8777 --token YOUR_PRINTED_TOKEN
   ```

   The runner first requests termination and then escalates to force termination when necessary. **On Windows, cleanup of a child program's own descendants has not been fully validated.**

**Do not wrap the bundled `encode` or `decode` command in a second `runner --protect` for the *same output*:** the bundled command already uses the closed-state lock/checkpoint, and double-protecting the same file can block on that lock. If you want an externally stoppable native compression job, run the built-in encoder as the runner's child **without** an extra `--protect`; the built-in checkpoint will recover on its next invocation after a forced kill:

```bash
python AutoDepthLive_v0.4.pyz runner run --port 8777 -- python AutoDepthLive_v0.4.pyz encode input.mp4 output.ut3 --max-depth 4
```

### After an unexpected stop

First **confirm the previous writer/child has exited**. Never restore a file while a surviving writer can overwrite it again. Then:

```bash
python AutoDepthLive_v0.4.pyz checkpoint status --output output.ut3
python AutoDepthLive_v0.4.pyz checkpoint recover --output output.ut3
```

Recovery rolls back only a **pending** incomplete operation, using the verified pre-run snapshot. A previously completed `closed` state is not undone by the `recover` command. When a protected output did not exist before the interrupted operation, rollback removes that unfinished output. If you used `runner --state-dir SOME_DIRECTORY`, supply the **same** `--state-dir` when inspecting/recovering and repeat `--output` for each originally protected output.

Do not delete the adjacent `.ultimodel-closed-<id>/` directory or its blobs while you might need recovery. The checkpoint system protects declared local output files—not other files, external services, program RAM, or physical power failures. A corrupt/missing snapshot results in a refusal rather than an invented restoration. Read-only streaming does not modify the archive and therefore does not require a checkpoint.

For source-script equivalents, troubleshooting, and recovery caveats, see **[STOP_AND_RECOVER.md](STOP_AND_RECOVER.md)**.
