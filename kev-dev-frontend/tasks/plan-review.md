# Validate — `visual-explainer:plan-review` ⛔ *(delegated)*

`visual-explainer:plan-review` produces the visual review (diagrams the user relies on to hold their mental model) and surfaces gaps. **Do not invoke it inline** — it loads the full visual-explainer reference and emits a large HTML document that would lodge in your context for the rest of the run. Delegate it per the shared delegation contract in `SKILL.md`:

```
Run `visual-explainer:plan-review` against the plan for <ITEM>.
- Plan artifact: <PLAN_PATH>; design brief: <BRIEF_PATH>; also read <CONTEXT.md>, <ADRs>.
- Save the review HTML under ~/.agent/diagrams/.
Return ONLY: (1) the absolute path to the HTML, and (2) a concise findings list
— risks, plan/UX deltas, anything not yet covered. Do NOT paste the HTML or CSS back.
```

⛔ **Gate.** Open the returned HTML for the user and present the findings. If a real gap surfaces (UI or contract), amend and re-run plan-review (fresh sub-agent) if substantial. **Hold the findings** — they must reach the handoff.
