import Mathlib.Analysis.Convex.Join
import Mathlib.Analysis.Convex.Topology
import Mathlib.Analysis.Convex.Combination
import Mathlib.Tactic

/-! Geometric free sums in real vector spaces. Theorems in this file use
actual convex hulls and actual topological interiors, rather than an
uninterpreted relation bearing the name "reflexive". -/

namespace ReflexiveDescent.Geometry

open Set
open scoped Pointwise

variable {E F D G : Type*}
variable [AddCommGroup E] [Module ℝ E] [AddCommGroup F] [Module ℝ F]
variable [AddCommGroup D] [Module ℝ D] [AddCommGroup G] [Module ℝ G]

def leftIn : E →ₗ[ℝ] E × F where
  toFun x := (x,0)
  map_add' _ _ := by simp
  map_smul' _ _ := by simp

def rightIn : F →ₗ[ℝ] E × F where
  toFun y := (0,y)
  map_add' _ _ := by simp
  map_smul' _ _ := by simp

def freeSum (P : Set E) (Q : Set F) : Set (E × F) :=
  convexHull ℝ (leftIn '' P ∪ rightIn '' Q)

def leftSection (C : Set (E × F)) : Set E := {x | (x,0) ∈ C}
def rightSection (C : Set (E × F)) : Set F := {y | (0,y) ∈ C}

theorem left_mem_freeSum {P : Set E} {Q : Set F} {x : E} (hx : x ∈ P) :
    (x,0) ∈ freeSum P Q :=
  subset_convexHull ℝ _ (Or.inl ⟨x,hx,rfl⟩)

theorem right_mem_freeSum {P : Set E} {Q : Set F} {y : F} (hy : y ∈ Q) :
    (0,y) ∈ freeSum P Q :=
  subset_convexHull ℝ _ (Or.inr ⟨y,hy,rfl⟩)

theorem freeSum_subset_product {P : Set E} {Q : Set F}
    (hP : Convex ℝ P) (hQ : Convex ℝ Q) (p0 : 0 ∈ P) (q0 : 0 ∈ Q) :
    freeSum P Q ⊆ P ×ˢ Q := by
  apply convexHull_min ?_ (hP.prod hQ)
  rintro z (⟨x,hx,rfl⟩ | ⟨y,hy,rfl⟩)
  · exact ⟨hx,q0⟩
  · exact ⟨p0,hy⟩

theorem sections_freeSum {P : Set E} {Q : Set F}
    (hP : Convex ℝ P) (hQ : Convex ℝ Q) (p0 : 0 ∈ P) (q0 : 0 ∈ Q) :
    leftSection (freeSum P Q) = P ∧ rightSection (freeSum P Q) = Q := by
  constructor
  · ext x; exact ⟨fun h => (freeSum_subset_product hP hQ p0 q0 h).1,left_mem_freeSum⟩
  · ext y; exact ⟨fun h => (freeSum_subset_product hP hQ p0 q0 h).2,right_mem_freeSum⟩

/-- An axis-supported generating set forces a unique coordinate free-sum
factorization; no assumption of that factorization is made. -/
theorem hull_axis_factorization (S : Set (E × F))
    (hS : ∀ z ∈ S, z.1 = 0 ∨ z.2 = 0) :
    convexHull ℝ S = freeSum (leftSection (convexHull ℝ S))
      (rightSection (convexHull ℝ S)) := by
  apply Subset.antisymm
  · apply convexHull_min ?_ (convex_convexHull ℝ _)
    rintro ⟨x,y⟩ hz
    rcases hS (x,y) hz with h | h
    · change x = 0 at h
      subst x
      exact right_mem_freeSum (P := leftSection (convexHull ℝ S))
        (Q := rightSection (convexHull ℝ S)) (subset_convexHull ℝ S hz)
    · change y = 0 at h
      subst y
      exact left_mem_freeSum (P := leftSection (convexHull ℝ S))
        (Q := rightSection (convexHull ℝ S)) (subset_convexHull ℝ S hz)
  · apply convexHull_min ?_ (convex_convexHull ℝ S)
    rintro z (⟨x,hx,rfl⟩ | ⟨y,hy,rfl⟩)
    · exact hx
    · exact hy

