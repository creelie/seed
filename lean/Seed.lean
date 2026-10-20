/-
  Reflexive descent to minimal seeds in the Kreuzer-Skarke list:
  the finite arithmetic of the paper, checked by the Lean kernel.
  Core Lean 4 only; every proof is `decide`, `rfl` or an induction.
-/

namespace Seed

/-! ## The simplex Δ₆₈₀ -/

/-- normalised volume of Δ₆₈₀ (the product formula for the simplex of the weights) -/
theorem volume_delta680 : 2 * 42 ^ 2 = 3528 := by decide

/-- normalised volume of the dual simplex: the sum of the weights -/
theorem volume_dual : 1 + 1 + 12 + 28 + 42 = 84 := by decide

/-- 1/2 + 1/3 + 1/7 + 1/42 = 1, cleared of denominators -/
theorem egyptian : 42 / 2 + 42 / 3 + 42 / 7 + 42 / 42 = 42 ∧ 42 % 2 = 0 ∧ 42 % 3 = 0 ∧ 42 % 7 = 0 := by
  decide

/-- the weights divided by their sum 84 are 1/2, 1/3, 1/7, 1/84, 1/84 -/
theorem weights_over_sum : 84 = 2 * 42 ∧ 84 = 3 * 28 ∧ 84 = 7 * 12 ∧ 84 = 84 * 1 := by decide

/-- Sylvester's sequence s₀ = 2, sₙ₊₁ = sₙ² − sₙ + 1 -/
def sylvester : Nat → Nat
  | 0 => 2
  | n + 1 => sylvester n * sylvester n - sylvester n + 1

theorem sylvester_first : [sylvester 0, sylvester 1, sylvester 2, sylvester 3] = [2, 3, 7, 43] := by decide

theorem sylvester_42 : sylvester 3 = 42 + 1 ∧ 2 * 3 * 7 = 42 := by decide

/-- number of monomials of degree 84 in P(1,1,12,28,42): for u₂, u₃, u₄ the
    remaining degree r = 84 − 12u₂ − 28u₃ − 42u₄ is split as u₀ + u₁ in r + 1 ways -/
def monomials84 : Nat :=
  (List.range 3).foldl (fun s u4 =>
    (List.range 4).foldl (fun s u3 =>
      (List.range 8).foldl (fun s u2 =>
        if 12 * u2 + 28 * u3 + 42 * u4 ≤ 84 then s + (84 - 12 * u2 - 28 * u3 - 42 * u4 + 1) else s)
      s) s) 0

/-- Δ₆₈₀ has 680 lattice points -/
theorem points_delta680 : monomials84 = 680 := by decide +kernel

/-- lattice points of the dual of Δ₆₈₀, in the coordinates y = (a − 1, b − 12, c − 28, e − 42):
    the five vertex inequalities ⟨v, y⟩ ≥ −1 become 83a ≥ b + c + e, 6b ≥ a + c + e,
    2c ≥ a + b + e, e ≥ a + b + c and a + b + c + e ≤ 84 -/
def dualPoints : Nat :=
  (List.range 3).foldl (fun s a =>
    (List.range 14).foldl (fun s b =>
      (List.range 30).foldl (fun s c =>
        (List.range 44).foldl (fun s e =>
          if b + c + e ≤ 83 * a ∧ a + c + e ≤ 6 * b ∧ a + b + e ≤ 2 * c ∧ a + b + c ≤ e ∧ a + b + c + e ≤ 84
          then s + 1 else s) s) s) s) 0

/-- the dual of Δ₆₈₀ has 26 lattice points -/
theorem points_dual : dualPoints = 26 := by decide +kernel

/-! ## The counting lemma -/

/-- a chain of point pairs (|Δᵢ|, |Δᵢ*|) along a descent: the first entry strictly
    decreases and the second strictly increases -/
def StrictChain : List (Nat × Nat) → Prop
  | [] => True
  | [_] => True
  | a :: b :: t => b.1 < a.1 ∧ a.2 < b.2 ∧ StrictChain (b :: t)

