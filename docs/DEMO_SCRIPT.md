# HisaarAI — edited demo under four minutes

The organizers explicitly encourage short clips, jump cuts, trimmed waits,
on-screen labels and one strong example. Do not record a continuous live model
run. Every clip must still show the real hosted app and persisted Google Cloud
evidence.

## Before recording

1. Use a 16:9 browser window at 1440×900 or 1920×1080, browser zoom 80–90%,
   notifications silenced, and the hosted app already signed in.
2. Prepare these real states in separate tabs:
   - [fresh verified recovery](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-aba694bdd8ee48e0)
   - [Model Armor block](https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-5d86da12456b4796)
   - live Agent Registry, Firestore, Model Armor and Cloud Trace links
   - repository architecture diagram
3. Record short clips. Cut loading, polling, account selection and dead air. Do
   not type live. Keep the final edit below 3:40 to preserve upload margin.
4. Add concise on-screen labels and accurate English narration. Show the app
   working within the first ten seconds.

## 0:00–0:18 — Outcome first

Open directly on the fresh `VERIFIED` recovery. Show the `BEFORE / CONTROL /
AFTER` strip, trusted receipt and `MATCH`.

> “A protected AP agent proposed sending a synthetic PKR 4.275 million invoice
> to an attacker-controlled destination. HisaarAI quarantined it before any
> receipt, obtained one human decision, and finished once at the trusted
> destination. The agent was compromised. The payment was not.”

On-screen: `OBSERVED SANDBOX RUN / n=1`.

## 0:18–0:38 — Before and deterministic control

Point to `PK-ATTACKER-9911`, Model Armor `CLEAR`, vendor-master v7
`PK-NSTAR-TRUSTED-8842`, and `QUARANTINED BEFORE UNSAFE RECEIPT`.

> “This harder fixture contains no obvious injection. Model Armor correctly
> clears it. Gemini proposes the invoice value, but deterministic Hisaar Gate
> catches the trusted-source mismatch because the LLM never owns execution.”

On-screen: `31.9s TO QUARANTINE / ZERO UNSAFE RECEIPTS`.

## 0:38–1:05 — Fleet and trusted reconstruction

Show the three specialist cards and read only their first sentence: Raasid
observes persisted evidence, Kashif bounds the blast radius to one unexecuted
proposal, and Muslih reconstructs the smallest correction from the vendor
master.

> “Separate roles get typed, bounded context. Quarantined invoice text never
> enters the clean standby. The recovery fleet reached approval-ready in 54.0
> seconds.”

## 1:05–1:30 — Memory and human boundary

Open the continuity chip: Day‑0, recovered Day‑7, recovered Day‑14 and pending
Day‑21. Point to the Day‑14 revision on the exact warrant, its digest, trusted
destination and ten-minute expiry. Use the short clip showing your real click on
`APPROVE EXACT WARRANT`.

> “The scheduled Day‑7 and Day‑14 events were recovered after a Vertex request
> validation change; their real creation times remain visible. This warrant
> binds the latest Day‑14 revision. Only the allowlisted Google commander can
> approve its exact server-rederived digest.”

## 1:30–1:55 — Finish exactly once

Cut to the completed state. Show the one receipt, recovery-runtime identity,
trusted fingerprint, Shaahid narrative and Gate `VERIFIED`. Click the public
`VERIFY ONE-RECEIPT REPLAY` button and show `MATCH / rcpt-5937483c4bcb`.

> “After approval, execution and deterministic verification took 10.8 seconds.
> Shaahid explains the result but cannot mark it verified. Replaying returns the
> same receipt; no second mutation is created.”

On-screen: `HUMAN REVIEW SHOWN SEPARATELY / TOTAL INCLUDES HUMAN TIME`.

## 1:55–2:12 — First-line defense

Jump to the persisted Model Armor control proof. Show `MATCH`, Protected AP
`WITHHELD`, zero Gemini invocations and no receipt.

> “For an obvious prompt injection, the exact extracted text is blocked before
> Gemini. If screening is unavailable or inconclusive, the Gate also fails
> closed.”

## 2:12–2:50 — Real Google Cloud proof

Show the `.run.app` address, exactly two Agent Registry entries, the two Runtime
resources with separate user-managed identities, Firestore authority, Model
Armor, the correlated six-span Trace, and the Day‑14 Memory revision.

> “These are live Google resources, not UI labels: Gemini 3.6 Flash and 3.5
> Flash‑Lite through Google ADK, two Agent Runtimes, Agent Registry, Memory Bank,
> Model Armor, Pub/Sub, Cloud Run, Firestore and Cloud Trace. Registry discovers
> agents; deterministic Gate code and the human retain authority.”

## 2:50–3:15 — Architecture and buyer value

Show the architecture diagram. Trace one line from invoice ingestion to
screening, proposal, Gate quarantine, clean reconstruction, human approval,
sandbox receipt and verification.

> “Accounts-payable teams need more than an alert. HisaarAI contains a poisoned
> agent and safely finishes interrupted work without copying contaminated
> context, self-approving, or paying twice.”

## 3:15–3:30 — Honest close

Return to the final `BEFORE / CONTROL / AFTER` strip.

> “This is one observed run on synthetic PDFs, a Firestore vendor master and a
> sandbox ledger—not a customer deployment or real-money claim. HisaarAI makes
> the enterprise recovery boundary visible, governed and replayable.”

## Public upload metadata

**Title:** HisaarAI — Governed Recovery for Compromised Agent Fleets | All Things Agentic 2026

**Description:**

> HisaarAI contains a compromised enterprise agent, excludes contaminated
> context, obtains one accountable human decision, and safely completes the
> interrupted work. This edited live-product demo shows real Google Model Armor,
> Gemini 3.6 Flash and 3.5 Flash-Lite agents through Google ADK, Agent Runtime,
> Memory Bank, Pub/Sub, Firestore and Cloud Trace.
>
> Track: Fortified Enterprise Fleet — All Things Agentic Hackathon 2026
>
> Live app: https://hisaarai-2wkruw66na-uc.a.run.app/
>
> Source: https://github.com/asadvendor-boop/HisaarAI
>
> #AllThingsAgenticHackathon #Gemini #GoogleCloud

Set visibility to **Public** and use a clean 16:9 frame showing the final
`VERIFIED` state as the thumbnail.
