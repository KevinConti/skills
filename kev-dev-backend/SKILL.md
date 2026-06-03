---
name: kev-dev-backend
description: An end-to-end backend development pipeline orchestrator. Takes one backend work item — a backlog id/path to a markdown task, or a freeform description — and drives it through the full structured workflow — plan with interactive-plan → validate with plan-review → write a handoff brief → implement → simplify/code-review → security-review → diff-review, honoring a human gate at each review and stopping before commit. To stay lean, the orchestrator delegates every context-heavy step — implementation, both visual-explainer reviews, and the cleanup/security passes — to focused sub-agents that hand back only a summary or an artifact path. Use whenever the user invokes /kev-dev-backend, or asks to take a backend task through this dev pipeline / planning-to-shipping process end-to-end. Frontend work has a separate flow. Drive the sub-skills in the fixed order below so no step is skipped and plan-review risks survive into implementation.
argument-hint: "<backlog item id/path or description of the work>"
---

<what-to-do>

You are the **orchestrator** for this backend development pipeline. You take one work item from a backlog task to a reviewed, ship-ready diff by invoking a fixed sequence of sub-skills, pausing at every human gate, and keeping your own context lean. You do the orchestration and the gates; sub-skills and delegated sub-agents do the heavy work.

**Read this skill progressively.** This file is a router. The standing rules and the concepts below stay resident, but **each step's full instructions live in its own doc under `tasks/`** — open a step's doc **only when you reach that step, never all upfront.** Reading them eagerly defeats the purpose: it refloods the context this pipeline works to keep lean and splits your attention across steps you aren't on yet. The pipeline table links each step to its doc; load one, do the step, move on.

Three standing rules:

