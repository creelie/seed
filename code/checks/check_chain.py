"""The reflexive descent of Delta_680 (Table III and Theorem D).

Default checks, from data/chain680.json (the lattice points of every Gamma_i):
  * each Gamma_i is the set of lattice points of its convex hull, is reflexive,
    and has the numbers of points, dual points and vertices of Table III;
  * Gamma_{i+1} is strictly inside Gamma_i;
  * steps 1 to 10 are covers by the climbing lemma: for every lattice point q'
    of Gamma_{i+1}^* outside Gamma_i^*, T^inf(H_q') = Gamma_{i+1};
  * Gamma_38 has no cover (it is r-minimal).
With --full (needs PALP for the depth searches, a few more minutes):
  * steps 11 to 38 are covers, by listing all covers of Gamma_i;
  * delta(Gamma_27) = 9 and delta(Gamma_32) = 4 by breadth-first search, so
    delta(Delta_680) <= 27 + 9 = 36.
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
import rhull, complete, greedy

full = '--full' in sys.argv
steps = [frozenset(tuple(p) for p in s) for s in json.load(open(os.path.join(ROOT, 'data', 'chain680.json')))]
table = json.load(open(os.path.join(ROOT, 'data', 'chain680_table.json')))
passes = fails = 0
def check(ok, what):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + what, flush=True)
    if ok: passes += 1
    else: fails += 1

check(len(steps) == 39, 'the descent has 38 steps, Gamma_0 to Gamma_38')
F = [rhull.facets(list(S)) for S in steps]
check(all(rhull.closure(list(S)) == S for S in steps), 'each Gamma_i is the set of lattice points of its hull')
check(all(rhull.is_reflexive(f) for f in F), 'each Gamma_i is reflexive')
check(all(steps[i + 1] < steps[i] for i in range(38)), 'Gamma_{i+1} is strictly inside Gamma_i')
duals = [greedy.dual_lattice(S, f)[0] for S, f in zip(steps, F)]
rows = [[i, len(S), len(Dl), len(rhull.vertices(S, f))] for i, (S, f, Dl) in enumerate(zip(steps, F, duals))]
check(all(r[:4] == t[:4] for r, t in zip(rows, table)), 'points, dual points and vertices agree with Table III')
D680 = rhull.closure([(-1, -1, -1, -1), (83, -1, -1, -1), (-1, 6, -1, -1), (-1, -1, 2, -1), (-1, -1, -1, 1)])
check(steps[0] == D680 and len(D680) == 680, 'Gamma_0 is Delta_680, with 680 lattice points')

# climbing lemma, steps 1..10
ok = True
for i in range(10):
    S, G = steps[i], steps[i + 1]
    extra = duals[i + 1] - duals[i]
    for q in extra:
        r = greedy.cut(S, q)
        if r is None or r[0] != G: ok = False
    print(f'  step {i + 1}: {len(S)} -> {len(G)}, {len(extra)} new dual points, climbing lemma {"holds" if ok else "FAILS"}', flush=True)
check(ok, 'steps 1 to 10 are covers by the climbing lemma')

check(not complete.covers(steps[38], F[38]), 'Gamma_38 has no cover, so it is r-minimal')

if full:
    ok = True
    for i in range(10, 38):
        t = time.time()
        cv = complete.covers(steps[i], F[i])
        good = any(frozenset(c) == steps[i + 1] for c in cv)
        ok &= good
        print(f'  step {i + 1}: {len(steps[i])} -> {len(steps[i + 1])}, cover among {len(cv)}: {good} ({time.time() - t:.0f} s)', flush=True)
    check(ok, 'steps 11 to 38 are covers, by listing all covers')
    from bfs_depth import exact_depth
    d27, info27 = exact_depth(sorted(steps[27]), verbose=False)
    d32, info32 = exact_depth(sorted(steps[32]), verbose=False)
    check(d27 == 9 and len(info27['minimal']) == 11, 'delta(Gamma_27) = 9, ending at an r-minimal polytope with 11 points')
    check(d32 == 4, 'delta(Gamma_32) = 4')
    check(27 + d27 == 36, 'delta(Delta_680) <= 27 + 9 = 36')

print(f'check_chain.py: {passes} passed, {fails} failed')
sys.exit(1 if fails else 0)
