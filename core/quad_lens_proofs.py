"""Ultimodel' Quad-Lens: adjustable validated proof-obligation threshold.

Only polynomials in x (degree <= 10) are accepted for exact symbolic
verification. No finite observations constitute a proof of global equality.
"""
import ast
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

MAX_DEGREE = 10


def _trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    if len(p) - 1 > MAX_DEGREE:
        raise ValueError('Polynomial degree limit exceeded (10).')
    return tuple(p)


def _add(a, b):
    return _trim([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0))
                  for i in range(max(len(a), len(b)))])


def _mul(a, b):
    if len(a) + len(b) - 2 > MAX_DEGREE and any(a) and any(b):
        raise ValueError('Polynomial degree limit exceeded (10).')
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, u in enumerate(a):
        for j, v in enumerate(b):
            out[i+j] += u*v
    return _trim(out)


def parse_polynomial(source):
    """Parse a restricted expression; never eval or execute user code."""
    if not isinstance(source, str) or not 1 <= len(source.strip()) <= 200:
        raise ValueError('Expression must contain 1-200 characters.')
    try:
        tree = ast.parse(source.replace('^', '**'), mode='eval')
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError('Invalid polynomial expression.') from exc
    if len(list(ast.walk(tree))) > 90:
        raise ValueError('Expression is too complex.')

    def walk(n):
        if isinstance(n, ast.Name) and n.id == 'x':
            return (Fraction(0), Fraction(1))
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            if abs(n.value) > 1e12:
                raise ValueError('Constant out of bounds.')
            return (Fraction(str(n.value)),)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            p = walk(n.operand)
            return tuple(-c for c in p) if isinstance(n.op, ast.USub) else p
        if isinstance(n, ast.BinOp):
            if isinstance(n.op, ast.Pow):
                if not isinstance(n.right, ast.Constant) or type(n.right.value) is not int or not 0 <= n.right.value <= 10:
                    raise ValueError('Exponent must be a whole number 0..10.')
                p, out = walk(n.left), (Fraction(1),)
                for _ in range(n.right.value):
                    out = _mul(out, p)
                return out
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Add): return _add(a, b)
            if isinstance(n.op, ast.Sub): return _add(a, tuple(-c for c in b))
            if isinstance(n.op, ast.Mult): return _mul(a, b)
            if isinstance(n.op, ast.Div) and len(b) == 1 and b[0]:
                return _trim([c / b[0] for c in a])
        raise ValueError('Only polynomials in x with rational arithmetic are supported.')

    return _trim(walk(tree.body))


def value(coefficients, x):
    """Horner evaluation in exact rational arithmetic."""
    y = Fraction(0)
    for c in reversed(coefficients):
        y = y*x + c
    return y


def proof_obligations(coefficients, center):
    """Different checkable mathematical claims, one credit per claim ID.

    Count measures scope of verified claims, NOT independent confirmations
    of a single theorem.
    """
    degree = len(coefficients)-1
    odd = any(c for i,c in enumerate(coefficients) if i%2)
    even = any(c for i,c in enumerate(coefficients) if not i%2)
    parity = 'both' if not odd and not even else 'even' if not odd else 'odd' if not even else 'neither'
    certs = [
        {'id':'real_domain_continuity', 'claim':'The polynomial is defined and continuous at every real x.',
         'verification':'Polynomials are finite sums/products of continuous real-valued monomials.',
         'scope':'all real numbers'},
        {'id':'exact_center_value', 'claim':f'f({center}) = {value(coefficients, center)}.',
         'verification':'Exact Horner evaluation over rational coefficients and rational center.',
         'scope':'the stated center only'},
        {'id':'parity', 'claim':f'The polynomial has parity class {parity}.',
         'verification':f'Coefficient parity: nonzero odd powers={odd}; nonzero even powers={even}; equivalently compare p(-x) with +/-p(x).',
         'scope':'all real numbers'},
    ]
    if degree == 0:
        tail = f'Both x to negative infinity and x to positive infinity have limit {coefficients[0]}.'
    else:
        sign = 1 if coefficients[-1] > 0 else -1
        right = '+infinity' if sign > 0 else '-infinity'
        left = '+infinity' if sign*(-1)**degree > 0 else '-infinity'
        tail = f'The leading term gives p(x) -> {left} as x -> -infinity and p(x) -> {right} as x -> +infinity.'
    certs.append({'id':'two_sided_tail', 'claim':tail,
                  'verification':f'Polynomial degree={degree}, leading coefficient={coefficients[-1]}.',
                  'scope':'asymptotic behavior of this polynomial'})

    locations = list(map(Fraction, (-3,-2,-1,0,1,2,3)))
    seen = {}
    for x in locations:
        y = value(coefficients, x)
        if y in seen:
            witness = (seen[y], x, y)
            certs.append({'id':'noninjectivity_witness',
                          'claim':f'Distinct inputs {witness[0]} and {witness[1]} both give {witness[2]}; p is not injective.',
                          'verification':'Exact evaluation of two different rational inputs with identical outputs.',
                          'scope':'all real numbers (existential counterexample)'})
            break
        seen[y] = x
    if degree == 1:
        certs.append({'id':'linear_injectivity',
                      'claim':'Nonzero-slope linear polynomial is strictly monotone and injective.',
                      'verification':f'For x!=y, p(x)-p(y)={coefficients[1]}(x-y)!=0.',
                      'scope':'all real numbers'})
    return certs


