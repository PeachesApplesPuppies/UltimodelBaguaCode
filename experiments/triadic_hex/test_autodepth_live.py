"""Regressions: seekable no-full-extraction, integrity, HTTP ranges, and cache."""
import hashlib
import io
import random
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import triadic_hex as tri
import autodepth_hex as auto
from autodepth_live import IndexedArchive, SeekableHEXFile, parse_range, make_http_server


class LiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ultimodel-live-test-')
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def make_archive(self, raw, depth=3, *, autodepth=False):
        src = self.folder/'original.bin'
        archive = self.folder/'source.ut3'
        src.write_bytes(raw)
        if autodepth:
            auto.encode(src, archive, max_depth=depth, min_leaf=256,
                        quality=1, max_evaluations=60)
        else:
            tri.encode(src, archive, depth=depth, quality=1)
        src.unlink()
        return archive

    def test_empty_archives(self):
        path = self.make_archive(b'')
        a = IndexedArchive(path)
        self.assertEqual(a.length, 0)
        self.assertEqual(a.read_range(0, 100), b'')
        self.assertEqual(a.verify_full()['sha256'], hashlib.sha256(b'').hexdigest())

    def test_single_value_and_small_sizes(self):
        for length in range(1, 16):
            with self.subTest(length=length):
                raw = bytes(range(length))
                a = IndexedArchive(self.make_archive(raw))
                self.assertEqual(a.read_range(0,length), raw)
                self.assertEqual(a.read_range(1,999),raw[1:])
                self.assertEqual(a.verify_full()['bytes'], length)

    def test_exhaustive_two_byte_values_read_sparse(self):
        raw = b''.join(bytes((i,j)) for i in range(256) for j in range(256))
        a = IndexedArchive(self.make_archive(raw,depth=4), cache_bytes=1024*32)
        for i in range(0,len(raw),113):
            self.assertEqual(a.read_range(i,113),raw[i:i+113])
        self.assertEqual(a.verify_full()['sha256'],hashlib.sha256(raw).hexdigest())

    def test_random_ranges_with_original_deleted(self):
        rng=random.Random(431)
        raw=rng.randbytes(160003)
        a=IndexedArchive(self.make_archive(raw,depth=5), cache_bytes=5000)
        for _ in range(500):
            pos=rng.randrange(len(raw)+5)
            n=rng.randrange(0,45000)
            self.assertEqual(a.read_range(pos,n),raw[pos:pos+n])
        self.assertLessEqual(a.stats()['max_cache_bytes_used'],5000)
        self.assertEqual(a.verify_full()['sha256'],hashlib.sha256(raw).hexdigest())

    def test_autodepth_archive_compatibility(self):
        raw=random.Random(2).randbytes(20000)*3 + b'XYZ'*10000
        a=IndexedArchive(self.make_archive(raw,depth=4,autodepth=True))
        self.assertEqual(a.read_range(20000,33333),raw[20000:53333])
        self.assertTrue(a.verify_full()['verified'])

    def test_reader_seek_and_readinto(self):
        raw=bytes(range(256))*200
        a=IndexedArchive(self.make_archive(raw))
        with a.file() as f:
            self.assertTrue(f.seekable())
            self.assertEqual(f.seek(100),100)
            self.assertEqual(f.read(14),raw[100:114])
            self.assertEqual(f.seek(-55,io.SEEK_END),len(raw)-55)
            array=bytearray(40)
            self.assertEqual(f.readinto(array),40)
            self.assertEqual(bytes(array),raw[-55:-15])
            f.seek(0)
            self.assertEqual(f.read(0),b'')
            self.assertEqual(f.read(8),raw[:8])
            f.seek(len(raw)+5)
            self.assertEqual(f.read(50),b'')
        with self.assertRaises(ValueError): f.read(1)

    def test_invalid_negative_offsets(self):
        a=IndexedArchive(self.make_archive(b'data'))
        for start,length in [(-1,2),(2,-1)]:
            with self.assertRaises(ValueError):a.read_range(start,length)
        with a.file() as f:
            with self.assertRaises(ValueError):f.seek(-1)

    def test_cache_hits_and_evictions(self):
        rng=random.Random(66)
        raw=rng.randbytes(50000)*3
        a=IndexedArchive(self.make_archive(raw,depth=2),cache_bytes=18000)
        _=a.read_range(0,2500)
        _=a.read_range(0,1000)
        self.assertGreaterEqual(a.stats()['cache_hits'],1)
        for k in range(0,len(raw),15000):a.read_range(k,2000)
        self.assertLessEqual(a.stats()['cache_bytes'],18000)
        self.assertGreater(a.stats()['cache_misses'],0)

    def test_per_leaf_cap_enforced(self):
        raw=b'R'*50000
        a=IndexedArchive(self.make_archive(raw,depth=0),max_leaf_bytes=1000)
        with self.assertRaisesRegex(ValueError,'max_leaf_bytes'):a.read_range(0,1)

    def test_untouched_leaf_detected_on_access(self):
        raw=random.Random(91).randbytes(43000)
        path=self.make_archive(raw,depth=2)
        good=IndexedArchive(path)
        leaf=next(n for n in good.nodes if n.kind==0 and n.payload_len>0)
        with path.open('r+b') as f:
            f.seek(leaf.payload_start)
            first=f.read(1)
            f.seek(leaf.payload_start)
            f.write(bytes([first[0]^0x80]))
        a=IndexedArchive(path)
        with self.assertRaises(ValueError):a.verify_full()

    def test_internal_sha_is_checked_by_full_verifier(self):
        raw=random.Random(17).randbytes(24000)
        path=self.make_archive(raw,depth=2)
        a=IndexedArchive(path)
        target=next(i for i,n in enumerate(a.nodes) if n.kind==1 and i!=a.root)
        # Locate target node digest in serialized archive without altering payloads.
        # Unique digest matches are overwhelmingly likely on random inputs.
        old=a.nodes[target].digest
        payload=path.read_bytes()
        occurrences=payload.count(old)
        self.assertEqual(occurrences,1)
        path.write_bytes(payload.replace(old,bytes([old[0]^1])+old[1:],1))
        corrupted=IndexedArchive(path)
        self.assertEqual(corrupted.read_range(0,20),raw[:20])
        with self.assertRaisesRegex(ValueError,'Internal node'):corrupted.verify_full()

    def test_reject_truncated_and_trailing(self):
        path=self.make_archive(b'abc'*1500)
        source=path.read_bytes()
        for variant in (source[:-1],source+b'X',b'broken'):
            path.write_bytes(variant)
            with self.assertRaises(ValueError):IndexedArchive(path)
            path.write_bytes(source)

    def test_parse_http_range(self):
        self.assertEqual(parse_range('bytes=0-3',100),(0,3))
        self.assertEqual(parse_range('bytes=95-',100),(95,99))
        self.assertEqual(parse_range('bytes=-10',100),(90,99))
        self.assertEqual(parse_range('bytes=0-999',100),(0,99))
        for value in ('bytes=10-1','bytes=100-','bytes=0-2,9-11', 'bytes=-0', 'wat'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):parse_range(value,100)

    def test_http_range_playback_style(self):
        raw=random.Random(49).randbytes(16000)
        a=IndexedArchive(self.make_archive(raw,depth=3))
        server=make_http_server(a,port=0)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        self.addCleanup(thread.join,timeout=2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url=f'http://127.0.0.1:{server.server_port}/video.mp4'
        with urllib.request.urlopen(url,timeout=10) as response:
            self.assertEqual(response.status,200)
            self.assertEqual(response.headers.get('Accept-Ranges'),'bytes')
            self.assertEqual(response.read(),raw)
        for header,start,end in [('bytes=2-19',2,20),('bytes=-55',len(raw)-55,len(raw)),
                                  ('bytes=100-',100,len(raw))]:
            req=urllib.request.Request(url,headers={'Range':header})
            with urllib.request.urlopen(req,timeout=10) as res:
                self.assertEqual(res.status,206)
                self.assertEqual(res.read(),raw[start:end])
        head=urllib.request.Request(url,method='HEAD')
        with urllib.request.urlopen(head,timeout=10) as res:
            self.assertEqual(res.status,200)
            self.assertEqual(int(res.headers['Content-Length']),len(raw))
        for header in ['bytes=16000-','bytes=0-1,10-12']:
            with self.assertRaises(urllib.error.HTTPError) as context:
                urllib.request.urlopen(urllib.request.Request(url,headers={'Range':header}),timeout=10)
            self.assertEqual(context.exception.code,416)
        with self.assertRaises(urllib.error.HTTPError) as context:
            urllib.request.urlopen(url.replace('video.mp4','other'),timeout=10)
        self.assertEqual(context.exception.code,404)

    def test_http_concurrent_ranges(self):
        rng=random.Random(981)
        raw=rng.randbytes(60000)
        a=IndexedArchive(self.make_archive(raw,depth=4),cache_bytes=8000)
        server=make_http_server(a,port=0)
        t=threading.Thread(target=server.serve_forever,daemon=True)
        t.start()
        self.addCleanup(t.join,timeout=2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url=f'http://127.0.0.1:{server.server_port}/video.mp4'
        errors=[]
        def read(pos):
            try:
                req=urllib.request.Request(url,headers={'Range':f'bytes={pos}-{pos+499}'})
                with urllib.request.urlopen(req,timeout=10) as res:
                    if res.read()!=raw[pos:pos+500]:
                        errors.append(pos)
            except Exception as exc:errors.append(str(exc))
        threads=[threading.Thread(target=read,args=(rng.randrange(59000),)) for _ in range(30)]
        for worker in threads:worker.start()
        for worker in threads:worker.join(timeout=15)
        self.assertFalse(errors)
        self.assertLessEqual(a.stats()['cache_bytes'],8000)


if __name__ == '__main__':unittest.main()
