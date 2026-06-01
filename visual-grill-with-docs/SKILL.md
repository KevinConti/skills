---
name: visual-grill-with-docs
description: Visual grilling session that presents each domain-modeling question in a live browser viewer (context, visual, hover-expand options), while updating CONTEXT.md and ADRs inline as decisions crystallise. The agent writes small JSON files; a self-contained SPA renders them with hot reload. Use when the user wants to stress-test a plan against their project's language and documented decisions and prefers visual question framing over plain chat.
---

<what-to-do>

Interview the user relentlessly about every aspect of their plan until you reach shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, write a small JSON file to the session folder; a self-contained SPA already open in the user's browser renders it within a second. Provide a recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead.

The viewer is read-only. The user always replies in chat.

</what-to-do>

<supporting-info>

## Architecture

The agent does **not** write HTML. The skill ships a self-contained SPA (`templates/viewer.html`) that lives in the session folder and is served by a tiny background HTTP server. The agent writes:

- `session.json` — session-wide state (slug, aesthetic, questions list, glossary delta, ADRs).
- `q-NN.json` — one per question.

The SPA polls `session.json` every ~750ms. When a new question id appears (or `currentQuestion` changes), it fetches the matching `q-NN.json` and re-renders in the existing tab. **You never re-open the browser** after session start.

## Reading list

Read these once at session start. Re-read when you need them.

- [QUESTION-CARD-FORMAT.md](./QUESTION-CARD-FORMAT.md) — JSON schema for `session.json` and `q-NN.json`.
- [references/visual-rules.md](./references/visual-rules.md) — the five themes and visual-type-by-question table.
- [references/session-protocol.md](./references/session-protocol.md) — server lifecycle, slug derivation, reply handling.
- [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) — glossary format for the project's `CONTEXT.md`.
- [ADR-FORMAT.md](./ADR-FORMAT.md) — ADR format and the "all three" bar for creating one.

## Session lifecycle

### Before question 1

1. Survey the project for existing docs: `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`. Note paths.
2. Derive a slug from the user's opening sentence (see [session-protocol.md](./references/session-protocol.md)).
3. **Start the session server.** Run the skill's script (path expands to wherever the skill is installed — typically `~/.claude/skills/visual-grill-with-docs/scripts/session.sh`):

   ```bash
   bash "$(dirname "$(readlink -f ~/.claude/skills/visual-grill-with-docs/SKILL.md 2>/dev/null || echo ~/.claude/skills/visual-grill-with-docs/SKILL.md)")/scripts/session.sh" start <slug>
   ```

   In practice: invoke `scripts/session.sh start <slug>` relative to the skill root. The script copies `viewer.html` into the session folder, picks a port, starts `python3 -m http.server` in the background, and opens the browser. It's idempotent — if a server is already running for this slug, it just reuses it.

4. **Pick the aesthetic theme** from [visual-rules.md](./references/visual-rules.md): `editorial`, `blueprint`, `paper-ink`, `monochrome`, or `ide-nord`. Vary from recent sessions.
5. Update `session.json` with the chosen `aesthetic`, the project's `contextPath`, and any pre-known terms in `glossary`.

### Per question

1. Pick the next concrete question. Have a recommended answer ready.
2. Choose the visual type from the table in [visual-rules.md](./references/visual-rules.md).
3. Write `q-NN.json` (next zero-padded id). Schema in [QUESTION-CARD-FORMAT.md](./QUESTION-CARD-FORMAT.md). Aim for ~50–80 lines.
4. Update `session.json`: append `{id, title, status: "pending"}` to `questions`, set `currentQuestion: N`. Update `glossary` / `adrs` if anything changed last turn.
5. Send ONE short chat line. Format: `Q{N} is open in your browser — reply here with your choice.` Do not call `open` — the tab refreshes itself.
6. Wait for the reply. Process per "Reply handling" below.

### Server health check

Before writing a new question (after a long pause or a system event), run `scripts/session.sh status <slug>`. If it exits non-zero, the server died — re-run `start`, then ask the user to refresh the tab.

