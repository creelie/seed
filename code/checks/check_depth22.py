"""Two 37-point reflexive 4-polytopes of transition depth 22 (D_4 >= 22).

data/depth22.json.gz lists every polytope reached from the two roots through covers, with its
lattice points, its PALP normal form, the indices of all its covers (null when the search did not
need them), a lower bound for its depth and its exact depth where the search found it.

Default checks (no external program):
  * each listed point set is the set of lattice points of its hull and is reflexive;
  * the roots are P_1 = conv(e1, e2, e3, u + 8 e4, u - 8 e4) and
    P_2 = conv(e1, e2, e3, u, u + 8 e4, e3 - 8 e4) with u = (-4,-2,-1,0), 37 lattice points each;
  * a cover has fewer lattice points than the polytope it covers;
  * the lower bounds are consistent: a polytope with bound b > 0 has at least one cover, all its
    covers are listed, and each has bound at least b - 1; so by induction on the number of points
    every bound is a lower bound for the depth, and the roots have depth at least 22;
  * from each root a chain of 22 covers with exact depths 21, 20, ..., 0 ends at a polytope with
    no cover, so the roots have depth exactly 22;
  * the unimodular map G of the paper carries the lattice points of P_1 onto those of the polytope
    Gamma_10 of the descent of the largest polytope (data/chain680.json), so that descent has a
    continuation of length 10 + 22 = 32.
With --full (needs PALP in the variable PALP; about two CPU-hours, spread over JOBS processes,
by default one for each CPU):
  * every listed normal form is the PALP normal form of the listed points, and every listed cover
    list is the complete list of covers computed again by complete.py.
"""
import gzip, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
import rhull

full = '--full' in sys.argv
D = json.load(gzip.open(os.path.join(ROOT, 'data', 'depth22.json.gz'), 'rt'))
N = D['nodes']
passes = fails = 0
def check(ok, what):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if ok: passes += 1
    else: fails += 1

S = [frozenset(tuple(p) for p in n['points']) for n in N]
ok = True
for s in S:
    F = rhull.facets(list(s))
    if not (rhull.is_reflexive(F) and rhull.closure(list(s)) == s): ok = False
check(ok, f'the {len(N)} listed point sets are lattice-point sets of reflexive polytopes')

e = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]
P1 = rhull.closure(e + [(-4, -2, -1, 8), (-4, -2, -1, -8)])
P2 = rhull.closure(e + [(-4, -2, -1, 0), (-4, -2, -1, 8), (0, 0, 1, -8)])
roots = [S.index(P) if P in S else None for P in (P1, P2)]
check(None not in roots and len(P1) == len(P2) == 37, 'the roots are P_1 and P_2, with 37 lattice points each')

check(all(len(S[c]) < len(S[i]) for i, n in enumerate(N) if n['covers'] for c in n['covers']),
      'each cover has fewer lattice points than the polytope it covers')

ok = True
for i, n in enumerate(N):
    b = n['bound']
    if b > 0 and not n['covers']: ok = False
    if b > 0 and any(N[c]['bound'] < b - 1 for c in n['covers']): ok = False
check(ok, 'the lower bounds are consistent: bound b > 0 forces a cover, and every cover has bound >= b - 1')
check(None not in roots and all(N[r]['bound'] == 22 for r in roots), 'both roots have depth at least 22')

ok = None not in roots
for r in (roots if None not in roots else []):
    i, d = r, 22
    while d > 0:
        nxt = [c for c in N[i]['covers'] or [] if N[c]['exact'] == d - 1]
        if not nxt: ok = False; break
        i, d = nxt[0], d - 1
    if N[i]['covers'] != []: ok = False
check(ok, 'from each root a chain of 22 covers with exact depths 21, ..., 0 ends at a polytope with no cover')

G = ((-1, -1, -1, -1), (-1, -1, 6, 0), (-1, 2, -1, 0), (1, -1, -1, 0))
det = round(__import__('numpy').linalg.det(__import__('numpy').array(G, float)))
chain = json.load(open(os.path.join(ROOT, 'data', 'chain680.json')))
image = {tuple(sum(G[r][c] * x[c] for c in range(4)) for r in range(4)) for x in P1}
check(abs(det) == 1 and image == {tuple(x) for x in chain[10]},
      'G is unimodular and maps the lattice points of P_1 onto those of Gamma_10 of the 680-point descent')

def recompute(i):
    cv = complete.covers(S[i], rhull.facets(list(S[i])))
    return sorted({key(r['nf']) for r in run_palp([(4, sorted(c)) for c in cv])}) if cv else []

if full:
    import complete, multiprocessing
    from palp import run_palp, key
    t0 = time.time(); bad = 0; done = 0
    R = run_palp([(4, sorted(s)) for s in S])
    keys_ok = all(key(r['nf']) == n['key'] for r, n in zip(R, N))
    check(keys_ok, 'every listed normal form is the PALP normal form of the listed points')
    todo = [i for i, n in enumerate(N) if n['covers'] is not None]
    with multiprocessing.Pool(int(os.environ.get('JOBS', os.cpu_count() or 1))) as pool:
        for i, got in zip(todo, pool.imap(recompute, todo, chunksize=4)):
            if got != sorted(N[c]['key'] for c in N[i]['covers']): bad += 1
            done += 1
            if done % 500 == 0: print(f'  {done} cover lists recomputed, {bad} differ, {time.time() - t0:.0f} s', flush=True)
    check(bad == 0, f'all {done} listed cover lists agree with complete.py')

print(f'{passes} checks passed, {fails} failed')
sys.exit(1 if fails else 0)
