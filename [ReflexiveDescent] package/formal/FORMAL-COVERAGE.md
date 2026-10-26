# Lean verification coverage — 26 October 2026

This supplement is substantial new formal verification. It is **not** a
formal proof of the entire manuscript or of the exact four-dimensional
maximum. No such claim should be added to the title, abstract or release.

## Completed kernel proofs

| Mathematical statement | Lean file / principal declaration |
| --- | --- |
| Product covers change one factor; saturated descents split and combine | `DescentProducts.lean`, `descent_product_iff`, `product_order_covers` |
| Shortest and longest lengths add in Cartesian cover graphs | `shortest_product`, `longest_product` |
| The pentagon's five-node graph has shortest length 1 and longest length 2; its r-fold product has lengths r and 2r | `FiniteBases.lean`, `power_shortest`, `power_longest` |
| Polar of a geometric free sum is the product of the polars | `FreeSumGeometry.lean`, `polar_freeSum` |
| Lattice points of a direct-sum free sum lie on the coordinate factors | `lattice_points_on_axes` |
| Every reflexive subpolytope factors, with reflexive coordinate sections | `reflexive_subpolytope_factors` |
| The full **geometric** subpolytope order is the product order | `freeSumOrderIso` |
| Exact descent-length decomposition, shortest and longest addition for the geometric orders | `FreeSumDepth.lean`, `freeSum_descent_lengths`, `freeSum_shortest`, `freeSum_longest` |
| Ordinary integer-coordinate lattices and integrality of their dot-product pairing | `CoordinateLattice.lean`, `coordinatePairing_integral` |
| Equivalence of the manuscript's lower-bound polar convention and the formal code's upper-bound convention for lattice polars | `PolarConvention.lean`, `dual_latticeHull_conventions_iff` |
| Finiteness, saturated descent existence, and attained shortest/longest lengths, given a finite ambient lattice-point list covering P | `FiniteReflexive.lean`, `finite_subpolytopes`, `reflexive_depth_extrema_exist` |
| A terminal element of the finite geometric order is r-minimal among all reflexive subpolytopes | `terminal_reflexive_iff_rminimal` |
| A strict reflexive interval supplies a chain of covers with the primal/dual point-difference bound, without assuming the inclusion is a cover | `IntervalDescents.lean`, `interval_descent_bound` |
| Superadditive depth ratios have either a finite limit equal to their least upper bound, or tend to positive infinity | `DepthGrowth.lean`, `depth_ratio_finite_limit`, `depth_ratio_infinite_limit` |
| All stored depth-22 graph inequalities and both exact 22-step root descents | `Depth22Certificate.lean`, `certificate_checked`, `root_0_shortest`, `root_1_shortest` |
| The low-dimensional numerical bounds imply every nontrivial 4D free-sum depth is at most 11; an explicit overlattice has a mixed lattice point | `FourDimensionalObstruction.lean` |

The geometry is represented by real convex hulls, topological interiors,
additive lattices and bilinear polar pairings. `Reflexive` explicitly uses
the usual IP-reflexive convention: the origin is the unique interior
lattice point and both the polytope and its polar are finite lattice hulls.
The order isomorphism is proved from those conditions; it is not an axiom
or a hypothesis named after the desired result.

The ordinary coordinate lattice and dot product are explicitly constructed.
The polar-sign convention is reconciled by a proved negation equivalence.
The general statements also apply to other supplied lattices and pairings.
Finiteness statements expose their finite ambient point-list hypothesis;
they do not assert a formal proof of the published volume theorem.

## Depth-22 graph: exact scope

The graph is extracted from the supplied `depth22.json.gz`, SHA-256
`7f6c0607002c6aa251e3a2af5466030663834660c8d8ad93e9c87e272323f443`.
It contains 5,592 nodes, 23,646 recorded edges and 5,250 positive-bound
nodes. The complete lower-certificate check is reduced by the Lean kernel,
and `#print axioms certificate_checked` reports no axioms. Both recorded
roots have shortest graph length exactly 22.

