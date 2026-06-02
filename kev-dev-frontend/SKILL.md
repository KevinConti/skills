---
name: kev-dev-frontend
description: An end-to-end frontend development pipeline orchestrator (opinionated; assumes the interactive-plan, impeccable, handoff, and visual-explainer skills). Takes one frontend work item — a backlog id/path or a freeform description — and drives it through a design-led structured workflow — read the backend reality → shape the UI with impeccable → commit a data contract shaped to that UI with interactive-plan → plan-review → handoff → implement → cleanup (simplify/code-review + impeccable polish) → security-review → diff-review — honoring a human gate at each review and stopping before commit. To stay lean on a token-heavy pipeline, the orchestrator delegates every context-heavy step — the backend read, both visual-explainer reviews, implementation, and the cleanup/security/polish passes — to focused sub-agents that hand back only a summary or an artifact path; only the interactive steps (impeccable shape, interactive-plan) and the gates stay in the main loop. Use whenever the user invokes /kev-dev-frontend or asks to take a frontend, UI, or UX task through this dev pipeline end-to-end. Backend-only work uses kev-dev-backend. Drive the sub-skills in the fixed order below so no step is skipped, the UI shape leads the data contract, and plan-review risks survive into implementation.
argument-hint: "<frontend work item id/path or description>"
---

<what-to-do>

You are the **orchestrator** for this frontend development pipeline. You take one UI/UX work item from a backlog task to a reviewed, ship-ready diff by invoking a fixed sequence of sub-skills, pausing at every human gate, and keeping your own context lean. You do the orchestration and the gates; sub-skills and delegated sub-agents do the heavy work. The defining difference from the backend pipeline: a frontend story has an extra **design beat**, and **the UI shape leads the data contract** — not the other way round.

**Read this skill progressively.** This file is a router. The standing rules and the concepts below stay resident, but **each step's full instructions live in its own doc under `tasks/`** — open a step's doc **only when you reach that step, never all upfront.** Reading them eagerly defeats the purpose: it refloods the context this pipeline works to keep lean and splits your attention across steps you aren't on yet. The pipeline table links each step to its doc; load one, do the step, move on.

Four standing rules:

1. **Honor every ⛔ gate.** The gates are where the user stays an effective collaborator and keeps their mental model of the code and the UI. Never skip one to "save time" — the gates *are* the value.
2. **Never commit or push.** The pipeline ends at diff-review approval and hands back. Shipping to `main` is the user's to do.
3. **Keep your own context lean by delegating the heavy steps.** You are a long-lived orchestrator: anything read or generated in *your* context stays resident for the whole run, and this pipeline is token-heavy enough to bloat fast. So push every context-heavy step into a sub-agent that hands back only a summary or an artifact path — the backend read (step 1), both visual-explainer reviews (steps 4 and 9), implementation (step 6), and the cleanup/security/polish passes (step 8). Keep inline only the cheap steps, the human gates, and the two **interactive** steps that need a live human — `impeccable shape` (step 2) and `interactive-plan` (step 3). See [Delegating the heavy steps](#delegating-the-heavy-steps).
4. **UI leads, contract follows.** This workflow is user-first — design the best user experience the backend can realistically support, then shape the contract the UI consumes to serve it rather than forcing the UI to conform to a backend-convenient contract. Don't let a premature contract shape the UX. See [Resolving the chicken-and-egg](#resolving-the-chicken-and-egg-why-this-order).

</what-to-do>

<supporting-info>

## The pipeline

Run these in order. **Open each step's linked doc when you reach it — not before.**

| Step | Mode | In one line | Full instructions |
|---|---|---|---|
| Preflight | — | Confirm the required skills are installed; STOP if any are missing | [tasks/preflight.md](tasks/preflight.md) |
| 0. Resolve | inline | Locate and confirm the work item | [tasks/resolve.md](tasks/resolve.md) |
| 1. Backend-reality read | delegated | Realism floor + contract regime (a/b/c) | [tasks/backend-reality.md](tasks/backend-reality.md) |
| 2. Shape — `impeccable shape` | inline ⛔ | Discovery interview → confirmed design brief; UI leads | [tasks/shape.md](tasks/shape.md) |
| 3. Commit contract — `interactive-plan` | inline ⛔ | Contract shaped to the UI; regime branch + backend backlog item | [tasks/contract.md](tasks/contract.md) |
| 4. Validate — `plan-review` | delegated ⛔ | Visual plan review; hold the findings for handoff | [tasks/plan-review.md](tasks/plan-review.md) |
| 5. Brief — `handoff` | inline | Context brief; fold in the plan-review hang-overs | [tasks/handoff.md](tasks/handoff.md) |
| 6a. Implement | delegated | Build the UI + wiring from the brief | [tasks/implement.md](tasks/implement.md) |
| 6b. Test coverage | delegated | Bring tests up to the codebase's bar | [tasks/test-coverage.md](tasks/test-coverage.md) |
| 7. Checkpoint | inline ⛔ | Review impl + tests + screenshot before cleanup | [tasks/checkpoint.md](tasks/checkpoint.md) |
| 8. Cleanup + review | delegated | polish → cleanup → security → audit, in order | [tasks/cleanup-review.md](tasks/cleanup-review.md) |
| 9. Review — `diff-review` + visual | delegated ⛔ | Visual diff review + rendered-UI screenshots | [tasks/diff-review.md](tasks/diff-review.md) |
| 10. Handback | inline | Stop before commit; surface backend deliverables | [tasks/handback.md](tasks/handback.md) |

## Resolving the chicken-and-egg (why this order)

"Don't wire before the UI shape" and "don't fix the UX before the *possible* contract" only conflict if "contract" is one thing. It's two: the **envelope** (what the backend can realistically support — step 1's floor) and the **committed contract** (the exact shape the UI consumes — step 3). Different fidelities, so they sequence cleanly: floor (cheap) → UI shape (step 2) → committed contract pinned to the UI (step 3). The **design brief is the bridge** — the UI's data needs *become* the contract spec.

