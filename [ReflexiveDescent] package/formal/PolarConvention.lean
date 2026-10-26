import FreeSumGeometry

namespace ReflexiveDescent.Geometry

open Set

variable {E D : Type*} [AddCommGroup E] [Module ℝ E] [AddCommGroup D] [Module ℝ D]

/-- The manuscript uses the lower-bound convention for the polar. -/
def negativePolar (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ) (P : Set E) : Set D :=
  {u | ∀ x ∈ P, -1 ≤ B u x}

theorem negativePolar_eq_neg_image (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ) (P : Set E) :
    negativePolar B P = Neg.neg '' polar B P := by
  ext u
  constructor
  · intro h
    refine ⟨-u,?_,by simp⟩
    intro x hx
    have hh := h x hx
    simpa only [map_neg,LinearMap.neg_apply] using (neg_le.2 hh)
  · rintro ⟨u,hu,rfl⟩ x hx
    have hh := hu x hx
    simp only [map_neg,LinearMap.neg_apply]
    linarith

theorem latticeHull_neg_image {L : AddSubgroup D} {P : Set D}
    (h : LatticeHull L P) : LatticeHull L (Neg.neg '' P) := by
  have hh := h.linear_image (-(LinearMap.id : D →ₗ[ℝ] D)) (fun x hx => L.neg_mem hx)
  simpa using hh

theorem dual_latticeHull_conventions_iff (B : D →ₗ[ℝ] E →ₗ[ℝ] ℝ)
    (L : AddSubgroup D) (P : Set E) :
    LatticeHull L (negativePolar B P) ↔ LatticeHull L (polar B P) := by
  rw [negativePolar_eq_neg_image]
  constructor
  · intro h
    have hh := latticeHull_neg_image h
    simpa [Set.image_image] using hh
  · exact latticeHull_neg_image

end ReflexiveDescent.Geometry

#print axioms ReflexiveDescent.Geometry.dual_latticeHull_conventions_iff
