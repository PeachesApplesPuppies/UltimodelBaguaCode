"""Crash-recovery / last-known-good checkpoint tests for AutoDepth Live."""
import hashlib
import json
import os
import random
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from closed_state import ClosedState, ClosedStateError, digest_file, default_state_dir
from breakable_runner import supervise, send_break


class ClosedStateTests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory(prefix='closed-state-')
        self.addCleanup(self.d.cleanup)
        self.folder=Path(self.d.name)
        self.output=self.folder/'result.ut3'
        self.state=self.folder/'state'

    def test_checkpoint_before_first_run_and_success(self):
        self.output.write_bytes(b'old state')
        with ClosedState([self.output],state_dir=self.state) as tx:
            pending=tx.begin()
            self.assertEqual(pending['phase'],'pending')
            self.assertEqual(pending['files'][0]['digest'],hashlib.sha256(b'old state').hexdigest())
            self.output.write_bytes(b'new complete state')
            self.assertEqual(tx.finish(True),'closed')
            self.assertEqual(tx.status()['phase'],'closed')
            # Snapshot from before successful run remains available.
            blob=self.state/'blobs'/hashlib.sha256(b'old state').hexdigest()
            self.assertEqual(blob.read_bytes(),b'old state')
        self.assertEqual(self.output.read_bytes(),b'new complete state')

    def test_break_rolls_back_in_place_modification(self):
        original=b'precious'*12345
        self.output.write_bytes(original)
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(b'CRASHED IN THE MIDDLE OF IN PLACE WRITE')
            self.assertEqual(tx.finish(False),'restored')
        self.assertEqual(self.output.read_bytes(),original)

    def test_nonexistent_new_output_deleted_on_failure(self):
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(b'partially written')
            tx.finish(False)
        self.assertFalse(self.output.exists())

    def test_orphan_pending_journal_recovers_after_restart(self):
        original=b'original closed state'*1000
        self.output.write_bytes(original)
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(b'half complete')
            # Simulate supervisor's unclean death (no finish call).
        with ClosedState([self.output],state_dir=self.state) as tx:
            self.assertTrue(tx.restore_pending())
            self.assertFalse(tx.restore_pending())
            self.assertEqual(tx.status()['phase'],'restored')
        self.assertEqual(self.output.read_bytes(),original)

    def test_second_begin_recovers_before_new_snapshot(self):
        self.output.write_bytes(b'known good')
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(b'bad')
        with ClosedState([self.output],state_dir=self.state) as tx:
            new=tx.begin()
            self.assertTrue(new['previous_crash_recovered'])
            self.assertEqual(self.output.read_bytes(),b'known good')
            self.assertEqual(new['files'][0]['digest'],hashlib.sha256(b'known good').hexdigest())
            tx.finish(False)

    def test_snapshot_corruption_refuses_destructive_recovery(self):
        self.output.write_bytes(b'original')
        with ClosedState([self.output],state_dir=self.state) as tx:
            entry=tx.begin()['files'][0]
            self.output.write_bytes(b'partial')
        (self.state/'blobs'/entry['digest']).write_bytes(b'corrupt snapshot')
        with ClosedState([self.output],state_dir=self.state) as tx:
            with self.assertRaisesRegex(ClosedStateError,'corrupt'):
                tx.restore_pending()
        self.assertEqual(self.output.read_bytes(),b'partial')  # refuses to make it worse

    def test_missing_backup_refuses_destructive_recovery(self):
        self.output.write_bytes(b'valuable')
        with ClosedState([self.output],state_dir=self.state) as tx:
            entry=tx.begin()['files'][0]
            self.output.write_bytes(b'partial')
        (self.state/'blobs'/entry['digest']).unlink()
        with ClosedState([self.output],state_dir=self.state) as tx:
            with self.assertRaises(ClosedStateError):tx.restore_pending()
        self.assertEqual(self.output.read_bytes(),b'partial')

    def test_multiple_outputs_and_failure(self):
        o2=self.folder/'another.bin'
        self.output.write_bytes(b'A')
        o2.write_bytes(b'B')
        with ClosedState([self.output,o2],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(b'X')
            o2.unlink()
            tx.finish(False)
        self.assertEqual(self.output.read_bytes(),b'A')
        self.assertEqual(o2.read_bytes(),b'B')

    def test_preserves_every_byte_in_1mb_random_snapshot(self):
        original=random.Random(77).randbytes(1048577)
        self.output.write_bytes(original)
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
            self.output.write_bytes(random.Random(4).randbytes(900000))
            tx.finish(False)
        self.assertEqual(self.output.read_bytes(),original)

    def test_reject_duplicate_outputs_and_different_path_set(self):
        with self.assertRaises(ValueError): ClosedState([self.output,self.output])
        self.output.write_bytes(b'x')
        with ClosedState([self.output],state_dir=self.state) as tx:
            tx.begin()
        with ClosedState([self.folder/'other'],state_dir=self.state) as tx:
            with self.assertRaises(ClosedStateError): tx.restore_pending()

    def test_bad_journal_is_not_silently_ignored(self):
        self.state.mkdir()
        (self.state/'journal.json').write_text('{not valid')
        with ClosedState([self.output],state_dir=self.state) as tx:
            with self.assertRaises(ClosedStateError):tx.begin()

    def test_reject_symlink_target(self):
        data=self.folder/'real';data.write_bytes(b'not safe to overwrite')
        self.output.symlink_to(data)
        with ClosedState([self.output],state_dir=self.state) as tx:
            with self.assertRaises(ClosedStateError):tx.begin()
        self.assertEqual(data.read_bytes(),b'not safe to overwrite')

    def test_default_state_dir_is_deterministic(self):
        x=default_state_dir([self.output])
        self.assertEqual(x,default_state_dir([self.output]))
        self.assertNotEqual(x,default_state_dir([self.folder/'other']))


class SupervisedCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory(prefix='supervised-checkpoint-')
        self.addCleanup(self.d.cleanup)
        self.folder=Path(self.d.name)
        self.out=self.folder/'output.bin'
        self.state_dir=self.folder/'checkpoint'

    def test_successful_command_commits_modified_output(self):
        self.out.write_bytes(b'old')
        child=[sys.executable,'-c',"import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(b'new')",str(self.out)]
        self.assertEqual(supervise(child,port=0,protect_outputs=[self.out],state_dir=self.state_dir),0)
        self.assertEqual(self.out.read_bytes(),b'new')
        with ClosedState([self.out],state_dir=self.state_dir) as tx:
            self.assertEqual(tx.status()['phase'],'closed')

    def test_nonzero_exit_rolls_back_modified_output(self):
        self.out.write_bytes(b'old')
        child=[sys.executable,'-c',"import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(b'bad');sys.exit(14)",str(self.out)]
        self.assertEqual(supervise(child,port=0,protect_outputs=[self.out],state_dir=self.state_dir),14)
        self.assertEqual(self.out.read_bytes(),b'old')

    def test_out_of_band_break_restores_old_file(self):
        self.out.write_bytes(b'old valid file')
        ready={};statuses=[]
        child=[sys.executable,'-c',
               "import pathlib,sys,time,os;pathlib.Path(sys.argv[1]).write_bytes(b'partial');pathlib.Path(sys.argv[2]).write_text('ready');time.sleep(60)",
               str(self.out),str(self.folder/'ready.txt')]
        t=threading.Thread(target=lambda:statuses.append(supervise(
            child,port=0,protect_outputs=[self.out],state_dir=self.state_dir,
            startup_cb=lambda port,token:ready.update(port=port,token=token))),daemon=True)
        t.start()
        deadline=time.monotonic()+5
        while not (self.folder/'ready.txt').exists() and time.monotonic()<deadline:time.sleep(.01)
        self.assertTrue((self.folder/'ready.txt').exists())
        send_break(ready['port'],ready['token'])
        t.join(timeout=4)
        self.assertFalse(t.is_alive())
        self.assertEqual(statuses,[130])
        self.assertEqual(self.out.read_bytes(),b'old valid file')
        self.assertEqual(json.loads((self.state_dir/'journal.json').read_text())['phase'],'restored')


if __name__=='__main__': unittest.main()

class OperationalIntegrationTests(unittest.TestCase):
    """End-to-end CLI test using only generated data, no original user media."""
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='closed-state-cli-')
        self.addCleanup(self.tmp.cleanup)
        self.d=Path(self.tmp.name)
        self.src=self.d/'source.bin'
        self.src.write_bytes(random.Random(2026).randbytes(45000))
        self.target=self.d/'archive.ut3'
        self.root=Path(__file__).parent

    def _run(self,*args,expect=0):
        r=subprocess.run([sys.executable,*map(str,args)],text=True,capture_output=True,timeout=30)
        self.assertEqual(r.returncode,expect, f'CMD:{args}\nOUT:{r.stdout}\nERR:{r.stderr}')
        return r

    def test_tri_encode_decode_commits_closed_states(self):
        tri=self.root/'triadic_hex.py'
        self.target.write_bytes(b'old stored bytes')
        self._run(tri,'encode',self.src,self.target,'--depth','1','--quality','1')
        self.assertNotEqual(self.target.read_bytes(),b'old stored bytes')
        with ClosedState([self.target]) as cp:
            self.assertEqual(cp.status()['phase'],'closed')
            backup=cp.status()['files'][0]
            self.assertEqual((cp.blob_dir / backup['digest']).read_bytes(),b'old stored bytes')
        out=self.d/'decoded.bin'
        self._run(tri,'decode',self.target,out)
        self.assertEqual(out.read_bytes(),self.src.read_bytes())
        with ClosedState([out]) as cp:
            self.assertEqual(cp.status()['phase'],'closed')
            self.assertFalse(cp.status()['files'][0]['existed'])

    def test_autodepth_cli_commits_closed_state(self):
        self._run(self.root/'autodepth_hex.py','encode',self.src,self.target,
                  '--max-depth','2','--min-leaf','1000','--quality','1',
                  '--max-evaluations','10')
        with ClosedState([self.target]) as cp:
            self.assertEqual(cp.status()['phase'],'closed')
        out=self.d/'out.bin'
        self._run(self.root/'autodepth_hex.py','decode',self.target,out)
        self.assertEqual(out.read_bytes(),self.src.read_bytes())

    def test_preexisting_unfinished_state_recovers_before_next_encoding(self):
        self.target.write_bytes(b'the original before crash')
        with ClosedState([self.target]) as cp:
            cp.begin()
            self.target.write_bytes(b'partial corruption')
        self._run(self.root/'triadic_hex.py','encode',self.src,self.target,
                  '--depth','1','--quality','1')
        with ClosedState([self.target]) as cp:
            status=cp.status()
            self.assertEqual(status['phase'],'closed')
            self.assertTrue(status['previous_crash_recovered'])
            snapshot=status['files'][0]
            self.assertEqual((cp.blob_dir / snapshot['digest']).read_bytes(),
                             b'the original before crash')

    def test_unexpected_external_change_not_adopted(self):
        self.target.write_bytes(b'baseline')
        with ClosedState([self.target]) as cp:
            cp.begin()
            cp.finish(True)
        self.target.write_bytes(b'corrupted externally')
        r=subprocess.run([sys.executable,str(self.root/'triadic_hex.py'),
                          'encode',str(self.src),str(self.target),
                          '--depth','1','--quality','1'],capture_output=True,text=True,timeout=30)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('Previously committed output changed',r.stderr)
        self.assertEqual(self.target.read_bytes(),b'corrupted externally')

    def test_restored_metadata_mode(self):
        if os.name=='nt':self.skipTest('POSIX mode permissions fixture')
        self.target.write_bytes(b'known good')
        self.target.chmod(0o640)
        with ClosedState([self.target]) as cp:
            cp.begin()
            self.target.write_bytes(b'bad')
            self.target.chmod(0o600)
            cp.finish(False)
        self.assertEqual(self.target.read_bytes(),b'known good')
        self.assertEqual(self.target.stat().st_mode & 0o777,0o640)

    def test_manual_checkpoint_cli_recovers_after_interruption(self):
        self.target.write_bytes(b'good')
        with ClosedState([self.target]) as cp:
            cp.begin()
            self.target.write_bytes(b'corrupted')
        result=self._run(self.root/'closed_state.py','recover','--output',self.target)
        self.assertIn('Recovered last closed state',result.stdout)
        self.assertEqual(self.target.read_bytes(),b'good')

    def test_stopped_before_writer_creates_any_output(self):
        from emergency_break import BreakController
        control=BreakController()
        control.request()
        # Stop before command setup should not create any file.
        with ClosedState([self.target]) as cp:
            cp.begin()
            cp.finish(False)
        self.assertFalse(self.target.exists())
