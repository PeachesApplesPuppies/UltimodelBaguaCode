#!/usr/bin/env python3
"""Ultimodel BREAK supervisor: run and stop a *subprocess group* on demand.

Examples:
  python breakable_runner.py run --port 8777 -- python autodepth_hex.py encode file.mp4 file.ut3
  python breakable_runner.py break --port 8777 --token YOUR_PRINTED_SESSION_TOKEN

BREAK is a request for immediate termination; the OS may take finite time to
schedule/terminate a process. SIGTERM is attempted, then SIGKILL/TerminateProcess
if needed. Python and C libraries can be forcibly stopped even without
cooperative checkpoints. Completed files are never modified by the supervisor;
the encoding tools use atomic commits so incomplete final archives are avoided.
"""
from __future__ import annotations

import argparse
import hmac
import json
import os
import secrets
import signal
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.request

from emergency_break import BreakController, install_break_signals, restore_break_signals
from live_player import stop_process_tree
from closed_state import ClosedState


def make_control_server(stop, host='127.0.0.1', port=0, *, secret=None):
    if host not in ('127.0.0.1', '::1'):
        raise ValueError('BREAK supervisor must bind to loopback only')
    token = secret or secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/__break':
                self.send_error(404)
                return
            if (self.client_address[0] not in ('127.0.0.1','::1') or
                    not hmac.compare_digest(self.headers.get('X-Ultimodel-Break',''),token)):
                self.send_error(403, 'Invalid BREAK token')
                return
            stop.request()
            self.send_response(202)
            self.send_header('Content-Length','0')
            self.end_headers()

        def log_message(self,*args):
            return  # no command contents or secret in HTTP logs

    server = ThreadingHTTPServer((host,port), Handler)
    server.daemon_threads=True
    server.break_token=token
    return server


def send_break(port,token):
    req=urllib.request.Request(f'http://127.0.0.1:{port}/__break',data=b'',method='POST',
                               headers={'X-Ultimodel-Break':token})
    with urllib.request.urlopen(req,timeout=3) as res:
        if res.status != 202:
            raise RuntimeError(f'BREAK not acknowledged: {res.status}')


def supervise(argv, *, port=8777, stop=None, startup_cb=None,
              protect_outputs=None, state_dir=None):
    """Run breakable child. Snapshot declared outputs BEFORE child launches.

    Normal successful exit commits the new closed state. Error, BREAK, or an
    exception restores the prior state. A hard-killed supervisor leaves the
    pending durable journal so the *next* invocation can recover it.
    """
    from contextlib import nullcontext
    if not argv:
        raise ValueError('Must provide a child command')
    if state_dir is not None and not protect_outputs:
        raise ValueError('--state-dir requires --protect')
    stop = stop or BreakController()
    checkpoint = (ClosedState(protect_outputs, state_dir=state_dir)
                  if protect_outputs else None)
    context = checkpoint if checkpoint is not None else nullcontext()
    with context:
        if checkpoint is not None:
            # This is before subprocess creation; no child can write yet.
            record = checkpoint.begin()
            if record['previous_crash_recovered']:
                print('Recovered interrupted previous job from last-known-good state',flush=True)
            print('Protected closed state:',checkpoint.state_dir,flush=True)
        else:
            print('No --protect outputs: BREAK works, but external writes are not rollback-protected',flush=True)
        server=None
        control_thread=None
        child=None
        old_handlers={}
        good=False
        try:
            server=make_control_server(stop,port=port)
            control_thread=threading.Thread(target=server.serve_forever,
                                            kwargs={'poll_interval':.05},daemon=True)
            control_thread.start()
            old_handlers = (install_break_signals(stop)
                            if threading.current_thread() is threading.main_thread() else {})
            if startup_cb is not None:
                startup_cb(server.server_port,server.break_token)
            else:
                print('BREAK supervisor port:',server.server_port,flush=True)
                print(f'BREAK command: python breakable_runner.py break --port {server.server_port} --token {server.break_token}',flush=True)
            opts={'start_new_session':True} if os.name!='nt' else {
                'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
            child=subprocess.Popen(argv,**opts)
            while True:
                if stop.requested:
                    stop_process_tree(child,grace_seconds=.25)
                    return 130
                if child.poll() is not None:
                    good=(child.returncode==0 and not stop.requested)
                    return child.returncode
                stop.wait(.025)
        finally:
            # Must stop child before rollback, or it could overwrite recovered files.
            if child is not None and child.poll() is None:
                stop_process_tree(child,grace_seconds=.25)
            if checkpoint is not None:
                checkpoint.finish(good)
            if server is not None:
                server.shutdown()
                server.server_close()
            if control_thread is not None:
                control_thread.join(timeout=1)
            restore_break_signals(old_handlers)


def cli():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    run=sub.add_parser('run',help='Start a breakable child process')
    run.add_argument('--port',type=int,default=8777)
    run.add_argument('--protect',action='append',default=[], metavar='OUTPUT',
                     help='File to snapshot before launch and restore on failure/BREAK; repeatable')
    run.add_argument('--state-dir',type=str,default=None,
                     help='Durable checkpoint directory; stable across restarts')
    run.add_argument('argv',nargs=argparse.REMAINDER)
    stop=sub.add_parser('break',help='Terminate the child process')
    stop.add_argument('--port',type=int,default=8777)
    stop.add_argument('--token',required=True)
    args=parser.parse_args()
    if args.command=='break':
        send_break(args.port,args.token)
        print('BREAK acknowledged',flush=True)
        return 0
    argv=args.argv[1:] if args.argv and args.argv[0]=='--' else args.argv
    return supervise(argv,port=args.port,protect_outputs=args.protect,state_dir=args.state_dir)


if __name__=='__main__':
    sys.exit(cli())
