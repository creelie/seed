import FreeSumGeometry

namespace ReflexiveDescent.Geometry

variable (ι : Type*) [Fintype ι]

/-- The actual coordinate lattice Z^ι inside R^ι. -/
def coordinateLattice : AddSubgroup (ι → ℝ) where
  carrier := {x | ∀ i, ∃ z : ℤ, x i = z}
  zero_mem' := by intro i; exact ⟨0,by simp⟩
  add_mem' := by
    intro x y hx hy i
    obtain ⟨a,ha⟩ := hx i
    obtain ⟨b,hb⟩ := hy i
    exact ⟨a+b,by simp [ha,hb]⟩
  neg_mem' := by
    intro x hx i
    obtain ⟨a,ha⟩ := hx i
    exact ⟨-a,by simp [ha]⟩

/-- The ordinary dot-product pairing, with no uninterpreted geometry. -/
def coordinatePairing : (ι → ℝ) →ₗ[ℝ] (ι → ℝ) →ₗ[ℝ] ℝ where
  toFun u := {
    toFun x := ∑ i, u i * x i
    map_add' x y := by simp [mul_add,Finset.sum_add_distrib]
    map_smul' a x := by simp [Finset.mul_sum,mul_left_comm] }
  map_add' u v := by
    apply LinearMap.ext; intro x
    simp [add_mul,Finset.sum_add_distrib]
  map_smul' a u := by
    apply LinearMap.ext; intro x
    simp [Finset.mul_sum,mul_assoc]

theorem coordinatePairing_integral (u x : ι → ℝ)
    (hu : u ∈ coordinateLattice ι) (hx : x ∈ coordinateLattice ι) :
    ∃ z : ℤ, coordinatePairing ι u x = z := by
  choose a ha using hu
  choose b hb using hx
  refine ⟨∑ i, a i * b i,?_⟩
  simp [coordinatePairing,ha,hb]

end ReflexiveDescent.Geometry

#print axioms ReflexiveDescent.Geometry.coordinatePairing_integral
