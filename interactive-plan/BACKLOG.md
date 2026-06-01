# interactive-plan — backlog

Pending work for the `interactive-plan` skill, tracked as `IP-XXX` ids. Each item
is written to be picked up cold (e.g. handed to `kev-dev-backend`). The skill's
own Phase 2b (IP-001) is, fittingly, about making these ids clickable in a card.

**Status:** `pending` · `in-progress` · `done` · `deferred`
**Priority:** `next` · `high` · `med` · `low`

---

## IP-001 · ADR + backlog inline reveal (slide-over panel)
**Status:** pending · **Priority:** next · **Phase:** 2b

When a card's prose references an ADR or a backlog item, light it up like a glossary
term — but open a right-side **slide-over panel** (page stays behind, non-blocking)
with the full content, instead of the small dictionary popover.

**Key architecture decision (already made):** ADRs (`docs/adr/*.md`) and backlog items
live in the *project repo*, outside the session folder the broker serves — so the SPA
can't fetch them. The agent must **embed the referenced content into the session
folder**. This preserves the broker's "serve only the session folder" invariant and
avoids opening it to arbitrary project paths (traversal risk).

**Build:**
1. `session.json`: give `adrs[]` a `body` (ADR markdown); add `backlog[]` (`{id, title, body}`).
2. Extend the prose linker (`linkGlossary`) to also tag ADR ids/titles and backlog ids
   (`IP-XXX`) as a distinct entity type that opens the panel, not the popover.
3. Slide-over panel: CSS + open/close animation, non-blocking, dismiss on Esc / backdrop click.
4. Markdown rendering in the panel. Open sub-decision: pull `marked` from CDN (consistent
   with how mermaid loads; SPA renders) vs. agent-supplied pre-rendered HTML (no new dep).
5. Docs: the backlog concept + "embed referenced ADR/backlog content into the session folder."

**Verify (headless Chrome):** id/title linked in prose; click opens the panel with rendered
markdown; Esc/backdrop dismiss; nothing fetched from outside the session folder.

---

## IP-002 · Open-ended option card (`kind:"open"`)
**Status:** pending · **Priority:** high

Port visual-grill's open-ended card for "sharpen fuzzy language" questions where the answer
space isn't a clean A/B/C. Single always-expanded card with `shape` (what a good answer looks
like) + `examples` + recommended framing. Needs the SPA `renderOption` branch + schema in
INTENT-FORMAT.md. Until then the agent frames discrete candidates as a normal options array.

---

## IP-003 · `two-worlds` A/B visual
**Status:** pending · **Priority:** med

Port visual-grill's side-by-side visual (`{type:"two-worlds", left, right}`, each a nested
visual) for "Option A vs Option B" contrasts. SPA `renderVisual` branch + CSS grid. Sequence
diagrams already work via the generic `mermaid` type; this is only the split-view.

---

## IP-004 · Tier 2 — selection → actions menu (generative requests)
**Status:** pending · **Priority:** high

The other half of the "click the text itself" design (Mode B). Highlight any word/phrase →
floating menu of actions that round-trip to the agent through the existing broker/doorbell loop:
*define this · flag as fuzzy · split into two terms · promote to ADR · ask the agent*. This is
the real Tier-2 surface, anchored to text rather than abstract buttons.

**Build:** new intent `kind`s in `broker.py` `ALLOWED_KINDS`; a selection-menu in the SPA
(`getSelection` + floating menu); agent handling per kind in SKILL.md (e.g. a "define" intent →
agent adds a glossary term and confirms; "make ADR" → drafts an ADR). Rides existing plumbing.

---

## IP-005 · Tier 3 — ambient awareness (`attention.json`)
**Status:** deferred · **Priority:** low

A pull-only `attention.json` the SPA writes (debounced, capped) summarizing what the user
lingers on — expanded options, dwell time. The agent reads it opportunistically *only when
already taking a turn*, never woken by it, to sharpen recommendations. Speculative; lowest
priority. (Direction: user→agent; distinct from readiness alerts which are agent→user.)

---

## IP-006 · Broker→browser push (SSE/WebSocket)
**Status:** pending · **Priority:** med

Replace browser→broker polling with server push. Fixes two things at once: the readiness-alert
lag when a tab is backgrounded (hidden tabs throttle the poll timer), and general round-trip
latency. The agent stays turn-based; only the broker↔browser leg changes. Bigger change — the
broker becomes a real (still local) server with an event stream.

---

## IP-007 · Concurrent same-slug guard (owner token)
**Status:** pending · **Priority:** low

Today two sessions that pick the same slug silently merge into one corrupted session folder
(idempotent `start` reuses the broker; both drain the same inbox/cursor). Fix: `start` writes an
owner token to `.owner`; on `start`, refuse with a clear error if `.owner` differs and the broker
is live, while still allowing same-session re-arm and crash recovery. Low priority for
single-developer use.

---

## IP-008 · Mermaid CDN fragility
**Status:** pending · **Priority:** med

The SPA does a top-level `import mermaid from "…jsdelivr…"`. If that CDN is unreachable the
*entire* module fails and nothing renders — not just diagrams. Fix: vendor the mermaid esm build
into `templates/` and import it relatively, **or** wrap it in a lazy/guarded import so a miss only
disables diagrams. (`marked`, if added in IP-001, has the same exposure.)

---

## IP-009 · Multiple themes
**Status:** deferred · **Priority:** low

interactive-plan ships one theme; visual-grill has five (`editorial`, `blueprint`, `paper-ink`,
`monochrome`, `ide-nord`). Pure aesthetics — port the theme blocks + an `aesthetic` field if
desired. Lowest priority.

---

## Shipped (for orientation)

- Bidirectional loop — broker (`POST /intent`) + file-watcher doorbell + cursor-drained agent loop.
- Tier-1 intents — `answer` / `freeform` / `skip`, expandable option cards (hover/pin + "Choose").
- Flicker fix — signature-gated rendering (no per-poll DOM rebuild).
- Readiness alerts — title flash + Web Notification + beep when a new card lands on a backgrounded tab.
- Doc output (Phase 1) — inline `CONTEXT.md` glossary + `docs/adr/` ADRs; `session.json` delta.
- Inline glossary reveal (Phase 2a) — auto-linked terms + e-reader-style definition popover.
