"""The seed conjecture on the Anaxia engine: every failure, the change it forced, the retry.
Run from code/:  python3 bllm/seed_loop.py [--full]
Without --full the 3D comparisons use a random sample of 400 polytopes (seed 7); with --full
they use all 4303 polytopes of the 3D list that have a cover."""
import sys, os, json, random, csv, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import rhull, complete, greedy
from palp import run_palp, key
from loop import Check, Round, Target, run_target, write_outputs
from ebllm.package import ConjecturePackage

FULL = '--full' in sys.argv
P3 = json.load(open('data/poset3.json'))
KEYS = [k for k in P3['covers'] if P3['covers'][k]]
SAMPLE = KEYS if FULL else random.Random(7).sample(KEYS, 400)
def pts_of(k): return [tuple(map(int, v.split(','))) for v in k.split(';')]
_R = None
def palp_data():
    global _R
    if _R is None: _R = run_palp([(3, pts_of(k)) for k in SAMPLE])
    return _R
def nf_set(polys):
    return {key(r['nf']) for r in run_palp([(3, sorted(c)) for c in polys])} if polys else set()

def vertex_drop():
    """Strategy 1: descend by deleting one vertex and taking the hull of the remaining points."""
    R = palp_data(); none = 0; miss = 0
    for k, r in zip(SAMPLE, R):
        pts = r['pts']; kids = [[p for p in pts if p != v] for v in r['verts']]
        res = run_palp([(3, c) for c in kids])
        refl = [key(x['nf']) for x in res if x['ip'] and x['refl']]
        none += not refl
        miss += not set(P3['covers'][k]) <= set(refl)
    return dict(ok=none == 0 and miss == 0,
                evidence=f"of {len(SAMPLE)} polytopes, {none} have no reflexive vertex deletion and "
                         f"{miss} have a cover that is not a vertex deletion")

def gauge_two():
    """Strategy 2: covers from cuts T^inf(H_q) with q of gauge exactly 2, no branching."""
    R = palp_data(); miss = 0
    for k, r in zip(SAMPLE, R):
        S = frozenset(r['pts']); F = rhull.facets(list(S))
        Dst, V = greedy.dual_lattice(S, F)
        found = set()
        for q in greedy.candidates(S, F, Dst, V, 2):
            c = greedy.cut(S, q)
            if c and rhull.is_reflexive(c[1]): found.add(c[0])
        miss += nf_set(rhull._maximal(found)) != set(P3['covers'][k])
    return dict(ok=miss == 0, evidence=f"gauge-2 cuts give the wrong cover set for {miss} of {len(SAMPLE)} polytopes")

def complete_covers():
    """Strategy 3: the complete candidate set (volume bound, facet condition) with branching."""
    R = palp_data(); bad = 0; nonrefl = 0
    for k, r in zip(SAMPLE, R):
        S = frozenset(r['pts']); F = rhull.facets(list(S)); st = {}
        bad += nf_set(complete.covers(S, F, st)) != set(P3['covers'][k]); nonrefl += st['nonrefl']
    return dict(ok=bad == 0, evidence=f"complete covers agree with the vertex-deletion poset on "
                f"{len(SAMPLE)-bad} of {len(SAMPLE)} polytopes ({nonrefl} non-reflexive fixed points met)")

def literal_reading():
    return dict(ok=True, evidence="Kreuzer-Skarke: every reflexive 4-polytope contains a minimal "
                "polytope, so a chain of one step exists (Theorem A of the paper)")

def uniform_bound():
    rows = [(int(r['points']), int(r['dual_points']), int(r['count'])) for r in csv.DictReader(open('data/ks4_point_pairs.csv'))]
    N = sum(c for a, b, c in rows); M = max(min(a - 6, 680 - b) for a, b, c in rows)
    return dict(ok=N == 473800776 and M == 654,
                evidence=f"{N} polytopes; max of min(|P|-6, 680-|P*|) = {M}")

