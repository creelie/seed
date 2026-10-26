# Reflexive descent — Lean supplement

Start with [FORMAL-COVERAGE.md](FORMAL-COVERAGE.md). It distinguishes the
completed geometric kernel proofs, the exact stored graph certificate,
and the unformalized census/geometry inputs. The exact D4 is not proved.

The entry point is `ReflexiveDescentFormal.lean`. `lakefile.toml` and
`lean-toolchain` pin the dependencies. `AxiomsAudit.lean` checks the
foundational dependencies of every target theorem.

On the current machine, `python run_lean.py` builds every positive module
in dependency order; it does not silently skip an empty target list.
For other machines use the portable Lake commands in the coverage file.

All positive modules compile. The separate negative-control file must
fail and is not part of the default build. Evidence, source hashes and
coverage flags are recorded in `verification.json` when the audit bundle
is finalized.

The formalizations and revisions were developed with ChatGPT/Codex
assistance at the user's request. No subagents were used for this task.
The manuscript author is Deep Bhattacharjee. The preceding joint work
with Ushashi Bhattacharya remains credited in the manuscript and original
references. Mathematical results and data inherited from that work are
not reattributed to the assistant.

The stored graph derives from the original `creelie/seed` certificate.
Mathlib is an external standard proof-library dependency under its own
license. The ordinary geometric definitions and target proofs are present
in the supplied Lean sources, not replaced with imported bespoke results
or axioms.