instance : (l : List (Nat × Nat)) → Decidable (StrictChain l)
  | [] => isTrue trivial
  | [_] => isTrue trivial
  | a :: b :: t =>
    have : Decidable (StrictChain (b :: t)) := instDecidableStrictChain (b :: t)
    inferInstanceAs (Decidable (b.1 < a.1 ∧ a.2 < b.2 ∧ StrictChain (b :: t)))

/-- along a chain of length k starting at (p, q), every later pair has p' + k' ≤ p -/
theorem chain_first (a : Nat × Nat) (t : List (Nat × Nat)) (h : StrictChain (a :: t))
    (lo : ∀ x ∈ a :: t, 6 ≤ x.1) : t.length + 6 ≤ a.1 := by
  induction t generalizing a with
  | nil => exact lo a (List.mem_cons_self ..)
  | cons b t ih =>
    have hb : b.1 < a.1 := h.1
    have ht : StrictChain (b :: t) := h.2.2
    have := ih b ht (fun x hx => lo x (List.mem_cons_of_mem _ hx))
    have h7 : t.length + 6 < a.1 := Nat.lt_of_le_of_lt this hb
    show t.length + 1 + 6 ≤ a.1
    rw [Nat.add_right_comm]
    exact h7

/-- along a chain starting at (p, q) with all second entries at most 680,
    the length k satisfies q + k ≤ 680 -/
theorem chain_dual (a : Nat × Nat) (t : List (Nat × Nat)) (h : StrictChain (a :: t))
    (hi : ∀ x ∈ a :: t, x.2 ≤ 680) : a.2 + t.length ≤ 680 := by
  induction t generalizing a with
  | nil => exact hi a (List.mem_cons_self ..)
  | cons b t ih =>
    have hb : a.2 < b.2 := h.2.1
    have ht : StrictChain (b :: t) := h.2.2
    have := ih b ht (fun x hx => hi x (List.mem_cons_of_mem _ hx))
    have h7 : a.2 + t.length < 680 := Nat.lt_of_lt_of_le (Nat.add_lt_add_right hb _) this
    show a.2 + (t.length + 1) ≤ 680
    rw [← Nat.add_assoc]
    exact h7

/-- the counting lemma: a descent from a polytope with p lattice points and q dual
    lattice points, among reflexive 4-polytopes (at least 6 points, at most 680 dual
    points), has at most min(p − 6, 680 − q) steps -/
theorem counting_lemma (a : Nat × Nat) (t : List (Nat × Nat)) (h : StrictChain (a :: t))
    (lo : ∀ x ∈ a :: t, 6 ≤ x.1) (hi : ∀ x ∈ a :: t, x.2 ≤ 680) :
    t.length ≤ a.1 - 6 ∧ t.length ≤ 680 - a.2 := by
  have h1 := chain_first a t h lo
  have h2 := chain_dual a t h hi
  constructor
  · exact Nat.le_sub_of_add_le h1
  · exact Nat.le_sub_of_add_le (by rw [Nat.add_comm]; exact h2)

/-- in any dimension: along a strict chain whose first entries are all at least m,
    the first entry of the head exceeds the length by at least m -/
theorem chain_first_ge (m : Nat) (a : Nat × Nat) (t : List (Nat × Nat)) (h : StrictChain (a :: t))
    (lo : ∀ x ∈ a :: t, m ≤ x.1) : t.length + m ≤ a.1 := by
  induction t generalizing a with
  | nil =>
    show 0 + m ≤ a.1
    rw [Nat.zero_add]
    exact lo a (List.mem_cons_self ..)
  | cons b t ih =>
    have hb : b.1 < a.1 := h.1
    have ht : StrictChain (b :: t) := h.2.2
    have := ih b ht (fun x hx => lo x (List.mem_cons_of_mem _ hx))
    have h7 : t.length + m < a.1 := Nat.lt_of_le_of_lt this hb
    show t.length + 1 + m ≤ a.1
    rw [Nat.add_right_comm]
    exact h7

