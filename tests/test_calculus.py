import math
import unittest
from core.instrument import compute

def calculate(source,rule,**kw):
    request=dict(A=source,B='0',t=2,rule=rule,plots=[])
    request.update(kw)
    return compute(request)

class CalculusTests(unittest.TestCase):
    def test_free_function(self):
        q=calculate('f(x)=3x^2+sinh(x)','derivative',polarity=-.5)
        self.assertAlmostEqual(q['quantities']['derivative']['value'],-.5*(12+math.cosh(2)))
    def test_anchored_integral_and_reverse(self):
        for a,b in [(0,2),(2,0),(2,2)]:
            q=calculate('f(x)=x^2','integral',anchor=a,t=b,polarity=-1)
            self.assertAlmostEqual(q['quantities']['integral']['value'],(a**3-b**3)/3)
            self.assertIn('+ C',q['antiderivative'])
    def test_special_integral(self):
        q=calculate('exp(-t^2)','integral',t=1)
        self.assertAlmostEqual(q['quantities']['integral']['value'],0.7468241328,8)
    def test_pole_even_at_neutral(self):
        q=calculate('1/(t-.25)','integral',polarity=0)
        self.assertIsNone(q['quantities']['integral']['value'])
    def test_promote_compose_and_differentiate(self):
        r=dict(name='J',kind='promotion',A='f(x)=2x',B='0',lens='A',polarity=-1,
               result='integral',anchor=1)
        q=calculate('J(t+1)','derivative',variables=[r])
        self.assertEqual(q['quantities']['A']['value'],-8)
        self.assertEqual(q['quantities']['derivative']['value'],-6)
    def test_reference_and_difference(self):
        q=calculate('t','integral',B='t^2',lens='B',sample_step=1)
        self.assertEqual(q['difference_table']['values'],[4,9,16])
        self.assertAlmostEqual(q['quantities']['integral']['value'],8/3)
