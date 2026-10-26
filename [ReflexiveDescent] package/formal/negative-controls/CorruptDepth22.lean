import Depth22Certificate

open ReflexiveDescent.Depth22

/-- Deliberately corrupt the first root's lower bound from 22 to 23. -/
def corruptFirst : Tree → Tree
  | .leaf row => .leaf {row with lower := row.lower+1}
  | .branch k left right => .branch k (corruptFirst left) right

set_option maxRecDepth 1000000
set_option maxHeartbeats 0

-- This false certificate MUST be rejected by the kernel computation.
example : checkTree 5592 (corruptFirst data) (corruptFirst data) = true := by
  decide +kernel
