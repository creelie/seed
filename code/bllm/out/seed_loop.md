## seed-literal and uniform bound

| Round | Strategy | Failed checks | Change made | Label after round |
|---|---|---|---|---|
| 1 | descend by vertex deletion | vertex-deletion-descends | replace vertex deletion by cuts T^inf(Delta cap {<x,q> >= -1}) at dual lattice points q | OPEN |
| 2 | cuts at gauge-2 dual points | gauge-two-cuts-complete | candidate q from the dual volume bound of Balletti-Kasprzyk-Nill and the facet condition; branch at non-reflexive fixed points | OPEN |
| 3 | complete candidate set with branching | none | - | OPEN |
| 4 | literal reading and counting bound | none | - | OPEN |

- round 1, `vertex-deletion-descends`: FAIL. of 400 polytopes, 7 have no reflexive vertex deletion and 237 have a cover that is not a vertex deletion
- round 2, `gauge-two-cuts-complete`: FAIL. gauge-2 cuts give the wrong cover set for 73 of 400 polytopes
- round 3, `complete-covers-3d`: pass. complete covers agree with the vertex-deletion poset on 400 of 400 polytopes (0 non-reflexive fixed points met)
- round 4, `literal-D-equals-1`: pass. Kreuzer-Skarke: every reflexive 4-polytope contains a minimal polytope, so a chain of one step exists (Theorem A of the paper)
- round 4, `uniform-654`: pass. 473800776 polytopes; max of min(|P|-6, 680-|P*|) = 654

Final label: **CANDIDATE**; blocking factors: human.

## seed-sharp

| Round | Strategy | Failed checks | Change made | Label after round |
|---|---|---|---|---|
| 1 | sweep all 473,800,776 polytopes | sweep-feasible | certify chains only for extreme polytopes and bound the constant from below by exact breadth-first depths | OPEN |
| 2 | certified chains and exact lower bounds | exact-lower-bounds | - | OPEN |

- round 1, `sweep-feasible`: FAIL. 162328050 polytopes have trivial bound above 40; certifying 'a few tens' needs a chain or an exact depth for each, at about 3 minutes for the largest
- round 2, `chain-680-length-38`: pass. certified chain from the 680-point polytope of length 38
- round 2, `exact-lower-bounds`: FAIL. exact depths of chain polytopes []; D_4 >= None

Final label: **OPEN**; blocking factors: proof, human.

