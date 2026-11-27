"""Finite-domain complementary Lens analysis and exact rank reconstruction."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import argparse
import json
import math


@dataclass(frozen=True)
class Lens:
    name: str
    observe: object


def width(n):
    if n < 1:
        raise ValueError('A fiber must be nonempty')
    return (n - 1).bit_length()


class Ouroboros:
    """Shared ordered finite domain, deterministic hashable Lens outputs.

    The supplementary code is a rank within a fiber. The decoder must share
    the same domain order, lenses, and selected indices. This is not a file
    compressor; observation storage and shared metadata have their own cost.
    """
    def __init__(self, domain, lenses):
        self.domain = tuple(domain)
        self.lenses = tuple(lenses)
        if not self.domain or len(set(self.domain)) != len(self.domain):
            raise ValueError('Domain must be nonempty with distinct hashable states')
        if len(set(l.name for l in self.lenses)) != len(self.lenses):
            raise ValueError('Lens names must be unique')
        self._observations = {x: tuple(l.observe(x) for l in self.lenses) for x in self.domain}
        self._cache = {}

    def indices(self, indices=None):
        ids = tuple(range(len(self.lenses))) if indices is None else tuple(indices)
        if len(set(ids)) != len(ids) or any(type(i) is not int or not 0 <= i < len(self.lenses) for i in ids):
            raise ValueError('Invalid Lens selection')
        return ids

    def observe(self, x, indices=None):
        return tuple(self._observations[x][i] for i in self.indices(indices))

    def _partition(self, ids):
        if ids not in self._cache:
            groups = defaultdict(list)
            for x in self.domain:
                groups[self.observe(x, ids)].append(x)
            fibers = {key: tuple(group) for key, group in groups.items()}
            ranks = {x: rank for group in fibers.values() for rank, x in enumerate(group)}
            self._cache[ids] = fibers, ranks
        return self._cache[ids]

    def analyze(self, indices=None):
        ids = self.indices(indices)
        fibers, _ = self._partition(ids)
        largest = max(map(len, fibers.values()))
        # Conditional entropy H(X|observations), for a uniform original state.
        residual = sum(len(g) * math.log2(len(g)) for g in fibers.values()) / len(self.domain)
        return {'lenses': [self.lenses[i].name for i in ids], 'states': len(self.domain),
                'distinct_observations': len(fibers), 'largest_fiber': largest,
                'supplement_bits': width(largest), 'lossless': largest == 1,
                'uniform_residual_entropy_bits': residual}

    def candidates(self, observation, indices=None):
        fibers, _ = self._partition(self.indices(indices))
        return fibers.get(tuple(observation), ())

    def encode(self, x, indices=None):
        ids = self.indices(indices)
        fibers, ranks = self._partition(ids)
        obs = self.observe(x, ids)
        b = width(max(map(len, fibers.values())))
        return obs, format(ranks[x], f'0{b}b') if b else ''

    def decode(self, observation, code, indices=None):
        ids = self.indices(indices)
        fibers, _ = self._partition(ids)
        b = width(max(map(len, fibers.values())))
        if not isinstance(code, str) or len(code) != b or any(c not in '01' for c in code):
            raise ValueError('Invalid supplementary bit string')
        group = fibers.get(tuple(observation), ())
        rank = int(code, 2) if code else 0
        if rank >= len(group):
            raise ValueError('Unknown observation or unused rank')
        return group[rank]

    def minimum_subsets(self, target_bits=0, max_lenses=16):
        """Exhaustively find all smallest subsets meeting a residual-bit target."""
        if type(target_bits) is not int or target_bits < 0:
            raise ValueError('target_bits must be a nonnegative integer')
        if len(self.lenses) > max_lenses:
            raise ValueError('Exhaustive subset search exceeds configured Lens limit')
        # More observations can only refine a partition.
        if self.analyze()['supplement_bits'] > target_bits:
            return []
        # Avoid retaining a full partition for each candidate subset.
        examined = 0
        for size in range(len(self.lenses)+1):
            found = []
            for ids in combinations(range(len(self.lenses)), size):
                examined += len(self.domain)
                if examined > 10_000_000:
                    raise ValueError('Subset search exceeded its work budget; reduce the domain or Lens count.')
                counts = Counter(tuple(obs[i] for i in ids) for obs in self._observations.values())
                if width(max(counts.values())) <= target_bits:
                    found.append(ids)
            if found:
                return found
        return []

    def trace(self, indices=None):
        """Measure residual ambiguity after each Lens; order-dependent marginal gain."""
        ids = self.indices(indices)
        rows = [self.analyze(())]
        for i in range(1, len(ids)+1):
            row = self.analyze(ids[:i])
            prev = rows[-1]
            row['worst_case_bits_removed'] = prev['supplement_bits'] - row['supplement_bits']
            row['uniform_information_gain_bits'] = prev['uniform_residual_entropy_bits'] - row['uniform_residual_entropy_bits']
            rows.append(row)
        return rows


def modulo_lenses(moduli):
    if any(type(m) is not int or m <= 0 for m in moduli):
        raise ValueError('Moduli must be positive integers')
    return [Lens(f'mod {m} #{i+1}', lambda n, m=m: n % m) for i,m in enumerate(moduli)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--size', type=int, default=15)
    p.add_argument('--moduli', nargs='+', type=int, default=[3,5])
    p.add_argument('--state', type=int, default=13)
    p.add_argument('--target-bits', type=int, default=0)
    a = p.parse_args()
    if not 1 <= a.size <= 10000 or not 0 <= a.state < a.size or len(a.moduli) > 12:
        p.error('Use a domain size of 1–10000, a state within the domain, and at most 12 Lenses.')
    model = Ouroboros(range(a.size), modulo_lenses(a.moduli))
    obs, code = model.encode(a.state)
    report = {'state': a.state, 'observations': obs, 'candidates': model.candidates(obs),
              'supplement': code, 'recovered': model.decode(obs,code), 'trace': model.trace(),
              'minimum_subsets': [model.analyze(ids) for ids in model.minimum_subsets(a.target_bits)]}
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
