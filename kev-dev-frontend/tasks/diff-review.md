# Review — `visual-explainer:diff-review` ⛔ + visual pass *(delegated)*

Like plan-review, **do not invoke inline.** Delegate diff-review *and* the rendered-UI capture to one sub-agent (per the shared delegation contract in `SKILL.md`):

```
For the pending changes for <ITEM>:
1. Run `visual-explainer:diff-review`; save the HTML under ~/.agent/diagrams/.
2. Render the built UI and capture screenshots across viewports (mobile/tablet/
   desktop) and key states; save them under ~/.agent/diagrams/.
Inputs: plan <PLAN_PATH>, design brief <BRIEF_PATH>, cleanup+review summaries <PASTE>.
Return ONLY: (1) the HTML path, (2) the screenshot paths, (3) a concise summary —
what was completed, remaining issues, deltas from the plan and the design brief.
Do NOT paste the HTML, CSS, or file contents back.
```

⛔ **Gate.** Open the HTML and the screenshots for the user. The user approves: code is sound, the UI looks right, states/responsive hold, mental model intact.
