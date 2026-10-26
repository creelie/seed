import DescentProducts

/-! The exact five-element cover graph and all of its Cartesian powers.
The identification with embedded lattice polygons is a separate geometric
statement, not an assumption hidden in these finite graph theorems. -/

namespace ReflexiveDescent

theorem lower_certificate {α : Type*} {c : α → α → Prop} (b : α → Nat)
    (terminal : ∀ x, (∀ y, ¬ c x y) → b x = 0)
    (edge : ∀ x y, c x y → b x ≤ b y + 1)
    {x : α} {k : Nat} (h : Descent c x k) : b x ≤ k := by
  induction h with
  | stop x ht => simp [terminal x ht]
  | step x y k hc _ ih => exact Nat.le_trans (edge x y hc) (Nat.add_le_add_right ih 1)

theorem upper_certificate {α : Type*} {c : α → α → Prop} (b : α → Nat)
    (edge : ∀ x y, c x y → b y + 1 ≤ b x)
    {x : α} {k : Nat} (h : Descent c x k) : k ≤ b x := by
  induction h with
  | stop x ht => exact Nat.zero_le _
  | step x y k hc _ ih => exact Nat.le_trans (Nat.add_le_add_right ih 1) (edge x y hc)

inductive PentagonNode | a | hb | hc | c | top deriving DecidableEq, Repr

open PentagonNode

def pentagonCover : PentagonNode → PentagonNode → Prop
  | top,hb | top,hc | top,c | hb,a | hc,a => True
  | _,_ => False

def pentagonLow : PentagonNode → Nat
  | a | c => 0
  | _ => 1

def pentagonHigh : PentagonNode → Nat
  | a | c => 0
  | hb | hc => 1
  | top => 2

theorem pentagon_lower (x : PentagonNode) (k : Nat)
    (h : Descent pentagonCover x k) : pentagonLow x ≤ k := by
  apply lower_certificate pentagonLow ?_ ?_ h
  · intro x ht
    cases x with
    | a => rfl
    | c => rfl
    | hb => exact False.elim (ht a trivial)
    | hc => exact False.elim (ht a trivial)
    | top => exact False.elim (ht c trivial)
  · intro x y hc
    cases x <;> cases y <;> simp_all [pentagonCover,pentagonLow]

theorem pentagon_upper (x : PentagonNode) (k : Nat)
    (h : Descent pentagonCover x k) : k ≤ pentagonHigh x := by
  apply upper_certificate pentagonHigh ?_ h
  intro x y hc
  cases x <;> cases y <;> simp_all [pentagonCover,pentagonHigh]

theorem pentagon_shortest : Shortest pentagonCover top 1 := by
  constructor
  · exact Descent.step top c 0 trivial
      (Descent.stop c (by intro y; cases y <;> simp [pentagonCover]))
  · exact pentagon_lower top

theorem pentagon_longest : Longest pentagonCover top 2 := by
  constructor
  · exact Descent.step top hb 1 trivial (Descent.step hb a 0 trivial
      (Descent.stop a (by intro y; cases y <;> simp [pentagonCover])))
  · exact pentagon_upper top

def PentagonPower : Nat → Type
  | 0 => Unit
  | r+1 => PentagonNode × PentagonPower r

def powerCover : (r : Nat) → PentagonPower r → PentagonPower r → Prop
  | 0 => fun _ _ => False
  | r+1 => ProductCover pentagonCover (powerCover r)

def powerRoot : (r : Nat) → PentagonPower r
  | 0 => ()
  | r+1 => (top,powerRoot r)

theorem power_shortest (r : Nat) : Shortest (powerCover r) (powerRoot r) r := by
  induction r with
  | zero => exact ⟨Descent.stop () (by intro y; exact id),fun _ _ => Nat.zero_le _⟩
  | succ r ih =>
    simpa [PentagonPower,powerRoot,powerCover,Nat.add_comm] using shortest_product pentagon_shortest ih

theorem power_longest (r : Nat) : Longest (powerCover r) (powerRoot r) (2*r) := by
  induction r with
  | zero =>
    constructor
    · exact Descent.stop () (by intro y; exact id)
    · intro k hk
      cases hk with
      | stop _ _ => exact Nat.le_refl _
      | step _ _ _ hc _ => exact False.elim hc
  | succ r ih =>
    simpa [PentagonPower,powerRoot,powerCover,Nat.mul_add,Nat.add_comm] using longest_product pentagon_longest ih

theorem unbounded_power_depth (N : Nat) :
    ∃ r k, Shortest (powerCover r) (powerRoot r) k ∧ N < k := by
  exact ⟨N+1,N+1,power_shortest (N+1),Nat.lt_succ_self N⟩

theorem unbounded_power_gap (N : Nat) :
    ∃ r k l, Shortest (powerCover r) (powerRoot r) k ∧
      Longest (powerCover r) (powerRoot r) l ∧ N < l-k := by
  refine ⟨N+1,N+1,2*(N+1),power_shortest (N+1),power_longest (N+1),?_⟩
  omega

end ReflexiveDescent

#print axioms ReflexiveDescent.pentagon_shortest
#print axioms ReflexiveDescent.pentagon_longest
#print axioms ReflexiveDescent.power_shortest
#print axioms ReflexiveDescent.power_longest
#print axioms ReflexiveDescent.unbounded_power_gap
