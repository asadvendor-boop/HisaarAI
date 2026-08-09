# Devpost submission draft

## Project name

HisaarAI — Governed Recovery for Compromised Agent Fleets

## Tagline

The agent was compromised. The payment was not.

## Track

Fortified Enterprise Fleet

## What it does

HisaarAI is a visual command room for Accounts Payable Operations leaders. It
contains a compromised enterprise agent,
excludes its contaminated context, and safely completes the business process
through a clean specialist fleet and one accountable human decision. In the live
Accounts Payable journey, real Model Armor blocks an obvious injection before
Gemini, while deterministic Hisaar Gate catches a harder semantic bank-detail
tamper that a content filter correctly clears. Raasid, Kashif and Muslih
reconstruct a trusted-source warrant; the clean AP standby executes it once;
Shaahid narrates the deterministic receipt comparison; only Gate can mark the incident
verified.

In one observed hosted run (`n=1`), a protected AP agent proposed an attacker
destination for a PKR 4.275M synthetic invoice. HisaarAI quarantined it before
any receipt in 41.1 seconds, obtained one accountable approval, and produced one
verified sandbox receipt to the trusted destination at 88.0 seconds. A public
read-only replay returned that same receipt with `MATCH`. This is the observed
demo transformation, not a generalized performance, customer-deployment or
production-money claim.

## How we built it

HisaarAI uses Google ADK on two callable Agent Runtime resources. The protected
AP agent uses Gemini 3.6 Flash; the recovery Runtime contains five distinct ADK
roles routed across Gemini 3.6 Flash and Gemini 3.5 Flash-Lite with explicit
thinking levels. An official Agent Registry readback discovers exactly those two
HisaarAI Runtime agents and their separate identities; Registry is catalog proof,
not approval authority. Cloud Run hosts one FastAPI/React command room, Pub/Sub
provides authenticated asynchronous delivery, Model Armor screens the PDF text
and exact model input, Firestore holds the transactional authority and
idempotent sandbox receipt, and Cloud Trace correlates the journey.

Memory Bank stores a genuine Day-0 revision under the final Recovery Runtime,
with Day-7/14/21 checkpoints scheduled against the same endpoint. The recovery
fleet materially reads the latest immutable revision to select trusted-vendor
reconstruction; missing future dates are shown as pending, never fabricated.

## Other data sources

The demonstration uses synthetic PDF fixtures as incoming evidence, a Firestore
vendor master as the trusted bank-detail source, and a Firestore sandbox ledger
as the receipt authority. No customer invoice, production ERP or real bank is
connected.

## What makes it different

Most agent-security demos stop after detection. HisaarAI proves the harder
enterprise outcome: safely finish the interrupted work without letting an LLM
self-approve, copying quarantined context, or paying twice. Its command room
makes the trust boundary visible to a non-technical judge in seconds.

## Findings and learnings

The most difficult boundary was preserving useful multi-agent reasoning without
making model output authoritative. We solved this with short typed role outputs,
clean-session execution input, a ten-minute Gate-owned warrant, Firestore state
and version transactions, and one receipt keyed by the stable launch-scoped
business key. We also calibrated Model Armor honestly: the committed injection is blocked
on exact extracted text, while the semantic tamper clears screening and is caught
by the trusted-source Gate.

The main learning was that role separation is useful only when authority is also
separated: agents interpret variable evidence, but typed bounded inputs limit
what crosses contexts, separate runtime identities isolate execution surfaces,
and deterministic Gate code plus the commander decide whether work may proceed.

## Accomplishments

- Real block-before-Gemini and semantic-tamper quarantine in one product
- Five specialized recovery roles on the final-named Recovery Runtime
- One human decision followed by one idempotent sandbox receipt
- Deterministic verification that cannot be overruled by the witness agent
- Genuine Day-0 Memory Bank evidence, with Day-7/14/21 capture scheduled on their real dates
- Official Agent Registry discovery of exactly the two HisaarAI Runtime agents
- One responsive command room with live Google provenance

## Built with

Gemini 3.6 Flash, Gemini 3.5 Flash-Lite, Google ADK, two Agent Runtime resources,
Agent Registry, Memory Bank, Model Armor, Vertex AI, Cloud Run, Pub/Sub, Cloud
Scheduler, Firestore, Cloud Logging, Cloud Trace, FastAPI, React and Vite.

## Links to fill at submission

- Live app: <https://hisaarai-2wkruw66na-uc.a.run.app/>
- Public read-only verified recovery: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-fbd18054a45e4c77>
- Public read-only Model Armor block: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-5d86da12456b4796>
- Public read-only clean control: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-473fbd809fca4195>
- Public repository: <https://github.com/asadvendor-boop/HisaarAI>
- Agent Registry evidence: <https://github.com/asadvendor-boop/HisaarAI/blob/main/docs/evidence/agent-registry.json>
- Demo video: `PENDING`
- Optional public article candidate: <https://github.com/asadvendor-boop/HisaarAI/blob/main/docs/BUILD_ARTICLE.md> (bonus eligibility/acceptance not confirmed)

## Testing instructions

Open either read-only proof link to inspect a genuine hosted incident without an
account. New launches and the exact-warrant approval are intentionally limited
to the allowlisted Incident Commander. The verified-recovery link is expected to
show the attacker proposal, quarantine, trusted destination, one receipt,
deterministic `MATCH` and `VERIFIED`. A judge can click the public read-only
receipt replay to recompute the warrant/source/receipt comparison and return the
same receipt without any mutation. The Model Armor link is expected to show
`MATCH`, zero Gemini calls and no receipt. Demo video: `PENDING` until a public
URL exists.
