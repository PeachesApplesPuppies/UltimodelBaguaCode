"""BREAK tests: network stop, OS stop, corrupted data, transactional abort."""
from __future__ import annotations

import io
import os
import random
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import triadic_hex as tri
import autodepth_hex as auto
from autodepth_live import IndexedArchive, make_http_server, send_break
from emergency_break import BreakController, StopRequested

ROOT=Path(__file__).parent


class BreakTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ultimodel-break-test-')
        self.addCleanup(self.tmp.cleanup)
        self.folder=Path(self.tmp.name)
        self.source=self.folder/'source.bin'
        self.source.write_bytes(random.Random(390).randbytes(12000))
        self.archive=self.folder/'archive.ut3'
        tri.encode(self.source,self.archive,depth=3,quality=1)

    def test_break_is_idempotent_and_raises(self):
        stop=BreakController()
        self.assertFalse(stop.requested)
        stop.check()
        stop.request()
        stop.request()
        self.assertTrue(stop.wait(0))
        self.assertTrue(stop.requested)
        with self.assertRaises(StopRequested):stop.check()

    def test_stopped_reader_never_returns_more_data(self):
        stop=BreakController()
        a=IndexedArchive(self.archive,stop=stop)
        self.assertEqual(a.read_range(0,100),self.source.read_bytes()[:100])
        stop.request()
        with self.assertRaises(StopRequested):a.read_range(0,1)
        with self.assertRaises(StopRequested):a.verify_full()

    def test_break_before_encode_preserves_existing_destination(self):
        stop=BreakController()
        for encoder,kw in [(tri.encode,dict(depth=3,quality=1)),
                           (auto.encode,dict(max_depth=2,min_leaf=100,quality=1,max_evaluations=5))]:
            out=self.folder/'write.ut3'
            out.write_bytes(b'KEEP THIS DATA')
            stop.request()
            with self.subTest(encoder=encoder.__module__):
                with self.assertRaises(StopRequested):encoder(self.source,out,stop=stop,**kw)
                self.assertEqual(out.read_bytes(),b'KEEP THIS DATA')

    def test_break_during_planning_keeps_old_archive(self):
        stop=BreakController()
        original=tri.best_leaf
        count=[0]
        def injection(data,q):
            count[0]+=1
            if count[0]==2:
                stop.request()
            return original(data,q)
        tri.best_leaf=injection
        try:
            out=self.folder/'old.ut3'
            out.write_bytes(b'preserve')
            with self.assertRaises(StopRequested):
                auto.encode(self.source,out,max_depth=3,min_leaf=64,quality=1,
                            max_evaluations=10,stop=stop)
            self.assertEqual(out.read_bytes(),b'preserve')
        finally:
            tri.best_leaf=original

    def test_cancel_tri_decode_does_not_commit(self):
        stop=BreakController()
        dest=self.folder/'existing.bin'
        dest.write_bytes(b'preserved')
        original=tri.decompress
        called=[0]
        def injection(raw,codec,limit):
            called[0]+=1
            value=original(raw,codec,limit)
            if called[0]==1:stop.request()
            return value
        tri.decompress=injection
        try:
            with self.assertRaises(StopRequested):tri.decode(self.archive,dest,stop=stop)
            self.assertEqual(dest.read_bytes(),b'preserved')
            self.assertEqual(list(self.folder.glob('.triadic-*')),[])
        finally:
            tri.decompress=original

    def test_break_endpoint_denies_unauthorized_and_stops_server(self):
        stop=BreakController()
        a=IndexedArchive(self.archive,stop=stop)
        server=make_http_server(a,port=0,stop_secret='high-entropy-test-token')
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        self.addCleanup(worker.join,timeout=2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url=f'http://127.0.0.1:{server.server_port}/__break'
        bad=urllib.request.Request(url,data=b'',method='POST',headers={'X-Ultimodel-Break':'wrong'})
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(bad,timeout=3)
        self.assertEqual(context.exception.code,403)
        self.assertFalse(stop.requested)
        self.assertTrue(send_break(server.server_port,'high-entropy-test-token'))
        self.assertTrue(stop.requested)
        worker.join(timeout=3)
        self.assertFalse(worker.is_alive())
        with self.assertRaises(StopRequested):a.read_range(0,2)
        self.assertEqual(a.stats()['cache_bytes'],0)

    def test_sigint_stops_foreground_stream_promptly(self):
        if os.name=='nt':
            self.skipTest('POSIX SIGINT subprocess test only')
        cmd=[sys.executable,str(ROOT/'autodepth_live.py'),'serve',str(self.archive),'--port','0']
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            first=proc.stdout.readline().strip()
            second=proc.stdout.readline().strip()
            self.assertIn('video.mp4',first)
            self.assertIn('BREAK command:',second)
            proc.send_signal(signal.SIGINT)
            proc.communicate(timeout=4)
            self.assertEqual(proc.returncode,0)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=3)

    def test_cli_break_stops_separate_process(self):
        cmd=[sys.executable,str(ROOT/'autodepth_live.py'),'serve',str(self.archive),'--port','0']
        proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            proc.stdout.readline()
            commandline=proc.stdout.readline().strip()
            self.assertIn('BREAK command:',commandline)
            parts=commandline.split()
            port=int(parts[parts.index('--port')+1])
            token=parts[parts.index('--token')+1]
            stop=subprocess.run([sys.executable,str(ROOT/'autodepth_live.py'),'break',
                                 '--port',str(port),'--token',token],capture_output=True,text=True,timeout=5)
            self.assertEqual(stop.returncode,0,stop.stderr)
            self.assertIn('BREAK acknowledged',stop.stdout)
            proc.communicate(timeout=4)
            self.assertEqual(proc.returncode,0)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=3)


