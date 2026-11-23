"""Offline equation-shape clustering with explicit interpretation boundaries.

This is alpha-equivalence of operator trees, NOT a symbolic algebra solver,
unit checker, or proof of shared physical laws. Inputs are parsed, not evaluated.
"""
import ast
from contextlib import closing
import hashlib
import itertools
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from uuid import UUID, uuid4

FUNCTIONS = frozenset("sin cos tan exp log ln log10 sqrt abs inv atan asin acos sinh cosh tanh".split())
OPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Pow: "^"}
MAX_VARIABLES = 7
MAX_EQUATIONS = 150
NOTE = ("Equal operator-tree shape under variable renaming only. This does not "
        "establish equivalent units, mechanisms, domains, causation, or validity. "
        "Check assumptions and counterexamples separately.")


def _parse_side(source):
    try:
        tree = ast.parse(source.replace("^", "**"), mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError("Invalid expression. Use explicit multiplication, e.g. m*a.") from exc
    if len(list(ast.walk(tree))) > 90:
        raise ValueError("Equation is too complex for this version.")

    def walk(n):
        if isinstance(n, ast.Name) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", n.id):
            if n.id in ("pi", "e"):
                return ("constant", n.id)
            if n.id in FUNCTIONS:
                raise ValueError("Functions require parentheses.")
            return ("var", n.id)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float):
            if abs(n.value) > 1e100:
                raise ValueError("Numeric constant is too large.")
            return ("number", str(Fraction(str(n.value))))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.UAdd, ast.USub)):
            child = walk(n.operand)
            if isinstance(n.op, ast.UAdd):
                return child
            if child[0] == "number":
                return ("number", str(-Fraction(child[1])))
            return ("neg", child)
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            return (OPS[type(n.op)], walk(n.left), walk(n.right))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id in FUNCTIONS and not n.keywords and len(n.args) == 1):
            return ("fn", n.func.id, walk(n.args[0]))
        raise ValueError("Only scalar operators, symbols, and listed unary functions are supported.")

    return walk(tree.body)


def _key(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True)


def _shape(n, mapping, algebra):
    op = n[0]
    if op == "var":
        return ("var", mapping[n[1]])
    if op in ("number", "constant"):
        return n
    if op == "fn":
        return ("fn", n[1], _shape(n[2], mapping, algebra))
    if op == "neg":
        return ("neg", _shape(n[1], mapping, algebra))
    if op in ("+", "*") and (op == "+" or algebra == "scalar"):
        items = []

        def gather(t):
            if t[0] == op:
                gather(t[1]); gather(t[2])
            else:
                items.append(_shape(t, mapping, algebra))

        gather(n)
        return (op, *sorted(items, key=_key))
    return (op, _shape(n[1], mapping, algebra), _shape(n[2], mapping, algebra))


def _display(n):
    if n[0] == "var":
        return "x" + str(n[1] + 1)
    if n[0] in ("number", "constant"):
        return n[1]
    if n[0] == "fn":
        return n[1] + "(" + _display(n[2]) + ")"
    if n[0] == "neg":
        return "-" + _display(n[1])
    if n[0] == "=":
        return _display(n[1]) + " = " + _display(n[2])
    return "(" + (" " + n[0] + " ").join(_display(part) for part in n[1:]) + ")"


