"""Equal-budget adversarial comparison, not a claim of universal superiority."""
import random
import unittest
from fractions import Fraction
from core.infinity_triad import OPERATIONS, _point, investigate

R=Fraction(10)
TRI=(-R,-1/R,Fraction(0),1/R,R)
POS=(Fraction(0),1/R,R/2,R,2*R)
NEG=(Fraction(0),-1/R,-R/2,-R,-2*R)

def collision(fn, samples):
    values=[fn(x) for x in samples]
    return len(values) != len(set(values))

class TestTriadAdversarial(unittest.TestCase):
    def test_equal_sampling_budget(self):
        self.assertEqual(len(TRI),len(POS))
        self.assertEqual(len(TRI),len(NEG))

    def test_even_sign_erasure(self):
        for a in range(1,26):
            funcs=(lambda x,a=a:a*x*x,lambda x,a=a:a*abs(x),
                   lambda x,a=a:x**4+a*x*x,
                   lambda x,a=a:1/(1+a*x*x))
            for f in funcs:
                self.assertTrue(collision(f,TRI))
                self.assertFalse(collision(f,POS))
                self.assertFalse(collision(f,NEG))

    def test_injective_controls(self):
        for a in range(1,26):
            funcs=(lambda x,a=a:a*x,lambda x,a=a:a*x**3,
                   lambda x,a=a:a*x**5,lambda x,a=a:x+a*x**3)
            for f in funcs:
                for xs in (TRI,POS,NEG):
                    self.assertFalse(collision(f,xs))

    def test_plateau_collisions(self):
        for a in range(1,26):
            f=lambda x,a=a:a*((x>0)-(x<0))
            for xs in (TRI,POS,NEG):
                self.assertTrue(collision(f,xs))

    def test_interior_collisions_missed_by_triad(self):
        for a in range(1,26):
            f=lambda x,a=a:a*x*(x-R/2)
            g=lambda x,a=a:a*x*(x+R/2)
            self.assertTrue(collision(f,POS))
            self.assertTrue(collision(g,NEG))
            self.assertFalse(collision(f,TRI))
            self.assertFalse(collision(g,TRI))

    def test_sample_spoofing_breaks_global_evenness_inference(self):
        h=lambda x:x*(x*x-R*R)*(x*x-(1/R)**2)
        f=lambda x:x*x
        g=lambda x:x*x+h(x)
        self.assertTrue(all(f(x)==g(x) for x in TRI))
        self.assertNotEqual(g(R/2),g(-R/2))
        self.assertNotEqual(f(R/2),g(R/2))

    def test_sample_spoofing_breaks_identity_inference(self):
        h=lambda x:x*(x*x-R*R)*(x*x-(1/R)**2)
        self.assertTrue(all(x==x+h(x) for x in TRI))
        self.assertNotEqual(R/2,R/2+h(R/2))

    def test_undefined_zero_is_preserved(self):
        result=investigate({'operation':'reciprocal','radius':'10'})
        self.assertFalse(result['far']['middle']['defined'])
        self.assertFalse(result['near_zero']['middle']['defined'])
        self.assertEqual(result['limits']['as_x_to_zero_from_negative'],'-infinity')

    def test_sign_and_magnitude_reconstruct_output_only(self):
        for op in OPERATIONS:
            for radius in ('2','3','10','1000000','20/3'):
                result=investigate({'operation':op,'radius':radius})
                for mode in ('far','near_zero'):
                    for lens in ('left','middle','right'):
                        observation=result[mode][lens]
                        if observation['defined']:
                            self.assertEqual(Fraction(observation['output']),
                                             observation['polarity']*Fraction(observation['magnitude']))

    def test_malformed_cardinality_inputs_are_validation_errors(self):
        for bad in ([],{},True,False,3,None):
            for key in ('cardinal_left','cardinal_right'):
                with self.subTest(key=key,bad=str(bad)), self.assertRaises(ValueError):
                    investigate({key:bad})

    def test_seeded_random_exact_rational_checks(self):
        rng=random.Random(21023)
        for _ in range(300):
            r=Fraction(rng.randint(2,10000),rng.randint(1,1000))
            if r<=1:continue
            for op in OPERATIONS:
                result=investigate({'radius':str(r),'operation':op})
                self.assertEqual(result['far']['left'],_point(op,-r))
                self.assertEqual(result['far']['right'],_point(op,r))
                self.assertEqual(result['near_zero']['left'],_point(op,-1/r))
                self.assertEqual(result['near_zero']['right'],_point(op,1/r))

if __name__=='__main__':
    unittest.main()