### After the final question

1. Ensure the project's actual `CONTEXT.md` and any ADRs match `session.json`'s glossary/ADR sections. The JSON is a snapshot; the project docs are the source of truth.
2. Mark every question `resolved` (with `answer`) or `parked` in `session.json`.
3. Send a closing chat line that lists which project files changed and the viewer URL (so the user can revisit). Optionally `scripts/session.sh stop <slug>` to free the port.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with existing language in `CONTEXT.md`, call it out on the next question's JSON — `context.quote` shows the current definition; the conflicting option carries a `conflict` field.

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. If you can frame discrete options ("Customer vs User vs Account"), use the standard options array. If the answer space is genuinely open, use the open-ended option variant (see [QUESTION-CARD-FORMAT.md](./QUESTION-CARD-FORMAT.md)).

### Discuss concrete scenarios

Put the scenario in `context.paragraphs`; use a sequence diagram or `two-worlds` visual to make it concrete; phrase the question around how the scenario should resolve.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: use a `code` visual with the disputed line as a `highlights` entry, quote the user's claim in `context.paragraphs`, and frame options as "which is right?"

### Update CONTEXT.md inline

When a term is resolved, update the project's `CONTEXT.md` immediately — don't batch. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md). Add the term to `session.json` → `glossary` and surface the update on the *next* question's `context.lastUpdate` field.

`CONTEXT.md` is a glossary. No implementation details. No specs. Just terms, definitions, relationships, and flagged ambiguities.

### Offer ADRs sparingly

Only offer to create an ADR when **all three** are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons.

If any is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md). When an ADR *is* created, add it to `session.json` → `adrs`.

## Reply handling

| Reply shape | Action |
|---|---|
| "A", "Option B", "go with C" | Acknowledge briefly. Update `CONTEXT.md` / ADR if applicable. Mark question `resolved` in `session.json` with a short `answer`. Write the next `q-NN.json` and update `currentQuestion`. |
| Hybrid ("B but with the X bit from A") | Restate the merged answer in chat for confirmation. On confirmation, treat as resolved. |
| User's own answer | Treat as a new resolved value. Update docs accordingly. |
| "Skip" / "park this" | Set the question's `status: "parked"` with a short `answer` note. Move on. |
| "Go back to Q2" | Do NOT edit `q-02.json`. Write the next-numbered `q-NN.json` as a follow-up. The sidebar already lets the user jump back to Q2's read-only view. |
| Reply contradicts existing `CONTEXT.md` | Flag the conflict in chat AND in the next question's `context.paragraphs` / option `conflict`. Resolve before moving on. |
| Ambiguous reply | Ask one short clarifying chat question (no new JSON). |
| User ends early | Run the "After the final question" steps with what's resolved. |

## Chat-line discipline

The viewer carries the weight. Chat lines should be short — typically one sentence — and never restate what the page already shows.

Good:
- `Q3 is open in your browser — reply here with your choice.`
- `Got it: Replacement aggregate. CONTEXT.md updated. Q4 is open.`
- `Conflict flagged in Q5 — your answer contradicts the existing definition of Customer. Q5 is open.`

Bad:
- A multi-paragraph chat message that re-explains the question.
- `ok` with no signal.
- Restating the recommended answer in chat (it's on the page).

## File structure for the project docs

**Single context (most repos):** one `/CONTEXT.md` at the repo root.

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

**Multiple contexts:** a `CONTEXT-MAP.md` at the root lists where each context lives. See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md) for the map format.

Create files lazily — only when there's something to write. If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## When NOT to use this skill

Reach for plain `grill-with-docs` (chat-only) when:

- The conversation is exploratory and you don't yet know what you're grilling about.
- Questions are coming faster than the JSON write cycle is worth.
- The user explicitly asks for "quick" questions.

The JSON+SPA pattern has a small fixed cost (one-time server start) and pays off across multiple questions in one session. For a one-shot question, plain chat is fine.

</supporting-info>
