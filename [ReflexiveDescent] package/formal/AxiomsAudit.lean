import ReflexiveDescentFormal
import Lean.Util.CollectAxioms

open Lean Elab Command in
run_cmd do
  let env ← getEnv
  let mut count : Nat := 0
  for (name, info) in env.constants.toList do
    if (`ReflexiveDescent).isPrefixOf name then
      match info with
      | .axiomInfo _ => throwError "Custom axiom declared: {name}"
      | .thmInfo _ =>
        let axioms ← collectAxioms name
        for ax in axioms do
          unless ax == `propext || ax == `Classical.choice || ax == `Quot.sound do
            throwError "Unapproved axiom in {name}: {ax}"
        logInfo m!"AUDIT {name}: {axioms}"
        count := count+1
      | _ => pure ()
  if count == 0 then throwError "No target theorems found"
  logInfo m!"AUDIT PASS: {count} target theorems; only standard foundational axioms"
