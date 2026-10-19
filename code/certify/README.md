# Certificate farm for the depth bound in dimension four

`bcert.py` gives a reflexive 4-polytope a chain of cuts. A cut keeps the lattice points
x of the current polytope with <x,q> >= -1 for a lattice point q of 3 Delta* outside Delta*;
PALP decides whether the hull is reflexive and counts its points and dual points. For
reflexive Gamma inside Delta the descent satisfies

    delta(Delta) <= min(|Delta| - |Gamma|, |Gamma*| - |Delta*|) + delta(Gamma),

and delta(Gamma) <= L(|Gamma|, |Gamma*|), the pair bound of `../data/pair_chain.csv`.
A polytope is certified at threshold T when the sum of the step costs along its chain plus
the pair bound of its last polytope is at most T.

`farm_shard.py` certifies every polytope of some row groups of the Hugging Face copy of the
Kreuzer-Skarke list (`calabi-yau-data/polytopes-4d`) whose pair bound exceeds T; polytopes
left above T by the fast search are searched again with every cut. `farm_plan.py` turns
`queue.json` into the job matrix of `.github/workflows/farm.yml`, and `farm_merge.py` merges
the summaries of a run into `results/<tag>`. `rowgroups.json` lists the row groups of the
thirty files (493 groups, 473,800,776 polytopes).

Run one job by hand:

    export PALP=/path/to/palp-2.21/poly.x
    python3 farm_shard.py 13:0,13:1 50 4 19500 out
