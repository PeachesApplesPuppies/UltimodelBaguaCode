import json
import unittest

from core.instrument import compute


class ColorTest(unittest.TestCase):
    def record(self, f, m):
        result = compute(dict(A="1", B="1", plots=[], frequency=f, magnitude=m, t=2))
        return json.loads(json.dumps(result, allow_nan=False))["color_contrast"]

    def test_factors_survive_export(self):
        for f, m in [(0, 4), (4, 0), (0, 0), (2, 6), (3, 4)]:
            record = self.record(str(f), str(m))
            self.assertEqual([record[k]["value"] for k in ("frequency","magnitude","product")],
                             [f, m, f*m])

    def test_expression_and_missing(self):
        record = self.record("t+1", "")
        self.assertEqual(record["frequency"]["source"], "t+1")
        self.assertEqual(record["frequency"]["value"], 3)
        self.assertIsNone(record["product"]["value"])

    def test_zero_and_undefined(self):
        record = self.record("0", "1/(t-2)")
        self.assertEqual(record["frequency"]["value"], 0)
        self.assertIsNone(record["product"]["value"])

    def test_visual_codes(self):
        def code(f, m):
            return self.record(str(f), str(m))["visual"]
        self.assertNotEqual(code(2, 6)["hex"], code(6, 2)["hex"])
        self.assertAlmostEqual(code(-2, -6)["angle_degrees"] - code(2, 6)["angle_degrees"], 180)
        self.assertEqual([code(f,m)["angle_degrees"] for f,m in [(0,4),(4,0),(0,0)]], [90,0,None])
        self.assertGreaterEqual(code(2,6)["contrast_ratio"], 4.5)
        self.assertIsNone(code("1/0", 1))

    def test_element_color_polarity(self):
        a,b="element(H, Z)","element(O, Z)"
        colors=[]
        for polarity in (-1,0,1):
            result=compute(dict(A=a,B=b,frequency=a,magnitude=b,polarity=polarity,plots=[]))
            code=result["color_contrast"]
            self.assertEqual(code["product"]["value"],8)
            self.assertEqual(code["visual"]["display_product"],8*polarity)
            colors.append(code["visual"]["hex"])
        self.assertEqual(len(set(colors)),3)
        self.assertEqual(len(set(colors[1][i:i+2] for i in (1,3,5))),1)
