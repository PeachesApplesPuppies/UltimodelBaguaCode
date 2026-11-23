# Ultimodel AutoDepth Live v0.4 — Closed-State Recovery

**2026-11-23.** Builds on Triadic HEX v0.1, AutoDepth v0.2, and AutoDepth Live / BREAK v0.3.

## Engineering goal

Preserve a **last-known-good closed state before a job that may alter persistent files**, so premature cancellation or a crash does not silently replace a completed archive with a partial output.

## Implemented

1. An independently controlled Python supervisor snapshots *declared output files* into content-addressed SHA-256 blobs before launching a child.
2. A durable JSON journal is atomically written with phase `pending`, filenames, whether each output existed, sizes and checksums. Snapshot data and journal are flushed using `fsync` where supported.
3. A graceful completion records phase `closed` and checksums of the committed outputs.
4. BREAK or a nonzero child exit terminates the child and restores the previous bytes; an absent-before-run file is removed.
5. On a new run after an unexpected termination, a `pending` journal is detected, the complete backups are verified before any changes, and outputs are restored before new work starts.
6. Recovered files retain bytes, POSIX permission mode and recorded modification time. The backup is a separate copy, not a hard link that an in-place write could corrupt.
7. The bundled Triadic/AutoDepth CLI and compressed zipapp automatically checkpoint their `encode` and `decode` outputs. For arbitrary programs, the `runner run --protect OUTPUT` option designates which files to safeguard.
8. Manually inspect or recover a pending state with `checkpoint status` and `checkpoint recover`.
9. A previously committed file changed outside the managed operation is rejected as a new baseline, rather than silently promoted to 'known good'.

## Results

- **85/85 tests passed** in a combined regression run across original fixed-depth, AutoDepth, live streaming, BREAK, and checkpoint components.
- **23/23 checkpoint-specific tests** passed, including multiple output files, failed child, external BREAK, simulated missing or corrupted backups, unclean restart, source-deleted recovery, and CLI integration.
- Compressed `AutoDepthLive_v0.4.pyz` end-to-end encode/decode matched a generated 58,400-byte input exactly; `checkpoint status` worked for both archived and decoded outputs.
- A **32,513,441-byte actual previously generated `.ut3` video archive** was copied, modified in place after a checkpoint, and fully restored; before/after SHA-256 was identical:
  `d3721aa2e406a7953db6c1a760e5f562444bcf6f6f0322cda5e61026cfb01998`.

## Limitations / threat model

- The state is the *protected local file set*, **not** a full process snapshot: RAM, sockets, playback position, services and undeclared files aren't captured.
- The supervisor can be killed by the OS. An independently running child may remain alive after that kill: ensure the child is stopped **before** restoring the old file. A child that changes files outside `--protect` can still cause side effects.
- Files changed by **other** processes concurrently are out of scope. Locks coordinate only other cooperating processes that use the same checkpoint directory.
- Power loss and cross-device filesystem behavior depend on OS/storage guarantees. Atomic rename is applied to each file, not as a multi-file transaction.
- A hash is an integrity check, not an information-recovery code. If both original and backup are destroyed, the content cannot be reconstructed.
- Complete snapshots cost approximately another full file's storage. Old content-addressed blobs are deliberately retained pending future garbage-collection controls; monitor free disk space.
- A completed process returning zero doesn't prove its output is semantically valid for its application. The underlying codec's structural/integrity verification remains necessary.
- Windows file locking and process-tree termination require separate platform testing. Unix/POSIX tests were performed here.

## Reproduction

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s . -p 'test*.py' -v
python AutoDepthLive_v0.4.pyz encode input.mp4 input.ut3 --max-depth 4
python AutoDepthLive_v0.4.pyz checkpoint status --output input.ut3
python AutoDepthLive_v0.4.pyz runner run --port 8777 --protect output.ut3 -- python my_writer.py output.ut3
# From another shell, using the actual token printed above:
python AutoDepthLive_v0.4.pyz runner break --port 8777 --token YOUR_SESSION_TOKEN
python AutoDepthLive_v0.4.pyz checkpoint recover --output output.ut3
```

## Next possible refinement

Implement orphan-process supervision independent of the controlling parent (to cover hard supervisor termination), versioned multi-output snapshot transactions, storage quotas and safe snapshot garbage collection, and playback-position resume bookmarks. These are **not** part of v0.4.