Null cover lists on zero-bound frontier nodes are empty **in this graph**.
This convention does not claim that those polytopes have no geometric
covers. The lower-certificate argument uses only positive-bound nodes.
Both exhibited root paths finish at a node recorded with an actually empty
cover list, not a null frontier list.

To transfer this finite graph result to the geometric polytopes one must
verify the point-set identification, reflexivity, and completeness of every
positive-bound geometric cover list. This supplement does **not** formalize
that transfer. The preceding manuscript's computational geometry
certificates remain separate evidence; they are not replaced by an axiom.

The negative control `negative-controls/CorruptDepth22.lean` deliberately
raises the first root's lower bound from 22 to 23. It must fail, and Lean
rejects it because the certificate proposition is false.

## Not completed

- Geometric identification of the concrete pentagon's entire five-element
  reflexive-subpolytope order with `PentagonNode`. The written facet proof
  and Python enumeration remain available, but are not a Lean proof.
- The triangle's 512-subset geometric enumeration, its exact profile
  150/240, and the general chain-count/interleaving formula.
- A global Lean definition of D_d together with formal proofs of all
  geometric classification, volume and maximum-attainment inputs. The
  Fekete theorem exposes superadditivity as a hypothesis.
- Geometric completeness of the stored 4D cover lists.
- A Lean reconstruction of the 71,870 occupied census pairs and the
  geometry of all twelve interval witnesses. The existing integer Python
  verifier still checks these relative to the supplied census.
- A theorem determining the exact D4.

Accordingly, **22 <= D4 <= 346 is not claimed as an end-to-end Lean theorem
about all reflexive four-polytopes in this supplement**. The manuscript's
mathematical/data-backed bounds and the proved abstract interval lemma
have their stated scopes. There is no placeholder theorem silently assuming
the exact value, cover completeness, or the global bound.

## Why the free-sum theorem does not close D4

Using the earlier geometric results D1=0, D2=5 and D3=11, a nontrivial
four-dimensional free sum has factor dimensions (1,3), (2,2), or (3,1).
Depth addition gives an upper bound of 11, 10, or 11, respectively. Thus a
four-polytope of depth 22 cannot be such a lattice free sum, even after a
unimodular coordinate change. The new theorem reduces deeper searches to
polytopes indecomposable in the specified lattice; it cannot supply a
matching global upper bound of 22.

Changing to an overlattice does not preserve the product proof. For the
free sum of [-1,1] with itself, the overlattice generated by (1,0), (0,1)
and (1/2,1/2) has the mixed point (1/2,1/2) on the diamond. That point lies
on neither coordinate factor. The failure is explicit and formalized.

An exact determination would require either a proof that every reflexive
four-polytope has a descent of at most 22, or a larger attained depth
matched by a universal upper bound. Neither argument has been obtained.

## Build and audit

Lean: `leanprover/lean4:v4.34.0-rc2`.
Mathlib: commit `85e3a25e006c35636f0e53b0e9296caca2685bc0`.
These match the available cached compiler and library; they are pinned,
not an assertion of the latest release.

For a portable build with Lake:

```sh
lake exe cache get
lake build
lake env lean AxiomsAudit.lean
```

The audit inspects every theorem declaration in the target namespace,
including generated auxiliary declarations. It rejects custom axioms and
dependencies beyond `propext`, `Classical.choice`, and `Quot.sound`.
Counts of audited declarations include auxiliary theorems and are not
counts of independent mathematical results.

The local convenience driver `run_lean.py` uses the existing cached package
tree. `replay_lean.py` runs Lean's own kernel replay tool relative to
imports; this is an environment-integrity check, not another proof
assistant. Replay status is recorded separately in `kernel-replay.json`.

No `sorry`, `admit`, `native_decide`, unsafe proof declaration, custom axiom,
new release, ZIP, DOI or journal submission is part of the positive build.
The negative-control file is intentionally excluded from the default build.
