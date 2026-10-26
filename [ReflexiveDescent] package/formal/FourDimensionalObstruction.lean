import FreeSumGeometry

namespace ReflexiveDescent

/-- The earlier paper's lower-dimensional maxima, used as explicit
numerical bounds here; this definition does not prove their geometry. -/
def lowDimBound : Nat → Nat
  | 1 => 0
  | 2 => 5
  | 3 => 11
  | _ => 0

theorem reducible_four_dimensional_bound (d e a b : Nat)
    (hd : 0<d) (he : 0<e) (hs : d+e=4)
    (ha : a≤lowDimBound d) (hb : b≤lowDimBound e) : a+b≤11 := by
  have hcases : (d=1 ∧ e=3) ∨ (d=2 ∧ e=2) ∨ (d=3 ∧ e=1) := by omega
  rcases hcases with ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ | ⟨rfl,rfl⟩ <;>
    norm_num [lowDimBound] at ha hb <;> omega

namespace Geometry

open Set

noncomputable def halfDiagonal : ℝ × ℝ := (1/2,1/2)
def enlargedLattice : AddSubgroup (ℝ × ℝ) :=
  AddSubgroup.closure {(1,0),(0,1),halfDiagonal}

theorem mixed_point_in_freeSum :
    halfDiagonal ∈ freeSum (Icc (-1:ℝ) 1) (Icc (-1:ℝ) 1) := by
  have hx := left_mem_freeSum (Q := Icc (-1:ℝ) 1) (show (1:ℝ) ∈ Icc (-1:ℝ) 1 by norm_num)
  have hy := right_mem_freeSum (P := Icc (-1:ℝ) 1) (show (1:ℝ) ∈ Icc (-1:ℝ) 1 by norm_num)
  have hh := (convex_convexHull ℝ _) hx hy
    (by norm_num : (0:ℝ)≤1/2) (by norm_num : (0:ℝ)≤1/2)
    (by norm_num : (1/2:ℝ)+1/2=1)
  simpa [freeSum,halfDiagonal,Prod.smul_mk,Prod.mk_add_mk] using hh

/-- An explicit counterexample to extending the axis-support lemma to an
overlattice which is not the specified direct-sum lattice. -/
theorem overlattice_has_mixed_point :
    ∃ z ∈ enlargedLattice, z ∈ freeSum (Icc (-1:ℝ) 1) (Icc (-1:ℝ) 1) ∧
      z.1≠0 ∧ z.2≠0 := by
  refine ⟨halfDiagonal,AddSubgroup.subset_closure (by simp),mixed_point_in_freeSum,?_,?_⟩ <;>
    norm_num [halfDiagonal]

end Geometry
end ReflexiveDescent

#print axioms ReflexiveDescent.reducible_four_dimensional_bound
#print axioms ReflexiveDescent.Geometry.overlattice_has_mixed_point
