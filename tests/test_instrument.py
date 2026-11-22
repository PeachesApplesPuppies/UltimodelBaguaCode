import unittest
from core.instrument import compute
from core.mathcore import scalar, parse

def calc(a,b,lens="A",**kw):
    return compute(dict(A=a,B=b,lens=lens,plots=[],**kw))
def val(d,k):
    return d["quantities"][k]["value"]
class InstrumentTests(unittest.TestCase):
    def test_equal(self):
        d=calc("1","1")
        self.assertEqual([val(d,k) for k in ("delta","magnitude","X")],[0,0,1])
        self.assertEqual(d["comparison"],"A = B")
    def test_polarity_and_reduction(self):
        for a,b in [(1,2),(3,6),(-1,1),(5,2),(2,6)]:
            d=calc(str(a),str(b));flip=calc(str(a),str(b),"B")
            for key,expected in dict(A=a,B=b,delta=b-a,oppositeDelta=a-b,magnitude=abs(b-a),X=b/a,inverseX=a/b).items():
                self.assertEqual(val(d,key),expected)
            self.assertEqual(val(flip,"A"),a);self.assertEqual(val(flip,"B"),b)
            self.assertEqual(val(flip,"delta"),-val(d,"delta"))
            self.assertEqual(val(flip,"X"),a/b)
    def test_zero(self):
        d=calc("1","0");self.assertIsNone(val(d,"quotient"));self.assertEqual(val(d,"X"),0)
        self.assertIsNone(val(calc("1","0","B"),"X"))
        d=calc("0","0");self.assertIsNone(val(d,"X"));self.assertEqual(val(d,"delta"),0)
    def test_linear_constant_periodic_exponential(self):
        import math
        for a,b,t,delta,flow in [("t","2*t",4,4,1),("t","t+5",1,5,0),("sin(t)","cos(t)",0,1,-1),("exp(t)","1",0,0,-1)]:
            d=calc(a,b,t=t);self.assertAlmostEqual(val(d,"delta"),delta)
            self.assertAlmostEqual(val(d,"flow"),flow)
            self.assertAlmostEqual(val(calc(a,b,"B",t=t),"flow"),-flow)
    def test_hidden_pole(self):
        for a,b,k in [("t-.013","1","X"),("(t-.013)^2","1","X"),("tan(t)","0","A")]:
            pole=1.5707963267948966 if a=="tan(t)" else .013
            d=compute(dict(A=a,B=b,lo=-2,hi=2,plots=[k]))
            ss=d["plots"][k];self.assertGreaterEqual(len(ss),2)
            self.assertTrue(all(not (s[0][0]<pole<s[-1][0]) for s in ss))
    def test_hole_survives_promotion(self):
        reg=[dict(kind="promotion",name="R1",A="t",B="2*t",lens="A",result="X")]
        self.assertIsNone(val(calc("R1","1",variables=reg,t=0),"A"))
        self.assertEqual(val(calc("R1","1",variables=reg,t=2),"A"),2)
    def test_recursive_comparison(self):
        r=[dict(kind="promotion",name="R1",A="t",B="2*t",lens="B",result="delta"),
           dict(kind="variable",name="C",expression="5"),
           dict(kind="promotion",name="R2",A="R1",B="C",lens="A",result="delta")]
        self.assertEqual(val(calc("R2","C",variables=r,t=3),"A"),8)
        with self.assertRaises(ValueError):calc("1","2",variables=[dict(kind="variable",name="C",expression="C+1")])
    def test_guard_and_symbols(self):
        d=calc("1/t","1",t=0);self.assertIsNone(val(d,"flow"))
        d=calc("k*t","0");self.assertEqual(d["quantities"]["delta"]["status"],"symbolic")
        self.assertEqual(val(calc("k*t","0",parameters={"k":2},t=4),"flow"),-2)
        self.assertIsNone(val(calc("abs(t)","0",t=0),"flow"))
    def test_operators(self):
        d=calc("inv(2)+abs(-2)","delta(2,5)^2/ratio(6,3)")
        self.assertEqual(val(d,"A"),2.5);self.assertEqual(val(d,"B"),4.5)
        self.assertEqual(d["comparison"],"A < B")
    def test_invalid(self):
        for s in ["().__class__","__import__('os')","x[1]","lambda: 5","sin()","3//t"]:
            with self.assertRaises(ValueError):parse(s)
        with self.assertRaises(ValueError):calc("1","2",lo=2,hi=1)
if __name__=="__main__":unittest.main()

