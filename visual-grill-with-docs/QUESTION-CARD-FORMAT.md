# Question format

The agent writes JSON; the SPA (`templates/viewer.html`) renders. This document is the contract between them.

Two files matter:
- `session.json` — session-wide state, written once at start and updated whenever questions resolve or docs change.
- `q-NN.json` — one per question (`q-01.json`, `q-02.json`, …).

The SPA polls `session.json` every ~750ms. When a new question id appears, the SPA fetches the matching `q-NN.json` and re-renders.

## `session.json`

```jsonc
{
  "slug": "order-cancellation-model",        // matches folder name
  "aesthetic": "editorial",                  // one of: editorial | blueprint | paper-ink | monochrome | ide-nord
  "startedAt": "2026-05-31T14:02:00Z",       // ISO-8601 UTC
  "contextPath": "/CONTEXT.md",              // project's CONTEXT.md path, or null
  "currentQuestion": 2,                       // id of the question to show (null until Q1 exists)

  "questions": [
    { "id": 1, "title": "Is a Customer the same entity as a User?", "status": "resolved", "answer": "distinct" },
    { "id": 2, "title": "When a customer changes their mind on an accepted Order, what happens?", "status": "pending" }
  ],

  "glossary": [
    { "term": "Customer", "definition": "A person or organization that places Orders.", "avoid": ["client", "buyer"] },
    { "term": "User", "definition": "A person who authenticates with the system.", "avoid": [] }
  ],

  "adrs": [
    { "id": "0003-replacement-as-aggregate.md", "title": "Replacement as a first-class aggregate", "status": "proposed" }
  ]
}
```

**Field notes:**
- `aesthetic` is locked at session start. Don't change mid-session — the SPA will re-theme everything.
- `currentQuestion` controls which question the viewer shows. Setting it pins the view; setting `null` lets the viewer default to the highest-id question. Update it whenever the agent wants to draw attention to a question (most often: the latest one).
- `questions[].status` is one of `pending | resolved | parked`. When `resolved`, include `answer` (a short summary phrase, not the full reply).
- `questions[].title` should match the question's `question` field in `q-NN.json` (give or take punctuation).
- `glossary` is the **delta** for this session — terms added or changed during the grilling. Don't dump the entire CONTEXT.md.
- `adrs` is just a list of ADRs created or proposed during this session. The real ADR file lives in `docs/adr/` in the project.

## `q-NN.json`

```jsonc
{
  "id": 2,
  "resolvedPills": ["Customer", "User", "Order"],   // pills shown in the header strip

  "context": {
    "paragraphs": [
      "Last turn you said an <strong>Order</strong> can be \"cancelled and replaced\" when a customer changes their mind. Your current glossary defines <strong>Order</strong> as immutable once accepted:",
      "So when you say \"replace\", are we creating a new Order, mutating the old one, or modelling this as a distinct operation? The answer shapes how every downstream context (Fulfillment, Billing) reacts to changes."
    ],
    "quote": { "term": "Order", "definition": "a request from a Customer for one or more items. Once accepted, an Order is immutable." },
    "lastUpdate": "Customer distinguished from User."     // optional; one-line note shown at the bottom of the band
  },

  "visual": {
    "type": "mermaid",
    "source": "flowchart TD\n  C([Customer])\n  O[\"Order<br/>(accepted, immutable?)\"]\n  F[\"Fulfillment\"]\n  B[\"Billing\"]\n  C -->|\"places\"| O\n  O -->|\"OrderPlaced\"| F\n  F -->|\"ShipmentDispatched\"| B"
  },

  "question": "When a customer changes their mind on an accepted Order, what actually happens to that Order?",

  "options": [
    {
      "letter": "A",
      "title": "Cancel and create a new Order",
      "summary": "The original Order is cancelled (terminal). A second, independent Order is created with the revised line items.",
      "recommended": false,
      "detail": "<code>OrderCancelled</code> is emitted for the original. A new <code>Order</code> is constructed from scratch — new ID, new <code>OrderPlaced</code>. The two are linked only by a <code>replaces</code> reference on the new Order's metadata.",
      "miniVisual": {
        "type": "code",
        "filename": "// pseudocode",
        "source": "orig.cancel()                  // emits OrderCancelled\nnew = Order.create(lineItems)  // emits OrderPlaced\nnew.replaces = orig.id         // metadata only"
      },
      "downstream": "Fulfillment and Billing see two independent events. Existing reactions just work — no new code paths. Reporting must aggregate the chain to show net revenue.",
      "conflict": null
    },
    {
      "letter": "C",
      "title": "Model 'Replacement' as its own concept",
      "summary": "Introduce a <code>Replacement</code> aggregate that points to the cancelled Order and the new Order.",
      "recommended": true,
      "rationale": "Preserves <code>Order</code> immutability (compatible with the current glossary). Makes the \"these two Orders are related\" fact a first-class domain concept. Future extensions (partial replacements, return-then-replace) have a natural home.",
      "detail": "A <code>Replacement</code> is created when a Customer initiates the change. It cancels the original Order and creates the new Order atomically, then emits <code>ReplacementCompleted</code> alongside the existing cancel/place events.",
      "miniVisual": {
        "type": "code",
        "source": "r = Replacement.start(orig, newLineItems)\n// emits: OrderCancelled, OrderPlaced, ReplacementCompleted"
      },
      "downstream": "One new aggregate to maintain. Consumers that don't care about replacements ignore the new event; reporting and customer service get a clean query target.",
      "conflict": null
    }
  ]
}
```

