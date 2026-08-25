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
reconstruct a trusted-source warrant; Clean AP validates the exact approved
request; Hisaar Gate, running under the application persistence identity,
commits the idempotent sandbox receipt and performs deterministic verification.
Shaahid narrates that comparison; only Gate can mark the incident verified.

In one observed hosted run (`n=1`), a protected AP agent proposed an attacker
destination for a PKR 4.275M synthetic invoice. HisaarAI quarantined it before
any receipt in 3.72 seconds and reached approval-ready in 29.8 seconds. After one
accountable human decision, automated execution and verification took 11.5
seconds and produced one trusted sandbox receipt. A public read-only replay
returned that same receipt with `MATCH`. The 71.7-second end-to-end time includes
30.4 seconds of human review. This is an observed sandbox transformation, not a
generalized performance, customer-deployment or production-money claim.

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

Memory Bank stores a genuine Day-0 → Day-7 → Day-14 predecessor chain under the
final Recovery Runtime. The scheduled Day-7 and Day-14 deliveries initially hit
a Vertex API validation change; after a one-line request fix on August 25, the
original jobs were recovered without backdating their real creation times. The
recovery path consumes a Firestore checkpoint mirror bound to the exact genuine
Memory Bank revision resource name; the fresh flagship warrant preserves the
resulting Day-14 binding. Day-21 remains pending until its scheduled date.

## Other data sources

The demonstration uses synthetic PDF fixtures as incoming evidence, a Firestore
vendor master as the trusted bank-detail source, and a Firestore sandbox ledger
as the receipt authority. No customer invoice, production ERP or real bank is
connected. The organizer publicly confirmed that this live Google Cloud pattern
with synthetic or de-identified data and the required controls satisfies the
Fortified Enterprise Fleet production-data language.

## What makes it different

Most agent-security demos stop after detection. HisaarAI proves the harder
enterprise outcome: safely finish the interrupted work without letting an LLM
self-approve, copying quarantined context, or paying twice. Its command room
makes the trust boundary visible to a non-technical judge in seconds.

## Why now

On August 25, Google Cloud [introduced Gemini Enterprise for Financial
Services](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-for-financial-services)
around specialized financial skills, secure data connections, acting agents and
centralized governance. HisaarAI explores the complementary recovery problem:
when a financial agent's context is poisoned, how can the institution contain
it, reconstruct trusted context and safely finish the work exactly once?
HisaarAI demonstrates aligned design principles; it does not claim integration
with the preview product.

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
- Verified Day-0 → Day-7 → Day-14 Memory Bank chain with real creation times and Day-21 pending
- Official Agent Registry discovery of exactly the two HisaarAI Runtime agents
- One responsive command room with live Google provenance

## Built with

Gemini 3.6 Flash, Gemini 3.5 Flash-Lite, Google ADK, two Agent Runtime resources,
Agent Registry, Memory Bank, Model Armor, Vertex AI, Cloud Run, Pub/Sub, Cloud
Scheduler, Firestore, Cloud Logging, Cloud Trace, FastAPI, React and Vite.

## Links to fill at submission

- Live app: <https://hisaarai-2wkruw66na-uc.a.run.app/>
- Public read-only verified recovery: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-1f8fa7d20b0e49b2>
- Public read-only Model Armor block: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-5d86da12456b4796>
- Public read-only clean control: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-473fbd809fca4195>
- Public repository: <https://github.com/asadvendor-boop/HisaarAI>
- Agent Registry evidence: <https://github.com/asadvendor-boop/HisaarAI/blob/main/docs/evidence/agent-registry.json>
- Demo video: `PENDING`
- Optional public article candidate: <https://github.com/asadvendor-boop/HisaarAI/blob/main/docs/BUILD_ARTICLE.md> (bonus eligibility/acceptance not confirmed)

## Required eligibility answers

- Google SDK/framework: Google Agent Development Kit (`google-adk==2.6.3`)
- Project start date: August 8, 2026
- Pre-existing/third-party disclosure: HisaarAI was created during the hackathon
  submission period. It uses open source Python, JavaScript and Google Cloud SDK
  dependencies declared in its lockfiles. No pre-existing product code or
  customer data was incorporated.

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