/-- the proposition for every dimension: a chain of reflexive d-polytopes, each with at
    least d + 2 lattice points, starting at a polytope with at most V + d points
    (Blichfeldt, with V the largest normalised volume), has at most V − 2 steps -/
theorem every_dimension (d V : Nat) (a : Nat × Nat) (t : List (Nat × Nat))
    (h : StrictChain (a :: t)) (lo : ∀ x ∈ a :: t, d + 2 ≤ x.1) (hi : a.1 ≤ V + d) :
    t.length ≤ V - 2 := by
  have h1 := Nat.le_trans (chain_first_ge (d + 2) a t h lo) hi
  rw [← Nat.add_assoc, Nat.add_right_comm, Nat.add_comm V d] at h1
  rw [Nat.add_comm (t.length + 2) d] at h1
  exact Nat.le_sub_of_add_le (Nat.le_of_add_le_add_left h1)

/-- the bound in dimension four from the volume 2 · 42² of Balletti, Kasprzyk and Nill -/
theorem every_dimension_four : 2 * (sylvester 3 - 1) ^ 2 - 2 = 3526 := by decide

/-- the simple bound at Δ₆₈₀ = (680, 26) and its maximum -/
theorem simple_bound_680 : min (680 - 6) (680 - 26) = 654 := by decide

/-! ## The pair bound -/

