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
end MobiusBoundary
