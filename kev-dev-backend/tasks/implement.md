# Implement — delegated sub-agent *(delegated)*

Spawn **one** implementation sub-agent with the Agent tool:

- `subagent_type: general-purpose`, foreground (you need its result before continuing).
- **No worktree isolation** — it edits the real working tree so the ship-phase skills operate on the actual diff.
- Its context is intentionally just the handoff brief + task — not this conversation.

Use this prompt shape:

```
You are implementing one work item in this repo. Your brief is the handoff
document at <HANDOFF_PATH> — read it first and in full. It links to the plan,
CONTEXT.md, any ADRs, the relevant code, and a list of risks/open items from
plan review. Treat the plan as decided; execute it faithfully.

- Implement the work, following the plan and respecting the captured risks.
- Verify as you go — run the build/tests; use the `verify` or `run` skills if
  they help confirm the change behaves.
- Match the surrounding code's conventions.

Escalation (this matters): if you hit a decision the handoff/plan does NOT
cover — an unresolved trade-off, a discovered gap, anything needing human
judgment — STOP and return with the specific question instead of guessing. A
clean halt is worth more than a wrong guess.

Return a concise summary: what you implemented (by file/area), what you tested
and the result, any deviations from the plan, and anything you escalated.
```
