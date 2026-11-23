"""Adversarial and exact-reconstruction checks for Triadic HEX v0.1."""
import hashlib
import os
import random
import struct
import tempfile
import unittest
from pathlib import Path
from triadic_hex import (encode,decode,HEADER,NODE,LEAF,BRANCH,MAGIC,
                         MAX_DEPTH,TRANSFORMS)

class TriadicTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def cycle(self,source,depth=3,quality=4,delete_input=False):
        original=self.root/'source.bin'; packed=self.root/'archive.ut3'; recovered=self.root/'restored.bin'
        original.write_bytes(source)
        info=encode(original,packed,depth=depth,quality=quality)
        if delete_input: original.unlink()
        res=decode(packed,recovered)
        self.assertEqual(source,recovered.read_bytes())
        self.assertEqual(hashlib.sha256(source).hexdigest(),res['sha256'])
        self.assertEqual(info['source_bytes'],len(source))
        self.assertEqual(info['archive_bytes'],packed.stat().st_size)
        self.assertEqual(res['node_count'],info['node_count'])
        return info,packed,recovered
    def test_empty(self): self.cycle(b'',depth=5)
    def test_one_two_three_bytes(self):
        for depth in (0,1,5):
            for n in (1,2,3):self.cycle(bytes(range(n)),depth=depth)
    def test_all_256_bytes(self):self.cycle(bytes(range(256)),delete_input=True)
    def test_all_65536_two_byte_combinations(self):
        b=b''.join(bytes((i,j)) for i in range(256) for j in range(256))
        self.cycle(b,depth=5,delete_input=True)
    def test_random_lengths_and_depths(self):
        rng=random.Random(1199)
        for depth in (0,1,2,3,4,5,6):
            for length in (0,1,2,3,4,7,8,9,26,80,81,82,254,255,256,257,4095,4096,4097):
                with self.subTest(depth=depth,length=length):
                    self.cycle(rng.randbytes(length),depth=depth)
    def test_large_random_block(self):
        rng=random.Random(42)
        self.cycle(rng.randbytes(3*65536),depth=5)
    def test_repetitions_are_deduplicated(self):
        rng=random.Random(123)
        unit=rng.randbytes(4096)
        info,_,_=self.cycle(unit*9,depth=2,delete_input=True)
        self.assertGreater(info['selection_counts'].get('deduplicated_leaves',0),0)
        self.assertLess(info['leaf_count'],9)
    def test_subtree_merges(self):
        rng=random.Random(123)
        unit=rng.randbytes(4096)
        info,_,_=self.cycle(unit*27,depth=3)
        self.assertGreater(info['selection_counts'].get('deduplicated_branches',0),0)
    def test_random_seed_reproducible(self):
        rng=random.Random(333)
        block=rng.randbytes(32768)*3
        a,packed,_=self.cycle(block,depth=3)
        bs=packed.read_bytes()
        self.cycle(block,depth=3)
        self.assertEqual(packed.read_bytes(),bs)
    def test_source_deleted(self): self.cycle(b'\0\xffrandom\x80'*1024,depth=3,delete_input=True)
    def test_source_overwrite_guard(self):
        src=self.root/'source.bin';src.write_bytes(b'protected')
        with self.assertRaises(ValueError):encode(src,src)
        self.assertEqual(src.read_bytes(),b'protected')
        arch=self.root/'archive.ut3';encode(src,arch)
        orig=arch.read_bytes()
        with self.assertRaises(ValueError):decode(arch,arch)
        self.assertEqual(arch.read_bytes(),orig)
    def test_invalid_requested_depth(self):
        src=self.root/'source.bin';src.write_bytes(b'abcdef')
        with self.assertRaises(ValueError):encode(src,self.root/'x',depth=MAX_DEPTH+1)
        with self.assertRaises(ValueError):encode(src,self.root/'x',depth=-1)
    def test_version_corruption(self):
        _,packed,out=self.cycle(b'abc'*200)
        raw=bytearray(packed.read_bytes());raw[8]=99;packed.write_bytes(raw)
        with self.assertRaises(ValueError):decode(packed,out)
    def test_corrupted_payload_rejected_without_overwriting_output(self):
        _,packed,out=self.cycle(b'abcdef'*450,depth=1)
        orig=out.read_bytes()
        raw=bytearray(packed.read_bytes())
        raw[-1]^=1
        packed.write_bytes(raw)
        with self.assertRaises(Exception):decode(packed,out)
        self.assertEqual(out.read_bytes(),orig)
    def test_truncated_archive(self):
        _,packed,out=self.cycle(b'abcdef'*50,depth=3)
        raw=packed.read_bytes();packed.write_bytes(raw[:-1])
        with self.assertRaises(ValueError):decode(packed,out)
    def test_trailing_garbage(self):
        _,packed,out=self.cycle(b'abc'*100)
        with packed.open('ab') as f:f.write(b'!')
        with self.assertRaisesRegex(ValueError,'Trailing'):decode(packed,out)
    def test_metadata_wrong_size(self):
        _,packed,out=self.cycle(b'abc'*100)
        data=bytearray(packed.read_bytes())
        data[10:18]=struct.pack('>Q',1)
        packed.write_bytes(data)
        with self.assertRaises(ValueError):decode(packed,out)
    def test_unknown_transform_rejected(self):
        _,packed,out=self.cycle(b'abcdef',depth=0)
        data=bytearray(packed.read_bytes())
        data[HEADER.size+NODE.size]=255
        packed.write_bytes(data)
        with self.assertRaises(ValueError):decode(packed,out)
    def test_codec_transforms_all_inverse(self):
        rng=random.Random(77)
        for name,(forward,reverse) in TRANSFORMS.items():
            for length in (0,1,2,3,4,7,8,9,31,64,257):
                b=rng.randbytes(length)
                self.assertEqual(reverse(forward(b),len(b)),b, (name,length))
    def test_depth_0_branchless(self):
        info,_,_=self.cycle(b'hello world'*7,depth=0)
        self.assertEqual(info['branch_count'],0)
    def test_length_and_bytewise_checks(self):
        content=b'data\x00'*999
        info,_,restored=self.cycle(content,depth=5)
        self.assertEqual(restored.stat().st_size,len(content))
        self.assertTrue(info['leaf_count']<=3**5)

if __name__=='__main__':unittest.main()
