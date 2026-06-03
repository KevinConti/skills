# Validate — `visual-explainer:plan-review` ⛔ *(delegated)*

`visual-explainer:plan-review` produces the visual review (the diagrams the user uses to hold their mental model of the codebase) and surfaces the gaps the grill missed. **Do not invoke it inline** — it loads the full visual-explainer reference (hundreds of lines of `SKILL.md` + `css-patterns.md`) and emits a large HTML document, all of which would lodge in your context for the rest of the run. Delegate it to a review sub-agent (follow the shared delegation contract in `SKILL.md`).

Spawn one sub-agent with the Agent tool — `subagent_type: general-purpose`, foreground (you need its result before continuing) — with this prompt shape:

```
Run the `visual-explainer:plan-review` skill against the plan for <ITEM>.
- Plan artifact: <PLAN_PATH>. Also read: <CONTEXT.md path>, <ADR paths>.
- Produce the visual plan-review HTML and save it under ~/.agent/diagrams/.

Return ONLY: (1) the absolute path to the HTML file, and (2) a concise text
list of the findings/gaps it surfaced — the risks, plan deltas, and anything
the plan does not yet cover. Do NOT paste the HTML or its CSS back.
```

⛔ **Gate.** Open the returned HTML for the user and present the sub-agent's findings list. Usually the plan's mitigations are sufficient and there's nothing to add. Occasionally a real gap needs a non-trivial change — if so, amend the plan (a focused follow-up grill question, or a direct edit to the plan doc), and if the change is substantial, **re-run plan-review** (spawn a fresh sub-agent). **Hold the findings** — they must reach the handoff. Do not proceed to handoff until the user is satisfied the plan is sound.
