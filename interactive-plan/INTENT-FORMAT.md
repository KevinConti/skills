# Intent + question protocol (prototype)

The contract between the SPA (`templates/viewer.html`), the broker
(`scripts/broker.py`), and the agent. This is the bidirectional cousin of
visual-grill-with-docs' one-directional format — here the page talks back.

## Two directions

**Outbox (agent → page), unchanged from a read-only viewer:**
- `session.json` — session state; the SPA polls it every ~750ms.
- `q-NN.json` — one per question; fetched when a new id appears.

**Inbox (page → agent), new:**
- The page `POST`s an intent to `/intent`.
- The broker validates it, stamps a monotonic `seq` + `ts`, and appends one
  JSON line to `inbox.ndjson`.
- `inbox.cursor` holds the last `seq` the **agent** has processed.

## Session folder

```
~/.agent/interactive-plan/<slug>/
├── viewer.html        ← SPA, copied at start
├── session.json       ← outbox: session state (polled)
├── q-01.json …        ← outbox: one per question (polled)
├── inbox.ndjson       ← inbox: appended by the broker on each POST
├── inbox.cursor       ← last seq the agent has drained (agent-owned)
├── .port / .server.pid / .server.log   ← bookkeeping (session.sh owns these)
```

## `session.json`

```jsonc
{
  "slug": "checkout-retry-policy",
  "status": "active",                   // "active" | "complete" (set "complete" at wrap-up)
  "startedAt": "2026-06-01T16:00:00Z",
  "contextPath": "/CONTEXT.md",         // project's CONTEXT.md path, or null
  "currentQuestion": 2,                 // id to display (null until Q1 exists)
  "questions": [
    { "id": 1, "title": "Retry budget owner?", "status": "resolved", "answer": "per-merchant" },
    { "id": 2, "title": "Idempotency key source?", "status": "pending" }
  ],
  "glossary": [                         // session DELTA — terms added/changed this session
    { "term": "Retry budget", "definition": "Per-merchant cap on automatic charge retries.", "avoid": ["retry limit"] }
  ],
  "adrs": [                             // ADRs created/proposed this session
    { "id": "0004-per-merchant-retry-budget.md", "title": "Retry budget is per-merchant", "status": "proposed" }
  ]
}
```

A **question**'s `status` ∈ `pending | resolved | parked`. Include `answer` when resolved/parked.

The **session**'s top-level `status` ∈ `active | complete`. Set it to `complete` at
wrap-up so the viewer shows a "Planning complete" recap instead of sitting on the
optimistic "Sent your answer" state forever. (The viewer also treats *every*
question being resolved/parked as complete, so marking the final answer resolved is
the floor; the explicit `status` is the clean signal.)

`glossary` and `adrs` are the **session delta** — the real glossary lives in the
project's `CONTEXT.md` and the real ADRs in `docs/adr/`. Don't dump the whole
`CONTEXT.md` into `glossary`. `contextPath` is the project's `CONTEXT.md` path
(or null if none yet).

The viewer **auto-links every `glossary` term** in the prose and reveals its
definition (+ `avoid` aliases) on click. So a term only lights up if it's in this
delta — when a card references an existing `CONTEXT.md` term, add it here too.

## `q-NN.json`

```jsonc
{
  "id": 2,
  "context": { "paragraphs": ["Last turn you said <strong>retries</strong> are per-merchant…"] },
  "visual": { "type": "mermaid", "source": "flowchart TD\n  A[Request] --> B{Idempotent?}" },
  "question": "Where does the idempotency key come from?",
  "options": [
    {
      "letter": "A", "title": "Client-supplied", "summary": "Caller passes a key header.",
      "recommended": true,
      "detail": "The caller generates a UUID per logical operation and sends it as <code>Idempotency-Key</code>.",
      "rationale": "Survives client retries and network blips — the caller owns the identity of the attempt.",
      "downstream": "Every public endpoint must document the header; gateways must forward it unmodified.",
      "miniVisual": { "type": "code", "source": "POST /charge\nIdempotency-Key: 7f3c-…" }
    },
    {
      "letter": "B", "title": "Server-derived", "summary": "Hash of the normalized payload.",
      "detail": "The server hashes the canonical request body to derive the key.",
      "downstream": "Two genuinely-distinct requests with identical bodies collide.",
      "conflict": "Contradicts the <strong>per-merchant retry</strong> decision from Q1 — a merchant retrying a changed cart would be deduped."
    }
  ]
}
```