if __name__=='__main__':unittest.main()


class PlaybackBreakTests(unittest.TestCase):
    def test_supervisor_kills_mock_player_on_break(self):
        from live_player import run_stream_session
        from autodepth_live import IndexedArchive, make_http_server
        import triadic_hex as tri
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);source=p/'x';archive=p/'x.ut3'
            source.write_bytes(b'example'*1000)
            tri.encode(source,archive,depth=1,quality=1)
            control=BreakController()
            indexed=IndexedArchive(archive,stop=control)
            server=make_http_server(indexed,port=0,stop_secret='test-token')
            # Mock player explicitly records PID. We stop the process by
            # sending BREAK to the stream, without ever signaling it directly.
            pidfile=p/'player.pid'
            child_script='import os,time,sys;open(sys.argv[1],"w").write(str(os.getpid()));time.sleep(60)'
            argv=[sys.executable,'-c',child_script,str(pidfile)]
            t=threading.Thread(target=run_stream_session,args=(server,control),
                               kwargs={'player_argv':argv},daemon=True)
            t.start()
            limit=time.monotonic()+3
            while not pidfile.exists() and time.monotonic()<limit:
                time.sleep(.01)
            self.assertTrue(pidfile.exists(),'Mock player did not start')
            self.assertTrue(send_break(server.server_port,'test-token'))
            t.join(timeout=3)
            self.assertFalse(t.is_alive(),'Supervisor did not stop promptly')
            self.assertTrue(control.requested)
            # On Linux, a terminated child may be a zombie briefly; the
            # supervisor calls .wait so it should have been reaped.
            self.assertFalse(Path('/proc/'+pidfile.read_text()).exists() if
                             Path('/proc').exists() else False)


class SupervisorBreakTests(unittest.TestCase):
    def test_stop_ignores_uncooperative_child_and_does_not_wait_60s(self):
        if os.name=='nt':self.skipTest('POSIX signal-ignore demonstration')
        from breakable_runner import supervise, send_break
        import socket
        # Give the supervisor a unique port so an independent process can
        # send the break signal out of band.
        holder={}
        outcome=[]
        with tempfile.TemporaryDirectory() as folder:
            pidfile=Path(folder)/'pid.txt'
            def cb(port,token):holder.update(port=port,token=token)
            # Child ignores SIGTERM: supervisor must escalate to SIGKILL.
            script=('import os,signal,time,sys;'
                    'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
                    'open(sys.argv[1],"w").write(str(os.getpid()));'
                    'time.sleep(60)')
            command=[sys.executable,'-c',script,str(pidfile)]
            def work():outcome.append(supervise(command,port=0,startup_cb=cb))
            worker=threading.Thread(target=work,daemon=True)
            worker.start()
            deadline=time.monotonic()+3
            while (not pidfile.exists() or 'port' not in holder) and time.monotonic()<deadline:
                time.sleep(.01)
            self.assertTrue(pidfile.exists())
            start=time.perf_counter()
            send_break(holder['port'],holder['token'])
            worker.join(timeout=4)
            elapsed=time.perf_counter()-start
            self.assertFalse(worker.is_alive(),'Subprocess supervisor failed to stop')
            self.assertEqual(outcome,[130])
            self.assertLess(elapsed,2.0)
            if Path('/proc').exists():
                self.assertFalse(Path('/proc/'+pidfile.read_text()).exists())

    def test_supervisor_break_requires_token(self):
        from breakable_runner import make_control_server,send_break
        stop=BreakController()
        srv=make_control_server(stop,port=0,secret='intentionally-fixed-test-token')
        t=threading.Thread(target=srv.serve_forever,daemon=True);t.start()
        try:
            with self.assertRaises(urllib.error.HTTPError) as cm:
                send_break(srv.server_port,'wrong')
            self.assertEqual(cm.exception.code,403)
            self.assertFalse(stop.requested)
            send_break(srv.server_port,'intentionally-fixed-test-token')
            self.assertTrue(stop.requested)
        finally:
            srv.shutdown();srv.server_close();t.join(timeout=2)
