# Brief — `handoff` *(inline — cheap)*

`handoff` is primarily a **context-management strategy** — it gives the implementation session the most useful context possible to work from before it hits compaction. Much of that (the design brief, the contract decision, `CONTEXT.md`/ADRs, the relevant code) the sub-agent could reach on its own; the handoff's **unique value is folding in the hanging items from plan-review** (the findings you held from it), which would otherwise be lost, so they get proper attention during the build.

Invoke `handoff`, weaving in the design brief, the contract decision (regime + decouple/block + the ADR), the still-open plan-review findings, and links to `CONTEXT.md`/ADRs/relevant code. Capture the handoff path; it becomes the implementation sub-agent's brief.
