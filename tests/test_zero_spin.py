import unittest
from core.instrument import compute

def calculate(a,b,c,**options):
    return compute(dict(A=a,B=b,spin_C=c,t=0,plots=[],**options))["zero_spin"]

class ZeroSpinTests(unittest.TestCase):
    def test_three_readings(self):
        r=calculate("1","1","0",reading_only=True)
        self.assertEqual([s["delta"]["value"] for s in r["steps"]],[0,-1,1])
        self.assertEqual([s["quotient"]["value"] for s in r["steps"]],[1,None,0])
        self.assertTrue(all(pt["rate"]["status"].startswith("undetermined") for pt in r["points"].values()))
    def test_rates_at_zero(self):
        r=calculate("t","-t","0",lens="B")
        self.assertEqual([pt["rate"]["value"] for pt in r["points"].values()],[1,-1,0])
        self.assertTrue(all(pt["sign"]=="neutral" for pt in r["points"].values()))
        self.assertTrue(all("every real q" in s["reason"] for s in r["steps"]))
        self.assertEqual([s["pair"] for s in r["steps"]],["B → A","A → C","C → B"])
    def test_undefined_input(self):
        pt=calculate("1/t","0","1")["points"]["A"]
        self.assertIsNone(pt["value"]["value"])
        self.assertIsNone(pt["rate"]["value"])