def polar (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ) (P : Set E) : Set D :=
  {u | ∀ x ∈ P, B u x ≤ 1}

def productPairing (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ)
    (C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ) : (D × G) →ₗ[ℝ] (E × F) →ₗ[ℝ] ℝ where
  toFun u := (B u.1).comp (LinearMap.fst ℝ E F) + (C u.2).comp (LinearMap.snd ℝ E F)
  map_add' u v := by
    apply LinearMap.ext; intro z
    simp [add_assoc,add_left_comm]
  map_smul' a u := by
    apply LinearMap.ext; intro z
    simp [smul_add]

theorem polar_freeSum (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ)
    (C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ) (P : Set E) (Q : Set F) :
    polar (productPairing B C) (freeSum P Q) = polar B P ×ˢ polar C Q := by
  ext u
  constructor
  · intro h
    constructor
    · intro x hx
      have hh := h (x,0) (left_mem_freeSum hx)
      simpa [productPairing] using hh
    · intro y hy
      have hh := h (0,y) (right_mem_freeSum hy)
      simpa [productPairing] using hh
  · rintro ⟨hP,hQ⟩ z hz
    have hh : freeSum P Q ⊆ {z | productPairing B C u z ≤ 1} := by
      apply convexHull_min ?_ ((convex_Iic (𝕜 := ℝ) (1:ℝ)).linear_preimage (productPairing B C u))
      rintro w (⟨x,hx,rfl⟩ | ⟨y,hy,rfl⟩)
      · simpa [productPairing,leftIn] using hP x hx
      · simpa [productPairing,rightIn] using hQ y hy
    exact hh hz

section Topology

variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [TopologicalSpace F] [IsTopologicalAddGroup F] [ContinuousSMul ℝ F]

theorem lattice_points_on_axes (L : AddSubgroup E) (M : AddSubgroup F)
    {P : Set E} {Q : Set F} (hP : Convex ℝ P) (hQ : Convex ℝ Q)
    (p0 : 0 ∈ interior P) (q0 : 0 ∈ Q)
    (uniqueP : ∀ x ∈ L, x ∈ interior P → x = 0)
    {z : E × F} (zL : z.1 ∈ L ∧ z.2 ∈ M) (hz : z ∈ freeSum P Q) :
    z.1 = 0 ∨ z.2 = 0 := by
  have pp0 : 0 ∈ P := interior_subset p0
  have hPI : Convex ℝ (leftIn '' P : Set (E × F)) := hP.linear_image leftIn
  have hQI : Convex ℝ (rightIn '' Q : Set (E × F)) := hQ.linear_image rightIn
  rw [freeSum,hPI.convexHull_union hQI ⟨(0,0),⟨0,pp0,rfl⟩⟩ ⟨(0,0),⟨0,q0,rfl⟩⟩] at hz
  rcases mem_convexJoin.1 hz with ⟨_,⟨x,hx,rfl⟩,_,⟨y,hy,rfl⟩,a,b,ha,hb,hab,rfl⟩
  by_cases hlt : a < 1
  · left
    have hi : a • x ∈ interior P := by
      have hh := hP.combo_interior_self_mem_interior p0 hx (sub_pos.mpr hlt) ha (sub_add_cancel 1 a)
      simpa using hh
    have hl : a • x ∈ L := by simpa [leftIn,rightIn] using zL.1
    simpa [leftIn,rightIn] using uniqueP (a • x) hl hi
  · right
    have hb0 : b=0 := by linarith
    simp [leftIn,rightIn,hb0]

end Topology

/-- A finite convex hull of points in the specified additive lattice. -/
def LatticeHull (L : AddSubgroup E) (P : Set E) : Prop :=
  ∃ S : Set E, S.Finite ∧ S ⊆ L ∧ P = convexHull ℝ S