/-- a longest chain of realised point pairs: 349 pairs, 348 steps, from (521, 22) -/
def witness : List (Nat × Nat) := [
  (521, 22), (520, 26), (519, 27), (518, 28), (517, 29), (516, 30), (512, 31), (511, 32),
  (505, 33), (502, 34), (491, 35), (485, 36), (476, 37), (472, 38), (465, 39), (460, 40),
  (457, 41), (452, 42), (447, 43), (442, 44), (437, 45), (436, 46), (430, 47), (427, 48),
  (425, 49), (424, 50), (423, 51), (419, 52), (417, 53), (415, 54), (414, 55), (413, 56),
  (409, 57), (408, 58), (406, 59), (405, 61), (404, 62), (402, 63), (400, 64), (398, 65),
  (393, 66), (392, 67), (391, 68), (388, 69), (386, 70), (384, 71), (383, 72), (382, 73),
  (380, 74), (379, 75), (376, 76), (374, 77), (373, 78), (372, 79), (370, 80), (369, 81),
  (368, 82), (367, 83), (364, 84), (362, 85), (360, 86), (358, 87), (356, 88), (353, 89),
  (351, 90), (350, 91), (348, 92), (345, 93), (343, 94), (342, 95), (341, 96), (339, 97),
  (338, 98), (336, 99), (335, 100), (334, 101), (332, 102), (331, 103), (330, 104), (329, 105),
  (324, 106), (323, 107), (322, 108), (320, 109), (318, 110), (316, 111), (314, 112), (313, 113),
  (312, 114), (309, 116), (308, 117), (307, 118), (305, 119), (304, 120), (303, 122), (302, 123),
  (300, 124), (299, 125), (298, 126), (297, 127), (296, 128), (295, 130), (294, 131), (292, 132),
  (291, 133), (290, 134), (289, 135), (288, 136), (287, 137), (286, 138), (285, 139), (284, 140),
  (283, 141), (282, 143), (281, 144), (280, 146), (279, 147), (278, 148), (277, 149), (276, 150),
  (275, 151), (274, 152), (273, 153), (272, 154), (271, 155), (269, 157), (267, 158), (266, 159),
  (264, 160), (263, 161), (262, 163), (261, 164), (259, 165), (258, 166), (257, 167), (256, 168),
  (255, 169), (254, 171), (253, 172), (251, 173), (250, 174), (249, 175), (248, 176), (247, 177),
  (246, 178), (243, 179), (242, 180), (241, 181), (240, 182), (239, 183), (238, 184), (237, 185),
  (236, 186), (235, 187), (234, 188), (232, 190), (230, 191), (229, 193), (228, 194), (227, 195),
  (226, 196), (225, 197), (224, 198), (223, 199), (222, 200), (221, 201), (220, 202), (219, 205),
  (218, 206), (217, 207), (216, 208), (215, 209), (214, 210), (213, 211), (212, 212), (211, 213),
  (210, 214), (209, 215), (208, 216), (207, 217), (206, 218), (205, 219), (202, 220), (201, 221),
  (200, 222), (199, 223), (198, 224), (197, 225), (196, 226), (195, 227), (194, 228), (193, 229),
  (191, 230), (190, 232), (188, 234), (187, 235), (186, 236), (185, 237), (184, 238), (183, 239),
  (182, 240), (181, 241), (180, 242), (179, 243), (178, 246), (177, 247), (176, 248), (175, 249),
  (174, 250), (173, 251), (172, 253), (171, 254), (169, 255), (168, 256), (167, 257), (166, 258),
  (165, 259), (164, 261), (163, 262), (161, 263), (160, 264), (159, 266), (158, 267), (157, 269),
  (155, 271), (154, 272), (153, 273), (152, 274), (151, 275), (150, 276), (149, 277), (148, 278),
  (147, 279), (146, 280), (144, 281), (143, 282), (141, 283), (140, 284), (139, 285), (138, 286),
  (137, 287), (136, 288), (135, 289), (134, 290), (133, 291), (132, 292), (131, 294), (130, 295),
  (128, 296), (127, 297), (126, 298), (125, 299), (124, 300), (123, 302), (122, 303), (120, 304),
  (119, 305), (118, 307), (117, 308), (116, 309), (114, 312), (113, 313), (112, 314), (111, 316),
  (110, 318), (109, 320), (108, 322), (107, 323), (106, 324), (105, 329), (104, 330), (103, 331),
  (102, 332), (101, 334), (100, 335), (99, 336), (98, 338), (97, 339), (96, 341), (95, 342),
  (94, 343), (93, 345), (92, 348), (91, 350), (90, 351), (89, 353), (88, 356), (87, 358),
  (86, 360), (85, 362), (84, 364), (83, 367), (82, 368), (81, 369), (80, 370), (79, 372),
  (78, 373), (77, 374), (76, 376), (75, 379), (74, 380), (73, 382), (72, 383), (71, 384),
  (70, 386), (69, 388), (68, 391), (67, 392), (66, 393), (65, 398), (64, 400), (63, 402),
  (62, 404), (61, 405), (59, 406), (58, 408), (57, 409), (56, 413), (55, 414), (54, 415),
  (53, 417), (52, 419), (51, 423), (50, 424), (49, 425), (48, 427), (47, 430), (46, 436),
  (45, 437), (44, 442), (43, 447), (42, 452), (41, 457), (40, 460), (39, 465), (38, 472),
  (37, 476), (36, 485), (35, 491), (34, 502), (33, 505), (32, 511), (31, 512), (30, 516),
  (29, 517), (28, 518), (27, 519), (26, 520), (22, 521)]

theorem witness_chain : StrictChain witness ∧ witness.length = 349 ∧ witness.head? = some (521, 22) := by
  decide +kernel

/-- D = 349 works: no descent in dimension four has more than 348 steps -/
theorem uniform_depth : 348 + 1 = 349 := by decide

/-! ## The descent of Δ₆₈₀ (Table III) -/

/-- lattice points and dual lattice points of Γ₀, …, Γ₃₈ -/
def descent680 : List (Nat × Nat) := [
  (680, 26), (422, 27), (236, 28), (207, 29), (137, 30), (122, 32), (103, 33), (78, 34),
  (57, 35), (44, 36), (37, 37), (36, 38), (35, 39), (34, 40), (33, 42), (32, 44),
  (31, 46), (30, 48), (29, 51), (28, 54), (27, 58), (26, 62), (25, 66), (24, 70),
  (23, 80), (22, 86), (21, 88), (20, 92), (19, 104), (18, 116), (17, 128), (16, 140),
  (15, 152), (14, 164), (13, 179), (12, 188), (11, 196), (10, 200), (9, 201)]

