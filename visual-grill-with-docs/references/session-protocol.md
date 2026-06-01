# Session protocol

How a `visual-grill-with-docs` session is structured on disk and over time.

## Slug

The slug names the session folder and shows in the sidebar.

- Derive it from the user's opening sentence: lower-case, kebab-case, 2–4 words. Strip filler ("the", "a", "of", "for", "with").
- Examples: `order-cancellation-model`, `auth-token-rotation`, `partial-refunds`, `webhook-retry-policy`.
- If the opening sentence is vague ("I want to talk about my plan"), ask one short clarifying question before picking the slug. Don't pick `untitled` or `session-N`.
- Slug is chosen once at session start and never changes. If the conversation drifts to a new topic mid-session, finish the current session, then start a new one.

## Folder layout

```
~/.agent/grill-sessions/<slug>/
├── viewer.html              ← SPA, copied from skill at session start
├── session.json             ← session-wide state, polled by the SPA every 750ms
├── q-01.json
├── q-02.json
├── ...
├── .port                    ← bookkeeping; HTTP server port
├── .server.pid              ← bookkeeping; HTTP server process id
└── .server.log              ← bookkeeping; server stderr/stdout
```

- The `.port`, `.server.pid`, `.server.log` files are owned by `scripts/session.sh`. Don't read or edit them directly — use the script's subcommands.
- `q-NN.json` is zero-padded to two digits (`q-01.json`, not `q-1.json`) so paths sort correctly past 10.

## Server lifecycle

The SPA needs a tiny HTTP server (the browser blocks `fetch()` to `file://` URLs). The skill ships `scripts/session.sh` to manage it.

```bash
# Start (idempotent — re-uses an existing server if running)
scripts/session.sh start <slug>

# Check if it's running; prints URL and exits 0 if yes, exits 1 if no
scripts/session.sh status <slug>

# Print the URL without opening the browser
scripts/session.sh url <slug>

# Stop the server and clean up bookkeeping
scripts/session.sh stop <slug>
```

`start` does five things, in order:
1. `mkdir -p ~/.agent/grill-sessions/<slug>/`
2. Copy `templates/viewer.html` to the session folder.
3. Seed `session.json` if it doesn't exist (empty questions, empty glossary, `editorial` aesthetic).
4. Pick a free port, launch `python3 -m http.server` in the background, write PID + port to bookkeeping files.
5. Wait for the server to bind, then `open` (macOS) / `xdg-open` (Linux) the viewer URL.

`stop` kills the PID and removes the bookkeeping files. The session folder and JSON files persist for audit.

**Custom root via env var:** set `VISUAL_GRILL_ROOT=/some/path` to relocate sessions out of `~/.agent/grill-sessions/`.

## Lifecycle (agent's perspective)

### At session start (before question 1)

1. Derive the slug from the user's opening sentence.
2. Survey the project for existing docs: `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/adr/`. Note paths.
3. Run `scripts/session.sh start <slug>` — this creates the folder, seeds `session.json`, starts the server, opens the browser.
4. **Pick the aesthetic theme** from [visual-rules.md](./visual-rules.md). Vary from recent sessions.
5. Update `session.json` with the chosen `aesthetic`, the project's `contextPath`, and an empty `questions` array.

### Per question

1. Pick the next concrete question from the grilling queue. Have a recommended answer ready.
2. Choose the visual type from the table in [visual-rules.md](./visual-rules.md).
3. Write `q-NN.json` to the session folder (where `NN` is the next zero-padded id). Schema in [QUESTION-CARD-FORMAT.md](../QUESTION-CARD-FORMAT.md).
4. Update `session.json`: append `{id: N, title, status: "pending"}` to `questions`, set `currentQuestion: N`. Update `glossary` / `adrs` if anything changed last turn.
5. Send ONE short chat line. Format: `Q{N} is open in your browser — reply here with your choice.` The browser auto-refreshes within ~750ms. **Do not call `open` again** — the existing tab updates in place.
6. Wait for the user's reply. Process per "Reply handling" below.

### Server health check (every few questions)

Before writing a new question, run `scripts/session.sh status <slug>`. If it exits non-zero, the server died (laptop slept, process killed, etc.). Re-run `start` — it's idempotent and will reuse the same folder + files, just bringing the server back. The browser tab will need a manual refresh from the user.

### After the final question

1. Ensure the project's actual `CONTEXT.md` and any ADRs match `session.json`'s glossary delta. The JSON is a snapshot; the project docs are the source of truth.
2. Update `session.json`: every question marked `resolved` or `parked` with answers populated.
3. Send a closing chat line: which project files changed + the viewer URL (so the user can revisit the session offline — the server can keep running, or `scripts/session.sh stop <slug>` to free the port).

## Reply handling

The user replies in chat. Map the reply to one of these patterns:

| Reply shape | Action |
|---|---|
| "A", "Option B", "go with C" | Acknowledge briefly. Update `CONTEXT.md` / ADR if applicable. Mark the question `resolved` with a short `answer` summary in `session.json`. Write the next `q-NN.json` + update `currentQuestion`. |
| Hybrid ("B but with the X bit from A") | Restate the merged answer in chat for confirmation. On confirmation, treat as resolved. |
| User's own answer | Treat as a new resolved value. Update docs accordingly. |
| "Skip" / "park this" | Set the question's `status` to `parked` in `session.json` with a short note in `answer`. Move on. |
| "Go back to Q2" | Do NOT edit `q-02.json`. Write the next-numbered `q-NN.json` as a follow-up that references Q2's prior answer. The sidebar already lets the user jump back to Q2's read-only view. |
| Reply contradicts existing `CONTEXT.md` | Flag the conflict in chat AND in the next question's `context.paragraphs` / `option.conflict`. Resolve before moving on. |
| Ambiguous reply | Ask one short clarifying chat question (no new JSON). |
| User ends early | Run the "After the final question" steps with what's resolved. |

## Tone of chat messages

The viewer carries the weight. Chat lines should be short — typically one sentence — and never restate what the page already shows.

Good:
- `Q3 is open in your browser — reply here with your choice.`
- `Got it: Replacement aggregate. CONTEXT.md updated. Q4 is open.`
- `Conflict flagged in Q5 — your answer contradicts the existing definition of Customer. Q5 is open.`

Bad:
- A multi-paragraph chat message that re-explains the question.
- `ok` with no signal.
- Restating the recommended answer in chat (it's on the page).

Once the server is running and the tab is open, "open in your browser" is shorthand for "updated in your existing tab." Don't open new tabs.

## When NOT to use this skill

Reach for plain `grill-with-docs` (chat-only) when:

- The conversation is exploratory and you don't yet know what you're grilling about.
- Questions are coming faster than the JSON write cycle is worth (rapid 5-second back-and-forth — fine, but use chat for it).
- The user explicitly asks for "quick" questions.

The JSON+SPA pattern has a small fixed cost (server start, first viewer load). It pays off across multiple questions in one session. For a one-shot question, plain chat is fine.
