"""Regression tests for simultaneous opposite wings and middle, plus cardinality."""
import unittest
from fractions import Fraction
from core.infinity_triad import investigate, OPERATIONS, SETS, _number, _point


class TriadTests(unittest.TestCase):
    def probe(self, **data):
        return investigate({"radius": "10", **data})

    def test_all_operations_have_all_three_lenses(self):
        for op in OPERATIONS:
            with self.subTest(op=op):
                data = self.probe(operation=op)
                self.assertEqual(set(data["far"][k]["input"] for k in ("left", "middle", "right")), {"-10", "0", "10"})
                self.assertEqual(set(data["near_zero"][k]["input"] for k in ("left", "middle", "right")), {"-1/10", "0", "1/10"})
                self.assertEqual(data["operation"], op)

    def test_reconstruction_for_every_defined_output(self):
        for op in OPERATIONS:
            for x in (Fraction(-10), Fraction(-1, 10), Fraction(0), Fraction(1, 10), Fraction(10)):
                with self.subTest(op=op, x=str(x)):
                    p = _point(op, x)
                    if p["defined"]:
                        self.assertEqual(p["output"], p["reconstruct_from_sign_and_magnitude"])
                    else:
                        self.assertEqual(op, "reciprocal")
                        self.assertEqual(x, 0)

    def test_absolute_loses_wing_sign(self):
        x = self.probe(operation="absolute")
        self.assertTrue(x["far"]["wing_outputs_equal"])
        self.assertEqual(x["far"]["left"]["output"], "10")
        self.assertEqual(x["far"]["right"]["output"], "10")
        self.assertEqual(x["information"]["polarity"], "lost")

    def test_square_loses_sign_but_grows_magnitude(self):
        x = self.probe(operation="square")
        self.assertEqual(x["far"]["left"]["output"], "100")
        self.assertTrue(x["far"]["wing_outputs_equal"])
        self.assertEqual(x["limits"]["as_x_to_negative_infinity"], "+infinity")

    def test_negation_swaps_polarity(self):
        x = self.probe(operation="negate")
        self.assertEqual(x["far"]["left"]["output"], "10")
        self.assertEqual(x["far"]["right"]["output"], "-10")
        self.assertFalse(x["far"]["wing_outputs_equal"])

    def test_reciprocal_zero_is_undefined(self):
        x = self.probe(operation="reciprocal")
        self.assertFalse(x["near_zero"]["middle"]["defined"])
        self.assertIsNone(x["near_zero"]["middle"]["output"])
        self.assertEqual(x["near_zero"]["left"]["output"], "-10")
        self.assertEqual(x["near_zero"]["right"]["output"], "10")
        self.assertEqual(x["limits"]["as_x_to_zero_from_negative"], "-infinity")
        self.assertEqual(x["limits"]["as_x_to_zero_from_positive"], "+infinity")

    def test_sign_loses_magnitude_not_sign(self):
        x = self.probe(operation="sign")
        self.assertEqual(x["far"]["left"]["output"], "-1")
        self.assertEqual(x["near_zero"]["left"]["output"], "-1")
        self.assertEqual(x["information"]["magnitude"], "lost")
        self.assertEqual(x["limits"]["at_zero"], "0")

    def test_radius_fractions_and_decimals(self):
        self.assertEqual(_number("5/2"), Fraction(5, 2))
        self.assertEqual(_number("2.5"), Fraction(5, 2))
        self.assertEqual(_number("10/2"), Fraction(5))

    def test_bad_radius(self):
        for value in ("0", "1", "1/2", "0/0", "2/0", "-2", "1e6", "infinity", "10**999", "1000001", {}, None, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.probe(radius=value)

    def test_bad_operation_and_set(self):
        for payload in ({"operation": "sin"}, {"operation": "__import__"},
                        {"cardinal_left": "omega"}, {"cardinal_right": "∞"}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.probe(**payload)

    def test_countable_bijections(self):
        for name in ("N", "Z", "Q"):
            self.assertEqual(self.probe(cardinal_left=name, cardinal_right="N")["cardinality"]["relation"], "=")

    def test_continuum_equivalence(self):
        self.assertEqual(self.probe(cardinal_left="R", cardinal_right="P(N)")["cardinality"]["relation"], "=")

    def test_cantor_strict_increase(self):
        self.assertEqual(self.probe(cardinal_left="N", cardinal_right="P(N)")["cardinality"]["relation"], "<")
        self.assertEqual(self.probe(cardinal_left="R", cardinal_right="P(R)")["cardinality"]["relation"], "<")
        self.assertEqual(self.probe(cardinal_left="P(R)", cardinal_right="N")["cardinality"]["relation"], ">")

    def test_cardinality_is_not_signed_scalar(self):
        for left in SETS:
            for right in SETS:
                value = self.probe(cardinal_left=left, cardinal_right=right)["cardinality"]
                self.assertIn("not absolute value", value["boundary"])
                self.assertIn(value["relation"], ("<", "=", ">"))

    def test_no_unsupported_infinity_arithmetic(self):
        result = self.probe()
        self.assertIn("infinity minus infinity", result["interpretation_boundary"])
        self.assertNotIn("infinity", result["far"]["right"]["output"])
        self.assertIn("Finite probes do not prove", result["interpretation_boundary"])

    def test_simultaneous_trajectories(self):
        t = self.probe()["trajectories"]
        self.assertEqual(len(t["samples"]), 8)
        self.assertEqual(t["samples"][0], {"n": 1, "negative": -1, "middle": 0,
                                          "positive": 1, "alternating": -1,
                                          "alternating_magnitude": 1})
        self.assertEqual(t["samples"][7]["alternating"], 8)
        self.assertEqual(t["proven_limits"]["alternating"], "no extended-real limit")
        self.assertEqual(t["proven_limits"]["alternating_magnitude"], "+infinity")

    def test_all_limit_tables_complete(self):
        keys = {"as_x_to_negative_infinity", "at_zero", "as_x_to_positive_infinity",
                "as_x_to_zero_from_negative", "as_x_to_zero_from_positive"}
        for op in OPERATIONS:
            self.assertEqual(set(self.probe(operation=op)["limits"]), keys)

    def test_complementary_wings_for_identity(self):
        x = self.probe(operation="identity", radius="100")
        self.assertEqual(x["far"]["left"]["input_polarity"], -1)
        self.assertEqual(x["far"]["middle"]["input_polarity"], 0)
        self.assertEqual(x["far"]["right"]["input_polarity"], 1)
        self.assertEqual(x["near_zero"]["distance"], "1/100")
        self.assertEqual(x["information"]["global_invertibility"], "invertible for all real inputs")


if __name__ == "__main__":
    unittest.main()
