"""The pair bound of Theorem B, in Python.

Recomputes L(p,q) on the 71,870 realised pairs with the Fenwick-tree program
pair_chain.py and checks: the stored data/pair_chain.csv; the maxima 654 and
348; and the witness data/pair_chain_witness.json, a chain of 349 realised
pairs from (521,22) with p strictly decreasing and q strictly increasing, so
that L(521,22) = 348 is attained and not only bounded.
"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.path.insert(0, ROOT)
from pair_chain import load, chain_lengths

passes = fails = 0
def check(ok, what):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + what)
    if ok: passes += 1
    else: fails += 1

pairs = load(os.path.join(ROOT, 'data', 'ks4_point_pairs.csv'))
L = chain_lengths(pairs)
stored = {(int(r['points']), int(r['dual_points'])): (int(r['count']), int(r['L']), int(r['minbound']))
          for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'pair_chain.csv')))}
check(all(stored[k] == (pairs[k], L[k], min(k[0] - 6, 680 - k[1])) for k in pairs) and len(stored) == len(pairs),
      'data/pair_chain.csv agrees with a fresh computation')
check(max(min(p - 6, 680 - q) for p, q in pairs) == 654, 'largest simple bound is 654')
mx = max(L.values())
check(mx == 348 and [k for k in L if L[k] == mx] == [(521, 22)] and pairs[(521, 22)] == 1,
      'largest pair bound is 348, only at (521,22), one polytope')
W = [tuple(x) for x in json.load(open(os.path.join(ROOT, 'data', 'pair_chain_witness.json')))]
check(len(W) == 349 and W[0] == (521, 22), 'the witness chain has 349 pairs and starts at (521,22)')
check(all(w in pairs for w in W), 'every pair of the witness is realised in the list')
check(all(W[i + 1][0] < W[i][0] and W[i + 1][1] > W[i][1] for i in range(348)),
      'along the witness p strictly decreases and q strictly increases')
check(all(L[W[i]] == 348 - i for i in range(349)), 'L decreases by one along the witness')
print(f'check_pairs.py: {passes} passed, {fails} failed')
sys.exit(1 if fails else 0)
