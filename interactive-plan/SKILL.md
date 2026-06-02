---
name: interactive-plan
description: Interactive planning session where the user answers questions and steers the plan directly in a live browser UI instead of in chat, while the agent updates the project's CONTEXT.md glossary and ADRs inline as decisions crystallize. The agent writes question cards as JSON, a bidirectional SPA renders them and POSTs the user's choices to a local broker, and a file watcher wakes the agent to react. Use for a GenUI-style living-artifact planning loop; for the chat-reply flow use visual-grill-with-docs.
---

<what-to-do>

Run a planning interview where the user's **primary input is the browser UI**, not chat. You write a question card (JSON); a bidirectional SPA renders it and lets the user click an option, type their own answer, or skip — POSTing that intent to a local broker. A background watcher wakes you; you react by writing the next card.

Ask one question at a time. Have a recommended answer ready. If a question can be answered by reading the codebase, do that instead of asking.

Crucially, the grilling produces a **durable deliverable**, not just a transcript: as decisions crystallize, update the project's `CONTEXT.md` (glossary) and ADRs inline. The project docs are the source of truth; the session JSON is a snapshot.

This is a separate skill from `visual-grill-with-docs` — different session root (`~/.agent/interactive-plan/`), different SPA, no shared state — but the doc output is the same. The difference is the bidirectional UI: the user answers in the page, not in chat.

</what-to-do>

<supporting-info>

## How the loop works

```
agent writes q-NN.json + session.json
        │
        ▼
   SPA polls session.json (750ms) ── renders the card
        │
   user clicks / types / skips
        │
        ▼
   POST /intent ──► broker.py appends to inbox.ndjson
        │
        ▼
   session.sh wait (background) sees seq > cursor, prints it, EXITS
        │
        ▼
   harness re-invokes the agent with the intent  ──► back to top
```

The watcher idles at the OS level — **zero tokens** while waiting. You are invoked once per *intent*, never per keystroke. Read [INTENT-FORMAT.md](./INTENT-FORMAT.md) once at session start; it is the full contract.

## Session start (before Q1)

