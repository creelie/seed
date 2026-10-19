"""Pair-chain bound for reflexive descents in dimension four.

Along a reflexive descent Delta_0 > Delta_1 > ... > Delta_k the number of lattice points strictly
decreases and the number of dual lattice points strictly increases, and every pair
(|Delta_i|, |Delta_i^*|) is realised by a polytope of the Kreuzer-Skarke list.  So k is at most the
length L(p,q) of the longest chain (p,q) = (p_0,q_0), (p_1,q_1), ... of realised pairs with p_i
strictly decreasing and q_i strictly increasing.  This script computes L on all realised pairs from
data/ks4_point_pairs.csv (the joint distribution of point counts over the whole list) and writes
data/pair_chain.csv with columns points,dual_points,count,L,minbound.

Usage: python3 pair_chain.py [csv]"""
import csv, sys, os, json
from collections import defaultdict

def load(path):
    pairs = {}
    with open(path) as f:
        r = csv.reader(f); next(r)
        for a in r:
            p, q, c = map(int, a); pairs[(p, q)] = pairs.get((p, q), 0) + c
    return pairs

def chain_lengths(pairs):
    """L(p,q) by increasing p with a Fenwick tree over q for suffix maxima."""
    N = max(q for _, q in pairs) + 2
    tree = [-1] * (N + 2)
    def upd(i, v):
        i = N + 1 - i
        while i <= N + 1:
            if tree[i] < v: tree[i] = v
            i += i & -i
    def qry(i):
        i = N + 1 - i; m = -1
        while i > 0:
            if tree[i] > m: m = tree[i]
            i -= i & -i
        return m
    byp = defaultdict(list)
    for p, q in pairs: byp[p].append(q)
    L = {}
    for p in sorted(byp):
        new = [(q, qry(q + 1) + 1 if qry(q + 1) >= 0 else 0) for q in byp[p]]
        for q, v in new:
            L[(p, q)] = v; upd(q, v)
    return L

def brute(pairs):
    """Quadratic check of chain_lengths, used by the test suite."""
    L = {}
    for p, q in sorted(pairs):
        L[(p, q)] = max([L[(a, b)] + 1 for (a, b) in L if a < p and b > q], default=0)
    return L

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'data', 'ks4_point_pairs.csv')
    pairs = load(path)
    L = chain_lengths(pairs)
    total = sum(pairs.values())
    with open(os.path.join(here, 'data', 'pair_chain.csv'), 'w') as f:
        f.write('points,dual_points,count,L,minbound\n')
        for (p, q) in sorted(pairs):
            f.write(f'{p},{q},{pairs[(p,q)]},{L[(p,q)]},{min(p-6,680-q)}\n')
    mx = max(L.values())
    print('polytopes', total, 'pairs', len(pairs))
    print('max min-bound', max(min(p-6, 680-q) for p, q in pairs))
    print('max pair-chain bound', mx, 'at', sorted(k for k, v in L.items() if v == mx),
          'count', sum(pairs[k] for k, v in L.items() if v == mx))
    print('Delta_680 pair-chain bound', L[(680, 26)])
    for X in [340, 320, 300, 280, 260, 250, 240, 220, 200, 150, 100]:
        n = sum(c for k, c in pairs.items() if L[k] > X)
        m = sum(c for (p, q), c in pairs.items() if min(p-6, 680-q) > X)
        print(f'bound above {X}: pair-chain {n}, min-bound {m}')
