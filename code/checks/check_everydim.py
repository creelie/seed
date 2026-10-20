"""Proposition (every dimension): a chain of reflexive d-polytopes has at most V_d - 2 steps.

Checks the arithmetic of the proposition and tests it against the data of the paper:
Sylvester's sequence and V_4 = 2(s_4-1)^2 = 3528; Blichfeldt's bound nvol + d attained by
the standard simplex; in dimensions two and three the longest chain of covers in the full
poset (not only the shortest descent) is at most V_d - 2 with V_2 = 9, V_3 = 72; and in
dimension four every polytope of the list has between d+2 = 6 and V_4 + 4 = 3532 points.
"""
import csv, json, os, sys
from fractions import Fraction
from itertools import product
from math import factorial
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..')
sys.setrecursionlimit(100000)

passes = fails = 0
def check(ok, what):
    global passes, fails
    print(('PASS ' if ok else 'FAIL ') + what)
    if ok: passes += 1
    else: fails += 1

s = [2]
for _ in range(5): s.append(s[-1] ** 2 - s[-1] + 1)
check(s[:5] == [2, 3, 7, 43, 1807], "Sylvester's sequence 2, 3, 7, 43, 1807")
check(2 * (s[3] - 1) ** 2 == 3528 and 2 * (s[3] - 1) ** 2 - 2 == 3526, 'V_4 = 2(s_4-1)^2 = 3528, so D_4 <= 3526')

def det(m):
    m = [[Fraction(x) for x in r] for r in m]; n = len(m); d = Fraction(1)
    for c in range(n):
        p = next((r for r in range(c, n) if m[r][c] != 0), None)
        if p is None: return Fraction(0)
        if p != c: m[c], m[p] = m[p], m[c]; d = -d
        d *= m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / m[c][c]
            for k in range(c, n): m[r][k] -= f * m[c][k]
    return d

ok = True
for d in range(1, 6):
    E = [[int(i == j) for j in range(d)] for i in range(d)]
    nvol = abs(det(E))                                  # normalised volume of conv(0, e_1, ..., e_d)
    pts = sum(1 for x in product((0, 1), repeat=d) if sum(x) <= 1)
    ok &= pts == nvol + d
check(ok, 'the standard simplex attains Blichfeldt: d+1 points, normalised volume 1, d = 1..5')

for d, V in ((2, 9), (3, 72)):
    P = json.load(open(os.path.join(ROOT, 'data', f'poset{d}.json')))['covers']
    memo = {}
    def height(k):
        if k not in memo: memo[k] = 0 if not P[k] else 1 + max(height(x) for x in P[k])
        return memo[k]
    H = max(height(k) for k in P)
    check(H <= V - 2, f'dimension {d}: longest chain of covers {H} <= V_{d} - 2 = {V - 2}')

rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'ks4_point_pairs.csv'))))
p = [int(r['points']) for r in rows]; q = [int(r['dual_points']) for r in rows]
check(min(p + q) >= 6 and max(p + q) <= 3532,
      f'dimension four: points and dual points lie in [{min(p + q)}, {max(p + q)}], inside [6, 3532]')
print(f'{passes} checks passed, {fails} failed')
sys.exit(1 if fails else 0)