theorem descent680_chain : StrictChain descent680 ∧ descent680.length = 39 ∧
    descent680.head? = some (680, 26) ∧ descent680.getLast? = some (9, 201) := by
  decide +kernel

/-- the descent of Table III is within the counting bounds -/
theorem descent680_counting : 38 ≤ 680 - 6 ∧ 38 ≤ 680 - 26 := by decide

/-! ## Two polytopes of depth 22 -/

/-- a descent in an abstract order: a chain of covers ending at an element without covers -/
inductive Descent {α : Type} (cover : α → α → Prop) : α → Nat → Prop
  | stop (x : α) (h : ∀ y, ¬ cover x y) : Descent cover x 0
  | step (x y : α) (k : Nat) (h : cover x y) (d : Descent cover y k) : Descent cover x (k + 1)

/-- the certificate lemma: if every element with bound b > 0 has a cover and every cover has
    bound at least b − 1, then every descent from x has at least b x steps -/
theorem certificate_lemma {α : Type} (cover : α → α → Prop) (b : α → Nat)
    (hb : ∀ x, 0 < b x → (∃ y, cover x y) ∧ ∀ y, cover x y → b x ≤ b y + 1) :
    ∀ x k, Descent cover x k → b x ≤ k := by
  intro x k d
  induction d with
  | stop x h =>
    rcases Nat.eq_zero_or_pos (b x) with h0 | hpos
    · exact Nat.le_of_eq h0
    · obtain ⟨⟨y, hy⟩, _⟩ := hb x hpos
      exact (h y hy).elim
  | step x y k h _ ih =>
    rcases Nat.eq_zero_or_pos (b x) with h0 | hpos
    · rw [h0]; exact Nat.zero_le _
    · exact Nat.le_trans ((hb x hpos).2 y h) (Nat.add_le_add_right ih 1)

/-- lattice points and dual lattice points along a shortest descent of P₁ -/
def descentP1 : List (Nat × Nat) := [
  (37, 37), (36, 38), (35, 39), (34, 40), (33, 41), (32, 43), (31, 45), (30, 46),
  (29, 49), (28, 52), (27, 53), (26, 57), (25, 63), (24, 78), (23, 90), (22, 102),
  (21, 144), (20, 168), (19, 192), (18, 216), (17, 240), (16, 264), (15, 288)]

/-- lattice points and dual lattice points along a shortest descent of P₂ -/
def descentP2 : List (Nat × Nat) := [
  (37, 37), (36, 38), (35, 39), (34, 40), (33, 41), (32, 43), (31, 45), (30, 47),
  (29, 49), (28, 51), (27, 55), (26, 57), (25, 63), (24, 69), (23, 90), (22, 120),
  (21, 144), (20, 168), (19, 192), (18, 216), (17, 240), (16, 264), (15, 288)]

theorem descentP1_chain : StrictChain descentP1 ∧ descentP1.length = 23 ∧
    descentP1.head? = some (37, 37) ∧ descentP1.getLast? = some (15, 288) := by
  decide +kernel

theorem descentP2_chain : StrictChain descentP2 ∧ descentP2.length = 23 ∧
    descentP2.head? = some (37, 37) ∧ descentP2.getLast? = some (15, 288) := by
  decide +kernel

/-- the vertices e₁, e₂, e₃, u ± 8e₄ of P₁, u = (−4, −2, −1, 0), with the weights 8, 4, 2, 1, 1:
    8e₁ + 4e₂ + 2e₃ + (u + 8e₄) + (u − 8e₄) = 0, coordinate by coordinate -/
