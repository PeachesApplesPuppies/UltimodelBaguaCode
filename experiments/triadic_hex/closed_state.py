"""Ultimodel v0.4: last-known-good closed-state checkpoint and crash recovery.

This module protects *declared output files* from interrupted child commands.
It does not promise to capture arbitrary operating-system/process memory,
external services, undeclared files, or multi-file atomic transactions.

The independent supervising process creates a durable content-hashed snapshot
before launching a child. A journal with phase='pending' is written only after
all snapshots are durable. On success it marks 'closed' after fsyncing outputs;
on failure or the next startup after an unclean shutdown it restores the prior
verified bytes. Snapshots are stored independently (never hard-linked to live
output files that a child could edit in-place).
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import stat
import tempfile
import time
from pathlib import Path
from typing import Sequence

CHUNK = 1 << 20
SCHEMA = 1


class ClosedStateError(RuntimeError):
    pass


def digest_file(path: Path):
    h = hashlib.sha256()
    count = 0
    with path.open('rb') as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            count += len(chunk)
            h.update(chunk)
    return h.hexdigest(), count


def _sync_dir(path: Path):
    if os.name != 'nt':
        fd = os.open(str(path), os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)


def _atomic_json(path: Path, value: dict):
    fd, name = tempfile.mkstemp(prefix='.closed-journal-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, sort_keys=True)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
        _sync_dir(path.parent)
    finally:
        if os.path.exists(name):
            os.unlink(name)


@contextlib.contextmanager
def _locked(state_dir: Path):
    """Cross-platform advisory lock; callers must use the same state_dir."""
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = state_dir / '.lock'
    with lock.open('a+b') as f:
        if os.name == 'nt':
            import msvcrt
            f.seek(0)
            if f.seek(0, os.SEEK_END) == 0:
                f.write(b'0')
                f.flush()
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def default_state_dir(outputs: Sequence[Path]) -> Path:
    paths = [Path(os.path.abspath(p)) for p in outputs]
    if not paths:
        raise ValueError('Specify at least one protected output path')
    joined = '\n'.join(sorted(str(p) for p in paths)).encode()
    suffix = hashlib.sha256(joined).hexdigest()[:16]
    return paths[0].parent / ('.ultimodel-closed-' + suffix)


class ClosedState:
    """Single writer protected output set. 'begin' and 'finish' are journalled.

    The lock is held for the duration of this object, including child execution,
    preventing a second managed process from changing this state concurrently.
    """

    def __init__(self, outputs: Sequence[Path], *, state_dir: Path | None = None):
        self.outputs = tuple(Path(os.path.abspath(p)) for p in outputs)
        if not self.outputs or len(set(self.outputs)) != len(self.outputs):
            raise ValueError('Outputs must be a nonempty set of distinct paths')
        self.state_dir = Path(state_dir).resolve(strict=False) if state_dir else default_state_dir(self.outputs)
        if any(p == self.state_dir or self.state_dir in p.parents for p in self.outputs):
            raise ValueError('Output may not be located inside its checkpoint state directory')
        self.journal_path = self.state_dir / 'journal.json'
        self.blob_dir = self.state_dir / 'blobs'
        self._cm = None
        self._entered = False

    def __enter__(self):
        self._cm = _locked(self.state_dir)
        self._cm.__enter__()
        self._entered = True
        self.blob_dir.mkdir(exist_ok=True)
        return self

    def __exit__(self, ty, value, tb):
        try:
            return self._cm.__exit__(ty, value, tb)
        finally:
            self._entered = False

    def _require_lock(self):
        if not self._entered:
            raise ClosedStateError('Use ClosedState as a context manager for locking')

    def _load(self):
        if not self.journal_path.exists():
            return None
        try:
            record = json.loads(self.journal_path.read_text('utf-8'))
        except (ValueError, UnicodeError, OSError) as err:
            raise ClosedStateError('Cannot read checkpoint journal; refusing to alter outputs') from err
        if record.get('schema') != SCHEMA or record.get('phase') not in ('pending', 'closed', 'restored'):
            raise ClosedStateError('Unknown checkpoint journal schema/phase')
        entries = record.get('files')
        if not isinstance(entries, list) or not all(isinstance(x, dict) for x in entries):
            raise ClosedStateError('Malformed checkpoint entries')
        expected = [str(x) for x in self.outputs]
        if [x.get('path') for x in entries] != expected:
            raise ClosedStateError('Protected path set does not match existing journal; refusing recovery')
        return record

    def _validate_target(self, target: Path):
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ClosedStateError(f'Protected output is not a regular file: {target}')

    def _capture(self, target: Path):
        self._validate_target(target)
        if not target.exists():
            return {'path': str(target), 'existed': False, 'digest': None, 'size': 0}
        # Copy bytes, fsync, then name by content hash. Explicitly do not hardlink.
        fd, temp = tempfile.mkstemp(prefix='.closed-blob-', dir=self.blob_dir)
        hasher = hashlib.sha256()
        size = 0
        try:
            with os.fdopen(fd, 'wb') as w, target.open('rb') as r:
                while True:
                    data = r.read(CHUNK)
                    if not data: break
                    size += len(data)
                    hasher.update(data)
                    w.write(data)
                w.flush()
                os.fsync(w.fileno())
            digest = hasher.hexdigest()
            final = self.blob_dir / digest
            if final.exists():
                if digest_file(final) != (digest, size):
                    raise ClosedStateError(f'Existing closed-state blob corrupted: {digest}')
                os.unlink(temp)
            else:
                os.replace(temp, final)
                _sync_dir(self.blob_dir)
            return {'path': str(target), 'existed': True, 'digest': digest, 'size': size,
                    'mode': stat.S_IMODE(target.stat().st_mode),
                    'mtime_ns': target.stat().st_mtime_ns}
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def _validate_snapshots(self, record):
        for entry in record['files']:
            if entry.get('existed') not in (True, False):
                raise ClosedStateError('Malformed exists flag')
            if not entry['existed']:
                continue
            digest, size = entry.get('digest'), entry.get('size')
            if not isinstance(digest, str) or len(digest) != 64 or not isinstance(size, int) or size < 0:
                raise ClosedStateError('Malformed blob digest or size')
            if any(c not in '0123456789abcdef' for c in digest):
                raise ClosedStateError('Malformed blob digest')
            blob = self.blob_dir / digest
            if not blob.is_file() or digest_file(blob) != (digest, size):
                raise ClosedStateError('Snapshot blob is missing or corrupt; refusing destructive recovery')

    def restore_pending(self):
        """Return True if a previous uncommitted operation was rolled back."""
        self._require_lock()
        record = self._load()
        if record is None or record['phase'] != 'pending':
            return False
        self._validate_snapshots(record)  # validate ALL snapshots before any writes
        for entry in record['files']:
            target = Path(entry['path'])
            self._validate_target(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            if entry['existed']:
                # If bytes already restored (e.g. interruption halfway through recovery), do nothing.
                if target.exists() and digest_file(target) == (entry['digest'], entry['size']):
                    continue
                fd, temp = tempfile.mkstemp(prefix='.closed-restore-', dir=target.parent)
                try:
                    with os.fdopen(fd, 'wb') as w, (self.blob_dir / entry['digest']).open('rb') as r:
                        shutil.copyfileobj(r, w, length=CHUNK)
                        w.flush()
                        os.fsync(w.fileno())
                    if isinstance(entry.get('mode'), int):
                        os.chmod(temp, entry['mode'])
                    if isinstance(entry.get('mtime_ns'), int):
                        os.utime(temp, ns=(entry['mtime_ns'], entry['mtime_ns']))
                    os.replace(temp, target)
                    _sync_dir(target.parent)
                finally:
                    if os.path.exists(temp): os.unlink(temp)
            else:
                if target.exists():
                    target.unlink()
                    _sync_dir(target.parent)
        record['phase'] = 'restored'
        record['restored_at_unix'] = time.time()
        _atomic_json(self.journal_path, record)
        return True

    def begin(self):
        """Snapshot before any child process may start. Auto-recover previous crash."""
        self._require_lock()
        restored = self.restore_pending()
        previous = self._load()
        if previous and previous['phase'] == 'closed':
            # A previously committed output that changed behind our back
            # must not silently be accepted as a new 'known good' baseline.
            recorded = previous.get('output_checksums')
            if not isinstance(recorded, list) or len(recorded) != len(self.outputs):
                raise ClosedStateError('Missing prior committed checksums')
            for path, entry in zip(self.outputs, recorded):
                self._validate_target(path)
                if entry.get('path') != str(path):
                    raise ClosedStateError('Malformed previous committed output record')
                actual = digest_file(path) if path.exists() else (None, 0)
                if actual != (entry.get('digest'), entry.get('size')):
                    raise ClosedStateError(
                        'Previously committed output changed outside the protected runner; '
                        'inspect it before adopting a new baseline')
        snapshots = [self._capture(target) for target in self.outputs]
        record = {'schema': SCHEMA, 'phase': 'pending', 'files': snapshots,
                  'prepared_at_unix': time.time(), 'previous_crash_recovered': restored}
        _atomic_json(self.journal_path, record)
        return record

    def finish(self, success: bool):
        self._require_lock()
        record = self._load()
        if record is None or record['phase'] != 'pending':
            raise ClosedStateError('No pending checkpoint to finish')
        if not success:
            self.restore_pending()
            return 'restored'
        for target in self.outputs:
            self._validate_target(target)
            if target.exists():
                with target.open('rb') as f:
                    os.fsync(f.fileno())
                _sync_dir(target.parent)
        record['phase'] = 'closed'
        record['completed_at_unix'] = time.time()
        record['output_checksums'] = [
            {'path': str(p), 'digest': digest_file(p)[0], 'size': p.stat().st_size}
            if p.exists() else {'path': str(p), 'digest': None, 'size': 0}
            for p in self.outputs
        ]
        _atomic_json(self.journal_path, record)
        return 'closed'

    def status(self):
        self._require_lock()
        record = self._load()
        return record or {'schema': SCHEMA, 'phase': 'none', 'files': []}


def cli():
    """Manually inspect or recover the last persisted closed state."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('status', 'recover'))
    parser.add_argument('--output', action='append', required=True, type=Path,
                        help='Previously protected output; repeat for multiple files')
    parser.add_argument('--state-dir', type=Path, default=None)
    args = parser.parse_args()
    with ClosedState(args.output, state_dir=args.state_dir) as checkpoint:
        if args.action == 'recover':
            recovered = checkpoint.restore_pending()
            print('Recovered last closed state' if recovered else
                  'No pending interrupted operation found')
        print(json.dumps(checkpoint.status(), indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(cli())
