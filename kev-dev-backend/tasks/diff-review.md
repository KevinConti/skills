# Review — `visual-explainer:diff-review` ⛔ *(delegated)*

Like plan-review, **do not invoke inline.** `visual-explainer:diff-review` reloads the full visual-explainer reference and emits another large HTML document — running it in your context is what would re-flood the ship phase you worked to keep clean. Delegate it (follow the shared delegation contract in `SKILL.md`).

Spawn one sub-agent with the Agent tool — `subagent_type: general-purpose`, foreground — with this prompt shape:

```
Run the `visual-explainer:diff-review` skill on the pending changes for <ITEM>.
- Plan artifact: <PLAN_PATH>; cleanup + security summaries: <PASTE>.
- Produce the visual diff-review HTML and save it under ~/.agent/diagrams/.

Return ONLY: (1) the absolute path to the HTML file, and (2) a concise text
summary — what was completed, remaining issues, and deltas from the plan.
Do NOT paste the HTML or its CSS back.
```

⛔ **Gate.** Open the returned HTML for the user and present the summary. The user reviews and approves.
