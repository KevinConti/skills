# Preflight — confirm required skills

Claude Code has no skill-level dependency manifest, so nothing guarantees the skills this pipeline calls are present — and built-ins can even be missing in a session running a different Claude Code build. Before you start, confirm each of these is available in the session. If any is absent, STOP and tell the user which ones and where they come from — don't start a pipeline that will die partway through:

- `interactive-plan` — personal skill
- `handoff` — personal skill
- `visual-explainer:plan-review` and `visual-explainer:diff-review` — visual-explainer plugin (install the `visual-explainer` plugin if missing)
- `simplify` **or** `code-review`, plus `security-review` — Claude Code built-ins; update Claude Code if missing. (Recent builds renamed `simplify` → `code-review`, so *either* satisfies this check — the cleanup step uses whichever is present.)
