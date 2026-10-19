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
the summaries of a run into `results/<tag>`. `queue.json` may also list the jobs explicitly; the
run `t50b` takes the row groups that the run `t50` left unfinished. `rowgroups.json` lists the
row groups of the thirty files (493 groups, 473,800,776 polytopes).

The second stage takes the polytopes left above T by the first (`results/<tag>/left.json`)
and certifies them with `hcert.py`. The cuts are the same, but the cost of a cut is the exact
length of the shortest maximal chain in the interval [Gamma, Delta] of the reflexive poset
whenever the smaller side of the difference has at most twelve points. Every maximal chain in
that interval consists of covers, so

    delta(Delta) <= ell[Gamma, Delta] + delta(Gamma).

The intermediate reflexive polytopes are the closed reflexive point sets Gamma u S, S inside
Delta minus Gamma (or, on the dual side, Delta* u S with S inside Gamma* minus Delta*), and
ell is the breadth-first distance from bottom to top in their Hasse diagram. A beam search
keeps the best partial chains, widening the beam when a polytope stays above T.
`hcert_shard.py` runs one job of `.github/workflows/farm-left.yml`, which reads
`left_queue.json`, and `hcert_merge.py` merges the run into `results/<tag>`.

Run one job by hand:

    export PALP=/path/to/palp-2.21/poly.x
    python3 farm_shard.py 13:0,13:1 50 4 19500 out
    python3 hcert_shard.py results/t50/left.json 0 10 50 4 out
