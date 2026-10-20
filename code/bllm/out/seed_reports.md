# Run report: Uniform transition depth

## 1. Axiom base

Lean's type theory with propext, Classical.choice, Quot.sound

## 2. Definition ledger (obligations)

- `uniform-bound` (theorem, weight 1.0): UNK, certified through its bridges
- `vertex-deletion-descends` (construction, weight 1.0): FAIL
- `gauge-two-cuts-complete` (construction, weight 1.0): FAIL
- `complete-covers-3d` (computation, weight 1.0): PASS
- `literal-D-equals-1` (lemma, weight 1.0): PASS, verified by Kreuzer-Skarke 1997
- `uniform-654` (computation, weight 1.0): PASS, verified by data/ks4_point_pairs.csv
- `uniform-348` (computation, weight 1.0): PASS, verified by data/ks4_point_pairs.csv, checks/pair_bound.c
- `low-dimensions` (computation, weight 1.0): PASS, verified by data/poset2.json, data/poset3.json
- `every-dimension` (proof, weight 1.0): PASS, verified by Blichfeldt 1914, BKN22, lean/Seed.lean

## 3. Dependency graph

- complete-covers-3d, literal-D-equals-1, uniform-654, uniform-348 ⇒ uniform-bound

## 5. Residue ledger

- none

## 8. Playbook

- core failures: 4, bullets: 4, density 1, rejected updates: 0
- [FAIL/FAIL] construction: vertex-deletion-descends failed its verifier
- [UNK/UNK] strategy: replace vertex deletion by cuts T^inf(Delta cap {<x,q> >= -1}) at dual lattice points q
- [FAIL/FAIL] construction: gauge-two-cuts-complete failed its verifier
- [UNK/UNK] strategy: candidate q from the dual volume bound of Balletti-Kasprzyk-Nill and the facet condition; branch at non-reflexive fixed points

## 14. Release label

**CANDIDATE**; factors {'proof': 1, 'formal': 1, 'code': 1, 'trace': 1, 'sim': 1, 'risk': 1, 'lit': 1, 'human': 0}; blocking: human

## 15. Human / referee checklist

- [ ] every definition typed, with its axiom scope
- [ ] proof, refutation and independence branches all considered
- [ ] every bridge has zero or named scope loss
- [ ] every unresolved star converted into a named residue
- [ ] the label is one of THEOREM, COUNTEREXAMPLE, CONDITIONAL, INDEPENDENCE, CANDIDATE, BUJ, OPEN

# Run report: Uniform transition depth, sharp form

## 1. Axiom base

Lean's type theory with propext, Classical.choice, Quot.sound

## 2. Definition ledger (obligations)

- `sharp` (theorem, weight 1.0): UNK
- `sweep-feasible` (computation, weight 1.0): FAIL
- `chain-680-length-38` (construction, weight 1.0): PASS
- `exact-lower-bounds` (computation, weight 1.0): PASS
- `depth-680-at-most-36` (construction, weight 1.0): PASS
- `depth-22` (construction, weight 1.0): PASS, verified by data/depth22.json.gz, checks/check_depth22.py
- `depth-680-at-most-32` (construction, weight 1.0): PASS, verified by data/chain680.json
- `sharp-constant` (proof, weight 1.0): FAIL
- `depth-680-at-most-31` (construction, weight 1.0): PASS, verified by data/descent9.json, checks/check_chain.py

## 3. Dependency graph

- (no bridges)

## 5. Residue ledger

- sharp

## 8. Playbook

- core failures: 5, bullets: 5, density 1, rejected updates: 0
- [FAIL/FAIL] computation: sweep-feasible failed its verifier
- [UNK/UNK] strategy: certify chains only for extreme polytopes and bound the constant from below by exact breadth-first depths
- [FAIL/FAIL] proof: sharp-constant failed its verifier
- [UNK/UNK] strategy: descend from step 9 of the chain through complete covers, choosing at each step the cover of least greedy rank; test the polytopes above P_1 and P_2 for depth 23
- [UNK/UNK] strategy: certify every polytope of the list at threshold 50 by chains of cuts (code/certify)

## 14. Release label

**OPEN**; factors {'proof': 0, 'formal': 1, 'code': 1, 'trace': 1, 'sim': 1, 'risk': 1, 'lit': 1, 'human': 0}; blocking: proof, human

## 15. Human / referee checklist

- [ ] every definition typed, with its axiom scope
- [ ] proof, refutation and independence branches all considered
- [ ] every bridge has zero or named scope loss
- [ ] every unresolved star converted into a named residue
- [ ] the label is one of THEOREM, COUNTEREXAMPLE, CONDITIONAL, INDEPENDENCE, CANDIDATE, BUJ, OPEN