theorem LatticeHull.convex {L : AddSubgroup E} {P : Set E}
    (h : LatticeHull L P) : Convex ℝ P := by
  obtain ⟨S,_,_,rfl⟩ := h
  exact convex_convexHull ℝ S

theorem LatticeHull.linear_image {L : AddSubgroup E} {M : AddSubgroup F}
    {P : Set E} (h : LatticeHull L P) (f : E →ₗ[ℝ] F)
    (hf : ∀ x ∈ L, f x ∈ M) : LatticeHull M (f '' P) := by
  obtain ⟨S,hfin,hL,rfl⟩ := h
  refine ⟨f '' S,hfin.image f,?_,f.image_convexHull S⟩
  rintro _ ⟨x,hx,rfl⟩
  exact hf x (hL hx)

theorem latticeHull_freeSum {L : AddSubgroup E} {M : AddSubgroup F}
    {P : Set E} {Q : Set F} (hP : LatticeHull L P) (hQ : LatticeHull M Q) :
    LatticeHull (L.prod M) (freeSum P Q) := by
  obtain ⟨S,hS,hL,rfl⟩ := hP
  obtain ⟨T,hT,hM,rfl⟩ := hQ
  refine ⟨leftIn '' S ∪ rightIn '' T,(hS.image leftIn).union (hT.image rightIn),?_,?_⟩
  · rintro _ (⟨x,hx,rfl⟩ | ⟨y,hy,rfl⟩)
    · exact ⟨hL hx,M.zero_mem⟩
    · exact ⟨L.zero_mem,hM hy⟩
  · simp only [freeSum,leftIn.image_convexHull,rightIn.image_convexHull,
      convexHull_convexHull_union_left,convexHull_convexHull_union_right]

theorem latticeHull_product {L : AddSubgroup E} {M : AddSubgroup F}
    {P : Set E} {Q : Set F} (hP : LatticeHull L P) (hQ : LatticeHull M Q) :
    LatticeHull (L.prod M) (P ×ˢ Q) := by
  obtain ⟨S,hS,hL,rfl⟩ := hP
  obtain ⟨T,hT,hM,rfl⟩ := hQ
  exact ⟨S ×ˢ T,hS.prod hT,fun _ h => ⟨hL h.1,hM h.2⟩,(convexHull_prod S T).symm⟩

theorem latticeHull_product_factors {L : AddSubgroup E} {M : AddSubgroup F}
    {P : Set E} {Q : Set F} (h : LatticeHull (L.prod M) (P ×ˢ Q))
    (hp : P.Nonempty) (hq : Q.Nonempty) : LatticeHull L P ∧ LatticeHull M Q := by
  have hfst : Prod.fst '' (P ×ˢ Q) = P := by
    ext x
    constructor
    · rintro ⟨z,hz,rfl⟩; exact hz.1
    · intro hx; obtain ⟨y,hy⟩ := hq; exact ⟨(x,y),⟨hx,hy⟩,rfl⟩
  have hsnd : Prod.snd '' (P ×ˢ Q) = Q := by
    ext y
    constructor
    · rintro ⟨z,hz,rfl⟩; exact hz.2
    · intro hy; obtain ⟨x,hx⟩ := hp; exact ⟨(x,y),⟨hx,hy⟩,rfl⟩
  constructor
  · simpa only [LinearMap.coe_fst,hfst] using
      h.linear_image (LinearMap.fst ℝ E F) (fun _ hx => hx.1)
  · simpa only [LinearMap.coe_snd,hsnd] using
      h.linear_image (LinearMap.snd ℝ E F) (fun _ hx => hx.2)

