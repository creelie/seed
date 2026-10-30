# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List, release 2.0.0

This release revises the preprint Hexagon 2610.00456v1. The upper bound for the largest transition depth in dimension four drops from 348 to 50: 22 ≤ D_4 ≤ 50, so the conjecture of a uniform transition depth holds with D = 51. The proof is a chain lemma together with a chain of cuts for each of the 92,422,743 polytopes whose pair bound exceeds 50. Every chain was replayed against all 473,800,776 polytopes of the Kreuzer–Skarke list, with all 493 row groups read, every polytope covered, and largest bound 50 (`code/certify/results/r50/replay.json`). The bound H_4 ≤ 348 for every descent is unchanged.

A new section proves by hand that the reflexive subpolytopes of a free sum P ⊕ Q are the free sums of reflexive subpolytopes of P and of Q, so shortest and longest descents add. Hence D_{d+e} ≥ D_d + D_e, D_d ≥ 11d/2 − 6, and D_d/d converges to a limit in [11/2, ∞]. The title page names the preprint, the abstract is shorter, and the exact value of D_4 stays open.

Assets: the PDF, the LaTeX source with the figures as PNG (tex.zip), and the arXiv package (tar.gz) with the checks, the data and the Lean file in `anc/`. GitHub-related contact: egspl@proton.me.
