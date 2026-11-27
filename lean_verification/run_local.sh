#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "$0")"
ROOT="$(pwd)"
mkdir -p results
OUT="$(mktemp -d "$ROOT/results/run-XXXXXXXX")"
exec > >(tee "$OUT/run.log") 2>&1
trap 'rc=$?; if [ "$rc" -eq 0 ]; then echo "PASS: Lean starter checks accepted"; else echo "NOT VERIFIED (exit $rc). See log."; fi; echo "Results: $OUT"; exit "$rc"' EXIT
echo "BCE / Lean Verification Department"
echo "Reports: $OUT"
for cmd in curl python3; do
  if ! command -v "$cmd" >/dev/null; then
    echo "Missing $cmd. On Ubuntu, run: sudo apt update && sudo apt install -y curl python3"
    exit 1
  fi
done
export PATH="$HOME/.elan/bin:$PATH"
if ! command -v elan >/dev/null; then
  installer="$(mktemp)"
  curl --fail --location --silent --show-error https://elan.lean-lang.org/elan-init.sh -o "$installer"
  sh "$installer" -y --default-toolchain none
  rm -f "$installer"
fi
elan toolchain install "$(cat lean-toolchain)"
lean --version
python3 -m unittest discover -s ../ouroboros_proof_compressor/tests -v
lean Smoke.lean | tee "$OUT/smoke.log"
if grep -Eiq 'sorryAx|declaration uses .?sorry' "$OUT/smoke.log"; then
  echo "Incomplete proof diagnostic"; exit 1
fi
python3 ../ouroboros_proof_compressor/proof_compressor.py \
  --project "$ROOT" --command lean --target ouroboros_chain \
  --timeout 45 --out "$OUT/compressor" reduce \
  ../ouroboros_proof_compressor/examples/Chain.lean \
  --lemmas hP hPQ hQR hUnused hDuplicate --mode exact --budget 64
python3 - "$OUT/compressor/report.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1]))
assert r['baseline']=='accepted',r
assert r['search_complete_for_configured_checker'],r
assert len(r['retained_lemmas'])==3,r
print("Expected minimum of three candidate lemmas verified.")
PY
lean "$OUT/compressor/accepted.lean"
echo "Starter only: this does not verify the full RH proof."
