import IntervalDescents

namespace ReflexiveDescent

theorem exists_descent {α : Type*} (c : α → α → Prop) (rank : α → Nat)
    (strict : ∀ x y, c x y → rank y < rank x) (x : α) : ∃ k, Descent c x k := by
  classical
  induction h : rank x using Nat.strong_induction_on generalizing x with
  | h n ih =>
    by_cases ht : ∀ y, ¬ c x y
    · exact ⟨0,Descent.stop x ht⟩
    · push Not at ht
      obtain ⟨y,hy⟩ := ht
      obtain ⟨k,hk⟩ := ih (rank y) (by simpa only [h] using strict x y hy) y rfl
      exact ⟨k+1,Descent.step x y k hy hk⟩

theorem descent_rank_bound {α : Type*} {c : α → α → Prop} (rank : α → Nat)
    (strict : ∀ x y, c x y → rank y < rank x) {x : α} {k : Nat}
    (h : Descent c x k) : k ≤ rank x := by
  induction h with
  | stop x ht => exact Nat.zero_le _
  | step x y k hc _ ih => have hh := strict x y hc; omega

theorem shortest_exists {α : Type*} (c : α → α → Prop) (rank : α → Nat)
    (strict : ∀ x y, c x y → rank y < rank x) (x : α) : ∃ k, Shortest c x k := by
  classical
  have h := exists_descent c rank strict x
  exact ⟨Nat.find h,Nat.find_spec h,fun j hj => Nat.find_min' h hj⟩

theorem longest_exists {α : Type*} (c : α → α → Prop) (rank : α → Nat)
    (strict : ∀ x y, c x y → rank y < rank x) (x : α) : ∃ k, Longest c x k := by
  classical
  let S := (Finset.range (rank x+1)).filter (fun k => Descent c x k)
  have hs : S.Nonempty := by
    obtain ⟨k,hk⟩ := exists_descent c rank strict x
    exact ⟨k,Finset.mem_filter.2 ⟨Finset.mem_range.2 (by have hh := descent_rank_bound rank strict hk; omega),hk⟩⟩
  refine ⟨S.max' hs,(Finset.mem_filter.1 (Finset.max'_mem S hs)).2,?_⟩
  intro j hj
  apply Finset.le_max'
  exact Finset.mem_filter.2 ⟨Finset.mem_range.2 (by have hh := descent_rank_bound rank strict hj; omega),hj⟩

namespace Geometry

open Set

variable {E D : Type*} [AddCommGroup E] [Module ℝ E] [AddCommGroup D] [Module ℝ D]
variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable {B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ} {L : AddSubgroup E} {LD : AddSubgroup D} {P : Set E}

noncomputable def pointSupport (S : Finset E) (Q : Set E) : Finset S := by
  classical
  exact Finset.univ.filter (fun x => x.val ∈ Q)

theorem support_hull_eq (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) (q : Subpolytopes B L LD P) :
    q.val = convexHull ℝ (Subtype.val '' (pointSupport S q.val : Set S)) := by
  classical
  obtain ⟨T,hT,hL,hHull⟩ := q.2.2.lattice
  apply Subset.antisymm
  · rw [hHull]
    apply convexHull_mono
    intro x hx
    have hqx : x ∈ q.val := by rw [hHull]; exact subset_convexHull ℝ T hx
    have hxs : x ∈ S := hS x (q.2.1 hqx) (hL hx)
    refine ⟨⟨x,hxs⟩,?_,rfl⟩
    simpa only [pointSupport,Finset.mem_coe,Finset.mem_filter,Finset.mem_univ,true_and] using subset_convexHull ℝ T hx
  · apply convexHull_min ?_ q.2.2.lattice.convex
    rintro x ⟨y,hy,rfl⟩
    simpa only [pointSupport,Finset.mem_coe,Finset.mem_filter,Finset.mem_univ,true_and] using hy

theorem pointSupport_injective (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) :
    Function.Injective (fun q : Subpolytopes B L LD P => pointSupport S q.val) := by
  intro q r hqr
  change pointSupport S q.val = pointSupport S r.val at hqr
  apply Subtype.ext
  rw [support_hull_eq S hS q,support_hull_eq S hS r,hqr]

/-- A finite ambient lattice-point list implies finiteness of the whole
geometric reflexive-subpolytope order, not just of a supplied graph. -/
theorem finite_subpolytopes (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) : Finite (Subpolytopes B L LD P) :=
  Finite.of_injective _ (pointSupport_injective S hS)

theorem support_strictly_decreases (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S)
    (q r : Subpolytopes B L LD P) (hqr : q<r) :
    (pointSupport S q.val).card < (pointSupport S r.val).card := by
  classical
  apply Finset.card_lt_card
  apply Finset.ssubset_iff_subset_ne.2
  constructor
  · intro x hx
    simp only [pointSupport,Finset.mem_filter,Finset.mem_univ,true_and] at hx ⊢
    exact hqr.le hx
  · intro he
    exact hqr.ne (pointSupport_injective S hS he)

theorem terminal_reflexive_iff_rminimal (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) (q : Subpolytopes B L LD P) :
    (∀ r, ¬ DownCover q r) ↔
      ∀ T : Set E, Reflexive B L LD T → T ⊆ q.val → T=q.val := by
  letI : Finite (Subpolytopes B L LD P) := finite_subpolytopes S hS
  rw [terminal_iff_minimal]
  constructor
  · intro hm T hT hsub
    let r : Subpolytopes B L LD P := ⟨T,hsub.trans q.2.1,hT⟩
    exact congrArg Subtype.val (hm r hsub)
  · intro hm r hr
    exact Subtype.ext (hm r.val r.2.2 hr)

theorem reflexive_descent_exists (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) (q : Subpolytopes B L LD P) :
    ∃ k, Descent DownCover q k :=
  exists_descent DownCover (fun q => (pointSupport S q.val).card)
    (fun x y h => support_strictly_decreases S hS y x h.lt) q

theorem reflexive_depth_extrema_exist (S : Finset E)
    (hS : ∀ x ∈ P, x ∈ L → x ∈ S) (q : Subpolytopes B L LD P) :
    (∃ k, Shortest DownCover q k) ∧ (∃ k, Longest DownCover q k) := by
  have hs : ∀ x y : Subpolytopes B L LD P, DownCover x y →
      (pointSupport S y.val).card < (pointSupport S x.val).card :=
    fun x y h => support_strictly_decreases S hS y x h.lt
  exact ⟨shortest_exists DownCover (fun q => (pointSupport S q.val).card) hs q,
    longest_exists DownCover (fun q => (pointSupport S q.val).card) hs q⟩

end Geometry
end ReflexiveDescent

#print axioms ReflexiveDescent.Geometry.finite_subpolytopes
#print axioms ReflexiveDescent.Geometry.reflexive_descent_exists
#print axioms ReflexiveDescent.Geometry.reflexive_depth_extrema_exist
#print axioms ReflexiveDescent.Geometry.terminal_reflexive_iff_rminimal
