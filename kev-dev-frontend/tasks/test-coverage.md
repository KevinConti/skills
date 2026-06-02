# Test coverage review — delegated sub-agent *(delegated)*

Spawn a sub-agent (`general-purpose`, foreground, **no worktree isolation** — it writes tests to the real tree) to bring the change's tests up to the codebase's standard:

```
Review the tests for the <ITEM> changes against THIS codebase's testing
conventions and coverage bar — find the existing test patterns (framework,
structure, naming, what's worth covering) and follow them. Add any missing
tests so the change meets that bar; skip trivia. Run the suite.
Return ONLY a concise summary: coverage added, gaps left open, suite result.
Do not paste test files back.
```