theorem axis_hull_sections (S : Set (E × F))
    (hS : ∀ z ∈ S, z.1=0 ∨ z.2=0) (h0 : (0 : E × F) ∈ convexHull ℝ S) :
    leftSection (convexHull ℝ S) = Prod.fst '' convexHull ℝ S ∧
    rightSection (convexHull ℝ S) = Prod.snd '' convexHull ℝ S := by
  change ((0:E),(0:F)) ∈ convexHull ℝ S at h0
  have hl : convexHull ℝ S ⊆ (leftIn.comp (LinearMap.fst ℝ E F)) ⁻¹' convexHull ℝ S := by
    apply convexHull_min ?_ ((convex_convexHull ℝ S).linear_preimage _)
    rintro ⟨x,y⟩ hz
    rcases hS (x,y) hz with hx | hy
    · change x=0 at hx
      simpa [leftIn,hx] using h0
    · change y=0 at hy
      simpa [leftIn,hy] using subset_convexHull ℝ S hz
  have hr : convexHull ℝ S ⊆ (rightIn.comp (LinearMap.snd ℝ E F)) ⁻¹' convexHull ℝ S := by
    apply convexHull_min ?_ ((convex_convexHull ℝ S).linear_preimage _)
    rintro ⟨x,y⟩ hz
    rcases hS (x,y) hz with hx | hy
    · change x=0 at hx
      simpa [rightIn,hx] using subset_convexHull ℝ S hz
    · change y=0 at hy
      simpa [rightIn,hy] using h0
  constructor
  · ext x
    constructor
    · intro hx; exact ⟨(x,0),hx,rfl⟩
    · rintro ⟨⟨x,y⟩,hx,rfl⟩; exact hl hx
  · ext y
    constructor
    · intro hy; exact ⟨(0,y),hy,rfl⟩
    · rintro ⟨⟨x,y⟩,hy,rfl⟩; exact hr hy

section TopologicalClosure

variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [TopologicalSpace F] [IsTopologicalAddGroup F] [ContinuousSMul ℝ F]

theorem origin_interior_freeSum {P : Set E} {Q : Set F}
    (p0 : 0 ∈ interior P) (q0 : 0 ∈ interior Q) :
    (0 : E × F) ∈ interior (freeSum P Q) := by
  let U : Set (E × F) := (1/2:ℝ) • (interior P ×ˢ interior Q)
  have hU : IsOpen U := (isOpen_interior.prod isOpen_interior).smul₀ (by norm_num)
  have hu0 : (0 : E × F) ∈ U := by
    exact ⟨0,⟨p0,q0⟩,by simp⟩
  have hs : U ⊆ freeSum P Q := by
    rintro _ ⟨⟨x,y⟩,⟨hx,hy⟩,rfl⟩
    have hh := (convex_convexHull ℝ _)
      (left_mem_freeSum (Q := Q) (interior_subset hx))
      (right_mem_freeSum (P := P) (interior_subset hy))
      (by norm_num : (0:ℝ) ≤ 1/2) (by norm_num : (0:ℝ) ≤ 1/2)
      (by norm_num : (1/2:ℝ)+1/2=1)
    simpa only [freeSum,Prod.smul_mk,Prod.mk_add_mk,smul_zero,add_zero,zero_add] using hh
  exact (hU.subset_interior_iff.2 hs) hu0

theorem section_origin_interior {C : Set (E × F)} (h0 : 0 ∈ interior C) :
    0 ∈ interior (leftSection C) ∧ 0 ∈ interior (rightSection C) := by
  constructor
  · exact preimage_interior_subset_interior_preimage
      (show Continuous (fun x : E => (x,(0:F))) from continuous_id.prodMk continuous_const) h0
  · exact preimage_interior_subset_interior_preimage
      (show Continuous (fun y : F => ((0:E),y)) from continuous_const.prodMk continuous_id) h0

end TopologicalClosure

section Reflexive

variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [TopologicalSpace F] [IsTopologicalAddGroup F] [ContinuousSMul ℝ F]

