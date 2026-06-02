# Cleanup + review *(delegated)*

Four passes, each its own delegated sub-agent, run **sequentially in this order** (never concurrent — each works the tree the next one reads or edits):

1. **`impeccable polish`** — final craft pass (spacing, hierarchy, states, motion, contrast). *Mutates the tree* (`general-purpose`, foreground, **no worktree isolation**).
2. **`simplify` / `code-review --fix`** — apply reuse/simplification/efficiency fixes; `code-review` also reports bugs. *Mutates the tree* (no worktree isolation).
3. **`security-review`** — report security findings on the changes. *Read-only.*
4. **`impeccable audit`** — a11y / performance / responsive checks on the finished code. *Read-only.*

Each sub-agent returns ONLY a compact result — a changed-by-file/area summary for the mutating passes, or findings (file/location + severity + one line) for the reads, never full files or diffs. Hold all four summaries; carry the findings into the diff-review gate.