def fingerprint(equation, algebra="scalar"):
    """Return stable relational signature and an aligned variable-role map."""
    if algebra not in ("scalar", "ordered"):
        raise ValueError("Choose scalar or ordered operator mode.")
    if not isinstance(equation, str) or not 3 <= len(equation.strip()) <= 240:
        raise ValueError("Enter an equation of 3–240 characters.")
    normalized = equation.replace("−", "-").replace("×", "*").replace("÷", "/").strip()
    sides = normalized.split("=")
    if len(sides) != 2 or not all(side.strip() for side in sides):
        raise ValueError("Use exactly one equality sign, e.g. F=m*a.")
    left, right = (_parse_side(s.strip()) for s in sides)

    def symbols(node):
        if node[0] == "var":
            return {node[1]}
        return set().union(*(symbols(item) for item in node[1:] if isinstance(item, tuple)))

    variables = sorted(symbols(left) | symbols(right))
    if len(variables) > MAX_VARIABLES:
        raise ValueError(f"At most {MAX_VARIABLES} distinct symbols per equation in this version.")
    best = None
    best_mapping = None
    best_tree = None
    for permutation in itertools.permutations(range(len(variables))):
        mapping = dict(zip(variables, permutation))
        a, b = _shape(left, mapping, algebra), _shape(right, mapping, algebra)
        tree = ("=", *sorted((a, b), key=_key))
        signature = _key((algebra, tree))
        if best is None or signature < best:
            best, best_mapping, best_tree = signature, mapping, tree
    return dict(signature=hashlib.sha256(best.encode()).hexdigest(),
                structure=_display(best_tree), algebra=algebra,
                roles={"x" + str(i+1): name for name, i in sorted(best_mapping.items(), key=lambda x:x[1])},
                variable_count=len(variables))


def group(entries):
    """Group only cross-domain exact shape matches; preserve each entry's limits."""
    buckets = {}
    for entry in entries:
        buckets.setdefault(entry["signature"], []).append(entry)
    families, unmatched = [], []
    for signature, members in buckets.items():
        domains = {m["domain"].strip().casefold() for m in members}
        if len(members) < 2 or len(domains) < 2:
            unmatched.extend(members)
            continue
        families.append(dict(id=signature[:12], signature=signature,
                             structure=members[0]["structure"], algebra=members[0]["algebra"],
                             domains=sorted({m["domain"] for m in members}),
                             members=members, status="Candidate structural correspondence",
                             interpretation_boundary=NOTE))
    return dict(families=sorted(families, key=lambda x:(-len(x["members"]), x["id"])),
                unmatched=unmatched, entries=entries, interpretation_boundary=NOTE)


def operate(payload, path=None):
    """Append-only saved equations; same local SQLite file as recognitions."""
    if payload.get("action") == "preview":
        return fingerprint(payload["equation"], payload.get("algebra", "scalar"))
    if payload.get("action") not in ("add", "catalog"):
        raise ValueError("Unknown equation-family action.")
    path = Path(path or os.environ.get("BCE_RECOGNITION_DB", Path.home()/".bce-ultimodel"/"recognitions.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=10)) as db:
        db.row_factory = sqlite3.Row
        db.execute("""CREATE TABLE IF NOT EXISTS equation_journal (
            seq INTEGER PRIMARY KEY, id TEXT UNIQUE, request TEXT UNIQUE, stamp TEXT, data TEXT NOT NULL)""")
        if payload["action"] == "add":
            request = str(UUID(payload["request"]))
            data = {key: str(payload.get(key, "")).strip() for key in
                    ("name", "domain", "equation", "assumptions", "limits", "units", "source")}
            if any(not data[k] for k in ("name", "domain", "equation", "assumptions", "limits")):
                raise ValueError("Name, domain, equation, assumptions, and analogy limits are required.")
            if any(len(v) > 700 for v in data.values()):
                raise ValueError("A field exceeds the 700-character limit.")
            data.update(fingerprint(data["equation"], payload.get("algebra", "scalar")))
            with db:
                existing = db.execute("SELECT id FROM equation_journal WHERE request=?", (request,)).fetchone()
                if not existing:
                    count = db.execute("SELECT COUNT(*) FROM equation_journal").fetchone()[0]
                    if count >= MAX_EQUATIONS:
                        raise ValueError(f"This prototype handles at most {MAX_EQUATIONS} saved equations.")
                    db.execute("INSERT INTO equation_journal(id,request,stamp,data) VALUES(?,?,?,?)",
                               (str(uuid4()), request, datetime.now(timezone.utc).isoformat(),
                                json.dumps(data, ensure_ascii=False)))
        records = []
        for row in db.execute("SELECT id, stamp, data FROM equation_journal ORDER BY seq"):
            records.append(dict(id=row["id"], timestamp=row["stamp"], **json.loads(row["data"])))
        if len(records) > MAX_EQUATIONS:
            raise ValueError(f"This prototype handles at most {MAX_EQUATIONS} saved equations.")
        return group(records)
