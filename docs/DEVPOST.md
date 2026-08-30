# Devpost submission draft

## Project name

HisaarAI — Governed Recovery for Compromised Agent Fleets

## Tagline

The agent was compromised. The payment was not.

## Track

Fortified Enterprise Fleet

## What it does

HisaarAI is for the finance approver whose routine job is to release one supplier
invoice to the correct bank. In one observed synthetic-sandbox run (`n=1`), a
compromised AP agent proposed an attacker destination for a PKR 4.275M invoice.
HisaarAI quarantined that proposal before any receipt, rebuilt the work from
trusted vendor data, obtained one finance approval, and produced one verified
sandbox receipt whose public read-only replay returned `MATCH`.

Model Armor blocks an obvious injection before Gemini; deterministic Hisaar Gate
catches the harder clean-looking bank-detail tamper that content screening
correctly clears. The recovery roles observe, bound and rebuild from trusted
sources. Agents propose; Hisaar Gate decides; the finance approver approves.
Hisaar Gate is an application-level deterministic authority layer in Cloud Run
and Firestore, not a claim of using Google's managed Agent Gateway product.

The observed sandbox run quarantined in 11.62 seconds and reached approval-ready
in 34.60 seconds. After the one human decision, automated execution and
verification took 7.01 seconds. The 55.41-second end-to-end time includes 13.80
seconds of human review. These are run-specific observations, not a generalized
performance, customer-deployment or production-money claim.

## How we built it

HisaarAI uses Google ADK on two callable Agent Runtime resources. The protected
AP agent uses Gemini 3.7 Flash; the recovery Runtime contains five distinct ADK
roles routed across Gemini 3.7 Flash and Gemini 3.5 Flash-Lite with explicit
thinking levels. An official Agent Registry readback discovers exactly those two
HisaarAI Runtime agents and their separate identities; Registry is catalog proof,
not approval authority. Cloud Run hosts one FastAPI/React command room, Pub/Sub
provides authenticated asynchronous delivery, Model Armor screens the PDF text
and exact model input, Firestore holds the transactional authority and
idempotent sandbox receipt, and Cloud Trace correlates the journey.

Memory Bank now holds a genuine Day-0 → Day-7 → Day-14 → Day-21 predecessor
chain under the final Recovery Runtime. The scheduled Day-7 and Day-14 deliveries
initially hit a Vertex API validation change; after a one-line request fix on
August 25, the original jobs were recovered without backdating their real
creation times. The scheduled Day-21 delivery succeeded on August 30 and links
to the Day-14 revision. The recovery path consumes a Firestore checkpoint mirror
bound to the exact genuine Memory Bank revision resource name; the flagship
warrant retains its demonstrated Day-21 binding.

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
- Verified Day-0 → Day-7 → Day-14 → Day-21 Memory Bank predecessor chain with real creation times
- Official Agent Registry discovery of exactly the two HisaarAI Runtime agents
- One responsive command room with live Google provenance

## Built with

Gemini 3.7 Flash, Gemini 3.5 Flash-Lite, Google ADK, two Agent Runtime resources,
Agent Registry, Memory Bank, Model Armor, Vertex AI, Cloud Run, Pub/Sub, Cloud
Scheduler, Firestore, Cloud Logging, Cloud Trace, FastAPI, React and Vite.

## Links to fill at submission

- Live app: <https://hisaarai-2wkruw66na-uc.a.run.app/>
- Public read-only verified recovery: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-a171b0ff1b9644e0>
- Public read-only Model Armor block: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-5d86da12456b4796>
- Public read-only clean control: <https://hisaarai-2wkruw66na-uc.a.run.app/?incident=inc-invoice-473fbd809fca4195>
- Public repository: <https://github.com/asadvendor-boop/HisaarAI>
- Judge claim map: <https://github.com/asadvendor-boop/HisaarAI/blob/main/docs/CLAIM_MAP.md>
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
