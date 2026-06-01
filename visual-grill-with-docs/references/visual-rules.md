# Visual rules

The aesthetic is **baked into `templates/viewer.html`**. The agent doesn't write CSS, pick fonts, or design palettes — it picks one of five themes at session start and the SPA handles the rest.

## The five themes

Pick exactly one per session. Set it in `session.json` → `aesthetic`. Don't change mid-session.

| Theme | Vibe | Fonts | Palette | Best for |
|---|---|---|---|---|
| `editorial` | Refined, magazine-like | Instrument Serif (display) + IBM Plex Sans + JetBrains Mono | Deep blue (#1e3a5f) + gold (#d4a73a) on cream | Policy / definitions / human-scale concepts |
| `blueprint` | Technical drawing | IBM Plex Sans + IBM Plex Mono | Deep slate (#1e293b) + cyan (#0891b2) on light slate, subtle grid | System architecture, infrastructure |
| `paper-ink` | Warm, informal, exploratory | Bricolage Grotesque + Fragment Mono | Terracotta (#c2410c) + sage (#65a30d) on warm cream | Open-ended modeling, early-stage thinking |
| `monochrome` | Terminal, dense, hacker | JetBrains Mono everything | Amber (#f59e0b) on near-black (dark only) | Low-level / protocol / format work |
| `ide-nord` | Calm, cool, code-editor | DM Sans + Fira Code | Nord palette (#5e81ac + #88c0d0) | Anything code-heavy, refactoring discussions |

All themes ship with both light and dark mode (toggled by OS preference, except `monochrome` which is dark-only). Each defines a full palette: `--bg`, `--surface`, `--surface-recessed`, `--border`, `--border-strong`, `--text`, `--text-dim`, `--accent`, `--hi`, `--conflict`. Mermaid auto-inherits these via `themeVariables`.

**Vary the pick across sessions.** Default to `editorial` if there's no strong reason — but if your last session used `editorial`, pick something else.

## Visual type by question

This is the only aesthetic decision per question: which visual best frames it.

| Question is about | Use |
|---|---|
| Entity relationships, who-talks-to-whom | `mermaid` with `flowchart TD` |
| State changes, lifecycle | `mermaid` with `stateDiagram-v2` (simple labels) or `flowchart TD` (complex labels) |
| Sequence of events between actors | `mermaid` with `sequenceDiagram` |
| Schema / data model | `mermaid` with `erDiagram` |
| Hierarchy / taxonomy | `mermaid` with `mindmap` |
| "Your code does X but you said Y" | `code` with highlighted substrings |
| Option A vs Option B contrast | `two-worlds` (left = A, right = B) |
| Decision tree / multi-path flow | `mermaid` flowchart with diamonds |
| Anything that doesn't fit | `html` escape hatch with inline SVG |

**Pick exactly one visual per question.** Don't stack multiple visuals in the top-level `visual` slot — that's a sign the question is actually two questions, split it.

**Mini-visuals on options** are encouraged when they help compare options concretely (often a 3–5 line code snippet showing the pseudocode for that option's approach).

## Mermaid notes (apply to every diagram you write)

- `flowchart TD` (top-down) is the default. `LR` only for 3–4 node linear flows.
- Use `<br/>` for line breaks in quoted labels. Never `\n` — Mermaid renders it as literal text.
- Don't write your own `theme:` / `themeVariables:` directives in the source. The SPA injects them based on the active aesthetic. Just write the diagram body starting with `flowchart TD`, `stateDiagram-v2`, etc.
- `stateDiagram-v2` has a strict label parser — colons, parens, `<br/>`, and HTML entities cause silent parse failures. For complex labels, use `flowchart TD` instead.
- Keep diagrams under 10–12 nodes. The SPA scrolls horizontally if needed, but readability degrades fast past that.

## What the agent does NOT do anymore

Compared to the original HTML-per-question mode, the agent is freed from:
- Writing CSS, picking fonts, picking accent colors.
- Layout decisions (header structure, accordion behavior, footer text).
- Mermaid container scaffolding and zoom controls.
- Dark-mode handling.
- Animation rules.

The SPA owns all of that. The agent's only visual decision per question is **which type of visual** (table above) and **what the diagram/code shows**.

## When the SPA falls short

If the viewer renders wrong (clipped, unreadable, wrong colors) the failure is in the SPA or the JSON, not in the agent's choice of aesthetic. Fix the SPA at `templates/viewer.html` — don't try to work around it in JSON.

Common JSON-side failures:
- Mermaid source with unescaped quotes or `\n` inside labels → fix the source.
- Code snippet with unescaped `<` or `>` → the SPA escapes for you, write the raw source.
- Visual `type` that the SPA doesn't recognize → use one of `mermaid`, `code`, `two-worlds`, `html`.
- Option `summary` or `detail` with `<script>` or event handlers → strip them, only inline tags allowed.
