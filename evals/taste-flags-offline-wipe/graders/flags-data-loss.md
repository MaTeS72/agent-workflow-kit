---
type: llm
weight: 3
---

PASS if the reply reports, as a blocker or must-fix finding, that `reconcile` clears the local recipe book when the server returns an empty result, so a user who is offline (or whose fetch fails) loses their recipes.
FAIL if the reply doesn't mention this, or treats it as minor or optional.
