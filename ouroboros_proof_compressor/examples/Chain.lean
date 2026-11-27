import Lean

-- Redundant local hypotheses are supplied in the candidate pool.
-- The statement and all surrounding source stay unchanged across trials.
theorem ouroboros_chain (P Q R : Prop)
    (hP : P) (hPQ : P → Q) (hQR : Q → R)
    (hUnused : True) (hDuplicate : P) : R := by
  -- OUROBOROS: LEMMAS
