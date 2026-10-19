# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List

First release of the paper "Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List" by Deep Bhattacharjee and Ushashi Bhattacharya, with its code, data and checks.

- Every reflexive polytope can be shrunk to an r-minimal polytope through reflexive polytopes, one cover at a time, and every r-minimal polytope contains a minimal seed.
- In dimension four no such descent has more than 348 steps, so the conjecture of a uniform transition depth holds with D = 349.
- The largest transition depths in dimensions two and three are 5 and 11.
- Two skew bipyramids with 37 lattice points each have transition depth exactly 22, proved by a certificate of 5,592 polytopes with their complete lists of covers. One of them is the tenth polytope of a descent of the 680-point simplex, the largest four-dimensional reflexive polytope, whose transition depth is at most 31. Hence 22 ≤ D_4 ≤ 348; the exact value of D_4 is open.

Every result is proved by hand in the paper. `code/run_checks.sh` runs 77 independent checks in C, C++, Python, Julia, Macaulay2 and shell, and `lean/Seed.lean` proves 24 Lean 4 theorems, each axiom-free or depending on propext only.

Assets: the PDF, the LaTeX source with the figures as PNG (tex.zip), and the arXiv package (tar.gz) with the checks, the data and the Lean file in `anc/`.