1. **Honor every ⛔ gate.** The gates are where the user stays an effective collaborator and keeps their mental model of the code. Never skip one to "save time" — the gates *are* the value.
2. **Never commit or push.** The pipeline ends at diff-review approval and hands back. Committing to `main` is the irreversible step and it's the user's to take (see [Handback](tasks/handback.md)).
3. **Keep your own context lean by delegating the heavy steps, not by clearing.** You are a long-lived orchestrator: anything read or generated in *your* context stays resident for the whole run. So push the context-heavy steps into sub-agents that hand back only a summary or an artifact path — implementation (step 4), both visual-explainer reviews (steps 2 and 7), and cleanup/security (step 6). Implementation delegates for *focus*; the review/cleanup skills delegate to *quarantine* their bulky skill-loading and large HTML output from your window. Keep inline only the cheap steps, the human gates, and the one interactive step (`interactive-plan`). See [Why delegate](#context-hygiene--why-delegate-instead-of-clear) and [the delegation contract](#delegating-the-review-and-cleanup-steps).

</what-to-do>

<supporting-info>

## The pipeline

Run these in order. **Open each step's linked doc when you reach it — not before.**

| Step | Mode | In one line | Full instructions |
|---|---|---|---|
| Preflight | — | Confirm the required skills are installed; STOP if any are missing | [tasks/preflight.md](tasks/preflight.md) |
| 0. Resolve | inline | Locate and confirm the work item | [tasks/resolve.md](tasks/resolve.md) |
| 1. Plan — `interactive-plan` | inline | Planning session → `CONTEXT.md`/ADRs + a concrete plan artifact | [tasks/plan.md](tasks/plan.md) |
| 2. Validate — `plan-review` | delegated ⛔ | Visual plan review; hold the findings for handoff | [tasks/plan-review.md](tasks/plan-review.md) |
| 3. Brief — `handoff` | inline | Implementation primer; fold in the plan-review findings | [tasks/handoff.md](tasks/handoff.md) |
| 4. Implement | delegated | Build from the handoff brief | [tasks/implement.md](tasks/implement.md) |
| 5. Checkpoint | inline ⛔ | Review the implementation summary before cleanup | [tasks/checkpoint.md](tasks/checkpoint.md) |
| 6. Cleanup | delegated | `simplify`/`code-review`, then `security-review` (sequential) | [tasks/cleanup.md](tasks/cleanup.md) |
| 7. Review — `diff-review` | delegated ⛔ | Visual diff review of the finished change | [tasks/diff-review.md](tasks/diff-review.md) |
| 8. Handback | inline | Stop before commit; hand back ready-to-ship | [tasks/handback.md](tasks/handback.md) |

## Context hygiene — why delegate instead of `/clear`

This pipeline deliberately separates planning from implementation so implementation stays focused and out of the "dumb zone." The classic way to get that boundary is to `/clear` and start a fresh session primed by the handoff doc.

Delegating to a sub-agent (the implement step) gives a *better* boundary in both directions:

- **Implementation stays clean** — the sub-agent sees only the handoff brief, never the long planning transcript. (This is the handoff doc's original "clear context" purpose, achieved for free.)
- **The orchestrator stays clean** — you get back only the sub-agent's *summary*, not every edit and tool call. That matters because the ship phase (reasoning about the diff) needs a clear head of its own, which `/clear` never gave you.

So: do **not** collapse this into one flat context, and do not ask the user to `/clear` mid-pipeline. The sub-agent boundary is the mechanism. The `handoff` step still earns its place — it's the brief that primes the sub-agent, and the durable record of plan-review risks.

## Delegating the review and cleanup steps

Implementation isn't the only context-heavy step. The two `visual-explainer` reviews (steps 2 and 7) and the cleanup/security passes (step 6) are read- and generate-heavy, and what you actually need from each is small: a findings list, a changed-files summary, an artifact path. Run them inline and they wreck your context — `visual-explainer` alone loads its full `SKILL.md` + `css-patterns.md` reference (well over two thousand lines) and writes a 30–40K-character HTML file that then sits in your window twice (the write *and* its result). That single pattern is what forces mid-pipeline auto-compaction before you even reach the ship phase.

So delegate them, with one shared **contract** (the delegated step docs point back here):

- **`subagent_type: general-purpose`, foreground** (you need the result before continuing); **no worktree isolation** for the cleanup pass (it edits the tree), so its changes land on the real diff.
- The sub-agent runs the skill in *its* context and **returns only a compact result** — a findings/summary text, plus (for the visual reviews) the **absolute path to the generated HTML**. It must **not** paste the HTML, CSS, or full file contents back.
- You open the HTML for the user at the gate and present the findings. The heavy reference material and the HTML body never enter your context.

This preserves every gate exactly — the user still sees the same diagrams and findings — while keeping your window lean enough that a normally-sized item never needs to compact. (Inline steps stay inline for good reasons: `interactive-plan` is live human collaboration with a chat escape hatch that only the top-level session receives; `handoff` is cheap because you already hold the plan context and only need to capture the doc's path; the gates and handback *are* your job.)

## The one tradeoff: implementation is unsupervised

A sub-agent is headless — the user can't course-correct it mid-run. The front-loaded planning is what de-risks this, and two things contain it: the **escalation rule** in the sub-agent prompt (halt and ask rather than guess), and the **light checkpoint** (a human gate right after implementation). That's far less than full supervision, but it's a real fail-fast valve. If a task is too exploratory to brief well, that's a signal not to use this skill for it (see below).

## When NOT to use this skill

- **A throwaway spike or a one-line fix** — the full planning ceremony is overkill. Just do the work.
- **Design exploration with no implementation target yet** — use `interactive-plan` (or chat-only `grill-with-docs`) directly; come back to `kev-dev-backend` once there's something to build.
- **Work you want to implement hands-on** — the delegation is headless. Run the steps manually instead.

## Running just the ship half

If the work is already implemented and only the back half is needed, skip to **step 6** and run cleanup → review → handback against the existing diff.

</supporting-info>
