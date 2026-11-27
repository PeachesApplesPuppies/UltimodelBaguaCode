import Mathlib

open scoped BigOperators
namespace MobiusBoundary

noncomputable def kernel (n : ℕ) : ℝ :=
  (ArithmeticFunction.moebius n : ℝ) / Real.sqrt (n : ℝ)

noncomputable def response (N : ℕ) : ℝ :=
  ∑ n ∈ Finset.range (N + 1), kernel n

noncomputable def restricted (p N : ℕ) : ℝ :=
  ∑ n ∈ (Finset.range (N + 1)).filter (fun n => ¬ p ∣ n), kernel n

noncomputable def boundary (p N : ℕ) : ℝ :=
  restricted p N - restricted p (N / p)

theorem boundary_decomposition (p N : ℕ) :
    restricted p N = restricted p (N / p) + boundary p N := by
  unfold boundary
  ring

theorem kernel_new_prime (p n : ℕ) (hp : p.Prime) (hc : p.Coprime n) :
    kernel (p * n) = -kernel n / Real.sqrt (p : ℝ) := by
  unfold kernel
  rw [ArithmeticFunction.isMultiplicative_moebius.map_mul_of_coprime hc,
    ArithmeticFunction.moebius_apply_prime hp]
  push_cast
  rw [Real.sqrt_mul (by positivity : (0 : ℝ) ≤ (p : ℝ))]
  ring

-- The target is deliberately a proposition, not an axiom or a claimed theorem.
def SubexponentialBoundary (p : ℕ) : Prop :=
  ∀ ε : ℝ, 0 < ε → ∃ C : ℝ, 0 ≤ C ∧
    ∀ N : ℕ, 1 ≤ N → |boundary p N| ≤ C * (N : ℝ) ^ ε

-- A sufficient estimate for a sequence with geometric time steps.
theorem geometric_budget (r C : ℝ) (hr : 1 < r) (hC : 0 ≤ C)
    (f u : ℕ → ℝ) (h0 : |f 0| ≤ C)
    (hrec : ∀ n, f (n+1) = f n + u (n+1))
    (hu : ∀ n, |u n| ≤ C * r ^ n) :
    ∀ n, |f n| ≤ (C * r / (r-1)) * r ^ n := by
  intro n
  have hd : 0 < r - 1 := by linarith
  have hD : C ≤ C * r / (r - 1) := by
    apply (le_div_iff₀ hd).2
    nlinarith
  induction n with
  | zero => simpa using h0.trans hD
  | succ n ih =>
    rw [hrec]
    calc
      |f n + u (n+1)| ≤ |f n| + |u (n+1)| := abs_add_le _ _
      _ ≤ (C * r / (r-1)) * r ^ n + C * r ^ (n+1) :=
        add_le_add ih (hu (n+1))
      _ = (C * r / (r-1)) * r ^ (n+1) := by
        rw [pow_succ]
        field_simp [ne_of_gt hd]
        <;> ring

#print axioms boundary_decomposition
#print axioms kernel_new_prime
#print axioms geometric_budget

-- Almond compensation: a = earlier magnitude, b = later magnitude,
-- d = elapsed logarithmic time. The exponential decay estimate is
-- an explicit hypothesis here, not a claim about the global matching.
theorem almond_pair_cost (a b d : ℝ)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : b ≤ a)
    (hoverlap : d ≤ a + b)
    (hdecay : a - b ≤ a * d / 2) :
    |a - b| ≤ a ^ 2 := by
  rw [abs_of_nonneg (sub_nonneg.mpr hab)]
  have hd : d ≤ 2 * a := by linarith
  have hm := mul_le_mul_of_nonneg_left hd ha
  nlinarith

-- Disjoint pairing bookkeeping: conditional on a supplied partition.
theorem compensation_budget (paired unmatched : ℝ)
    (pcost debt : ℝ) (hp : |paired| ≤ pcost)
    (hu : |unmatched| ≤ debt) :
    |paired + unmatched| ≤ pcost + debt :=
  (abs_add_le _ _).trans (add_le_add hp hu)

-- Time decay of an old contribution is distinct from new forcing.
theorem decay_step_budget (old fresh a : ℝ)
    (ha : 0 ≤ a) (ha1 : a ≤ 1) :
    |a * old + fresh| ≤ |old| + |fresh| := by
  calc
    |a * old + fresh| ≤ |a * old| + |fresh| := abs_add_le _ _
    _ ≤ |old| + |fresh| := by
      rw [abs_mul, abs_of_nonneg ha]
      have h := mul_le_mul_of_nonneg_right ha1 (abs_nonneg old)
      linarith

#print axioms almond_pair_cost
#print axioms compensation_budget
#print axioms decay_step_budget


-- Zero signed residual does not imply zero absolute magnitude.
theorem zero_residual_hides_magnitude :
    ∃ a b : ℝ, a + b = 0 ∧ |a| + |b| = 2 := by
  exact ⟨1, -1, by norm_num, by norm_num⟩

-- No finite clean prefix can rule out all later failures
-- without further structural assumptions.
theorem finite_clean_counterexample (N : ℕ) :
    ∃ bad : ℕ → Prop, (∀ n < N, ¬ bad n) ∧ bad N := by
  refine ⟨fun n => n = N, ?_, rfl⟩
  intro n hn h
  exact (ne_of_lt hn) h

#print axioms zero_residual_hides_magnitude
#print axioms finite_clean_counterexample

end MobiusBoundary
