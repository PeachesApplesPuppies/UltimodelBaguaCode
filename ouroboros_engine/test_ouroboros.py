import unittest
from itertools import product
from math import lcm, ceil
from ouroboros import Ouroboros, Lens, modulo_lenses

class Tests(unittest.TestCase):
    def roundtrips(self, m, ids=None):
        for x in m.domain:
            obs, code = m.encode(x, ids)
            self.assertEqual(m.decode(obs, code, ids), x)
            self.assertEqual(len(code), m.analyze(ids)['supplement_bits'])

    def test_two_eyes(self):
        m = Ouroboros(range(15), modulo_lenses([3,5]))
        self.assertEqual(m.candidates((1,),[0]), (1,4,7,10,13))
        self.assertEqual(m.candidates((3,),[1]), (3,8,13))
        self.assertEqual(m.encode(13), ((1,3),''))
        self.assertEqual(m.minimum_subsets(), [(0,1)])
        self.assertEqual([r['supplement_bits'] for r in m.trace()], [4,3,0])
        self.roundtrips(m)

    def test_non_coprime(self):
        m = Ouroboros(range(24),modulo_lenses([4,6]))
        self.assertEqual(m.candidates((1,1)), (1,13))
        self.assertEqual(m.analyze()['supplement_bits'],1)
        self.assertEqual(m.minimum_subsets(),[])
        self.roundtrips(m)

    def test_redundant(self):
        m = Ouroboros(range(15),modulo_lenses([3,3,5]))
        self.assertEqual(m.minimum_subsets(),[(0,2),(1,2)])
        self.assertEqual(m.trace()[2]['worst_case_bits_removed'],0)
        self.assertAlmostEqual(m.trace()[2]['uniform_information_gain_bits'],0)
        self.roundtrips(m)

    def test_token_and_rank(self):
        m=Ouroboros(product(range(8),repeat=2),[Lens('xor',lambda x:x[0]^x[1]),Lens('start',lambda x:x[0])])
        self.assertEqual(m.analyze([0])['supplement_bits'],3)
        self.assertEqual(m.analyze()['supplement_bits'],0)
        self.roundtrips(m,[0]); self.roundtrips(m)

    def test_arbitrary_lenses(self):
        m=Ouroboros(range(32),[Lens('low',lambda x:x&7),Lens('high',lambda x:x>>3),Lens('constant',lambda x:0)])
        self.assertEqual(m.minimum_subsets(),[(0,1)])
        self.assertEqual(m.minimum_subsets(2),[(0,)])
        self.assertEqual(m.minimum_subsets(5),[()])
        self.roundtrips(m,[]); self.roundtrips(m,[2]); self.roundtrips(m)

    def test_invalid(self):
        m=Ouroboros(range(5),modulo_lenses([2]))
        for obs,code in [((1,),'11'),((9,),'00'),((0,),'0'),((0,),'ab')]:
            with self.assertRaises(ValueError): m.decode(obs,code)
        with self.assertRaises(ValueError): m.analyze([0,0])
        with self.assertRaises(ValueError): Ouroboros([1,1],[])
        with self.assertRaises(ValueError): modulo_lenses([0])

    def test_exhaustive_modular_formula(self):
        cases=roundtrips=0
        for a,b,n in product(range(1,9),range(1,9),range(1,33)):
            m=Ouroboros(range(n),modulo_lenses([a,b]))
            self.assertEqual(m.analyze()['largest_fiber'],ceil(n/lcm(a,b)))
            for x in m.domain:
                obs,code=m.encode(x)
                self.assertEqual(m.decode(obs,code),x)
                roundtrips+=1
            cases+=1
        print(f'Exhaustive modular grid: {cases} configurations, {roundtrips} successful round trips')

if __name__=='__main__':unittest.main(verbosity=2)
