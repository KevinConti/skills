# Draft the design brief — shape sub-agent *(delegated)*

`impeccable shape`'s discovery interview is a *live* interaction — a headless sub-agent can't run it, and running it inline both bloats your context and splits the question channel (chat here, then the UI in the contract step). So **don't run `shape`.** Instead, delegate a sub-agent to **draft** the brief using impeccable's design judgment and surface what still needs deciding. The open design questions then get asked in the UI by `interactive-plan` (next step), so every question lives in one channel and the brief lives on disk where compaction can't lose it.

Spawn a sub-agent (`general-purpose`, foreground):

```
Draft a design brief for <ITEM>, applying impeccable's design judgment. Do NOT
run `impeccable shape` — its discovery interview needs a live user, which you
don't have. You are drafting, not interviewing.

Read and follow these first (under ~/.claude/skills/impeccable/):
- reference/shape.md — the brief structure + the discovery question set.
- SKILL.md — the design laws (color strategy, scene-sentence theming, layout/
  motion, the anti-slop + category-reflex checks), and the register reference it
  points to: reference/brand.md (marketing / landing / content surfaces) or
  reference/product.md (app UI / dashboards / tools). Pick the register the way
  impeccable would, from the feature.
- the project's PRODUCT.md / DESIGN.md if present (impeccable's load-context.mjs
  locates them), and the realism floor from the backend-reality step: <FLOOR>.

Produce two things:
1. A DRAFT design brief in impeccable's 10-section format (Feature Summary;
   Primary User Action; Design Direction — color strategy + scene-sentence theme
   + 2–3 named anchor references; Scope; Layout Strategy; Key States; Interaction
   Model; Content Requirements; Recommended References; Open Questions). Decide
   everything PRODUCT.md/DESIGN.md + the prompt already pin down; leave genuinely
   open calls open. Write the brief to a file under ~/.agent/ and report its path.
2. The OPEN design questions — the decisions you could NOT confidently make
   without the user (typically the Design-Direction forks, an ambiguous key
   state, or an interaction choice). For each: a one-line question, a recommended
   answer, and 2–4 options where the choice is discrete. Assert-then-confirm —
   lead with the recommendation. These get asked in interactive-plan's UI next.

Return ONLY: (1) the brief file path, and (2) the open-questions list — never the
full brief text.
```

This is a **draft, not a confirmed brief** — the user weighs in on the open questions via `interactive-plan` (next step), and reviews the whole plan at plan-review. Hold the **brief path + the open-questions list** for the contract step.