**Field notes:**
- `id` must match the file name. `q-02.json` ⇒ `"id": 2`.
- `resolvedPills` is a snapshot of terms resolved up to this question. Used as the header strip's running glossary view.
- `context.paragraphs` accepts inline HTML — `<strong>`, `<em>`, `<code>` are encouraged for bolding canonical terms. **Do not write `<script>` or anything dynamic** — there's no sandboxing.
- `context.quote` shows a current-glossary definition that the question is challenging. Optional.
- `context.lastUpdate` is the one-line "Glossary updated last turn: …" note. Include only when something actually changed.
- `visual` is required. See the visual types below.
- `question` is plain text. Single sentence, no HTML.
- `options` is required. Either an array of 2–4 option objects (standard form) **or** a single open-ended card (see below).

### Standard option fields

| Field | Required | Notes |
|---|---|---|
| `letter` | optional | Defaults to A/B/C/… by index. |
| `title` | yes | 3–6 words. |
| `summary` | yes | One sentence. Inline HTML allowed. |
| `recommended` | yes (boolean) | Exactly one option should be `true` (zero is OK if you have no recommendation). |
| `detail` | yes | 1–2 paragraphs. Inline HTML allowed. |
| `miniVisual` | optional | Per-option visual. Same shape as the top-level `visual`. |
| `rationale` | required if `recommended` | Why this option specifically. Lives inside the body, not the chrome. |
| `downstream` | yes | What changes elsewhere if this is chosen. |
| `conflict` | optional | Explanation of any glossary/ADR conflict. Renders as a red-bordered callout. |

### Open-ended variant

When the question doesn't have a clean option list (typical for "sharpen fuzzy language"), provide a single option with `kind: "open"`:

```jsonc
"options": [
  {
    "kind": "open",
    "title": "Open question",
    "shape": "A good answer names one of: Customer, User, or 'both, but distinct'.",
    "examples": [
      "Customer — the buying party",
      "User — the authenticating party",
      "Both, but distinct — a User may act for one or more Customers"
    ],
    "rationale": "I lean toward 'both, but distinct' — your B2B use case has a buyer team acting on behalf of an org."
  }
]
```

The open card stays expanded by default; no accordion behavior.

## Visual types

The `visual` field (and `miniVisual` on options) is one of:

### `mermaid`

```jsonc
{ "type": "mermaid", "source": "flowchart TD\n  A --> B" }
```

The SPA renders client-side using Mermaid 10 with `theme: "base"` and themed colors from the active aesthetic. Use `flowchart TD` (top-down) for most diagrams; LR only for simple 3–4 node linear flows. Use `<br/>` for line breaks inside quoted labels (never `\n`).

### `code`

```jsonc
{
  "type": "code",
  "filename": "src/order.ts",          // optional, shown above the code
  "source": "function cancel(o) {\n  ...\n}",
  "highlights": ["function cancel"]    // optional, substrings wrapped in <span class="hl">
}
```

### `two-worlds`

For Option A vs Option B contrast — two side-by-side visuals.

```jsonc
{
  "type": "two-worlds",
  "left":  { "title": "Cancel + new",  "body": { "type": "mermaid", "source": "..." } },
  "right": { "title": "Replacement",   "body": { "type": "mermaid", "source": "..." } }
}
```

`body` can be any visual type (recursive). Don't nest `two-worlds` inside `two-worlds`.

### `html`

```jsonc
{ "type": "html", "source": "<svg>...</svg>" }
```

Raw HTML escape hatch. Use for inline SVG sketches or anything the other types don't cover. **No `<script>` tags or event handlers** — the SPA does not sandbox this.

## Quick reference

| If it's about… | Section / field |
|---|---|
| Which question is shown | `session.json` → `currentQuestion` |
| Term pills in the header | `q-NN.json` → `resolvedPills` |
| Why we're asking now | `q-NN.json` → `context.paragraphs` |
| The current glossary definition being challenged | `q-NN.json` → `context.quote` |
| The visual | `q-NN.json` → `visual` |
| The question itself | `q-NN.json` → `question` |
| Choices, with hover/click detail | `q-NN.json` → `options[]` |
| Recommended marker + rationale | option `recommended: true` + `rationale` field (inside the body) |
| Conflict with existing docs | option's `conflict` field |
| Glossary delta in the sidebar | `session.json` → `glossary` |
| ADRs in the sidebar | `session.json` → `adrs` |

## What does NOT go in JSON

- The agent's full reasoning chain. The page should feel curated.
- Restatement of the question in three different ways. State it once, in `question`.
- Speculative future questions. Those live in the agent's queue, not in JSON.
- Long backstory in the context band. Two or three sentences max.
- `<script>` tags or any executable HTML. The SPA injects values into `innerHTML` for the rich fields (context, summary, detail, etc.) — inline `<strong>`, `<em>`, `<code>`, `<br>` are fine; nothing else.
