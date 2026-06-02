# Preflight — confirm required skills

Claude Code has no skill-level dependency manifest, so confirm each of these is available before you start; if any is absent, STOP and tell the user which and where it comes from rather than failing partway:

- `interactive-plan` — personal skill
- `impeccable` — personal skill; used as `impeccable shape`, `impeccable craft`, `impeccable polish`/`audit`
- `handoff` — personal skill
- `visual-explainer:plan-review` and `visual-explainer:diff-review` — visual-explainer plugin
- `simplify` **or** `code-review`, plus `security-review` — Claude Code built-ins (recent builds renamed `simplify` → `code-review`; either satisfies this)
