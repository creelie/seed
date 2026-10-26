import Mathlib.Order.Cover
import Lean.Elab.Tactic.Omega

/-!
Exact saturated-descent lengths in a Cartesian cover graph.
No geometric or census assumptions are made implicitly: the geometric
order isomorphism must be supplied separately when this theorem is applied
to reflexive polytopes.
-/

namespace ReflexiveDescent

universe u v

inductive Descent {α : Type u} (cover : α → α → Prop) : α → Nat → Prop
  | stop (x : α) (h : ∀ y, ¬ cover x y) : Descent cover x 0
  | step (x y : α) (k : Nat) (h : cover x y)
      (d : Descent cover y k) : Descent cover x (k + 1)

def ProductCover {α : Type u} {β : Type v}
    (c : α → α → Prop) (d : β → β → Prop)
    (p q : α × β) : Prop :=
  (c p.1 q.1 ∧ p.2 = q.2) ∨ (p.1 = q.1 ∧ d p.2 q.2)

theorem product_terminal_iff {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop} (a : α) (b : β) :
    (∀ q, ¬ ProductCover c d (a,b) q) ↔
      (∀ x, ¬ c a x) ∧ (∀ y, ¬ d b y) := by
  constructor
  · intro h
    exact ⟨fun x hx => h (x,b) (Or.inl ⟨hx,rfl⟩),
      fun y hy => h (a,y) (Or.inr ⟨rfl,hy⟩)⟩
  · rintro ⟨hc,hd⟩ ⟨x,y⟩ (h | h)
    · exact hc x h.1
    · exact hd y h.2

theorem split_descent {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    {p : α × β} {k : Nat} (h : Descent (ProductCover c d) p k) :
    ∃ m n, k = m+n ∧ Descent c p.1 m ∧ Descent d p.2 n := by
  induction h with
  | stop p ht =>
    have hh := (product_terminal_iff p.1 p.2).1 ht
    exact ⟨0,0,rfl,Descent.stop _ hh.1,Descent.stop _ hh.2⟩
  | step p q k hc _ ih =>
    obtain ⟨m,n,hk,hm,hn⟩ := ih
    rcases hc with ⟨hc,he⟩ | ⟨he,hd⟩
    · exact ⟨m+1,n,by omega,Descent.step _ _ _ hc hm,he ▸ hn⟩
    · exact ⟨m,n+1,by omega,he ▸ hm,Descent.step _ _ _ hd hn⟩

theorem combine_descents {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    {a : α} {b : β} {m n : Nat}
    (ha : Descent c a m) (hb : Descent d b n) :
    Descent (ProductCover c d) (a,b) (m+n) := by
  induction ha with
  | stop a ht =>
    induction hb with
    | stop b hs =>
      exact Descent.stop _ ((product_terminal_iff a b).2 ⟨ht,hs⟩)
    | step b b' n hc _ ih =>
      simpa using Descent.step (a,b) (a,b') n (Or.inr ⟨rfl,hc⟩)
        (by simpa only [Nat.zero_add] using ih)
  | step a a' m hc _ ih =>
    simpa [Nat.add_assoc,Nat.add_comm,Nat.add_left_comm] using
      Descent.step (a,b) (a',b) (m+n) (Or.inl ⟨hc,rfl⟩) ih

theorem descent_product_iff {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    (a : α) (b : β) (k : Nat) :
    Descent (ProductCover c d) (a,b) k ↔
      ∃ m n, k=m+n ∧ Descent c a m ∧ Descent d b n := by
  constructor
  · exact split_descent
  · rintro ⟨m,n,rfl,hm,hn⟩
    exact combine_descents hm hn

def Shortest {α : Type u} (c : α → α → Prop) (x : α) (k : Nat) : Prop :=
  Descent c x k ∧ ∀ j, Descent c x j → k ≤ j

def Longest {α : Type u} (c : α → α → Prop) (x : α) (k : Nat) : Prop :=
  Descent c x k ∧ ∀ j, Descent c x j → j ≤ k

theorem shortest_product {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    {a : α} {b : β} {m n : Nat}
    (ha : Shortest c a m) (hb : Shortest d b n) :
    Shortest (ProductCover c d) (a,b) (m+n) := by
  refine ⟨combine_descents ha.1 hb.1,?_⟩
  intro k hk
  obtain ⟨i,j,rfl,hi,hj⟩ := split_descent hk
  exact Nat.add_le_add (ha.2 i hi) (hb.2 j hj)

theorem longest_product {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    {a : α} {b : β} {m n : Nat}
    (ha : Longest c a m) (hb : Longest d b n) :
    Longest (ProductCover c d) (a,b) (m+n) := by
  refine ⟨combine_descents ha.1 hb.1,?_⟩
  intro k hk
  obtain ⟨i,j,rfl,hi,hj⟩ := split_descent hk
  exact Nat.add_le_add (ha.2 i hi) (hb.2 j hj)

theorem product_order_covers {α : Type u} {β : Type v}
    [PartialOrder α] [PartialOrder β] (p q : α × β) :
    q ⋖ p ↔ ProductCover (fun a a' => a' ⋖ a) (fun b b' => b' ⋖ b) p q := by
  rw [Prod.covBy_iff]
  simp only [ProductCover]
  constructor
  · rintro (⟨h,e⟩ | ⟨h,e⟩)
    · exact Or.inl ⟨h,e.symm⟩
    · exact Or.inr ⟨e.symm,h⟩
  · rintro (⟨h,e⟩ | ⟨e,h⟩)
    · exact Or.inl ⟨h,e.symm⟩
    · exact Or.inr ⟨h,e.symm⟩

/-- Transport an entire descent along an equivalence preserving covers. -/
theorem transport_descent {α : Type u} {β : Type v}
    {c : α → α → Prop} {d : β → β → Prop}
    (e : α ≃ β) (he : ∀ x y, c x y ↔ d (e x) (e y))
    {x : α} {k : Nat} (h : Descent c x k) : Descent d (e x) k := by
  induction h with
  | stop x ht =>
    apply Descent.stop
    intro z hz
    exact ht (e.symm z) ((he x (e.symm z)).2 (by simpa using hz))
  | step x y k hc _ ih => exact Descent.step _ _ _ ((he x y).1 hc) ih

end ReflexiveDescent

#print axioms ReflexiveDescent.descent_product_iff
#print axioms ReflexiveDescent.shortest_product
#print axioms ReflexiveDescent.longest_product
#print axioms ReflexiveDescent.product_order_covers