/-- The standard IP-reflexive convention: a lattice polytope with the
origin as its unique interior lattice point, and a lattice polar.
The unique-interior-point condition is explicit, not an inferred axiom. -/
structure Reflexive (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ)
    (L : AddSubgroup E) (LD : AddSubgroup D) (P : Set E) : Prop where
  lattice : LatticeHull L P
  origin : 0 ∈ interior P
  uniqueInterior : ∀ x ∈ L, x ∈ interior P → x=0
  dualLattice : LatticeHull LD (polar B P)

theorem reflexive_freeSum {B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ}
    {C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ}
    {L : AddSubgroup E} {M : AddSubgroup F} {LD : AddSubgroup D} {MD : AddSubgroup G}
    {P : Set E} {Q : Set F} (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q) :
    Reflexive (productPairing B C) (L.prod M) (LD.prod MD) (freeSum P Q) := by
  refine ⟨latticeHull_freeSum hP.lattice hQ.lattice,
    origin_interior_freeSum hP.origin hQ.origin,?_,?_⟩
  · intro z hz hi
    have hh := interior_mono (freeSum_subset_product hP.lattice.convex hQ.lattice.convex
      (interior_subset hP.origin) (interior_subset hQ.origin)) hi
    rw [interior_prod_eq] at hh
    exact Prod.ext (hP.uniqueInterior z.1 hz.1 hh.1) (hQ.uniqueInterior z.2 hz.2 hh.2)
  · rw [polar_freeSum]
    exact latticeHull_product hP.dualLattice hQ.dualLattice

theorem reflexive_subpolytope_factors {B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ}
    {C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ}
    {L : AddSubgroup E} {M : AddSubgroup F} {LD : AddSubgroup D} {MD : AddSubgroup G}
    {P : Set E} {Q : Set F} (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q)
    {K : Set (E × F)}
    (hK : Reflexive (productPairing B C) (L.prod M) (LD.prod MD) K)
    (hsub : K ⊆ freeSum P Q) :
    K = freeSum (leftSection K) (rightSection K) ∧
    Reflexive B L LD (leftSection K) ∧ Reflexive C M MD (rightSection K) ∧
    leftSection K ⊆ P ∧ rightSection K ⊆ Q := by
  obtain ⟨S,hfin,hSL,hHull⟩ := hK.lattice
  have haxes : ∀ z ∈ S, z.1=0 ∨ z.2=0 := by
    intro z hz
    apply lattice_points_on_axes L M hP.lattice.convex hQ.lattice.convex hP.origin
      (interior_subset hQ.origin) hP.uniqueInterior (hSL hz)
    exact hsub (hHull ▸ subset_convexHull ℝ S hz)
  have hfac : K = freeSum (leftSection K) (rightSection K) := by
    simpa only [← hHull] using hull_axis_factorization S haxes
  have hsec : leftSection K = Prod.fst '' K ∧ rightSection K = Prod.snd '' K := by
    simpa only [← hHull] using axis_hull_sections S haxes (hHull ▸ interior_subset hK.origin)
  have hlh : LatticeHull L (leftSection K) := by
    have hh := hK.lattice.linear_image (LinearMap.fst ℝ E F) (fun _ hz => hz.1)
    simpa only [LinearMap.coe_fst,← hsec.1] using hh
  have hrh : LatticeHull M (rightSection K) := by
    have hh := hK.lattice.linear_image (LinearMap.snd ℝ E F) (fun _ hz => hz.2)
    simpa only [LinearMap.coe_snd,← hsec.2] using hh
  have hlsub : leftSection K ⊆ P := by
    intro x hx
    exact (freeSum_subset_product hP.lattice.convex hQ.lattice.convex
      (interior_subset hP.origin) (interior_subset hQ.origin) (hsub hx)).1
  have hrsub : rightSection K ⊆ Q := by
    intro y hy
    exact (freeSum_subset_product hP.lattice.convex hQ.lattice.convex
      (interior_subset hP.origin) (interior_subset hQ.origin) (hsub hy)).2
  have hdual : LatticeHull (LD.prod MD)
      (polar B (leftSection K) ×ˢ polar C (rightSection K)) := by
    rw [← polar_freeSum,← hfac]
    exact hK.dualLattice
  have hp0 : (0:D) ∈ polar B (leftSection K) := by intro x hx; simp
  have hq0 : (0:G) ∈ polar C (rightSection K) := by intro y hy; simp
  have hduals := latticeHull_product_factors hdual ⟨0,hp0⟩ ⟨0,hq0⟩
  have h0s := section_origin_interior hK.origin
  refine ⟨hfac,⟨hlh,h0s.1,?_,hduals.1⟩,⟨hrh,h0s.2,?_,hduals.2⟩,hlsub,hrsub⟩
  · intro x hx hi; exact hP.uniqueInterior x hx (interior_mono hlsub hi)
  · intro y hy hi; exact hQ.uniqueInterior y hy (interior_mono hrsub hi)

