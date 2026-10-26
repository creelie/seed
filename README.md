# Reflexive Descent to Minimal Seeds: Uniform Bounds and Free Sums

Current research revision: **v1.3.0**, by **Deep Bhattacharjee**.
The earlier joint work with Ushashi Bhattacharya is retained and credited.

Current manuscript and complete release folder:
[`[ReflexiveDescent] package`](%5BReflexiveDescent%5D%20package).
The [release](https://github.com/creelie/seed/releases/tag/v1.3.0) has
version-specific archival information in its DOI receipt.

The revision adds the free-sum order theorem, exact depth families and
Lean verification of the core geometric and descent results. It includes
81 named source theorems, a 255-declaration axiom audit including generated
auxiliaries, and kernel checks of the stored depth-22 graph. Read
[`FORMAL-COVERAGE.md`](%5BReflexiveDescent%5D%20package/formal/FORMAL-COVERAGE.md)
before interpreting the verification claims.

**The exact D4 is not proved.** The stated range is 22 <= D4 <= 346
relative to the supplied KS census. Geometric cover completeness and the
census are not verified end to end in Lean. The arbitrary-descent bound
remains 348. This archive is not a journal acceptance or a full closure.

## Previous release documentation

The following describes the preceding manuscript and checks. The current
revision and verification scope above supersede its version-specific claims.

# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23483239.svg)](https://doi.org/10.5281/zenodo.23483239)

Deep Bhattacharjee and Ushashi Bhattacharya

This repository holds the paper, the data and the independent checks for
*Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List*. The paper is
in [`preprints/ReflexiveDescent.pdf`](preprints/ReflexiveDescent.pdf)
and its LaTeX source in [`paper/`](paper/).

## What is proved

A reflexive polytope Γ inside a reflexive polytope Δ is a *cover* of Δ when no
reflexive polytope lies strictly between them. A *reflexive descent* of Δ is a
chain of covers that ends at an r-minimal polytope, one that contains no
smaller reflexive polytope. The *transition depth* δ(Δ) is the length of the
shortest descent, and D_d is the largest transition depth among the reflexive
polytopes of dimension d.

1. Every reflexive polytope has a reflexive descent, every descent ends at an
   r-minimal polytope, and every r-minimal polytope contains a minimal seed.
2. In dimension four no reflexive descent has more than 348 steps. Every chain
   of reflexive polytopes has strictly decreasing point counts and strictly
   increasing dual point counts, and the longest such chain through the pairs
   that occur among the 473,800,776 polytopes of the Kreuzer–Skarke list has
   348 steps. Hence D_4 ≤ 348, and the conjecture of a uniform transition depth
   holds with D = 349.
3. D_2 = 5, attained only by the triangle with ten lattice points, and
   D_3 = 11, attained by exactly two polytopes, with 35 and 31 lattice points.
4. The polytopes P_1 = conv(e_1, e_2, e_3, u + 8e_4, u − 8e_4) and
   P_2 = conv(e_1, e_2, e_3, u, u + 8e_4, e_3 − 8e_4), with u = (−4, −2, −1, 0),
   skew bipyramids over a reflexive tetrahedron with 37 lattice points each,
   have transition depth exactly 22. The lower bound is a certificate of 5,592
   polytopes with their complete lists of covers, checked one polytope at a
   time (the certificate lemma of the paper). P_1 is the polytope reached after
   ten steps of the descent of the largest polytope Δ_680, and Δ_680 has
   transition depth at most 31. Hence 22 ≤ D_4 ≤ 348.
5. In every dimension d ≥ 4, every chain of reflexive polytopes has at most
   2(s_d − 1)² − 2 steps, where s_1 = 2, s_{k+1} = s_k² − s_k + 1 is Sylvester's
   sequence. This follows from Blichfeldt's bound on lattice points and the
   volume theorem of Balletti, Kasprzyk and Nill, with no classification.

6. The cuts that produce the covers never need the second case of the cut
   proposition in dimension three, nor at any of the 5,250 polytopes of the
   depth-22 certificate that have covers: every cut H_q met by the procedure is
   reflexive and equals the cover (32,129 and 50,280 pairs). Whether the second
   case occurs anywhere in dimension four is open.

The exact value of D_4 is open.

## Layout

| Path | Contents |
|---|---|
| `paper/` | `main.tex`, the figures as PNG and the script that draws them; `paper1/` the compiled paper, `paper2/` its LaTeX source as a zip |
| `preprints/` | the compiled paper |
| `code/` | the programs used in the paper: convex hulls and lattice points (`rhull.py`), complete covers (`complete.py`), cuts and climbs (`greedy.py`), exact depths by breadth-first search (`bfs_depth.py`), the pair bound (`pair_chain.py`), the certification of the descent of Δ_680 (`certify_chain.py`), and the certificate farm for upper bounds (`certify/`) |
| `code/data/` | the joint distribution of point counts over the four-dimensional list, the pair bounds and a longest chain, the cover relation in dimensions two and three, the descent of Δ_680 with its certificates, the shorter descent from its step 9 (`descent9.json`), and the depth-22 certificate for P_1 and P_2 (`depth22.json.gz`) |
| `code/checks/` | independent checks in C, C++, Python, Julia and Macaulay2 |
| `code/bllm/` | the failure, change and retry log of the search, run on the Anaxia engine |
| `lean/Seed.lean` | 27 theorems in Lean 4 (core library only) on the finite arithmetic, the counting lemma in dimension four and in every dimension, the certificate lemma and the map from P_1 to step 10 of the descent of Δ_680 |

## Running the checks

```sh
python3 -m pip install -r requirements.txt
PALP=/path/to/poly.x bash code/run_checks.sh          # 87 checks
FULL=1 PALP=/path/to/poly.x bash code/run_checks.sh   # 98 checks, recomputes every cover of the descents and checks the cuts at the depth-22 certificate
```

The script needs gcc, g++, Python 3 with numpy and scipy, Julia, Macaulay2 and
Lean 4 (the version in `lean/lean-toolchain`); a missing tool is reported and
its checks are skipped. PALP (Kreuzer and Skarke's `poly.x`) is needed for one
comparison in the default run and for `FULL=1`, which recomputes the 5,251 cover
lists of the depth-22 certificate (about two CPU-hours, spread over all CPUs). The Kreuzer–Skarke list itself is not stored here:
the point counts were read from its public copy on Hugging Face
(`calabi-yau-data/polytopes-4d`).

## Citation

See [`CITATION.cff`](CITATION.cff). Zenodo archives each GitHub release under
its own version DOI and gathers all of them under one concept DOI; the paper
cites the version DOI of release v1.1.0.

| | DOI |
| --- | --- |
| release v1.1.0 (version DOI) | [10.5281/zenodo.23486780](https://doi.org/10.5281/zenodo.23486780) |
| release v1.0.1 (version DOI) | [10.5281/zenodo.23483443](https://doi.org/10.5281/zenodo.23483443) |
| release v1.0.0 (version DOI) | [10.5281/zenodo.23483240](https://doi.org/10.5281/zenodo.23483240) |
| all versions (concept DOI) | [10.5281/zenodo.23483239](https://doi.org/10.5281/zenodo.23483239) |

Everything in the paper, with the data, the checks and the release assets, is
also collected in one file,
[`ReflexiveDescent_masterzipfinal2.zip`](https://github.com/creelie/seed/raw/main/ReflexiveDescent_masterzipfinal2.zip).

## License

MIT for the code; the paper is licensed CC BY 4.0.