1. **Survey the project docs.** Look for `CONTEXT.md`, `CONTEXT-MAP.md`, and `docs/adr/`; note their paths (you'll keep them in sync). A `CONTEXT-MAP.md` means a multi-context repo — work out which context the topic belongs to. See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).
2. Derive a kebab-case slug from the user's opening sentence (2–4 words).
3. Start the server (path resolves to wherever the skill is installed):

   ```bash
   bash ~/.claude/skills/interactive-plan/scripts/session.sh start <slug>
   ```

   This creates `~/.agent/interactive-plan/<slug>/`, copies the SPA, seeds `session.json` + empty `inbox.ndjson` + `inbox.cursor=0`, starts `broker.py`, and opens the browser.
4. Set `session.json` → `contextPath` (the project's `CONTEXT.md` path, or null), write `q-01.json`, then set `currentQuestion: 1` and append `{id:1, title, status:"pending"}` to `questions`.
5. **Arm the watcher** — run this with the Bash tool and `run_in_background: true`:

   ```bash
   bash ~/.claude/skills/interactive-plan/scripts/session.sh wait <slug>
   ```

6. Send ONE short chat line: `Q1 is open in your browser — answer there.` Then end your turn. The background watcher will re-invoke you when the user acts.

## On each wake (the watcher exited)

1. The tool result contains the new intent line(s). **Drain authoritatively anyway:** read `inbox.ndjson` and take every line with `seq > inbox.cursor`.
2. Coalesce: for `answer`/`freeform` on the same `qid`, last write wins. Use the client `id` to skip any intent you already processed (idempotency).
3. React per `kind` (see table in [INTENT-FORMAT.md](./INTENT-FORMAT.md)):
   a. Resolve or park the question in `session.json` with a short `answer`.
   b. **Capture the decision into docs** — this is the deliverable, see "Capturing decisions into docs" below. If the answer pins or changes domain language, update the project's `CONTEXT.md` *now* and add the term to `session.json` → `glossary`. If it clears the ADR bar, write the ADR to `docs/adr/` and append to `session.json` → `adrs`.
   c. Write the next `q-NN.json` and set `currentQuestion`. If the answer conflicts with existing `CONTEXT.md`/an ADR, surface it on the relevant option's `conflict` field or in `context.paragraphs`. **If that was the last question** (nothing left to ask), do NOT write a new card — go straight to **Wrap up**, which closes the viewer out. Leaving it here strands the viewer on "Sent your answer".
4. **Advance the cursor:** write the max processed `seq` to `inbox.cursor`.
5. **Re-arm** `session.sh wait <slug>` in the background again.
6. Send one short chat line. When docs changed, say so: `Got it: per-merchant. CONTEXT.md updated. Q2 is open.` Then end the turn.

If the watcher printed `{"timeout": true}`, no one acted within the window — just re-arm it (optionally check in with the user).

## Capturing decisions into docs

The grilling exists to produce a durable record, not a transcript. As decisions land, keep the project docs current — don't batch to the end. Formats: [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md), [ADR-FORMAT.md](./ADR-FORMAT.md).

- **Update CONTEXT.md inline.** When a term resolves, write it to the project's `CONTEXT.md` immediately and add it to `session.json` → `glossary` (the session delta — don't dump the whole file). `CONTEXT.md` is a glossary: terms, definitions, relationships, flagged ambiguities. No specs, no implementation detail.
- **Challenge against the glossary.** If the user's language conflicts with an existing `CONTEXT.md` definition, flag it — quote the current definition in `context`, and carry the clash on the conflicting option's `conflict` field. Resolve before moving on.
- **Sharpen fuzzy language.** When a term is vague or overloaded, make the canonical-term choice the question. (Until the open-ended card lands — see Roadmap — frame the discrete candidates as a normal options array.)
- **Cross-reference with code.** When the user states how something works, check whether the code agrees. On a contradiction, use a `code` visual with the disputed line and frame the options as "which is right?"
- **Offer ADRs sparingly.** Create an ADR only when **all three** hold: hard to reverse, surprising without context, and the result of a real trade-off. If any is missing, skip it. When created, write `docs/adr/NNNN-*.md` and add it to `session.json` → `adrs`.
- **File structure.** Single-context repos: one `/CONTEXT.md`. Multi-context: a `CONTEXT-MAP.md` points to per-context files. Create files lazily — only when there's a first term or ADR to write.
- **The viewer lights up your glossary.** Any term in `session.json` → `glossary` is auto-linked in the prose and reveals its definition on click. So keep the delta current — and when a card *references* an existing `CONTEXT.md` term (even one defined in a past session), add it to the delta so the viewer lights it up too.

## Authoring option cards

Each option is a **compact row** (letter, title, one-line summary, recommended badge) in the Decision pane. Hovering or focusing a row reveals that option's detail in the **Evidence pane** on the left, so fill `detail`, `downstream`, and (on the recommended option) `rationale`; add a `miniVisual` when a 3–5 line snippet or tiny diagram makes the option concrete; set `conflict` when an option clashes with an earlier decision. Keep the row skimmable; the Evidence pane is where the trade-off lives. Committing is the explicit **Choose** button on the row, so reading detail never submits. Full field table in [INTENT-FORMAT.md](./INTENT-FORMAT.md).

The layout is **fold-locked**: a typical card (context + visual + question + options) fits one viewport, and only genuinely verbose context/visuals scroll, within the Evidence pane. So keep context to a few sentences and visuals modestly sized.

## Health check

Before writing a new card after a long gap, run `session.sh status <slug>`. Non-zero exit means the broker died — re-run `start` (idempotent) and ask the user to refresh the tab.

## Chat is the escape hatch, not the main channel

The user *can* still answer in chat — treat a chat reply exactly like a `freeform` intent. But the point of this skill is the UI. Keep chat lines to one sentence and never restate what the card already shows.

## Wrap up

The viewer holds an optimistic "Sent your answer" state after every answer and only clears it when the next card arrives — so **you must close the session out explicitly**. Never just stop after the last answer; that strands the viewer until it goes stale.

When planning is done (user says so, or you've covered the tree):

1. **Reconcile the docs.** Ensure the project's actual `CONTEXT.md` and any ADRs match `session.json`'s `glossary`/`adrs` — the JSON is a snapshot; the project docs are the source of truth.
2. Mark every question `resolved`/`parked`, and set `session.json` → `"status": "complete"`. This flips the viewer to a "Planning complete" recap. (The viewer also treats *all questions resolved/parked* as complete, so marking the final answer resolved is the floor; `status` is the explicit signal — set both.)
3. Summarize in chat **which project files changed** plus the resolved answers, and optionally `session.sh stop <slug>` to free the port. The JSON files persist for review.

## Reading list

- [INTENT-FORMAT.md](./INTENT-FORMAT.md) — the full inbox/outbox + cursor contract, JSON schemas, security note.
- [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) — glossary format for the project's `CONTEXT.md` (single vs multi-context, lazy creation).
- [ADR-FORMAT.md](./ADR-FORMAT.md) — ADR format and the "all three" bar for when to create one.
- `scripts/session.sh` — `start` / `status` / `stop` / `url` / `wait`.
- `scripts/broker.py` — static server + `POST /intent`; `scripts/wait.py` — the doorbell.
- `templates/viewer.html` — the bidirectional SPA: fold-locked Evidence | Decision layout, mermaid + code visuals, inline glossary reveal, one theme.

## Built

- **Tier-1 intents** — `answer` / `freeform` / `skip`. Compact option rows; hover/focus a row to preview its detail in the Evidence pane, "Choose" on the row to commit.
- **Fold-locked layout** — thin progress top bar over a two-pane Evidence | Decision split; a typical card fits one viewport, only verbose content scrolls (within a pane). Collapses to a single column under 900px.
- **Completion state** — when the session is done (`status: "complete"`, or all questions resolved/parked) the viewer shows a "Planning complete" recap of decisions instead of a stuck "Sent your answer" spinner. A soft-timeout also calms the spinner if the agent goes quiet.
- **Doc output** — updates the project's `CONTEXT.md` glossary and `docs/adr/` ADRs inline as decisions resolve; `session.json` carries the `glossary`/`adrs` delta.
- **Inline glossary reveal** — every term in `session.json` → `glossary` auto-lights-up wherever it appears in the prose (whole-word, skips code/diagrams, longest-match-first); click → an e-reader-style popover with the definition + "avoid" aliases. Pure client-side, no round-trip. Define-once-link-everywhere.
- **Readiness alerts** — when the next card arrives and the tab is backgrounded, the viewer flashes the title, fires a Web Notification (permission requested on the first answer), and soft-beeps. Fully client-side; the agent does nothing. Caveat: hidden tabs throttle the poll, so for long absences (>5 min) the alert can lag by up to a throttled interval.

## Roadmap

Pending work is tracked in [BACKLOG.md](./BACKLOG.md) as `IP-XXX` items. Next up is **IP-001** — inline reveal for ADRs + backlog items via a right-side slide-over panel (surface decision settled; the open sub-decision is `marked` vs. agent-supplied HTML for markdown). Also queued: the Tier-2 selection→actions menu (IP-004), open-ended option cards (IP-002), `two-worlds` visual (IP-003), broker→browser push to fix readiness-alert throttling (IP-006), and the mermaid CDN-fragility fix (IP-008). We deliberately skipped a passive glossary/ADR *sidebar* in favor of the inline click-the-text direction.

</supporting-info>
