/-
  Stock algebra for the governance patch-gap (paper Section 4.3).

  Discrete time. R_d t = finds at step t, R_p t = patches at step t,
  S t = stock of known-but-unpatched ambiguities. The only modeling
  assumption is the stock-flow identity S (t+1) = S t + R_d t - R_p t.

  G = R_d / R_p is stated in cross-multiplied form so core Lean (no
  Mathlib) suffices: for R_p t > 0, "G t > 1" is "R_d t > R_p t", and
  "G falls from t to t+1" is "R_d (t+1) * R_p t < R_d t * R_p (t+1)".

  Nothing here is about any legal system. It pins the definitions the
  paper uses so the G-versus-S distinction cannot drift in prose.
-/
namespace PatchGap

structure Flow where
  Rd : Nat → Int
  Rp : Nat → Int
  S  : Nat → Int
  step : ∀ t, S (t + 1) = S t + Rd t - Rp t

/-- The stock rises at a step exactly when discovery outpaces repair. -/
theorem stock_rises_iff (f : Flow) (t : Nat) :
    f.S t < f.S (t + 1) ↔ f.Rp t < f.Rd t := by
  rw [f.step t]; omega

/-- The stock is flat exactly when the rates are equal (G = 1). -/
theorem stock_flat_iff (f : Flow) (t : Nat) :
    f.S (t + 1) = f.S t ↔ f.Rd t = f.Rp t := by
  rw [f.step t]; omega

/-- If discovery beats repair on every step of a window, the stock grows
    by at least one per step over that window. -/
theorem stock_grows_on_window (f : Flow) (t0 : Nat) :
    ∀ k : Nat, (∀ j, j < k → f.Rp (t0 + j) < f.Rd (t0 + j)) →
      f.S t0 + k ≤ f.S (t0 + k) := by
  intro k
  induction k with
  | zero => intro _; simp
  | succ n ih =>
    intro h
    have hn : f.S t0 + n ≤ f.S (t0 + n) := ih (fun j hj => h j (by omega))
    have hs := f.step (t0 + n)
    have hlt := h n (by omega)
    have e : t0 + (n + 1) = t0 + n + 1 := by omega
    rw [e, hs]
    omega

/-- Once repair keeps pace on every later step, the stock never rises again. -/
theorem stock_nonincreasing_after (f : Flow) (t0 : Nat)
    (h : ∀ t, t0 ≤ t → f.Rd t ≤ f.Rp t) :
    ∀ k : Nat, f.S (t0 + k) ≤ f.S t0 := by
  intro k
  induction k with
  | zero => simp
  | succ n ih =>
    have hs := f.step (t0 + n)
    have hle := h (t0 + n) (by omega)
    have e : t0 + (n + 1) = t0 + n + 1 := by omega
    rw [e, hs]
    omega

/-- G falling is not the stock falling: a concrete flow where G drops
    from 10 to 3 between steps 0 and 1 while S rises on both steps. -/
def witness : Flow where
  Rd := fun t => if t = 0 then 10 else 6
  Rp := fun t => if t = 0 then 1 else 2
  S  := fun t => if t = 0 then 0 else 4 * (t : Int) + 5
  step := by
    intro t
    cases t with
    | zero => decide
    | succ n => simp; omega

theorem g_falls_while_stock_rises :
    -- G(0) = 10 > 1 and G(1) = 3 > 1
    witness.Rp 0 < witness.Rd 0 ∧ witness.Rp 1 < witness.Rd 1 ∧
    -- G(1) < G(0), cross-multiplied: Rd 1 * Rp 0 < Rd 0 * Rp 1
    witness.Rd 1 * witness.Rp 0 < witness.Rd 0 * witness.Rp 1 ∧
    -- S rises on both steps
    witness.S 0 < witness.S 1 ∧ witness.S 1 < witness.S 2 := by
  decide

end PatchGap
