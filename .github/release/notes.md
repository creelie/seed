# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List, release 1.1.0

New in this release is a bound in every dimension (Proposition 11 of the paper). For d ≥ 4, every chain of reflexive polytopes of dimension d has at most 2(s_d − 1)² − 2 steps, where s_1 = 2, s_{k+1} = s_k² − s_k + 1 is Sylvester's sequence; in particular the largest transition depth satisfies D_d ≤ 2(s_d − 1)² − 2. The proof combines Blichfeldt's bound on the number of lattice points of a lattice polytope with the theorem of Balletti, Kasprzyk and Nill on the largest volume of a reflexive polytope, and needs no classification. The step from the two inequalities to the bound is a theorem of the Lean file for every d, and a new check compares the bound with the posets of dimensions two and three and the point counts in dimension four.

The search record was rerun on the Anaxia engine, release 3.1.1 (10.5281/zenodo.23484395). The paper cites its archive by the version DOI of release 1.0.1.

The four-dimensional results are those of release 1.0.0: 22 ≤ D_4 ≤ 348, two polytopes of depth exactly 22, and a descent of the 680-point polytope in at most 31 steps. There are now 83 checks and 27 Lean 4 theorems.

Assets: the PDF, the LaTeX source with the figures as PNG (tex.zip), and the arXiv package (tar.gz) with the checks, the data and the Lean file in `anc/`.
