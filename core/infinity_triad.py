"""Three simultaneous lenses: negative wing, middle, positive wing.

The finite probes and one-sided/asymptotic claims are deliberately distinct.
Cardinalities are set sizes, not signed values on the extended real line.
This module uses only the Python standard library.
"""
from fractions import Fraction
import re

OPERATIONS = ("identity", "negate", "absolute", "square", "reciprocal", "sign")
SETS = {
    "N": (0, "Natural numbers", "aleph_0"),
    "Z": (0, "Integers", "aleph_0"),
    "Q": (0, "Rational numbers", "aleph_0"),
    "R": (1, "Real numbers", "2^aleph_0"),
    "P(N)": (1, "Subsets of the natural numbers", "2^aleph_0"),
    "P(R)": (2, "Subsets of the real numbers", "2^(2^aleph_0)"),
}

# These are mathematical results for the six explicitly supported functions.
# '0-' and '0+' denote directional approaches, not signed zeros as values.
LIMITS = {
    "identity":  ("-infinity", "0", "+infinity", "0-", "0+"),
    "negate":    ("+infinity", "0", "-infinity", "0+", "0-"),
    "absolute":  ("+infinity", "0", "+infinity", "0+", "0+"),
    "square":    ("+infinity", "0", "+infinity", "0+", "0+"),
    "reciprocal":("0-", "undefined", "0+", "-infinity", "+infinity"),
    "sign":      ("-1", "0", "+1", "-1", "+1"),
}
PROPERTIES = {
    "identity":   ("retained", "retained", "yes", "invertible for all real inputs"),
    "negate":     ("reversed", "retained", "yes", "invertible for all real inputs"),
    "absolute":   ("lost", "retained", "yes", "not one-to-one: x and -x share an output"),
    "square":     ("lost", "squared", "yes", "not one-to-one: x and -x share an output"),
    "reciprocal": ("retained", "reciprocal", "no", "invertible only for nonzero real inputs"),
    "sign":       ("retained", "lost", "yes", "not one-to-one: all positive inputs share +1"),
}
BOUNDARY = ("Finite probes do not prove a limit. This version's limit labels are "
            "pre-established mathematical results for six named functions. "
            "Cardinality describes the size of sets, not signed scalar magnitude; "
            "infinity minus infinity is not a defined scalar arithmetic operation.")


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Radius must be a positive decimal or simple fraction.")
    value = str(value).strip()
    if len(value) > 28 or not re.fullmatch(r"\d{1,7}(?:\.\d{1,7})?(?:/\d{1,7}(?:\.\d{1,7})?)?", value):
        raise ValueError("Radius must be a positive decimal or simple fraction.")
    try:
        radius = (Fraction(value.split("/")[0]) / Fraction(value.split("/")[1])
                  if "/" in value else Fraction(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("Radius denominator must be nonzero.") from exc
    if not 1 < radius <= 1_000_000:
        raise ValueError("Choose a radius greater than 1 and no more than 1,000,000.")
    return radius


def _str(v):
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _sign(v):
    return (v > 0) - (v < 0)


def _apply(operation, x):
    if operation == "identity":
        return x
    if operation == "negate":
        return -x
    if operation == "absolute":
        return abs(x)
    if operation == "square":
        return x * x
    if operation == "reciprocal":
        return 1 / x if x else None
    if operation == "sign":
        return Fraction(_sign(x))
    raise ValueError("Unsupported transformation.")


def _point(operation, x):
    output = _apply(operation, x)
    return {
        "input": _str(x), "input_polarity": _sign(x), "input_magnitude": _str(abs(x)),
        "defined": output is not None,
        "output": _str(output) if output is not None else None,
        "polarity": _sign(output) if output is not None else None,
        "magnitude": _str(abs(output)) if output is not None else None,
        "reconstruct_from_sign_and_magnitude": _str(Fraction(_sign(output)) * abs(output)) if output is not None else None,
    }


def _sweep(operation, distance):
    left, center, right = (_point(operation, x) for x in (-distance, Fraction(0), distance))
    return {
        "distance": _str(distance), "left": left, "middle": center, "right": right,
        "wing_outputs_equal": left["defined"] and right["defined"] and left["output"] == right["output"],
        "both_wings_defined": left["defined"] and right["defined"],
    }


def _cardinals(left, right):
    if not isinstance(left, str) or not isinstance(right, str) or left not in SETS or right not in SETS:
        raise ValueError("Unknown set. Choose N, Z, Q, R, P(N), or P(R).")
    a, b = SETS[left], SETS[right]
    relation = "=" if a[0] == b[0] else ("<" if a[0] < b[0] else ">")
    return {
        "left": {"set": left, "description": a[1], "cardinality": a[2]},
        "right": {"set": right, "description": b[1], "cardinality": b[2]},
        "relation": relation,
        "why": ("Same known cardinality. Infinite sets may admit a bijection despite different descriptions."
                if relation == "=" else
                "Known strict size inequality; Cantor's diagonal/power-set arguments establish the gap."),
        "boundary": "Cardinality has no positive/negative sign and is not absolute value of a scalar.",
    }



def _trajectories():
    """Exact sample of three reference paths and a sign-alternating divergence."""
    samples = []
    for n in range(1, 9):
        samples.append({"n": n, "negative": -n, "middle": 0, "positive": n,
                        "alternating": (-1) ** n * n, "alternating_magnitude": n})
    return {
        "samples": samples,
        "proven_limits": {"negative": "-infinity", "middle": "0",
                          "positive": "+infinity", "alternating": "no extended-real limit",
                          "alternating_magnitude": "+infinity"},
        "proof_outline": "Even n give +n toward +infinity; odd n give -n toward -infinity. "
                         "Thus (-1)^n*n has no extended-real limit, while its absolute value equals n "
                         "and tends to +infinity. Finite samples illustrate, but do not establish, this proof.",
    }

def investigate(payload):
    """Compute three-point far and near probes plus separate set-cardinality evidence."""
    if not isinstance(payload, dict):
        raise ValueError("Input must be an object.")
    operation = payload.get("operation", "absolute")
    if operation not in OPERATIONS:
        raise ValueError("Unsupported transformation.")
    radius = _number(payload.get("radius", "10"))
    near = Fraction(1, 1) / radius
    asym = LIMITS[operation]
    sign, magnitude, zero, invert = PROPERTIES[operation]
    return {
        "method": "Both sides and middle / three-lens probe",
        "operation": operation,
        "radius": _str(radius),
        "far": _sweep(operation, radius),
        "near_zero": _sweep(operation, near),
        "trajectories": _trajectories(),
        "limits": {
            "as_x_to_negative_infinity": asym[0], "at_zero": asym[1],
            "as_x_to_positive_infinity": asym[2],
            "as_x_to_zero_from_negative": asym[3],
            "as_x_to_zero_from_positive": asym[4],
        },
        "information": {
            "polarity": sign, "magnitude": magnitude,
            "defined_at_zero": zero == "yes", "global_invertibility": invert,
            "reconstruction": "For each defined real output y, sign(y) times abs(y) equals y. "
                              "This does not mean y determines its original input x.",
        },
        "cardinality": _cardinals(payload.get("cardinal_left", "N"),
                                 payload.get("cardinal_right", "R")),
        "interpretation_boundary": BOUNDARY,
    }