def run(expression='x^2', *, left='-10', right='10',
        tolerance='1/100', min_validated_proofs=3, max_rounds=32):
    """Inspect in rounds while searching for at least N distinct proof claims.

    Stop as verified only when BOTH the proof threshold and width criterion
    are met. An unreachable proof threshold is explicitly reported.
    """
    if type(min_validated_proofs) is not int or not 1 <= min_validated_proofs <= 12:
        raise ValueError('min_validated_proofs must be an integer from 1 to 12.')
    if type(max_rounds) is not int or not 1 <= max_rounds <= 128:
        raise ValueError('max_rounds must be an integer from 1 to 128.')
    try:
        a, b, tol = Fraction(left), Fraction(right), Fraction(tolerance)
    except (TypeError, ValueError, ZeroDivisionError) as exc:
        raise ValueError('Bounds and tolerance must be finite rational values.') from exc
    if not a < b or not 0 < tol <= (b-a):
        raise ValueError('Require left < right and a positive tolerance no larger than the interval.')
    if max(abs(a), abs(b)) > 1000000 or tol.denominator > 100000000:
        raise ValueError('Bounds or tolerance exceed prototype limits.')
    c = (a+b)/2
    polynomial = parse_polynomial(expression)
    candidates = proof_obligations(polynomial, c)
    certificates, history = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for index in range(max_rounds):
            m_left, m_right = (a+c)/2, (c+b)/2
            points = (a, m_left, m_right, b)
            values = tuple(pool.map(lambda x: value(polynomial, x), points))
            new_cert = candidates[index] if index < len(candidates) else None
            if new_cert is not None:
                certificates.append(new_cert)
            width = b-a
            history.append({'round':index, 'positions':tuple(map(str,points)),
                            'values':tuple(map(str,values)), 'width':str(width),
                            'new_proof':new_cert['id'] if new_cert else None,
                            'validated_proofs':len(certificates)})
            numerical_met = width <= 2*tol
            proof_met = len(certificates) >= min_validated_proofs
            if numerical_met and proof_met:
                status='validated_threshold_met'
                break
            if numerical_met and len(certificates) == len(candidates) and not proof_met:
                status='insufficient_distinct_proofs'
                break
            a, b = m_left, m_right
        else:
            status='round_cap_before_threshold'
    return {'expression':expression, 'center':str(c), 'min_validated_proofs':min_validated_proofs,
            'validated_count':len(certificates), 'available_distinct_proofs':len(candidates),
            'proofs':certificates, 'history':history, 'status':status,
            'numerical_tolerance':str(tol),
            'limits':'Only distinct validated claims in a restricted polynomial model count; samples do not prove global symmetry. Claim count is not a probability, or independent confirmations of one proposition.'}
