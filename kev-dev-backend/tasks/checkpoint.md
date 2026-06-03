# Checkpoint ⛔ (light) *(inline)*

Present the sub-agent's summary — what it implemented, what it tested, deviations from the plan, anything it escalated.

⛔ **Gate.** The user approves proceeding to cleanup, sends it back for fixes (re-delegate with the correction), or takes over manually. This is the fail-fast valve that stands in for the supervision you'd otherwise have *during* implementation — keep it light, because diff-review is the substantive review. If the sub-agent escalated a question, resolve it with the user here before continuing.
