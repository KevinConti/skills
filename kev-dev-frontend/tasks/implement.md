# Implement — delegated sub-agent *(delegated)*

Spawn **one** implementation sub-agent (`general-purpose`, foreground, **no worktree isolation**, context = the handoff brief only):

```
You are implementing one frontend work item. Your brief is the handoff document
at <HANDOFF_PATH> — read it first and in full. It contains the confirmed design
brief, the agreed data contract (a real endpoint, or a mock to build against),
plan-review risks, and links to the plan/CONTEXT/ADRs. Treat the brief and
contract as decided; execute them faithfully.

- Build the UI to the design brief; you may use `impeccable craft` with the brief
  already confirmed (it will skip re-shaping and go straight to build + iterate).
- Wire per the contract — the real endpoint (through whatever adapter/shaping layer the plan specifies) or the agreed mock/stub.
- Verify visually — render it, screenshot across viewports, check the key states
  (empty/loading/error/edge) and responsive behavior.
- Match the project's framework, component library, and conventions.

Escalation: if you hit a decision the brief/contract does NOT cover, STOP and
return with the specific question instead of guessing.

Return a concise summary (what you built by area, states covered, deviations,
anything escalated) AND the path(s) to a screenshot of the result. Do not paste
file contents back.
```