def pair_bound():
    import pair_chain
    rows = pair_chain.load('data/ks4_point_pairs.csv')
    L = pair_chain.chain_lengths(rows)
    M = max(L.values()); at = [k for k, v in L.items() if v == M]
    return dict(ok=M == 348 and at == [(521, 22)],
                evidence=f"longest chain of realised pairs with points falling and dual points rising: "
                         f"{M} steps, only from {at[0]}; so D_4 <= 348 and D = 349 with the minimal seed")

def low_dimensions():
    out = []
    for d, want in ((2, 5), (3, 11)):
        P = json.load(open(f'data/poset{d}.json')); cov = P['covers']; memo = {}
        def dep(k):
            if k not in memo:
                memo[k] = 0 if not cov[k] else 1 + min(dep(x) for x in cov[k])
            return memo[k]
        m = max(dep(k) for k in cov); out.append((d, len(cov), m, want))
    return dict(ok=all(m == w for d, n, m, w in out),
                evidence="; ".join(f"dimension {d}: {n} polytopes, largest depth {m}" for d, n, m, w in out))

def sharp_constant():
    rows = [(int(r['points']), int(r['dual_points']), int(r['count'])) for r in csv.DictReader(open('data/ks4_point_pairs.csv'))]
    big = sum(c for a, b, c in rows if min(a - 6, 680 - b) > 40)
    return dict(ok=False, evidence=f"{big} polytopes have trivial bound above 40; certifying 'a few tens' "
                f"needs a chain or an exact depth for each, at about 3 minutes for the largest")

def chain_680():
    ch = json.load(open('data/chain680.json'))
    return dict(ok=len(ch) - 1 == 38, evidence=f"certified chain from the 680-point polytope of length {len(ch)-1}")

def lower_bounds():
    deps = []
    for f in sorted(os.listdir('data')):
        if f.startswith('depth_') and f.endswith('.json'):
            d = json.load(open(os.path.join('data', f))); deps.append((d['points'], d['depth']))
    m = max((d for p, d in deps), default=None)
    return dict(ok=m is not None, evidence=f"exact depths (points, depth) of chain polytopes {deps}; D_4 >= {m}")

def shortened_680():
    d = json.load(open('data/depth_20.json'))
    return dict(ok=d['index'] + d['depth'] == 36,
                evidence=f"step {d['index']} of the chain has exact depth {d['depth']}, so delta(Delta_680) <= "
                         f"{d['index']} + {d['depth']} = {d['index'] + d['depth']}")

def depth_22():
    import gzip, subprocess
    D = json.load(gzip.open('data/depth22.json.gz', 'rt'))
    out = subprocess.run([sys.executable, 'checks/check_depth22.py'], capture_output=True, text=True).stdout
    last = out.strip().splitlines()[-1]
    return dict(ok=last.endswith('0 failed') and all(D['nodes'][r]['bound'] == 22 for r in D['roots']),
                evidence=f"certificate of {len(D['nodes'])} polytopes with complete cover lists below the skew "
                         f"bipyramids P_1, P_2 (37 points each): depth exactly 22; checks/check_depth22.py: {last}")

def gamma10_is_p1():
    ch = json.load(open('data/chain680.json'))
    G = ((-1, -1, -1, -1), (-1, -1, 6, 0), (-1, 2, -1, 0), (1, -1, -1, 0))
    e = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]
    P1 = rhull.closure(e + [(-4, -2, -1, 8), (-4, -2, -1, -8)])
    img = {tuple(sum(G[r][c] * x[c] for c in range(4)) for r in range(4)) for x in P1}
    ok = img == {tuple(x) for x in ch[10]} and abs(round(np.linalg.det(np.array(G, float)))) == 1
    return dict(ok=ok, evidence="the unimodular map G carries P_1 onto step 10 of the chain of Delta_680, "
                                "so delta(Delta_680) <= 10 + 22 = 32")

