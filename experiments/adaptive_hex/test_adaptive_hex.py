"""Reproducible, bounded tests for Adaptive HEX. No source movie required."""
import hashlib
import os
import random
import struct
import tempfile
import unittest
from pathlib import Path

from adaptive_hex import (MAGIC, HEADER, BLOCK, TRANS, CODEC, CANDIDATES, MAX_BLOCK,
                          best_block, decode, encode)
from transforms import TRANSFORMS

class AdaptiveTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        self.source=self.root/'source.bin'
        self.arch=self.root/'compressed.uhx'
        self.result=self.root/'recovered.bin'

    def check(self, blob, block=1024, quality=4, delete=True):
        self.source.write_bytes(blob)
        a=encode(self.source,self.arch,block_size=block,brotli_quality=quality)
        self.assertEqual(a['source_bytes'],len(blob))
        self.assertEqual(a['sha256'],hashlib.sha256(blob).hexdigest())
        if delete:self.source.unlink()
        b=decode(self.arch,self.result)
        self.assertTrue(b['verified'])
        self.assertEqual(b['sha256'],a['sha256'])
        self.assertEqual(self.result.read_bytes(),blob)
        return a,b

    def test_empty(self): self.check(b'')
    def test_256_values(self): self.check(bytes(range(256)))
    def test_all_65536_2byte_pairs(self):
        self.check(b''.join(bytes((i,j)) for i in range(256) for j in range(256)),block=4096)
    def test_one_byte_lengths_boundaries(self):
        rand=random.Random(322)
        for n in [1,2,3,4,5,6,7,8,9,13,31,63,64,65,255,256,257,1023,1024,1025,4095,4096,4097]:
            with self.subTest(n=n):self.check(rand.randbytes(n),block=1024)
    def test_binary_zero_ff(self):self.check(b'\0\xff'*4000,block=512)
    def test_repetitive(self): self.check(b'ULTIMODEL!'*7000,block=1024)
    def test_random_roundtrips(self):
        rng=random.Random(20261123)
        for n in range(35):
            blob=rng.randbytes(rng.randint(0,15000))
            with self.subTest(trial=n):self.check(blob,block=1024)
    def test_true_hex_advantage_synthetic(self):
        rng=random.Random(42)
        data=bytes((rng.randrange(64)|((i%4)<<6)) for i in range(100000))
        a,b=self.check(data,block=8192)
        self.assertTrue(any('hex6+2' in k for k in a['selection_counts']),a)
        self.assertLess(a['archive_bytes'],len(data)*0.85)
    def test_entropy_resists_compression_and_is_stored(self):
        r=random.Random(23)
        data=r.randbytes(150000)
        a,b=self.check(data,block=8192)
        self.assertEqual(a['selection_counts'],{'raw/store':a['blocks']})
        self.assertGreater(a['archive_bytes'],len(data))
    def test_adaptive_multiple_choices(self):
        rng=random.Random(11)
        block=8192
        noise=rng.randbytes(block)
        synthetic=bytes((rng.randrange(64)|((i%4)<<6)) for i in range(block))
        repetitive=b'abcXYZ'*(block//6)+b'abcXYZ'[:block%6]
        a,b=self.check(noise+synthetic+repetitive,block=block)
        self.assertGreaterEqual(len(a['selection_counts']),3,a)
    def test_all_transforms_reversible(self):
        rng=random.Random(112)
        for tr, (forward,backward) in TRANSFORMS.items():
            for n in [0,1,2,3,4,5,7,8,9,16,31,64,257,1000]:
                with self.subTest(transform=tr,n=n):
                    b=rng.randbytes(n)
                    self.assertEqual(backward(forward(b),len(b)),b)
    def test_source_exists_is_not_needed_to_decode(self):
        a,b=self.check(b'source-deleted'*1234,delete=True)
        self.assertFalse(self.source.exists())
    def test_checksum_and_integrity(self):
        self.check(b'A'*3000,delete=False)
        saved=bytearray(self.arch.read_bytes())
        offset=HEADER.size + BLOCK.size
        saved[offset]^=1
        self.arch.write_bytes(saved)
        with self.assertRaises((ValueError,Exception)):
            decode(self.arch,self.root/'badresult')
        self.assertFalse((self.root/'badresult').exists())
    def test_preserve_existing_output_on_bad_file(self):
        self.source.write_bytes(b'S'*9000);encode(self.source,self.arch,block_size=1024)
        self.result.write_bytes(b'EXISTING')
        b=bytearray(self.arch.read_bytes());b[HEADER.size + BLOCK.size]^=1
        self.arch.write_bytes(b)
        with self.assertRaises(Exception):decode(self.arch,self.result)
        self.assertEqual(self.result.read_bytes(),b'EXISTING')
    def test_truncated_header(self):
        self.arch.write_bytes(b'A');
        with self.assertRaises(ValueError):decode(self.arch,self.result)
    def test_bad_magic(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        b=bytearray(self.arch.read_bytes());b[0]=0
        self.arch.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'magic/version'):decode(self.arch,self.result)
    def test_bad_version(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        b=bytearray(self.arch.read_bytes());b[8]=2
        self.arch.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'magic/version'):decode(self.arch,self.result)
    def test_trailing_bytes(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        with self.arch.open('ab') as f:f.write(b'BAD')
        with self.assertRaisesRegex(ValueError,'trailing'):decode(self.arch,self.result)
    def test_truncated_payload(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        self.arch.write_bytes(self.arch.read_bytes()[:-3])
        with self.assertRaises(ValueError):decode(self.arch,self.result)
    def test_unsupported_method(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        b=bytearray(self.arch.read_bytes());b[HEADER.size]=0xff
        self.arch.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'Unsupported transform'):decode(self.arch,self.result)
    def test_bad_block_count(self):
        self.source.write_bytes(b'B'*3000);encode(self.source,self.arch,block_size=512)
        b=bytearray(self.arch.read_bytes());b[13:17]=struct.pack('>I',1000)
        self.arch.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'block count'):decode(self.arch,self.result)
    def test_invalid_settings(self):
        self.source.write_bytes(b'123')
        for bs in (-1,0,MAX_BLOCK+1):
            with self.assertRaises(ValueError):encode(self.source,self.arch,block_size=bs)
        for q in (-1,12):
            with self.assertRaises(ValueError):encode(self.source,self.arch,brotli_quality=q)
    def test_input_output_alias(self):
        self.source.write_bytes(b'123')
        with self.assertRaisesRegex(ValueError,'different'):encode(self.source,self.source)
        encode(self.source,self.arch)
        before=self.arch.read_bytes()
        with self.assertRaisesRegex(ValueError,'different'):decode(self.arch,self.arch)
        self.assertEqual(self.arch.read_bytes(),before)
    def test_determinism(self):
        rng=random.Random(42);data=rng.randbytes(32768)
        self.source.write_bytes(data)
        encode(self.source,self.arch,block_size=2048,brotli_quality=4)
        first=self.arch.read_bytes()
        encode(self.source,self.root/'second.uhx',block_size=2048,brotli_quality=4)
        self.assertEqual(first,(self.root/'second.uhx').read_bytes())
    def test_no_archive_source_mutation(self):
        blob=b'\xff\x00'*12345
        a,b=self.check(blob,delete=False)
        self.assertEqual(self.source.read_bytes(),blob)
    def test_selected_block_is_minimum_of_defined_candidates(self):
        import brotli
        from adaptive_hex import compress
        from transforms import TRANSFORMS
        rng=random.Random(223)
        for data in [rng.randbytes(8192),b'A'*8192,
                     bytes((rng.randrange(64)|((i%4)<<6)) for i in range(8192))]:
            tr,codec,payload=best_block(data,quality=4)
            sizes=[len(compress(TRANSFORMS[t][0](data),c,4)) for t,c in CANDIDATES]
            self.assertEqual(len(payload),min(sizes))

    def test_corrupted_stored_block_detected_by_sha(self):
        rng=random.Random(22)
        self.source.write_bytes(rng.randbytes(4096))
        a=encode(self.source,self.arch,block_size=4096)
        self.assertEqual(a['selection_counts'],{'raw/store':1})
        b=bytearray(self.arch.read_bytes())
        b[HEADER.size+BLOCK.size+1]^=1
        self.arch.write_bytes(b)
        with self.assertRaisesRegex(ValueError,'Block SHA-256'):decode(self.arch,self.result)
        self.assertFalse(self.result.exists())

    def test_no_external_paths_stored(self):
        blob=b'a'*10000
        self.check(blob)
        encoded=self.arch.read_bytes()
        self.assertNotIn(str(self.root).encode(),encoded)

if __name__=='__main__':unittest.main()