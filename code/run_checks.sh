#!/usr/bin/env bash
# Runs every independent check of the paper and prints one summary line.
#   C          checks/pair_bound.c      pair bound by quadratic search, Table I
#   C++        checks/delta680.cpp      Delta_680, its dual, the end simplex
#   Python     checks/check_pairs.py    pair bound by a Fenwick tree, the witness chain
#              checks/check_chain.py    the descent of Table III (add FULL=1 for all covers)
#              checks/check_poset3.py   depths and heights in dimension three
#              checks/check_depth22.py  two polytopes of depth 22 (add FULL=1 to recompute covers)
#   Julia      checks/polygons.jl       the sixteen polygons from scratch, Table II
#   Macaulay2  checks/delta680.m2       Delta_680 with the Polyhedra package
#   Lean 4     ../lean/Seed.lean        the finite arithmetic and the counting lemma
# Tools are taken from PATH, or from CC, CXX, PYTHON, JULIA, M2, LEAN.
# A tool that is missing is reported and its checks are skipped.
set -u
cd "$(dirname "$0")"
CC=${CC:-gcc}; CXX=${CXX:-g++}; PYTHON=${PYTHON:-python3}
JULIA=${JULIA:-julia}; M2=${M2:-M2}; LEAN=${LEAN:-lean}
BUILD=$(mktemp -d); trap 'rm -rf "$BUILD"' EXIT
LOG="$BUILD/all.log"; : > "$LOG"
skipped=()

run() {   # run <name> <command...>
  local name=$1; shift
  echo "== $name" | tee -a "$LOG"
  "$@" 2>&1 | tee -a "$LOG"
  return "${PIPESTATUS[0]}"
}
have() { command -v "$1" >/dev/null 2>&1; }

status=0
if have "$CC"; then
  "$CC" -O2 -o "$BUILD/pair_bound" checks/pair_bound.c && run "C: pair bound" "$BUILD/pair_bound" data/ks4_point_pairs.csv || status=1
else skipped+=("C"); fi
if have "$CXX"; then
  "$CXX" -O2 -std=c++17 -o "$BUILD/delta680" checks/delta680.cpp && run "C++: Delta_680" "$BUILD/delta680" || status=1
else skipped+=("C++"); fi
if have "$PYTHON"; then
  run "Python: pair bound" "$PYTHON" checks/check_pairs.py || status=1
  if [ "${FULL:-0}" = 1 ]; then run "Python: descent of Delta_680 (full)" "$PYTHON" checks/check_chain.py --full || status=1
  else run "Python: descent of Delta_680" "$PYTHON" checks/check_chain.py || status=1; fi
  run "Python: dimension three" "$PYTHON" checks/check_poset3.py || status=1
  if [ "${FULL:-0}" = 1 ]; then run "Python: depth 22 (full)" "$PYTHON" checks/check_depth22.py --full || status=1
  else run "Python: depth 22" "$PYTHON" checks/check_depth22.py || status=1; fi
else skipped+=("Python"); fi
if have "$JULIA"; then
  run "Julia: polygons" "$JULIA" --startup-file=no checks/polygons.jl || status=1
else skipped+=("Julia"); fi
if have "$M2"; then
  run "Macaulay2: Delta_680" "$M2" --script checks/delta680.m2 || status=1
else skipped+=("Macaulay2"); fi
if have "$LEAN"; then
  echo "== Lean 4: ../lean/Seed.lean" | tee -a "$LOG"
  ( cd ../lean && "$LEAN" Seed.lean ) > "$BUILD/lean.out" 2>&1 || status=1
  cat "$BUILD/lean.out" | tee -a "$LOG"
  nthm=$(grep -c '^theorem ' ../lean/Seed.lean)
  nok=$(grep -cE "does not depend on any axioms|depends on axioms: \[propext\]$" "$BUILD/lean.out")
  if [ "$nthm" = "$nok" ] && ! grep -q error "$BUILD/lean.out"; then
    echo "PASS Lean: $nthm theorems, each axiom-free or on propext only" | tee -a "$LOG"
  else
    echo "FAIL Lean: $nok of $nthm theorems checked" | tee -a "$LOG"; status=1
  fi
else skipped+=("Lean"); fi

pass=$(grep -c '^PASS' "$LOG"); fail=$(grep -c '^FAIL' "$LOG")
[ ${#skipped[@]} -gt 0 ] && echo "skipped (tool not found): ${skipped[*]}"
echo "$pass checks passed, $fail failed"
[ "$fail" = 0 ] && [ "$status" = 0 ]
