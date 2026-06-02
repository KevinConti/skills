# Commit the contract + plan architecture — `interactive-plan` ⛔ *(inline — interactive)*

With the UI pinned, run **`interactive-plan`** to design the **data contract that serves the chosen UI** (shaped to the UI's needs through whatever frontend-facing layer the app has — an adapter/view-model, an API gateway, a tailored endpoint, or client-side transforms), plus the frontend architecture/wiring and domain language. It's interactive (the user answers in the live UI), so it stays **inline**. It updates `CONTEXT.md`/ADRs as decisions land. Behavior flexes by regime:

- **(a) fixed endpoint** — adapt the frozen endpoint to the UI through whatever frontend-facing shaping the app supports (an adapter, view-model, gateway, or client-side transform). If there's no room to adapt and the endpoint genuinely can't serve the UI, surface the gap before continuing.
- **(b) greenfield endpoint** — finalize the endpoint to serve the UI; write the agreed contract as an **ADR**.
- **(c) open API** — design the contract from the UI's needs; write it as an **ADR**.

For **(b) and (c)** the endpoint won't exist yet when the frontend builds, so ⛔ **ask the user: decouple or block?**
- **Decouple** — build the UI against a **mock/stub of the agreed contract**; the contract ADR becomes a deliverable to the backend track (a `kev-dev-backend` run or the backend team).
- **Block** — the frontend waits for the backend to deliver the real endpoint. Run plan-review and the handoff (with the contract ADR), then go to handback with status "planned, pending backend," and resume at the implement step once the endpoint lands.

Either way — decouple or block — **write a backlog item for the backend endpoint that references the proposed contract ADR**, so the backend work is tracked and the ADR has an owner.

Record the regime + decouple/block choice; they drive the implement and handback steps. Ensure the combined plan artifact exists — design brief + contract + architecture — that's what plan-review consumes.
