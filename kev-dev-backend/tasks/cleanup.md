# Cleanup — `simplify`/`code-review`, then `security-review` *(delegated)*

Both passes are read-heavy and what you need back from each is small, so delegate each to its own sub-agent (follow the shared delegation contract in `SKILL.md`). Run them in **two sequential sub-agents, never concurrently** — cleanup mutates the very files `security-review` reads, so cleanup must fully finish first.

**Cleanup sub-agent** (`general-purpose`, foreground, **no worktree isolation** — it edits the real tree). Use whichever cleanup skill preflight found:

- `simplify` — applies reuse/simplification/efficiency fixes directly (quality only). Prefer it if present.
- `code-review` — the renamed successor in recent builds. Pass `--fix` so it actually applies the cleanups (without it, it only reports). It also hunts correctness bugs, so expect bug findings alongside the cleanups.

```
Run `<simplify | code-review --fix>` on the current working tree to clean up
the <ITEM> changes. Apply the fixes directly to the files.
Return ONLY a concise summary: what you changed (by file/area) and any bugs
found. Do not paste full file contents or diffs back.
```

**Security sub-agent** (`general-purpose`, foreground), spawned **only after the cleanup sub-agent returns**:

```
Run the `security-review` skill on the pending changes on this branch.
Return ONLY the findings: each issue with file/location, severity, and a
one-line description. Do not paste full file contents back.
```

Hold both summaries. If cleanup changed anything material, note it so it isn't a surprise in diff-review; carry any security findings into the diff-review gate.
