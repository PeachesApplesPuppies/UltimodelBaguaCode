"""Auto-depth triadic HEX tests: exact reconstruction and adversarial checks."""
import hashlib
import random
import tempfile
import unittest
from pathlib import Path

import triadic_hex as tri
from autodepth_hex import encode, Planner


class AutoDepthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)

    def cycle(self, raw, **kwargs):
        original=self.root/'source.bin'
        container=self.root/'encoded.ut3'
        recovered=self.root/'restored.bin'
        original.write_bytes(raw)
        metrics=encode(original,container,**kwargs)
        original.unlink()  # genuine WAV-only-like source-absent reconstruction
        res=tri.decode(container,recovered)
        self.assertEqual(recovered.read_bytes(),raw)
        self.assertEqual(res['sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(metrics['archive_bytes'],container.stat().st_size)
        self.assertTrue(res['byte_exact_verified_against_root_hash'])
        self.assertLessEqual(metrics['chosen_depth'],metrics['max_depth'])
        self.assertLessEqual(metrics['expanded_regions'],metrics['max_split_explorations'])
        self.assertGreaterEqual(len(metrics['branch_trace']),1)
        self.assertEqual(metrics['branch_trace'][0]['address'],'root')
        self.assertEqual(metrics['branch_trace'][0]['bytes'],len(raw))
        return metrics,container,recovered

    def test_zero_and_tiny_files(self):
        for n in range(0,9):
            for depth in (0,1,5):
                with self.subTest(length=n,depth=depth):
                    self.cycle(bytes(range(n)),max_depth=depth,min_leaf=1,quality=2)

    def test_all_256_one_byte_values(self):
        self.cycle(bytes(range(256)),max_depth=4,min_leaf=32,quality=3)

    def test_exhaustive_65536_two_byte_combinations(self):
        raw=b''.join(bytes((a,b)) for a in range(256) for b in range(256))
        self.cycle(raw,max_depth=4,min_leaf=1024,quality=2)

    def test_random_sizes_and_alignment(self):
        rng=random.Random(4281)
        for mode in ('balanced','aligned'):
            for n in (0,1,2,3,47,48,49,255,256,257,512,1023,4095,4096,4103,32768):
                with self.subTest(mode=mode,n=n):
                    self.cycle(rng.randbytes(n),max_depth=4,min_leaf=256,
                               boundary_mode=mode,quality=2)

    def test_fuzzed_inputs(self):
        rng=random.Random(0xA9DF)
        for _ in range(40):
            n=rng.randrange(0,8000)
            self.cycle(rng.randbytes(n),max_depth=3,min_leaf=512,quality=1,
                       boundary_mode=rng.choice(('balanced','aligned')))

    def test_repeated_blocks_produce_shared_leaf(self):
        rng=random.Random(3)
        raw=rng.randbytes(100000)*3
        report,_,_=self.cycle(raw,max_depth=3,min_leaf=8192,quality=2)
        # Repetitions must be *capable* of sharing; whether it wins in archive
        # size depends on compressor window and data.
        self.assertGreaterEqual(report['planning_events'].get('matching_leaf_reused',0),1)

    def test_content_dependent_depth_can_vary(self):
        rng=random.Random(32)
        # Synthetic blocks with a larger duplicated span and nonduplicate
        # siblings. We assert exact reconstruction, NOT predetermined choices.
        part=rng.randbytes(98304)
        raw=part*3 + rng.randbytes(3*98304) + (b'abcde'*59000)
        self.cycle(raw,max_depth=5,min_leaf=8192,quality=2)

    def test_leaf_only_with_zero_depth(self):
        result,_,_=self.cycle(bytes(range(256))*25,max_depth=0,min_leaf=1)
        self.assertEqual(result['chosen_depth'],0)
        self.assertEqual(result['branch_count'],0)

    def test_budget_pruning_still_lossless(self):
        rng=random.Random(24)
        r,_,_=self.cycle(rng.randbytes(180000),max_depth=9,min_leaf=128,
                         max_evaluations=2,quality=1)
        self.assertGreaterEqual(r['planning_events'].get('budget_pruned',0),1)
        self.assertLessEqual(r['expanded_regions'],2)

    def test_input_output_path_protection(self):
        f=self.root/'a';f.write_bytes(b'untouched')
        with self.assertRaises(ValueError):encode(f,f)
        self.assertEqual(f.read_bytes(),b'untouched')

    def test_invalid_parameters(self):
        source=self.root/'a';source.write_bytes(b'hello')
        for opts in ({'max_depth':-1},{'max_depth':tri.MAX_DEPTH+1},
                     {'min_leaf':0},{'quality':12},{'boundary_mode':'unknown'},
                     {'max_evaluations':0}):
            with self.subTest(opts=opts):
                with self.assertRaises(ValueError):encode(source,self.root/'archive',**opts)

    def test_corruption_preserves_existing_destination(self):
        _,archive,restored=self.cycle(b'repeatedDATA'*5000,max_depth=4,min_leaf=256)
        old=restored.read_bytes()
        raw=bytearray(archive.read_bytes())
        raw[-1]^=1
        archive.write_bytes(raw)
        with self.assertRaises(Exception):tri.decode(archive,restored)
        self.assertEqual(restored.read_bytes(),old)

    def test_archives_deterministic(self):
        data=random.Random(12).randbytes(50000)
        _,archive,_=self.cycle(data,max_depth=4,min_leaf=1024,quality=2)
        a=archive.read_bytes()
        self.cycle(data,max_depth=4,min_leaf=1024,quality=2)
        self.assertEqual(archive.read_bytes(),a)

    def test_aligned_boundaries_offer_distinct_splits(self):
        p=Planner(b'A'*500000,quality=1,max_depth=3,min_leaf=1024,
                  boundary_mode='aligned',max_evaluations=100)
        cuts=list(p.boundaries(0,500000))
        self.assertGreaterEqual(len(set(cuts)),2)
        self.assertTrue(all(0<x<y<500000 for x,y in cuts))

    def test_auto_plan_dedup_cost_accounting(self):
        raw=random.Random(91).randbytes(2048)*3
        p=Planner(raw,quality=2,max_depth=2,min_leaf=256,
                  boundary_mode='balanced',max_evaluations=500)
        plan=p.calculate()
        self.assertEqual(plan.size,sum(r.bytes_on_disk for r in plan.records.values()))
        self.assertGreaterEqual(p.events['matching_leaf_reused'],1)


if __name__=='__main__':unittest.main()
