"""Playback process supervisor for AutoDepth Live.

The compressed archive remains untouched. This module owns the launched
player and stops it when BREAK is requested or the local stream ends.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading

from emergency_break import BreakController


def stop_process_tree(process: subprocess.Popen, grace_seconds=1.5):
    """Best-effort bounded cleanup of a child playback process and its group."""
    if process is None or process.poll() is not None:
        return
    if os.name != 'nt':
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        except PermissionError:
            process.terminate()
    else:
        # Windows termination is immediate for this child; grandchildren may
        # require a Windows Job Object to guarantee complete tree shutdown.
        process.terminate()
    try:
        process.wait(timeout=grace_seconds)
    except subprocess.TimeoutExpired:
        if os.name != 'nt':
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            process.kill()
        process.wait(timeout=1.5)


def run_stream_session(server, controller: BreakController, *, player_argv=None):
    """Serve a local .ut3 stream, optionally launch a player, honor BREAK.

    With player_argv, use literal argv. The final item must be the stream URL
    added by the caller. Returns after the player exits or BREAK is requested.
    """
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={'poll_interval': 0.05}, daemon=True)
    thread.start()
    player = None
    try:
        if player_argv is not None:
            opts = {'start_new_session': True} if os.name != 'nt' else {
                'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
            player = subprocess.Popen(player_argv, **opts)
        while thread.is_alive() and not controller.requested:
            if player is not None and player.poll() is not None:
                break
            controller.wait(0.05)
    finally:
        controller.request()
        server.shutdown()
        server.server_close()
        stop_process_tree(player)
        thread.join(timeout=1)