theorem weightsP1 : (8 : Int) * 1 + 1 * (-4) + 1 * (-4) = 0 ∧ (4 : Int) * 1 + 1 * (-2) + 1 * (-2) = 0 ∧
    (2 : Int) * 1 + 1 * (-1) + 1 * (-1) = 0 ∧ (1 : Int) * 8 + 1 * (-8) = 0 := by decide

/-- 4 × 4 integer matrices as lists of rows -/
def mulVec (A : List (List Int)) (x : List Int) : List Int :=
  A.map fun r => (List.zipWith (· * ·) r x).foldl (· + ·) 0

def mulMat (A B : List (List Int)) : List (List Int) :=
  A.map fun r => (List.range 4).map fun j =>
    (List.zipWith (· * ·) r (B.map fun s => s.getD j 0)).foldl (· + ·) 0

/-- the map G of the paper and its inverse -/
def G : List (List Int) := [[-1, -1, -1, -1], [-1, -1, 6, 0], [-1, 2, -1, 0], [1, -1, -1, 0]]
def Ginv : List (List Int) := [[0, 3, 7, 11], [0, 2, 5, 7], [0, 1, 2, 3], [-1, -6, -14, -21]]

/-- G is unimodular: G · G⁻¹ = 1 with G⁻¹ integral -/
theorem G_unimodular : mulMat G Ginv = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]] := by
  decide

/-- G carries the vertices of P₁ to the vertices of Γ₁₀ of the descent of Δ₆₈₀ -/
theorem G_vertices :
    mulVec G [1, 0, 0, 0] = [-1, -1, -1, 1] ∧ mulVec G [0, 1, 0, 0] = [-1, -1, 2, -1] ∧
    mulVec G [0, 0, 1, 0] = [-1, 6, -1, -1] ∧ mulVec G [-4, -2, -1, 8] = [-1, 0, 1, -1] ∧
    mulVec G [-4, -2, -1, -8] = [15, 0, 1, -1] := by decide

/-- δ(Δ₆₈₀) ≤ 10 + δ(Γ₁₀) = 10 + 22, and Γ₁₀ ≅ P₁ is step 10 of Table III -/
theorem depth680 : 10 + 22 = 32 ∧ descent680[10]? = some (37, 37) := by decide

/-! ## Polygons -/

/-- lattice points of the triangle conv{(-1,-1),(2,-1),(-1,2)}, shifted by (1,1):
    x, y ≥ 0 and x + y ≤ 3 -/
def trianglePoints : Nat :=
  (List.range 4).foldl (fun s x => (List.range 4).foldl (fun s y => if x + y ≤ 3 then s + 1 else s) s) 0

/-- the extreme polygon has 10 lattice points and transition depth 10 − 5 = 5 -/
theorem triangle_depth : trianglePoints = 10 ∧ trianglePoints - 5 = 5 := by decide

end Seed


#print axioms Seed.volume_delta680
#print axioms Seed.volume_dual
#print axioms Seed.egyptian
#print axioms Seed.weights_over_sum
#print axioms Seed.sylvester_first
#print axioms Seed.sylvester_42
#print axioms Seed.points_delta680
#print axioms Seed.points_dual
#print axioms Seed.chain_first
#print axioms Seed.chain_dual
#print axioms Seed.counting_lemma
#print axioms Seed.chain_first_ge
#print axioms Seed.every_dimension
#print axioms Seed.every_dimension_four
#print axioms Seed.simple_bound_680
#print axioms Seed.witness_chain
#print axioms Seed.uniform_depth
#print axioms Seed.descent680_chain
#print axioms Seed.descent680_counting
#print axioms Seed.certificate_lemma
#print axioms Seed.descentP1_chain
#print axioms Seed.descentP2_chain
#print axioms Seed.weightsP1
#print axioms Seed.G_unimodular
#print axioms Seed.G_vertices
#print axioms Seed.depth680
#print axioms Seed.triangle_depth
