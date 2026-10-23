"""Exact verification of the two-cover certificate proving D_4 <= 347.

Run with numpy and scipy installed. Qhull proposes vertices only; every facet
is enumerated with integer arithmetic and every original point is verified.
The global census is the repository's supplied Kreuzer--Skarke histogram.
"""
from pathlib import Path
import itertools, json, csv, sys
import numpy as np
from scipy.spatial import ConvexHull
CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE))
import rhull, greedy

def facets_exact(pts):
    pts = list(pts)
    hull = ConvexHull(np.array(pts, dtype=float), qhull_options='Qt')
    V = [pts[int(i)] for i in hull.vertices]
    facets = set()
    for face in itertools.combinations(V, len(pts[0])):
        a = rhull._normal(face)
        if a is None:
            continue
        c = sum(x*y for x, y in zip(a, face[0]))
        values = [sum(x*y for x, y in zip(a, v))-c for v in V]
        if min(values) == 0 and max(values) > 0:
            facets.add((tuple(a), c))
        elif max(values) == 0 and min(values) < 0:
            facets.add((tuple(-x for x in a), -c))
    assert facets and all(sum(x*y for x, y in zip(a, v)) >= c
                          for a, c in facets for v in pts)
    return sorted(facets)

rhull.facets = facets_exact
with open(CODE/'data/ks4_point_pairs.csv') as f:
    pairs = {(int(x['points']), int(x['dual_points'])): int(x['count'])
             for x in csv.DictReader(f)}
assert sum(pairs.values()) == 473800776
# An independent suffix dynamic program: all updates for one p happen after
# evaluating that p, to enforce strict decrease in the first coordinate.
bound, best = {}, [-1]*682
for p in sorted({p for p, q in pairs}):
    pending = {q: best[q+1]+1 for a, q in pairs if a == p}
    for q, value in pending.items():
        bound[(p, q)] = value
        best[q] = max(best[q], value)
    for q in range(680, -1, -1):
        best[q] = max(best[q], best[q+1])
assert [(p, q, pairs[(p, q)]) for (p, q), v in bound.items() if v == 348] == [(521,22,1)]
assert max(v for v in bound.values() if v < 348) == 347
with open(CODE/'data/top347_certificate.json') as f:
    cert = json.load(f)
sets, fs, duals = [], [], []
for stage in cert['stages']:
    S = frozenset(tuple(v) for v in stage['lattice_points'])
    V = [tuple(v) for v in stage['vertices']]
    assert rhull.closure(V) == S
    F = facets_exact(S)
    assert rhull.is_reflexive(F)
    dual, _ = greedy.dual_lattice(S, F)
    assert (len(S), len(dual)) == (stage['points'], stage['dual_points'])
    assert bound[(len(S), len(dual))] == stage['pair_bound']
    sets.append(S); fs.append(F); duals.append(dual)
for i in range(2):
    assert sets[i+1] < sets[i]
    for q in duals[i+1]-duals[i]:
        cut = greedy.cut(sets[i], q)
        assert cut is not None and cut[0] == sets[i+1]
assert [(len(S), len(D)) for S, D in zip(sets, duals)] == [(521,22),(516,23),(257,24)]
assert 2+bound[(257,24)] == 249
print('PASS: histogram counts sum to 473800776; unique pair-bound-348 polytope;')
print('PASS: exact reflexivity, full point sets, and both cover maximality tests;')
print('PASS: exceptional shortest depth <= 249; global shortest depth D_4 <= 347.')
