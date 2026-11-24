import Mathlib

/-!
Phase II draft; not compiled. These are elementary supporting lemmas,
not a formalization of the zeta-specific spectral energy theorem.
-/
namespace ChatGiblet

theorem geometricBlockSummable
    (f : ℕ → ℂ) (C r : ℝ)
    (hr0 : 0 ≤ r) (hr1 : r < 1)
    (h : ∀ n : ℕ, ‖f n‖ ≤ C * r ^ n) :
    Summable f := by
  have hg : Summable (fun n : ℕ => C * r ^ n) :=
    (summable_geometric_of_lt_one hr0 hr1).mul_left C
  exact hg.of_norm_bounded h

theorem twoBlockMax (a b z c : ℝ)
    (hc : 0 < c) (h : z ≤ c * (a + b)) :
    z / (2 * c) ≤ max a b := by
  apply (div_le_iff₀ (show 0 < 2 * c by positivity)).2
  have hab : a + b ≤ 2 * max a b := by
    linarith [le_max_left a b, le_max_right a b]
  calc
    z ≤ c * (a + b) := h
    _ ≤ c * (2 * max a b) := mul_le_mul_of_nonneg_left hab hc.le
    _ = max a b * (2 * c) := by ring

end ChatGiblet