## Delegating the heavy steps

This pipeline is token-heavy: the two `visual-explainer` reviews each load the full visual-explainer reference (well over two thousand lines) and write a 30–40K-character HTML file; the backend read, implementation, and cleanup/security passes each churn through large amounts of source. Run any of them inline and it lodges in your window for the rest of the run — that single pattern is what forces mid-pipeline auto-compaction. So delegate them all, under one shared **contract** (the delegated step docs point back here):

- **`subagent_type: general-purpose`, foreground** (you need the result before continuing); **no worktree isolation** for the steps that mutate the tree (implementation and test-writing in step 6, and the `impeccable polish` / `simplify` passes in step 8), so changes land on the real diff.
- The sub-agent runs the skill(s) in *its* context and **returns only a compact result** — a findings/summary text, plus (for the visual reviews) the **absolute paths to the generated HTML and screenshots**. It must **not** paste HTML, CSS, or full file contents back.
- You open the artifacts for the user at the gate and present the findings. The heavy reference material and HTML body never enter your context.

This preserves every gate exactly — the user still sees the same diagrams, screenshots, and findings — while keeping your window lean. **Inline steps stay inline for good reasons:** `impeccable shape` and `interactive-plan` are live human collaboration (the user answers in a UI/chat that only the top-level session receives); `handoff` is cheap because you already hold the plan context and only need the doc's path; the gates and handback *are* your job.

## The one tradeoff: implementation is unsupervised

A sub-agent is headless — the user can't course-correct it mid-run. The front-loaded design + planning is what de-risks this, and two things contain it: the **escalation rule** in the sub-agent prompt (halt and ask rather than guess), and the **step-7 checkpoint** (a human gate right after implementation). For frontend, the checkpoint's screenshot and the step-9 visual pass recover the designer's-eye review you'd otherwise want during the build.

## When NOT to use this skill

- **Backend-only work** — use `kev-dev-backend`.
- A throwaway spike or one-off tweak — the full ceremony is overkill.
- Pure design exploration with no build target — use `impeccable shape` (or `craft`) directly; come back once there's something to build.
- Work you want to implement hands-on — the delegation is headless.

## Running just part of it

If the work is already planned, skip to **step 6**. If it's already built and you want only the back half, skip to **step 8** and run cleanup → review → handback against the existing diff. (Block-regime stories resume at step 6 once the backend endpoint lands.)

</supporting-info>
