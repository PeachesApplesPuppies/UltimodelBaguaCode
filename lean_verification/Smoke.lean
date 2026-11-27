import Lean

set_option maxRecDepth 10000
set_option maxHeartbeats 2000000

-- The two complementary residue Lenses distinguish all 15 states.
theorem twoEyes : ∀ a b : Fin 15,
    a.val % 3 = b.val % 3 → a.val % 5 = b.val % 5 → a = b := by
  decide

-- Neither Lens alone distinguishes all states.
theorem firstLensLossy : (0 : Nat) % 3 = 3 % 3 ∧ (0 : Nat) ≠ 3 := by decide
theorem secondLensLossy : (0 : Nat) % 5 = 5 % 5 ∧ (0 : Nat) ≠ 5 := by decide

#print axioms twoEyes
#print axioms firstLensLossy
#print axioms secondLensLossy


-- Temporal boundary: abstract additive bookkeeping only.
-- Integer-valued model; does not formalize the real weights or RH.
theorem boundaryPairing (current previous delayed boundary : Int)
    (h : boundary = current - previous) :
    current - delayed = (previous - delayed) + boundary := by
  omega

-- Exact finite telescoping of successive boundary increments.
def boundarySum (f : Nat → Int) : Nat → Int
  | 0 => 0
  | n+1 => boundarySum f n + (f (n+1) - f n)

theorem boundaryTelescopes (f : Nat → Int) (n : Nat) :
    boundarySum f n = f n - f 0 := by
  induction n with
  | zero => simp [boundarySum]
  | succ n ih =>
    simp only [boundarySum, ih]
    omega

#print axioms boundaryPairing
#print axioms boundaryTelescopes
