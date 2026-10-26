import DescentProducts
import FreeSumGeometry

namespace ReflexiveDescent

universe u v

abbrev DownCover {α : Type u} [PartialOrder α] (x y : α) : Prop := y ⋖ x

theorem descent_orderIso_iff {α : Type u} {β : Type v}
    [PartialOrder α] [PartialOrder β] (e : α ≃o β) (x : α) (k : Nat) :
    Descent DownCover (e x) k ↔ Descent DownCover x k := by
  constructor
  · intro h
    have hh : Descent DownCover (e.symm (e x)) k := transport_descent (c := DownCover) (d := DownCover) e.symm.toEquiv
      (fun a b => (apply_covBy_apply_iff (a := b) (b := a) e.symm).symm) h
    simpa using hh
  · exact transport_descent e.toEquiv
      (fun a b => (apply_covBy_apply_iff (a := b) (b := a) e).symm)

theorem descent_product_order_iff {α : Type u} {β : Type v}
    [PartialOrder α] [PartialOrder β] (x : α) (y : β) (k : Nat) :
    Descent DownCover (x,y) k ↔
      ∃ m n, k=m+n ∧ Descent DownCover x m ∧ Descent DownCover y n := by
  have hh : Descent DownCover (x,y) k ↔
      Descent (ProductCover (α := α) (β := β) DownCover DownCover) (x,y) k := by
    constructor
    · exact transport_descent (Equiv.refl _)
        (fun p q => product_order_covers p q)
    · exact transport_descent (Equiv.refl _)
        (fun p q => (product_order_covers p q).symm)
  exact hh.trans (descent_product_iff x y k)

namespace Geometry

variable {E F D G : Type*}
variable [AddCommGroup E] [Module ℝ E] [AddCommGroup F] [Module ℝ F]
variable [AddCommGroup D] [Module ℝ D] [AddCommGroup G] [Module ℝ G]
variable [TopologicalSpace E] [IsTopologicalAddGroup E] [ContinuousSMul ℝ E]
variable [TopologicalSpace F] [IsTopologicalAddGroup F] [ContinuousSMul ℝ F]
variable {B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ} {C : G →ₗ[ℝ] F →ₗ[ℝ] ℝ}
variable {L : AddSubgroup E} {M : AddSubgroup F} {LD : AddSubgroup D} {MD : AddSubgroup G}
variable {P : Set E} {Q : Set F}

/-- This statement is about the actual reflexive-subpolytope orders
defined using real convex hulls, interiors, additive lattices and polars. -/
theorem freeSum_descent_lengths (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q)
    (p : Subpolytopes B L LD P) (q : Subpolytopes C M MD Q) (k : Nat) :
    Descent DownCover (freeSumOrderIso hP hQ (p,q)) k ↔
      ∃ m n, k=m+n ∧ Descent DownCover p m ∧ Descent DownCover q n :=
  (descent_orderIso_iff (freeSumOrderIso hP hQ) (p,q) k).trans
    (descent_product_order_iff p q k)

theorem freeSum_shortest (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q)
    {p : Subpolytopes B L LD P} {q : Subpolytopes C M MD Q} {m n : Nat}
    (hp : Shortest DownCover p m) (hq : Shortest DownCover q n) :
    Shortest DownCover (freeSumOrderIso hP hQ (p,q)) (m+n) := by
  constructor
  · exact (freeSum_descent_lengths hP hQ p q (m+n)).2 ⟨m,n,rfl,hp.1,hq.1⟩
  · intro k hk
    obtain ⟨i,j,rfl,hi,hj⟩ := (freeSum_descent_lengths hP hQ p q k).1 hk
    exact Nat.add_le_add (hp.2 i hi) (hq.2 j hj)

theorem freeSum_longest (hP : Reflexive B L LD P) (hQ : Reflexive C M MD Q)
    {p : Subpolytopes B L LD P} {q : Subpolytopes C M MD Q} {m n : Nat}
    (hp : Longest DownCover p m) (hq : Longest DownCover q n) :
    Longest DownCover (freeSumOrderIso hP hQ (p,q)) (m+n) := by
  constructor
  · exact (freeSum_descent_lengths hP hQ p q (m+n)).2 ⟨m,n,rfl,hp.1,hq.1⟩
  · intro k hk
    obtain ⟨i,j,rfl,hi,hj⟩ := (freeSum_descent_lengths hP hQ p q k).1 hk
    exact Nat.add_le_add (hp.2 i hi) (hq.2 j hj)

end Geometry
end ReflexiveDescent

#print axioms ReflexiveDescent.Geometry.freeSum_descent_lengths
#print axioms ReflexiveDescent.Geometry.freeSum_shortest
#print axioms ReflexiveDescent.Geometry.freeSum_longest