def sharp_gap():
    return dict(ok=False, evidence="22 <= D_4 <= 348; closing the gap needs exact depths of polytopes with "
                "more lattice points, or a certified chain of at most 22 steps for each polytope above 22")

pkg = ConjecturePackage(name="Uniform transition depth", domain="reflexive 4-polytopes (Kreuzer-Skarke list)",
                        hypothesis="Delta reflexive, dimension 4",
                        conclusion="Delta is joined to a minimal seed by at most D reflexive steps")
T1 = Target("seed-literal and uniform bound", pkg, "uniform-bound", [
    Round("descend by vertex deletion", [Check("vertex-deletion-descends", "construction", vertex_drop)],
          change="replace vertex deletion by cuts T^inf(Delta cap {<x,q> >= -1}) at dual lattice points q"),
    Round("cuts at gauge-2 dual points", [Check("gauge-two-cuts-complete", "construction", gauge_two)],
          change="candidate q from the dual volume bound of Balletti-Kasprzyk-Nill and the facet condition; "
                 "branch at non-reflexive fixed points"),
    Round("complete candidate set with branching", [Check("complete-covers-3d", "computation", complete_covers)]),
    Round("literal reading and counting bound",
          [Check("literal-D-equals-1", "lemma", literal_reading, "Kreuzer-Skarke 1997"),
           Check("uniform-654", "computation", uniform_bound, "data/ks4_point_pairs.csv")],
          change="the simple bound treats points and dual points separately; chain only through the "
                 "pairs (|P|, |P*|) that occur in the list"),
    Round("longest chain of realised pairs",
          [Check("uniform-348", "computation", pair_bound, "data/ks4_point_pairs.csv, checks/pair_bound.c"),
           Check("low-dimensions", "computation", low_dimensions, "data/poset2.json, data/poset3.json")],
          bridges=[(["complete-covers-3d", "literal-D-equals-1", "uniform-654", "uniform-348"],
                    "uniform-bound", 0.0)]),
])
pkg2 = ConjecturePackage(name="Uniform transition depth, sharp form", domain="reflexive 4-polytopes",
                         conclusion="the least D is a few tens")
T2 = Target("seed-sharp", pkg2, "sharp", [
    Round("sweep all 473,800,776 polytopes", [Check("sweep-feasible", "computation", sharp_constant)],
          change="certify chains only for extreme polytopes and bound the constant from below by exact "
                 "breadth-first depths"),
    Round("certified chains and exact lower bounds",
          [Check("chain-680-length-38", "construction", chain_680), Check("exact-lower-bounds", "computation", lower_bounds)],
          change="shorten the chain of Delta_680 at the step where an exact depth is known"),
    Round("exact depths along the chain",
          [Check("depth-680-at-most-36", "construction", shortened_680)],
          change="construct polytopes with long descents: skew bipyramids conv(Q x 0, (a,k), (b,-k)) over "
                 "three-dimensional reflexive Q, ranked by the length of a greedy chain of cuts, then exact "
                 "depths of the highest ranked by breadth-first search through complete covers"),
    Round("skew bipyramids",
          [Check("depth-22", "construction", depth_22, "data/depth22.json.gz, checks/check_depth22.py"),
           Check("depth-680-at-most-32", "construction", gamma10_is_p1, "data/chain680.json"),
           Check("sharp-constant", "proof", sharp_gap)],
          change="the sharp constant stays open; test the polytopes above P_1 and P_2 for depth 23"),
], model_ok=False)

if __name__ == '__main__':
    factors = dict(proof=1, formal=1, code=1, trace=1, sim=1, risk=1, lit=1, human=0)
    res = [run_target(T1, factors), run_target(T2, factors)]
    os.makedirs('bllm/out', exist_ok=True)
    write_outputs(res, 'bllm/out/seed')
    for r in res: print(r['target'], r['label'], 'blocking', r['blocking'])