### Option fields

| Field | Required | Where it shows |
|---|---|---|
| `letter` | optional | head; defaults to A/B/C… by index |
| `title` | yes | head (escaped) |
| `summary` | yes | head (escaped) — one line |
| `recommended` | boolean | adds the head badge; exactly one option should be `true` |
| `detail` | optional | Evidence pane — 1–2 paragraphs; **inline HTML allowed** |
| `rationale` | shown only if `recommended` | Evidence pane, under "Why recommended" |
| `downstream` | optional | Evidence pane — what changes elsewhere if chosen |
| `conflict` | optional | bordered callout in the Evidence pane when the option clashes with a prior decision |
| `miniVisual` | optional | per-option visual in the Evidence pane; same shape as the top-level `visual` |

**Interaction (fold-locked two-pane layout).** The Decision pane (right) shows the
question and a compact row per option (letter / title / one-line summary / rec
badge). Hovering or focusing a row (tapping it on touch) reveals that option's
detail in the Evidence pane (left), which otherwise shows the question's context +
visual. The right pane never reflows, so the page never scrolls past the fold.
Committing is the explicit **Choose** button on the row, so reading detail never
submits.

Visuals supported in the prototype SPA: `mermaid` and `code`
(`{type:"code", filename?, source, highlights?}`), usable for both `visual` and
`miniVisual`. Anything else renders blank.

Rich text fields — `context.paragraphs` and option `detail`/`rationale`/
`downstream`/`conflict` — allow inline `<strong>`/`<em>`/`<code>` authored **by
the agent**. Option `title`/`summary` are escaped by the SPA. Never put
`<script>` or event handlers in any field; the SPA injects rich fields as raw
`innerHTML`.

## Intent (one line of `inbox.ndjson`)

```jsonc
{ "seq": 5, "id": "c3f1-…", "qid": 2, "kind": "answer",   "value": "A",  "note": "", "ts": "…" }
{ "seq": 6, "id": "9d22-…", "qid": 2, "kind": "freeform", "value": "From the order id", "note": "", "ts": "…" }
```

| `kind` | Meaning | Agent action |
|---|---|---|
| `answer` | Picked an option | `value` is the letter. Resolve Q, write next card. |
| `freeform` | Typed their own answer | `value` is free text. Treat as resolved value. |
| `skip` | Skip / park | Mark `parked`, move on. |
| `goback` | (reserved) jump back | Write a follow-up; never edit the old card. |

- `id` is client-generated → **idempotency key**. Track processed ids so a
  double-fired watcher never double-acts.
- `seq` is broker-assigned and monotonic → **ordering + cursor**.
- The broker truncates `value`/`note` to 2000 chars and rejects unknown kinds.

## The agent's cursor protocol

1. Woken by `session.sh wait` (it prints the new intents).
2. **Drain authoritatively:** read `inbox.ndjson`, take lines with
   `seq > inbox.cursor`. (The watcher is the doorbell; the file is the truth.)
3. Coalesce: for `answer`/`freeform` on the same `qid`, **last write wins**
   (the user may have changed their mind before you woke).
4. React: update `session.json` + write the next `q-NN.json`.
5. **Advance** `inbox.cursor` to the max `seq` you processed.
6. Re-arm `session.sh wait`. If intents arrived while you were working, it
   exits immediately and you loop again — nothing is lost.

## Security note (the trust boundary moved)

In a read-only viewer the agent authored every byte, so raw `innerHTML` was
safe. Here the **user** can submit `freeform` text. Never echo raw user input
into a rich field without escaping. The SPA escapes option/title fields; if you
surface a user's freeform answer back in `context.paragraphs`, escape it first.
The broker stays loopback-only and size-limits payloads.