abbrev Subpolytopes (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ)
    (L : AddSubgroup E) (LD : AddSubgroup D) (P : Set E) :=
  {K : Set E // K ⊆ P ∧ Reflexive B L LD K}

theorem freeSum_mono {P P' : Set E} {Q Q' : Set F}
    (hP : P ⊆ P') (hQ : Q ⊆ Q') : freeSum P Q ⊆ freeSum P' Q' :=
  convexHull_mono (union_subset_union (image_mono hP) (image_mono hQ))

noncomputable def freeSumOrderIso {B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ}
    {C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ}
    {L : AddSubgroup E} {M : AddSubgroup F} {LD : AddSubgroup D} {MD : AddSubgroup G}
    {P : Set E} {Q : Set F} (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q) :
    (Subpolytopes B L LD P × Subpolytopes C M MD Q) ≃o
      Subpolytopes (productPairing B C) (L.prod M) (LD.prod MD) (freeSum P Q) where
  toFun p := ⟨freeSum p.1.1 p.2.1,freeSum_mono p.1.2.1 p.2.2.1,
    reflexive_freeSum p.1.2.2 p.2.2.2⟩
  invFun k := by
    have hf := reflexive_subpolytope_factors hP hQ k.2.2 k.2.1
    exact (⟨leftSection k.1,hf.2.2.2.1,hf.2.1⟩,
      ⟨rightSection k.1,hf.2.2.2.2,hf.2.2.1⟩)
  left_inv p := by
    have hs := sections_freeSum p.1.2.2.lattice.convex p.2.2.2.lattice.convex
      (interior_subset p.1.2.2.origin) (interior_subset p.2.2.2.origin)
    exact Prod.ext (Subtype.ext hs.1) (Subtype.ext hs.2)
  right_inv k := by
    have hf := reflexive_subpolytope_factors hP hQ k.2.2 k.2.1
    exact Subtype.ext hf.1.symm
  map_rel_iff' := by
    intro p q
    change (freeSum p.1.1 p.2.1 ⊆ freeSum q.1.1 q.2.1) ↔
      (p.1.1 ⊆ q.1.1 ∧ p.2.1 ⊆ q.2.1)
    constructor
    · intro h
      have hp := freeSum_subset_product q.1.2.2.lattice.convex q.2.2.2.lattice.convex
        (interior_subset q.1.2.2.origin) (interior_subset q.2.2.2.origin)
      exact ⟨fun _ hx => (hp (h (left_mem_freeSum hx))).1,
        fun _ hy => (hp (h (right_mem_freeSum hy))).2⟩
    · rintro ⟨hp,hq⟩; exact freeSum_mono hp hq

end Reflexive

end ReflexiveDescent.Geometry

#print axioms ReflexiveDescent.Geometry.hull_axis_factorization
#print axioms ReflexiveDescent.Geometry.polar_freeSum
#print axioms ReflexiveDescent.Geometry.lattice_points_on_axes
#print axioms ReflexiveDescent.Geometry.reflexive_freeSum
#print axioms ReflexiveDescent.Geometry.reflexive_subpolytope_factors
#print axioms ReflexiveDescent.Geometry.freeSumOrderIso
