"""Transition depths of the reflexive 3-polytopes from the cover relation.

Reads data/poset3.json (covers of each of the 4,319 polytopes, keyed by PALP
normal form) and recomputes depth and height by induction, ignoring the
stored values; then checks the statements of Section VI: D_3 = 11 by exactly
two r-maximal polytopes with 35 and 31 lattice points and height 23, longest
descent 28 (the polytope with 35 points, depth 8), simple counting bound 33,
16 r-minimal polytopes, 21,841 covers, mean depth 5.67 and mean height 10.23.
"""
import json, os, sys
from fractions import Fraction
from functools import lru_cache
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import rhull

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = json.load(open(os.path.join(ROOT, 'data', 'poset3.json')))
cov = P['covers']
passes = fails = 0
def check(ok, what):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + what)
    if ok: passes += 1
    else: fails += 1

def verts(k): return [tuple(map(int, v.split(','))) for v in k.split(';')]

check(len(cov) == 4319, '4,319 reflexive 3-polytopes')
check(all(c in cov for k in cov for c in cov[k]), 'every cover is itself in the list')

@lru_cache(None)
def dh(k):
    c = cov[k]
    if not c: return (0, 0)
    return (1 + min(dh(x)[0] for x in c), 1 + max(dh(x)[1] for x in c))

D = {k: dh(k) for k in cov}
pts, dpts = {}, {}
for k in cov:
    S = rhull.closure(verts(k)); F = rhull.facets(list(S))
    assert rhull.is_reflexive(F)
    pts[k] = len(S)
    # dual: the polytope spanned by the facet normals
    dpts[k] = len(rhull.closure([tuple(int(t) for t in a) for a, c in F]))

check(sum(len(v) for v in cov.values()) == 21841, '21,841 covers in all')
mins = [k for k in cov if not cov[k]]
check(len(mins) == 16, 'sixteen r-minimal polytopes')
covered = {c for k in cov for c in cov[k]}
maxs = [k for k in cov if k not in covered]
d3 = max(v[0] for v in D.values())
deep = [k for k in cov if D[k][0] == d3]
check(d3 == 11 and sorted(pts[k] for k in deep) == [31, 35], 'D_3 = 11, attained by two polytopes, with 31 and 35 lattice points')
check(all(k in maxs and D[k][1] == 23 for k in deep), 'both are r-maximal and have longest descents of 23 steps')
want = [{(1,0,0),(1,2,0),(-3,-2,0),(1,2,4),(-3,-2,-4)},
        {(1,0,0),(0,1,0),(1,0,2),(1,-4,-2),(-2,3,2),(-2,-1,-2)}]
from palp import run_palp, key
nf = [key(r['nf']) for r in run_palp([(3, sorted(rhull.closure(list(w)))) for w in want])] if os.environ.get('PALP') else None
if nf is not None:
    check(sorted(nf) == sorted(deep), 'the vertices printed in the paper give these two polytopes')
hmax = max(v[1] for v in D.values())
tall = [k for k in cov if D[k][1] == hmax]
check(hmax == 28 and len(tall) == 1 and pts[tall[0]] == 35 and D[tall[0]][0] == 8,
      'longest descent 28 steps, for a polytope with 35 points, whose depth is 8')
simple = max(min(pts[k] - 5, 39 - dpts[k]) for k in cov)
check(simple == 33, 'simple counting bound min(|P|-5, 39-|P*|) is at most 33')
md = Fraction(sum(v[0] for v in D.values()), len(D)); mh = Fraction(sum(v[1] for v in D.values()), len(D))
check(round(float(md), 2) == 5.67 and round(float(mh), 2) == 10.23, 'mean depth 5.67, mean height 10.23')
check(all(D[k] == (P['depth'][k], P['height'][k]) for k in cov), 'stored depths and heights agree with the recomputation')
print(f'check_poset3.py: {passes} passed, {fails} failed')
sys.exit(1 if fails else 0)
