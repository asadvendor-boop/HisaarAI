# HisaarAI judge claim map

Every outcome below is bounded to synthetic enterprise-shaped data and the
Firestore sandbox ledger. The flagship measurements come from one observed
hosted incident (`n=1`); they are not customer validation, production-money
impact or a population benchmark.

| Buyer outcome or judge-facing claim | Baseline or counterfactual | Mechanism that must be visible | Proof artifact |
|---|---|---|---|
| An AP operator can recover a PKR 4.275M invoice to the trusted sandbox destination after an attacker destination is proposed. | The protected agent proposed `PK-ATTACKER-9911`. Directly applying that proposal would target the wrong fingerprint; this unsafe counterfactual was never executed. | Model Armor correctly returns `CLEAR` for the clean-looking tamper. Hisaar Gate independently compares the proposal with vendor master v7 and quarantines the mismatch before any receipt. | [Verified hosted recovery](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-a171b0ff1b9644e0) and its [public incident readback](https://hisaarai-2wkruw66na-uc.a.run.app/api/incidents/inc-invoice-a171b0ff1b9644e0). |
| The interrupted work is reconstructed without reusing the quarantined destination and needs one accountable finance decision. | Stopping at quarantine leaves the legitimate invoice unfinished; automatically trusting the model would let it self-authorize. Neither is the demonstrated recovery path. | The recovery roles observe, bound and rebuild from persisted evidence and trusted vendor data. The warrant binds `PK-NSTAR-TRUSTED-8842`; the allowlisted finance operator approves once, while models retain proposal-only authority. | The same [verified recovery](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-a171b0ff1b9644e0) shows the findings, trusted vendor, warrant, approval transition and Runtime identities. |
| The observed sandbox effect occurs exactly once at the application level. | A retry without an idempotency boundary could create a second receipt. HisaarAI does not claim Pub/Sub itself provides universal exactly-once effects. | Hisaar Gate keys the receipt by the stable launch-scoped business key, persists one receipt and recomputes the warrant/source/receipt comparison on replay without mutating again. | Receipt `rcpt-4e956f47bb9d` in the [verified recovery](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-a171b0ff1b9644e0); public [replay readback](https://hisaarai-2wkruw66na-uc.a.run.app/api/incidents/inc-invoice-a171b0ff1b9644e0/replay) returns `VERIFIED` and `MATCH`. |
| Explicit prompt injection is blocked before Gemini as defense in depth. | This is a separate security fixture, not the semantic-tamper flagship and not evidence that every PDF attack is detected. | Model Armor returns `MATCH`; the incident fails closed with zero Gemini invocations and no receipt. | [Hosted Model Armor proof](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-5d86da12456b4796) and its [public readback](https://hisaarai-2wkruw66na-uc.a.run.app/api/incidents/inc-invoice-5d86da12456b4796). |
| The recovery runs on the stated governed Google Cloud agent stack. | A diagram or agent biography alone would not prove deployed use or authority separation. | The fresh video must show Runtime activity and Gate intervention; Agent Registry catalogs the two Runtime agents, Memory Bank supplies the genuine revision binding, and Model Armor screens context. | [Agent Registry readback](evidence/agent-registry.json), [continuity chain](evidence/continuity-chain.json), [architecture](media/architecture.png), hosted provenance links and the final continuous demo video. |

## Submission boundary

The final video must show the unique mechanism firing on one fresh hosted run:
the model proposes the attacker fingerprint, Hisaar Gate quarantines it before a
receipt, trusted reconstruction produces an approval-ready warrant, one human
approves, Gate persists one verified sandbox receipt, and replay returns
`MATCH`. Fleet names, Model Armor and architecture support this story; they do
not replace it.
