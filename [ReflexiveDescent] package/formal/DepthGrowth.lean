import Mathlib.Analysis.Subadditive
import Mathlib.Tactic

namespace ReflexiveDescent

open Set Filter Topology

def SuperadditiveDepth (D : Nat → Nat) : Prop := ∀ m n, D m + D n ≤ D (m+n)
noncomputable def depthRatio (D : Nat → Nat) (n : Nat) : ℝ := D n / n

theorem negative_depth_subadditive {D : Nat → Nat} (hD : SuperadditiveDepth D) :
    Subadditive (fun n => -(D n : ℝ)) := by
  intro m n
  have hh : (D m : ℝ) + D n ≤ D (m+n) := by exact_mod_cast hD m n
  linarith

/-- The finite-limit branch of the extended Fekete conclusion, including
the exact least-upper-bound characterization of the limit. -/
theorem depth_ratio_finite_limit {D : Nat → Nat} (hD : SuperadditiveDepth D)
    (hbounded : BddAbove (range (depthRatio D))) :
    ∃ L : ℝ, Tendsto (depthRatio D) atTop (𝓝 L) ∧
      (∀ n, 0<n → depthRatio D n ≤ L) ∧
      (∀ A, (∀ n, 0<n → depthRatio D n ≤ A) → L ≤ A) := by
  let h := negative_depth_subadditive hD
  have hb : BddBelow (range (fun n => -(D n : ℝ) / n)) := by
    obtain ⟨A,hA⟩ := hbounded
    refine ⟨-A,?_⟩
    rintro _ ⟨n,rfl⟩
    simpa only [neg_div,depthRatio] using neg_le_neg (hA ⟨n,rfl⟩)
  have ht : Tendsto (depthRatio D) atTop (𝓝 (-h.lim)) := by
    change Tendsto (fun n => (D n : ℝ)/n) atTop (𝓝 (-h.lim))
    simpa only [neg_div,neg_neg] using (h.tendsto_lim hb).neg
  refine ⟨-h.lim,ht,?_,?_⟩
  · intro n hn
    have hh := h.lim_le_div hb (Nat.ne_of_gt hn)
    simp only [neg_div] at hh
    change (D n : ℝ)/n ≤ -h.lim
    linarith
  · intro A hA
    exact le_of_tendsto ht (eventually_atTop.2 ⟨1,fun n hn => hA n (by omega)⟩)

/-- In the remaining branch the ratios tend to positive infinity. -/
theorem depth_ratio_infinite_limit {D : Nat → Nat} (hD : SuperadditiveDepth D)
    (hunbounded : ¬ BddAbove (range (depthRatio D))) :
    Tendsto (depthRatio D) atTop atTop := by
  let h := negative_depth_subadditive hD
  apply tendsto_atTop.2
  intro A
  obtain ⟨x,⟨n,rfl⟩,hn⟩ := not_bddAbove_iff.1 hunbounded (max A 0 + 1)
  have hn0 : n ≠ 0 := by
    intro hz
    subst n
    simp only [depthRatio,CharP.cast_eq_zero,div_zero] at hn
    linarith [le_max_right A (0:ℝ)]
  have hr : A < depthRatio D n := by linarith [le_max_left A (0:ℝ)]
  have he := h.eventually_div_lt_of_div_lt hn0
    (show -(D n : ℝ)/n < -A by simpa [depthRatio,neg_div] using neg_lt_neg hr)
  filter_upwards [he] with k hk
  simp only [neg_div] at hk
  change A ≤ (D k : ℝ)/k
  linarith

end ReflexiveDescent

#print axioms ReflexiveDescent.depth_ratio_finite_limit
#print axioms ReflexiveDescent.depth_ratio_infinite_limit
