# Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23483239.svg)](https://doi.org/10.5281/zenodo.23483239)

Deep Bhattacharjee and Ushashi Bhattacharya

This repository holds the paper, the data and the independent checks for
*Reflexive Descent to Minimal Seeds in the Kreuzer–Skarke List*, release
v2.0.0. The paper is in [`preprints/ReflexiveDescent.pdf`](preprints/ReflexiveDescent.pdf)
and its LaTeX source in [`paper/main.tex`](paper/main.tex). It revises the
preprint Hexagon 2610.00456v1.

## What is proved

A reflexive polytope Γ inside a reflexive polytope Δ is a *cover* of Δ when no
reflexive polytope lies strictly between them. A *reflexive descent* of Δ is a
chain of covers that ends at an r-minimal polytope, one that contains no
smaller reflexive polytope. The *transition depth* δ(Δ) is the length of the
shortest descent, h(Δ) the length of the longest, and D_d and H_d are their
largest values among the reflexive polytopes of dimension d.

1. Every reflexive polytope has a reflexive descent, every descent ends at an
   r-minimal polytope, and every r-minimal polytope contains a minimal seed.
2. D_2 = 5, attained only by the triangle with ten lattice points, and
   D_3 = 11, attained by exactly two polytopes, with 35 and 31 lattice points.
3. 22 ≤ D_4 ≤ 50 and H_4 ≤ 348. The lower bound is attained by two skew
   bipyramids P_1, P_2 with 37 lattice points (a certificate of 5,592
   polytopes). The upper bound: every polytope whose pair bound exceeds 50
   (92,422,743 of the 473,800,776 polytopes of the list) carries a chain of
   cuts whose descents are bounded by the chain lemma of the paper; every chain
   was replayed against the whole list (`code/certify/results/r50/replay.json`:
   all 493 row groups, all 92,422,743 polytopes covered, largest bound 50).
   Hence the conjecture of a uniform transition depth holds with D = 51.
4. Free sums: the reflexive subpolytopes of P ⊕ Q are the free sums of
   reflexive subpolytopes of P and of Q, so δ and h add. Hence
   D_{d+e} ≥ D_d + D_e, D_d ≥ 11d/2 − 6, and D_d/d converges to a limit in
   [11/2, ∞].
5. In every dimension d ≥ 4, every chain of reflexive polytopes has at most
   2(s_d − 1)² − 2 steps, where s_d is Sylvester's sequence.

The exact value of D_4, and whether D_d/d has a finite limit, are open.

The folder [`[ReflexiveDescent] package`](%5BReflexiveDescent%5D%20package)
holds the material of release v1.3.0 (a Lean supplement and its manuscript);
its range 22 ≤ D_4 ≤ 346 is superseded by the bound 50 above.

## Layout

| Path | Contents |
|---|---|
| `paper/` | `main.tex`, the figures as PNG and the script that draws them; `paper1/` the compiled paper, `paper2/` its LaTeX source as a zip |
| `preprints/` | the compiled paper |
| `code/` | the programs used in the paper: convex hulls and lattice points (`rhull.py`), complete covers (`complete.py`), cuts and climbs (`greedy.py`), exact depths by breadth-first search (`bfs_depth.py`), the pair bound (`pair_chain.py`), the certification of the descent of Δ_680 (`certify_chain.py`), and the certificate farm and its replay for the bound D_4 ≤ 50 (`certify/`) |
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
its own version DOI and gathers all of them under one concept DOI.

| | DOI |
| --- | --- |
| release v1.3.0 (version DOI) | [10.5281/zenodo.23653341](https://doi.org/10.5281/zenodo.23653341) |
| release v1.2.0 (version DOI) | [10.5281/zenodo.23539317](https://doi.org/10.5281/zenodo.23539317) |
| release v1.1.1 (version DOI) | [10.5281/zenodo.23487205](https://doi.org/10.5281/zenodo.23487205) |
| release v1.1.0 (version DOI) | [10.5281/zenodo.23486780](https://doi.org/10.5281/zenodo.23486780) |
| release v1.0.1 (version DOI) | [10.5281/zenodo.23483443](https://doi.org/10.5281/zenodo.23483443) |
| release v1.0.0 (version DOI) | [10.5281/zenodo.23483240](https://doi.org/10.5281/zenodo.23483240) |
| all versions (concept DOI) | [10.5281/zenodo.23483239](https://doi.org/10.5281/zenodo.23483239) |

Everything in the paper, with the data, the checks and the release assets, is
also collected in one file,
[`ReflexiveDescent_masterzipfinal2.zip`](https://github.com/creelie/seed/raw/main/ReflexiveDescent_masterzipfinal2.zip).

## License

MIT for the code; the paper is licensed CC BY 4.0.
