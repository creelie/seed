# Reflexive descent: uniform bounds and free sums

Review revision prepared 26 October 2026 from the supplied Annals source ZIP
and Hexagon 2610.00456v1 source ZIP. Original inputs are preserved in `inputs/`.

## Results and limits

The original uniform-existence conjecture is proved by the finite reflexive
subpolytope order. The revised manuscript supplies an explicit terminating
algorithm and a classification-free four-dimensional bound of 3526, using
the published Balletti–Kasprzyk–Nill volume theorem.

The new direct-sum-lattice free-sum theorem identifies the entire reflexive
subpolytope order with the product of the factor orders. Both shortest and
longest saturated descent lengths add. The explicitly defined pentagon
family in dimension 2r has shortest length r, longest length 2r, and complete
exponential descent profile t^r(1+t)^r. This proves by a direct geometric
argument that depths and shortest–longest gaps can grow with dimension.

Two exact integer enumerators check all 512 subsets of the triangle base.
Its 79 embedded reflexive subpolygons give shortest length 5, longest length
6, and chain counts 150 and 240. Free sums give exact lengths 5r and 6r.
The extremal depths are superadditive and their ratio to dimension has an
extended limit. These results do not determine the optimal growth rate.

The twelve existing interval witnesses have been freshly rechecked using
integer arithmetic. They give 22 <= D4 <= 346 **relative to the supplied
Kreuzer–Skarke census and published classification**. They do not independently
regenerate that census. The bound 348 for every descent is a separate result.
The exact value of D4 remains open. The original 5592-node depth-22 cover
reconstruction was not rerun here; it is explicitly identified as a preceding
certificate when used for the stronger 22r family.

A new Lean supplement in ormal/ verifies the geometric free-sum order isomorphism, depth addition, interval and finite-order lemmas, and the stored depth-22 graph certificate. The full manuscript and the exact D4 remain unformalized; see ormal/FORMAL-COVERAGE.md for the precise assumptions and remaining obligations. The
new results have not received independent human peer review, and no claim
of journal acceptance or priority after an exhaustive literature review is made.

## Files

- `manuscript/main.tex`: one coherent revised manuscript, aomart format,
  sole author Deep Bhattacharjee, original joint work credited in a footnote
  and reference, no margin line numbering.
- `manuscript/ReflexiveDescentUniformBoundsFreeSums.pdf`: compiled manuscript.
- `manuscript/anc/verify_free_sums.py`: standard-library exact base verifiers.
- `manuscript/anc/seed_intervals.py`: standalone exact interval verifier.
- `manuscript/anc/triangle-certificate.json` and `pentagon-certificate.json`:
  complete embedded orders, covers, profiles, depths and heights.
- `source-sha256.json`: source and data hashes.
- `AI-PROVENANCE.md`: description of assistance and verification scope.

Run both Python files in `manuscript/anc/` with Python 3. They require no
third-party package. Compile `manuscript/main.tex` with pdfLaTeX twice, using
the supplied class and figures. There is no new release, ZIP or DOI in this
review revision.

## Data attribution

The twelve interval records and histogram are copied from the existing
Anaxia research revision. The coordinate source is the Kreuzer–Skarke
classification, M. Kreuzer and H. Skarke, Adv. Theor. Math. Phys. 4 (2000),
1209–1230, DOI 10.4310/ATMP.2000.v4.n6.a2, distributed at
https://huggingface.co/datasets/calabi-yau-data/polytopes-4d under CC BY-SA 4.0.
Derivative coordinate/certificate data retain CC BY-SA 4.0. Source digests
and attribution are stored in `seed_top346.json`. The supplied aomart class
retains its embedded license notice. This review folder does not relicense
third-party data or software.
