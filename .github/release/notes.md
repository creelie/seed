# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List, release 1.2.0

The paper is set as a single-column journal article (amsart) and cites this release by its GitHub link and the concept DOI. The definition of the cut operator is replaced by a direct statement of the cut proposition: a cut H_q either equals the cover or is not reflexive and contains the cover as a maximal reflexive subpolytope. A new check, `code/checks/check_cuts.py`, shows that the second case never occurs in dimension three (4,303 polyhedra with covers, 32,129 pairs of a cover and a dual vertex) and, with `FULL=1`, at the 5,250 polytopes of the depth-22 certificate that have covers (50,280 pairs). The description of the descent of the 680-point simplex and the open question on the 35-point polytope are corrected.

The bounds are unchanged: 22 ≤ D_4 ≤ 348, two polytopes of depth exactly 22, a descent of the 680-point polytope in at most 31 steps, and D_d ≤ 2(s_d − 1)² − 2 in every dimension d ≥ 4. There are 87 checks (98 with `FULL=1`) and 27 Lean 4 theorems.

Assets: the PDF, the LaTeX source with the figures as PNG (tex.zip), and the arXiv package (tar.gz) with the checks, the data and the Lean file in `anc/`.
