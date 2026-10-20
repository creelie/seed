## seed-literal and uniform bound

| Round | Strategy | Failed checks | Change made | Label after round |
|---|---|---|---|---|
| 1 | descend by vertex deletion | vertex-deletion-descends | replace vertex deletion by cuts T^inf(Delta cap {<x,q> >= -1}) at dual lattice points q | OPEN |
| 2 | cuts at gauge-2 dual points | gauge-two-cuts-complete | candidate q from the dual volume bound of Balletti-Kasprzyk-Nill and the facet condition; branch at non-reflexive fixed points | OPEN |
| 3 | complete candidate set with branching | none | - | OPEN |
| 4 | literal reading and counting bound | none | - | OPEN |
| 5 | longest chain of realised pairs | none | - | CANDIDATE |

- round 1, `vertex-deletion-descends`: FAIL. of 400 polytopes, 7 have no reflexive vertex deletion and 237 have a cover that is not a vertex deletion
- round 2, `gauge-two-cuts-complete`: FAIL. gauge-2 cuts give the wrong cover set for 73 of 400 polytopes
- round 3, `complete-covers-3d`: pass. complete covers agree with the vertex-deletion poset on 400 of 400 polytopes (0 non-reflexive fixed points met)
- round 4, `literal-D-equals-1`: pass. Kreuzer-Skarke: every reflexive 4-polytope contains a minimal polytope, so a chain of one step exists (Theorem A of the paper)
- round 4, `uniform-654`: pass. 473800776 polytopes; max of min(|P|-6, 680-|P*|) = 654
- round 5, `uniform-348`: pass. longest chain of realised pairs with points falling and dual points rising: 348 steps, only from (521, 22); so D_4 <= 348 and D = 349 with the minimal seed
- round 5, `low-dimensions`: pass. dimension 2: 16 polytopes, largest depth 5; dimension 3: 4319 polytopes, largest depth 11
- round 5, `every-dimension`: pass. Blichfeldt's bound |P| <= nvol P + d and the volume theorem of Balletti-Kasprzyk-Nill give D_d <= 2(s_d-1)^2 - 2 for d >= 4; checks/check_everydim.py: 6 checks passed, 0 failed

Final label: **CANDIDATE**; blocking factors: human.

## seed-sharp

| Round | Strategy | Failed checks | Change made | Label after round |
|---|---|---|---|---|
| 1 | sweep all 473,800,776 polytopes | sweep-feasible | certify chains only for extreme polytopes and bound the constant from below by exact breadth-first depths | OPEN |
| 2 | certified chains and exact lower bounds | none | - | OPEN |
| 3 | exact depths along the chain | none | - | OPEN |
| 4 | skew bipyramids | sharp-constant | descend from step 9 of the chain through complete covers, choosing at each step the cover of least greedy rank; test the polytopes above P_1 and P_2 for depth 23 | OPEN |
| 5 | descent from step 9 | sharp-constant | certify every polytope of the list at threshold 50 by chains of cuts (code/certify) | OPEN |

- round 1, `sweep-feasible`: FAIL. 162328050 polytopes have trivial bound above 40; certifying 'a few tens' needs a chain or an exact depth for each, at about 3 minutes for the largest
- round 2, `chain-680-length-38`: pass. certified chain from the 680-point polytope of length 38
- round 2, `exact-lower-bounds`: pass. exact depths (points, depth) of chain polytopes [(15, 4), (20, 9)]; D_4 >= 9
- round 3, `depth-680-at-most-36`: pass. step 27 of the chain has exact depth 9, so delta(Delta_680) <= 27 + 9 = 36
- round 4, `depth-22`: pass. certificate of 5592 polytopes with complete cover lists below the skew bipyramids P_1, P_2 (37 points each): depth exactly 22; checks/check_depth22.py: 7 checks passed, 0 failed
- round 4, `depth-680-at-most-32`: pass. the unimodular map G carries P_1 onto step 10 of the chain of Delta_680, so delta(Delta_680) <= 10 + 22 = 32
- round 4, `sharp-constant`: FAIL. 22 <= D_4 <= 348; closing the gap needs exact depths of polytopes with more lattice points, or a certified chain of at most 22 steps for each polytope above 22
- round 5, `depth-680-at-most-31`: pass. a descent of 22 covers from step 9 of the chain (44 to 19 points, each a complete cover), so delta(Delta_680) <= 9 + 22 = 31
- round 5, `sharp-constant`: FAIL. 22 <= D_4 <= 348; closing the gap needs exact depths of polytopes with more lattice points, or a certified chain of at most 22 steps for each polytope above 22

Final label: **OPEN**; blocking factors: proof, human.

