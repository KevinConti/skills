---
name: kev-dev-backend
description: Kevin's end-to-end backend development pipeline orchestrator. Takes one backend work item — a backlog id/path to a markdown task, or a freeform description — and drives it through the full structured workflow — plan with interactive-plan → validate with plan-review → write a handoff brief → implement → simplify/code-review → security-review → diff-review, honoring a human gate at each review and stopping before commit. To stay lean, the orchestrator delegates every context-heavy step — implementation, both visual-explainer reviews, and the cleanup/security passes — to focused sub-agents that hand back only a summary or an artifact path. Use whenever Kevin invokes /kev-dev-backend, or asks to take a backend task through his dev pipeline / planning-to-shipping process end-to-end. Frontend work has a separate flow. Drive the sub-skills in the fixed order below so no step is skipped and plan-review risks survive into implementation.
argument-hint: "<backlog item id/path or description of the work>"
---

<what-to-do>

You are the **orchestrator** for Kevin's development pipeline. You take one work item from a backlog task to a reviewed, ship-ready diff by invoking a fixed sequence of sub-skills, pausing at every human gate, and keeping each phase's context clean. You do the orchestration and the gates; the sub-skills and a delegated implementation sub-agent do the work.

Three standing rules:

1. **Honor every ⛔ gate.** The gates are where Kevin stays an effective collaborator and keeps his mental model of the code. Never skip one to "save time" — the gates *are* the value.
2. **Never commit or push.** The pipeline ends at diff-review approval and hands back. Committing to `main` is the irreversible step and it's Kevin's to take (see [Handback](#handback--stop-before-commit)).
3. **Keep your own context clean by delegating the heavy steps, not by clearing.** You are a long-lived orchestrator: anything read or generated in *your* context stays resident for the whole run. So push the context-heavy steps into sub-agents that hand back only a summary or an artifact path — implementation (step 4), both visual-explainer reviews (steps 2 and 7), and cleanup/security (step 6). Implementation delegates for *focus*; the review/cleanup skills delegate to *quarantine* their bulky skill-loading and large HTML output from your window. Keep inline only the cheap steps, the human gates, and the one interactive step (`interactive-plan`). See [Why delegate](#context-hygiene--why-delegate-instead-of-clear) and [the review-sub-agent contract](#delegating-the-review-and-cleanup-steps).

</what-to-do>

<supporting-info>

## The pipeline

Run these in order. Each step says what to invoke, what it consumes/produces, and whether it ends in a gate.

### Preflight — confirm required skills

Claude Code has no skill-level dependency manifest, so nothing guarantees the skills this pipeline calls are present — and built-ins can even be missing in a session running a different Claude Code build. Before step 1, confirm each of these is available in the session. If any is absent, STOP and tell Kevin which ones and where they come from — don't start a pipeline that will die partway through:

- `interactive-plan` — personal skill (in `kevin/`)
- `handoff` — personal skill (`~/.claude/skills`)
- `visual-explainer:plan-review` and `visual-explainer:diff-review` — visual-explainer plugin (install the `visual-explainer` plugin if missing)
- `simplify` **or** `code-review`, plus `security-review` — Claude Code built-ins; update Claude Code if missing. (Recent builds renamed `simplify` → `code-review`, so *either* satisfies this check — step 6 uses whichever is present.)

### 0. Resolve the work item

The argument is either a backlog **id/path** or a **freeform description**.

- If it looks like a path or id, locate the backlog markdown in the repo (try the path as-given, then `backlog/`, `docs/`, `tasks/`, or an issue tracker). Read it.
- If it's freeform, treat the text as the work description.

Restate the scope in a sentence or two and confirm you're on the right item before starting. This is a light check, not a gate.

### 1. Plan — `interactive-plan`

Invoke `interactive-plan` to run the planning session — Kevin answers in the live browser UI (chat is the escape hatch), the skill presents a recommended answer per question, and it updates the project's `CONTEXT.md` glossary and ADRs inline as decisions crystallize, refining the work toward implementation-ready.

Before moving on, make sure the plan exists as a **concrete artifact** — the refined backlog/plan doc plus `CONTEXT.md` and any ADRs — because that's what `plan-review` consumes next.

### 2. Validate — `visual-explainer:plan-review` ⛔ (delegated)

`visual-explainer:plan-review` produces the visual review (the diagrams Kevin uses to hold his mental model of the codebase) and surfaces the gaps the grill missed. **Do not invoke it inline** — it loads the full visual-explainer reference (hundreds of lines of `SKILL.md` + `css-patterns.md`) and emits a large HTML document, all of which would lodge in your context for the rest of the run. Delegate it to a review sub-agent (see [the review-sub-agent contract](#delegating-the-review-and-cleanup-steps)).

Spawn one sub-agent with the Agent tool — `subagent_type: general-purpose`, foreground (you need its result before continuing) — with this prompt shape:

```
Run the `visual-explainer:plan-review` skill against the plan for <ITEM>.
- Plan artifact: <PLAN_PATH>. Also read: <CONTEXT.md path>, <ADR paths>.
- Produce the visual plan-review HTML and save it under ~/.agent/diagrams/.

Return ONLY: (1) the absolute path to the HTML file, and (2) a concise text
list of the findings/gaps it surfaced — the risks, plan deltas, and anything
the plan does not yet cover. Do NOT paste the HTML or its CSS back.
```

⛔ **Gate.** Open the returned HTML for Kevin and present the sub-agent's findings list. Usually the plan's mitigations are sufficient and there's nothing to add. Occasionally a real gap needs a non-trivial change — if so, amend the plan (a focused follow-up grill question, or a direct edit to the plan doc), and if the change is substantial, **re-run plan-review** (spawn a fresh sub-agent). **Hold the findings** — they must reach the handoff doc in step 3. Do not proceed to handoff until Kevin is satisfied the plan is sound.

### 3. Brief — `handoff`

Invoke `handoff` with the focus "implement \<item\>". This produces the implementation primer.

Critically: ensure the handoff doc captures **every risk and open item plan-review surfaced**, plus links to the plan, `CONTEXT.md`, ADRs, and the relevant code. These must reach implementation — the handoff is the only thing the sub-agent will see. **Capture the handoff doc's path**; it becomes the sub-agent's brief in the next step.

### 4. Implement — delegated sub-agent

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

### 5. Checkpoint ⛔ (light)

Present the sub-agent's summary — what it implemented, what it tested, deviations from the plan, anything it escalated.

⛔ **Gate.** Kevin approves proceeding to cleanup, sends it back for fixes (re-delegate with the correction), or takes over manually. This is the fail-fast valve that stands in for the supervision you'd otherwise have *during* implementation — keep it light, because diff-review is the substantive review. If the sub-agent escalated a question, resolve it with Kevin here before continuing.

### 6. Cleanup — `simplify`/`code-review`, then `security-review` (delegated)

Both passes are read-heavy and what you need back from each is small, so delegate each to its own sub-agent (see [the review-sub-agent contract](#delegating-the-review-and-cleanup-steps)). Run them in **two sequential sub-agents, never concurrently** — cleanup mutates the very files `security-review` reads, so cleanup must fully finish first.

**6a — Cleanup sub-agent** (`general-purpose`, foreground, **no worktree isolation** — it edits the real tree). Use whichever cleanup skill preflight found:

- `simplify` — applies reuse/simplification/efficiency fixes directly (quality only). Prefer it if present.
- `code-review` — the renamed successor in recent builds. Pass `--fix` so it actually applies the cleanups (without it, it only reports). It also hunts correctness bugs, so expect bug findings alongside the cleanups.

```
Run `<simplify | code-review --fix>` on the current working tree to clean up
the BL-<NNNN> changes. Apply the fixes directly to the files.
Return ONLY a concise summary: what you changed (by file/area) and any bugs
found. Do not paste full file contents or diffs back.
```

**6b — Security sub-agent** (`general-purpose`, foreground), spawned **only after 6a returns**:

```
Run the `security-review` skill on the pending changes on this branch.
Return ONLY the findings: each issue with file/location, severity, and a
one-line description. Do not paste full file contents back.
```

Hold both summaries. If cleanup changed anything material, note it so it isn't a surprise in diff-review; carry any security findings into the diff-review gate.

### 7. Review — `visual-explainer:diff-review` ⛔ (delegated)

Same as step 2: **do not invoke inline.** `visual-explainer:diff-review` reloads the full visual-explainer reference and emits another large HTML document — running it in your context is what would re-flood the ship phase you worked to keep clean. Delegate it (see [the review-sub-agent contract](#delegating-the-review-and-cleanup-steps)).

Spawn one sub-agent with the Agent tool — `subagent_type: general-purpose`, foreground — with this prompt shape:

```
Run the `visual-explainer:diff-review` skill on the pending changes for <ITEM>.
- Plan artifact: <PLAN_PATH>; cleanup + security summaries from step 6: <PASTE>.
- Produce the visual diff-review HTML and save it under ~/.agent/diagrams/.

Return ONLY: (1) the absolute path to the HTML file, and (2) a concise text
summary — what was completed, remaining issues, and deltas from the plan.
Do NOT paste the HTML or its CSS back.
```

⛔ **Gate.** Open the returned HTML for Kevin and present the summary. Kevin reviews and approves.

### 8. Handback — stop before commit

On approval, **stop**. Do not commit or push. Summarize what's ready to ship and, if useful, draft a commit message Kevin can paste. The push to `main` is his to make.

---

## Context hygiene — why delegate instead of `/clear`

Kevin's pipeline deliberately separates planning from implementation so implementation stays focused and out of the "dumb zone." The classic way to get that boundary is to `/clear` and start a fresh session primed by the handoff doc.

Delegating to a sub-agent (step 4) gives a *better* boundary in both directions:

- **Implementation stays clean** — the sub-agent sees only the handoff brief, never the long planning transcript. (This is the handoff doc's original "clear context" purpose, achieved for free.)
- **The orchestrator stays clean** — you get back only the sub-agent's *summary*, not every edit and tool call. That matters because the ship phase (reasoning about the diff) needs a clear head of its own, which `/clear` never gave you.

So: do **not** collapse this into one flat context, and do not ask Kevin to `/clear` mid-pipeline. The sub-agent boundary is the mechanism. The `handoff` step still earns its place — it's the brief that primes the sub-agent, and the durable record of plan-review risks.

## Delegating the review and cleanup steps

Implementation isn't the only context-heavy step. The two `visual-explainer` reviews (steps 2 and 7) and the cleanup/security passes (step 6) are read- and generate-heavy, and what you actually need from each is small: a findings list, a changed-files summary, an artifact path. Run them inline and they wreck your context — `visual-explainer` alone loads its full `SKILL.md` + `css-patterns.md` reference (well over two thousand lines) and writes a 30–40K-character HTML file that then sits in your window twice (the write *and* its result). That single pattern is what forces mid-pipeline auto-compaction before you even reach the ship phase.

So delegate them, with one shared **contract**:

- **`subagent_type: general-purpose`, foreground** (you need the result before continuing); **no worktree isolation** for the step that mutates the tree (6a), so its changes land on the real diff.
- The sub-agent runs the skill in *its* context and **returns only a compact result** — a findings/summary text, plus (for the visual reviews) the **absolute path to the generated HTML**. It must **not** paste the HTML, CSS, or full file contents back.
- You open the HTML for Kevin at the gate and present the findings. The heavy reference material and the HTML body never enter your context.

This preserves every gate exactly — Kevin still sees the same diagrams and findings — while keeping your window lean enough that a normally-sized item never needs to compact. (Inline steps stay inline for good reasons: `interactive-plan` is live human collaboration with a chat escape hatch that only the top-level session receives; `handoff` is cheap because you already hold the plan context and only need to capture the doc's path; the gates and handback *are* your job.)

## The one tradeoff: implementation is unsupervised

A sub-agent is headless — Kevin can't course-correct it mid-run. His front-loaded planning is what de-risks this, and two things contain it: the **escalation rule** in the sub-agent prompt (halt and ask rather than guess), and the **light checkpoint** in step 5 (a human gate right after implementation). That's far less than full supervision, but it's a real fail-fast valve. If a task is too exploratory to brief well, that's a signal not to use this skill for it (see below).

## When NOT to use this skill

- **A throwaway spike or a one-line fix** — the full planning ceremony is overkill. Just do the work.
- **Design exploration with no implementation target yet** — use `interactive-plan` (or chat-only `grill-with-docs`) directly; come back to `kev-dev-backend` once there's something to build.
- **Work you want to implement hands-on** — the delegation is headless. Run the steps manually instead.

## Running just the ship half

If the work is already implemented and Kevin wants only the back half, skip to **step 6** and run cleanup → review → handback against the existing diff.

</supporting-info>
