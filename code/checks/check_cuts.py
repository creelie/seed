"""The second case of the cut proposition does not occur in dimension three, nor at the
polytopes of the depth-22 certificate.  For every reflexive polyhedron Delta of the
dimension-three poset (and, with --full, every polytope of the certificate whose covers
are listed), the covers are recomputed by the procedure of the covers corollary; for each
cover Gamma and each vertex q of Gamma^* outside Delta^*, the cut
H_q = conv{x in Delta : <x,q> >= -1} is formed and compared with Gamma.
Checks: every candidate cut met by the procedure is reflexive, and H_q = Gamma always.
Run from code/:  python3 checks/check_cuts.py [--full]"""
import gzip, json, os, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
CODE = os.path.dirname(HERE)
sys.path.insert(0, CODE)
import rhull, complete

passes = fails = 0
def check(name, ok, info=''):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + name + (f'  [{info}]' if info else ''), flush=True)
    if ok: passes += 1
    else: fails += 1

def examine(points):
    S = frozenset(rhull.closure(points)); F = rhull.facets(list(S))
    st = {}; cov = complete.covers(S, F, stats=st)
    V, Dst, w = complete.dual_points_and_weights(S, F)
    pairs = differ = 0
    for G in cov:
        for a, c in rhull.facets(list(G)):
            q = tuple(a)
            if q in Dst: continue
            pairs += 1
            if frozenset(rhull.closure([x for x in S if sum(u * v for u, v in zip(x, q)) >= -1])) != frozenset(G):
                differ += 1
    return st.get('nonrefl', 0), pairs, differ

def dim3(k):
    return examine([tuple(map(int, v.split(','))) for v in k.split(';')])

def dim4(n):
    return examine([tuple(p) for p in n['points']])

def run(label, items, fn, expect_pairs):
    with Pool(os.cpu_count() or 1) as P:
        R = P.map(fn, items, chunksize=8)
    nonrefl = sum(r[0] for r in R); pairs = sum(r[1] for r in R); differ = sum(r[2] for r in R)
    check(f'{label}: every candidate cut met by the procedure is reflexive', nonrefl == 0, f'{nonrefl} non-reflexive')
    check(f'{label}: number of (cover, vertex of the dual cover outside Delta^*) pairs', pairs == expect_pairs, str(pairs))
    check(f'{label}: H_q equals the cover in every case (no second case)', differ == 0, f'{differ} differ')

if __name__ == '__main__':
    p = json.load(open(os.path.join(CODE, 'data', 'poset3.json')))
    keys = [k for k in p['covers'] if p['covers'][k]]
    check('dimension three: reflexive polyhedra with covers', len(keys) == 4303, str(len(keys)))
    run('dimension three', keys, dim3, 32129)
    if '--full' in sys.argv:
        D = json.load(gzip.open(os.path.join(CODE, 'data', 'depth22.json.gz'), 'rt'))['nodes']
        nodes = [n for n in D if n['covers']]
        check('certificate: polytopes with listed covers', len(nodes) == 5250, str(len(nodes)))
        run('certificate (dimension four)', nodes, dim4, 50280)
    print(f'{passes} checks passed, {fails} failed')
