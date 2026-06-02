# Backend-reality read → realism floor + contract regime *(delegated)*

Reading the backend to understand what's feasible is context-heavy, and what you need back is small — so delegate it (per the shared delegation contract in `SKILL.md`). Spawn a sub-agent (`general-purpose`, foreground):

```
Read the backend relevant to <ITEM> and report, concisely:
1. Realism floor — what data/computation the UI can honestly draw on
   (entities, endpoints, derivable values). Just the envelope, not a contract.
2. Contract regime for this story, one of:
   (a) endpoint fixed — it exists and is frozen
   (b) use-case built, endpoint greenfield — capability exists, endpoint shape open
   (c) API decisions open — substantial API decisions still waiting on the UX
Return ONLY this note (a few lines). Do not paste source files back.
```

State the regime to the user (it drives the contract step); correct it with them if the read got it wrong. Not a gate.
