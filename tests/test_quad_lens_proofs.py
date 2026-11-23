"""Regression tests for Quad-Lens adjustable validated-proof threshold."""
import unittest
from fractions import Fraction
from core.quad_lens_proofs import parse_polynomial, value, proof_obligations, run


class ProofThresholdTests(unittest.TestCase):
    def test_polynomial_parser_and_exact_value(self):
        p=parse_polynomial('x^2+x*(x^2-100)*(x^2-1/100)')
        self.assertEqual(value(p,Fraction(5)),-Fraction(934625,100))

    def test_minimum_changes_depth(self):
        shallow=run('x^2',tolerance='5',min_validated_proofs=1)
        deeper=run('x^2',tolerance='5',min_validated_proofs=5)
        self.assertEqual(shallow['status'],'validated_threshold_met')
        self.assertEqual(deeper['status'],'validated_threshold_met')
        self.assertLess(len(shallow['history']),len(deeper['history']))
        self.assertLess(shallow['validated_count'],deeper['validated_count'])

    def test_impossible_threshold_fails_explicitly(self):
        r=run('x^3',tolerance='5',min_validated_proofs=12)
        self.assertEqual(r['status'],'insufficient_distinct_proofs')
        self.assertLess(r['validated_count'],12)

    def test_old_spoofer_fails_symbolic_parity(self):
        even=run('x^2',tolerance='5',min_validated_proofs=3)
        spoof=run('x^2+x*(x^2-100)*(x^2-1/100)',tolerance='5',min_validated_proofs=3)
        self.assertIn('even',next(p for p in even['proofs'] if p['id']=='parity')['claim'])
        self.assertIn('neither',next(p for p in spoof['proofs'] if p['id']=='parity')['claim'])

    def test_noninjectivity_witness_is_exact(self):
        p=proof_obligations(parse_polynomial('x^2'),Fraction(0))
        self.assertEqual(sum(x['id']=='noninjectivity_witness' for x in p),1)

    def test_linear_injectivity_not_false_collision(self):
        p=proof_obligations(parse_polynomial('5*x+3'),Fraction(0))
        self.assertTrue(any(x['id']=='linear_injectivity' for x in p))
        self.assertFalse(any(x['id']=='noninjectivity_witness' for x in p))

    def test_half_interval_preserves_center(self):
        result=run('x^2')
        for previous,current in zip(result['history'],result['history'][1:]):
            self.assertEqual(Fraction(current['width']),Fraction(previous['width'])/2)
            self.assertEqual(current['positions'][0],previous['positions'][1])
            self.assertEqual(current['positions'][3],previous['positions'][2])

    def test_never_count_samples_as_proofs(self):
        result=run('x^2')
        self.assertTrue(all(p['id']!='samples_matched' for p in result['proofs']))

    def test_reject_malformed_inputs(self):
        for number in (0,13,True,1.5,-1,'2'):
            with self.assertRaises(ValueError):run(min_validated_proofs=number)
        for equation in ('1/x','__import__("os")','sin(x)','x**-1','a*x','x^11'):
            with self.assertRaises(ValueError):run(equation)

    def test_round_cap(self):
        r=run('x^2',tolerance='1/100000',min_validated_proofs=5,max_rounds=2)
        self.assertEqual(r['status'],'round_cap_before_threshold')

    def test_rational_evaluation_fuzz(self):
        import random
        rng=random.Random(813)
        for _ in range(2000):
            a,b,c=(rng.randint(-100,100) for _ in range(3))
            x=Fraction(rng.randint(-12,12),rng.randint(1,12))
            p=parse_polynomial(f'{a}*x^2+{b}*x+{c}')
            self.assertEqual(value(p,x),a*x*x+b*x+c)


if __name__=='__main__':
    unittest.main()
