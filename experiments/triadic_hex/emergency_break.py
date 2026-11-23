"""Explicit stop-state shared by Ultimodel long-running operations.

Cooperative checkpoints + OS signals are complementary: Python code checks the
stop event between chunks; CTRL-C/SIGTERM interrupts the foreground process.
No user-facing claim of a hard real-time or physically instantaneous guarantee.
"""
from __future__ import annotations

import signal
import threading


class StopRequested(InterruptedError):
    """Operation was cancelled by the user; no partial output should be committed."""


class BreakController:
    def __init__(self):
        self._event = threading.Event()

    @property
    def requested(self):
        return self._event.is_set()

    def request(self):
        self._event.set()

    def wait(self, timeout=None):
        return self._event.wait(timeout)

    def check(self):
        if self._event.is_set():
            raise StopRequested('Ultimodel BREAK requested')


def install_break_signals(controller: BreakController):
    """Install SIGINT/SIGTERM handlers in the MAIN thread, returning old handlers.

    First signal requests cooperative cancellation; a second signal triggers a
    KeyboardInterrupt so a stubborn operation can be interrupted immediately.
    """
    previous = {}
    for signame in ('SIGINT', 'SIGTERM'):
        if not hasattr(signal, signame):
            continue
        sig = getattr(signal, signame)
        old = signal.getsignal(sig)
        previous[sig] = old
        def handler(signum, frame, *, token=controller):
            if token.requested:
                raise KeyboardInterrupt('Repeated stop signal')
            token.request()
        signal.signal(sig, handler)
    return previous


def restore_break_signals(previous):
    for sig, handler in previous.items():
        signal.signal(sig, handler)
