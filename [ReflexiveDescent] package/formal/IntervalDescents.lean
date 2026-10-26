import FreeSumDepth
import Mathlib.Order.Atoms.Finite

namespace ReflexiveDescent

theorem terminal_iff_minimal {α : Type*} [PartialOrder α] [Finite α] (x : α) :
    (∀ y, ¬ DownCover x y) ↔ ∀ y, y≤x → y=x := by
  constructor
  · intro ht y hy
    by_cases he : y=x
    · exact he
    · obtain ⟨z,_,hz⟩ := exists_le_covBy_of_lt (lt_of_le_of_ne hy he)
      exact False.elim (ht z hz)
  · intro hm y hy
    exact hy.ne (hm y hy.le)

inductive CoverPath {α : Type*} (c : α → α → Prop) : α → α → Nat → Prop
  | refl (x : α) : CoverPath c x x 0
  | step (x y z : α) (k : Nat) (h : c x y) (p : CoverPath c y z k) :
      CoverPath c x z (k+1)

theorem path_append_descent {α : Type*} {c : α → α → Prop}
    {x y : α} {k m : Nat} (h : CoverPath c x y k) (d : Descent c y m) :
    Descent c x (k+m) := by
  induction h with
  | refl x => simpa using d
  | step x y z k hc _ ih =>
    simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using Descent.step x y (k+m) hc (ih d)

theorem path_point_bound {α : Type*} {c : α → α → Prop}
    (points : α → Nat) (strict : ∀ x y, c x y → points y < points x)
    {x y : α} {k : Nat} (p : CoverPath c x y k) : k+points y ≤ points x := by
  induction p with
  | refl x => simp
  | step x y z k hc _ ih => have hh := strict x y hc; omega

theorem path_dual_bound {α : Type*} {c : α → α → Prop}
    (dual : α → Nat) (strict : ∀ x y, c x y → dual x < dual y)
    {x y : α} {k : Nat} (p : CoverPath c x y k) : k+dual x ≤ dual y := by
  induction p with
  | refl x => simp
  | step x y z k hc _ ih => have hh := strict x y hc; omega

theorem interval_path_exists {α : Type*} [PartialOrder α] [Finite α]
    (points : α → Nat) (strict : ∀ x y, y<x → points y < points x)
    (x y : α) (hy : y≤x) : ∃ k, CoverPath DownCover x y k := by
  classical
  induction h : points x using Nat.strong_induction_on generalizing x with
  | h n ih =>
    by_cases he : y=x
    · subst y; exact ⟨0,CoverPath.refl x⟩
    · obtain ⟨z,hyz,hzx⟩ := exists_le_covBy_of_lt (lt_of_le_of_ne hy he)
      obtain ⟨k,hk⟩ := ih (points z) (by simpa only [h] using strict x z hzx.lt) z hyz rfl
      exact ⟨k+1,CoverPath.step x z y k hzx hk⟩

/-- The interval argument does not assume that the proposed inclusion
is itself a cover. Its hypotheses are strict monotonicity of point counts
and the existence of a descent from the child. -/
theorem interval_descent_bound {α : Type*} [PartialOrder α] [Finite α]
    (points dual : α → Nat)
    (hpoints : ∀ x y, y<x → points y < points x)
    (hdual : ∀ x y, y ⋖ x → dual x < dual y)
    {x y : α} (hy : y≤x) {m : Nat} (dm : Descent DownCover y m) :
    ∃ n, Descent DownCover x n ∧
      n ≤ min (points x-points y) (dual y-dual x)+m := by
  obtain ⟨k,hk⟩ := interval_path_exists points hpoints x y hy
  have hp := path_point_bound points (fun a b h => hpoints a b h.lt) hk
  have hd := path_dual_bound dual hdual hk
  have hkp : k ≤ points x-points y := by omega
  have hkd : k ≤ dual y-dual x := by omega
  exact ⟨k+m,path_append_descent hk dm,Nat.add_le_add_right (le_min hkp hkd) m⟩

end ReflexiveDescent

#print axioms ReflexiveDescent.interval_path_exists
#print axioms ReflexiveDescent.interval_descent_bound
