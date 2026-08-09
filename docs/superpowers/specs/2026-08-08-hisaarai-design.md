# HisaarAI — Judge-First Product Design

**Date:** 2026-08-09
**Track:** Fortified Enterprise Fleet
**Status:** Approved lean build specification
**Product rule:** Maximize judge-visible scoring value, not system breadth.

## 1. The product in one sentence

HisaarAI catches a compromised Accounts Payable agent before money moves,
quarantines its contaminated context, assembles a clean specialist recovery
fleet, obtains one human decision, and completes the correct sandbox payment
exactly once.

The first 30 seconds of every judge-facing artifact must make this transformation
obvious:

> A poisoned invoice compromised an AI payment agent. Hisaar stopped the money,
> quarantined the contaminated context, assembled a clean recovery team,
> obtained one human decision, and completed the correct payment exactly once.

HisaarAI is not a generic security dashboard, invoice chatbot, agent framework or
compliance simulator. It is one memorable governed-recovery product.

## 2. Score-maximization strategy

The official Stage Two rubric awards 40% for Innovation and Operational Utility,
30% for Architectural Discipline and Tech Stack, and 30% for Demo and
Production Readiness. Each retained feature must earn one of those scores or be
required for eligibility.

The overview names the current track Fortified Enterprise Fleet while the Stage
Two text still contains older Multi-Agent Nexus language. HisaarAI deliberately
satisfies both: it is an institutional fleet with persistent context and governed
data access, and it delegates a genuinely complex recovery to specialized agents
with visible failure-tolerant routing.

### 2.1 Innovation and Operational Utility — target 5/5

Judges see a concrete, high-value problem: autonomous payment agents increase
speed but can act on poisoned or semantically tampered invoices. Merely detecting
the attack still leaves the business process unfinished.

HisaarAI's twist is **safe completion after compromise**:

1. Intercept the unsafe payment proposal.
2. Quarantine the influenced execution and its derived context.
3. Reconstruct the decision from trusted vendor records.
4. Present one bounded recovery warrant to a human commander.
5. Reassign execution to a clean standby.
6. Complete one correct sandbox mutation.
7. Verify the result and replay receipt.

This is autonomous action over a messy PDF and institutional records, not a chat
response. The human makes one accountable decision; agents perform the detection,
investigation, planning, reassignment, execution and verification.

The judge-facing persona is an overstretched institutional finance operator who
cannot manually investigate every automated invoice. The demo remains a clearly
labelled sandbox and makes no claim of moving real money.

### 2.2 Architectural Discipline and Tech Stack — target 5/5

The architecture is deliberately small but real:

- **Gemini 3.6 Flash and Gemini 3.5 Flash Lite:** reasoning and structured agent
  work, with the model and thinking level visible per agent.
- **Google ADK:** distinct agent roles receiving typed bounded inputs.
- **Two callable Agent Runtime resources:** one protected AP Runtime and one
  recovery fleet Runtime, using separate runtime identities.
- **Memory Bank:** one genuine Day-0 checkpoint exists now; Day 7, Day 14 and
  Day 21 are scheduled and remain `PENDING` until their actual dates.
- **Model Armor:** direct prompt/document screening before Gemini receives the
  committed security fixture.
- **Pub/Sub:** asynchronous invoice arrival.
- **Firestore:** incident state, trusted vendor record, warrant and sandbox
  receipt.
- **Cloud Run:** the command room, Hisaar Gate and sandbox APIs.
- **Agent Observability / Cloud Trace and Logging:** one correlated trace across
  the visible recovery.

The architecture demonstrates separation through agent roles, typed bounded
inputs, separate runtime identities and deterministic authority, not through a
large number of microservices or databases. Hisaar Gate is deterministic
application code and remains the only authority allowed to approve state
transitions or release a sandbox mutation.

Failure tolerance is visible: invalid agent output, timeout or missing evidence
causes a safe `BLOCKED` outcome; compromised context is never copied into the
standby; duplicate execution returns the existing receipt.

Model Armor is fail-closed. Only an explicit successful, conclusive
`NO_MATCH_FOUND` result may release screened text to Gemini. A successful
`MATCH_FOUND` result persists `BLOCKED` with reason `MODEL_ARMOR_MATCH`.
Unavailability, transport or permission errors, partial/skipped execution,
malformed results and unknown outcomes persist
`BLOCKED` with reason `SCREENING_UNAVAILABLE`. Both blocked branches invoke
Gemini zero times and create no receipt.

### 2.3 Demo and Production Readiness — target 5/5

The public proof package contains:

- One polished command-room UI driven by persisted backend state.
- One continuous, unedited, English demo no longer than four minutes, once it is
  recorded and published; until then its status remains `PENDING`.
- Visible Google Cloud proof: `.run.app` URL, both Runtime resource identities,
  Memory Bank and a correlated trace or log view.
- A public repository with a clean architecture diagram, concise README and
  reproducible local/deployment instructions.
- One genuine flagship journey plus a short Model Armor control beat.
- A clear limitations statement: sandbox ledger, committed fixtures and observed
  demo behavior only.

Judges should not need to inspect test reports, hash manifests or raw JSON to
understand the product. Technical evidence supports the story instead of
replacing it.

## 3. Scope

### 3.1 Build

- Text-based PDF invoice intake through one Pub/Sub event.
- A committed injection-control invoice that Model Armor blocks before Gemini.
- A committed semantic-tamper invoice whose text is not an injection but whose
  bank fingerprint conflicts with the trusted vendor master.
- A committed clean invoice that follows the normal path.
- One governed recovery journey from tamper detection to verified completion.
- Six judge-visible agent roles with Urdu/Arabic names and clear responsibilities.
- One deterministic Gate, one human approval and one idempotent sandbox receipt.
- Genuine multi-week continuity artifacts created on their actual dates.
- One responsive visual command room.

### 3.2 Do not build

- Agent Gateway unless it is already enabled and takes less than two hours to
  connect after the core demo works.
- Terraform, organization-wide IAM forensics or Policy Troubleshooter evidence.
- Multiple Firestore databases, a microservice mesh or twelve custom identities.
- Custom challenge-nonce infrastructure or a bespoke cryptographic protocol.
- Research-grade evaluation, held-out custodians, statistical accuracy claims,
  P95 claims or resource-cap calibration.
- Repository-wide SHA matching, code-freeze ceremonies or content-addressed
  release manifests.
- Push-triggered GitHub CI/CD.
- Features, screens or proof panels not visible in the four-minute story.

Dependency lockfiles are retained solely so a clean checkout installs the same
dependencies. They are not release gates and do not trigger any workflow.

## 4. Lean deployment topology

### 4.1 Protected AP Runtime

Contains the primary AP agent. It may read the screened invoice view and propose
a sandbox payment. It cannot write the sandbox ledger directly.

### 4.2 Recovery Fleet Runtime

Contains Raasid, Kashif, Muslih, the clean AP standby and Shaahid. The agents have
separate ADK roles, typed outputs and bounded inputs. They may inspect bounded
incident evidence and propose recovery actions but cannot self-approve Hisaar
Gate.

### 4.3 One Cloud Run application

One deployable application contains:

- the command-room frontend and backend-for-frontend;
- authenticated invoice/event endpoints;
- deterministic Hisaar Gate transitions;
- trusted vendor-master and sandbox-ledger tool endpoints;
- read-only evidence and trace-summary endpoints.

These modules remain separate in code, but one deployment keeps development and
operations fast. State-changing handlers authenticate the caller, re-read the
authoritative warrant and use Firestore transactions.

### 4.4 One Firestore database

Collections are intentionally minimal:

- `incidents`
- `events`
- `vendor_master`
- `warrants`
- `sandbox_receipts`
- `continuity_checkpoints`

The incident document holds the current state and version. The receipt document
uses the stable launch-scoped business idempotency key so Pub/Sub redelivery or duplicate execution cannot create a
second payment.

### 4.5 Three user-managed service accounts

Use exactly `hisaar-app`, `hisaar-ap-runtime` and
`hisaar-recovery-runtime`. Every Cloud Run or Agent Runtime deployment names its
full service-account email explicitly; the default Compute Engine service account
is never used. Google-managed platform service agents may still perform their
documented control-plane work.

## 5. Agents and model routing

Only these two model identifiers are allowed at runtime:

- `gemini-3.6-flash`
- `gemini-3.5-flash-lite`

| Agent | Model | Thinking | Judge-visible job |
|---|---|---:|---|
| Protected AP Agent | `gemini-3.6-flash` | Medium | Reads screened invoice context and proposes the payment |
| Raasid — Observer | `gemini-3.5-flash-lite` | Default/minimal | Turns persisted events into a concise incident observation |
| Kashif — Investigator | `gemini-3.6-flash` | High | Explains the bounded blast radius and cites trusted evidence |
| Muslih — Recovery Planner | `gemini-3.6-flash` | High | Drafts the smallest safe recovery warrant |
| Clean AP Standby | `gemini-3.6-flash` | Medium | Executes only the approved trusted-source payment |
| Shaahid — Witness | `gemini-3.5-flash-lite` | Default/minimal | Narrates deterministic verification and replay results |

The UI displays each agent's name, model, role and current state. Runtime logs
record requested model, actual model and thinking setting. There is no silent
cross-model fallback.

Hisaar Gate, not Shaahid or another LLM, decides whether the incident becomes
`VERIFIED`.

## 6. The flagship journey

1. The user launches the committed semantic-tamper invoice from the command room.
2. Pub/Sub delivers the invoice event asynchronously.
3. Model Armor screens the exact text that will enter the AP agent and reports no
   prompt-injection match.
4. The protected AP agent proposes the invoice's altered bank fingerprint.
5. Hisaar Gate compares it with the trusted vendor master, blocks execution and
   persists `QUARANTINED`.
6. Raasid summarizes what happened from persisted events.
7. Kashif investigates only the correlated incident evidence and identifies the
   invoice as the influence source.
8. Muslih drafts a warrant using the trusted vendor record and a clean-context
   instruction.
9. Hisaar Gate materializes the authoritative warrant and ten-minute expiry.
10. The command room shows an attempted pre-approval execution returning
    `APPROVAL_REQUIRED`.
11. The authenticated commander approves the exact current warrant.
12. Hisaar Gate atomically changes the state to `APPROVED` and releases one
    execution opportunity.
13. The clean standby writes the trusted payment to the sandbox ledger.
14. Repeating the same request returns the existing receipt.
15. Deterministic checks compare warrant, vendor source and receipt; Shaahid
    narrates `MATCH`; Hisaar Gate persists `VERIFIED`.

The quick security-control beat uses a separate injection fixture. Model Armor
blocks it before the AP agent runs, producing zero proposal and zero mutation.
If Model Armor is unavailable, errored or inconclusive, the same input is blocked
safely and is never described as an attack detection.

## 7. Deterministic authority

The lean state machine is:

`DETECTED → QUARANTINED → INVESTIGATING → PLAN_READY → AWAITING_APPROVAL → APPROVED → COMPLETED → VERIFIED`

`BLOCKED` is the sole failure terminal, with a required reason.

All state changes use a Firestore transaction that checks the current state and
version. Gemini calls and external tool calls run outside transaction callbacks.

The approval boundary uses:

- a Google Sign-In ID token held in browser memory and sent as a bearer token;
- backend verification of Google's signature, issuer, expiry and the exact OAuth
  web-client audience;
- an allowlisted stable `sub` commander subject; email is display-only;
- an exact same-origin, JSON-only request;
- a server-side reload of the current warrant and trusted source version;
- a ten-minute warrant expiry; and
- one atomic `AWAITING_APPROVAL → APPROVED` transition.

There is no auth cookie or separate browser nonce collection. A duplicate or
stale approval cannot create another execution opportunity because the expected
state/version no longer matches. Human rejection persists the commander subject,
rationale and server timestamp, transitions to `BLOCKED/HUMAN_REJECTED` and
creates no execution opportunity. An expired current warrant transitions to
`BLOCKED/WARRANT_EXPIRED`; retry starts a new recovery attempt from quarantine,
retains the launch-scoped business idempotency key and creates a fresh warrant. Wrong
identity is denied without changing incident state.

Authentication is route-specific even though one Cloud Run service hosts the
application. Every Google token is checked for signature, issuer, expiry, exact
route audience and expected subject or service-account email.
`/api/commander/*` accepts only the configured Google web-client audience and
allowlisted human subject; commander mutations also require same-origin JSON.
`/internal/pubsub/events` accepts only the configured Pub/Sub push audience and
`hisaar-app` identity. Its strict discriminated envelope admits only
`invoice.received`, `continuity.checkpoint` and `recovery.execute`, each with an
event-specific idempotency key. The Cloud Run application invokes the two Vertex
Agent Runtime resources using its configured Google client credentials; runtime
resource names and separate deployed runtime identities are recorded as
provenance. There are no per-runtime HTTP tool routes. Issuer validity alone
never grants authority. The browser launch request publishes and returns; the UI
polls persisted state rather than waiting synchronously for Pub/Sub to call the
same service.

## 8. Command-room experience

The product is one connected fortress-style command room, not several dashboards.
It prioritizes comprehension over evidence density.

### 8.1 Above the fold

- Headline: **The agent was compromised. The payment was not.**
- One-sentence product explanation.
- Current incident state and amount at risk.
- Six agent cards showing role, model and live status.
- A single `Run flagship incident` action using the committed sandbox fixture.

### 8.2 Central story

- Left: invoice versus trusted vendor bank fingerprint.
- Center: animated but backend-driven recovery timeline.
- Right: warrant panel with source, intended correction, expiry and digest.
- Approval and rejection controls appear only for the commander.

### 8.3 Outcome

- `Unsafe payment: blocked`
- `Trusted payment: completed once`
- Receipt identifier and replay `MATCH`
- Shaahid verification summary
- Google Cloud provenance chips linking both Runtime resources, Memory Bank and
  correlated Trace evidence

No fake map, simulated log stream, invented latency or decorative security score
is permitted.

## 9. Genuine multi-week context

Fortified Enterprise Fleet explicitly asks how agents maintain context across
weeks of asynchronous operation. Day 0 was bootstrapped directly through the
Memory Bank API by the local deployer under the final Recovery Runtime and is the
only checkpoint that exists now. Cloud Scheduler is configured in
`Asia/Karachi` to publish date-keyed events through the authenticated Pub/Sub
boundary on Day 7, Day 14 and Day 21, but those checkpoints remain `PENDING`
until their actual dates. If created on schedule, each future checkpoint stores
a short operational fact, its prior checkpoint reference and the actual server
timestamp in Memory Bank and Firestore. Creation is date-gated and idempotent by
calendar date.

The demo shows only the real checkpoints available at recording time—currently
Day 0—and one material use: the recovery fleet retrieves the latest trusted
operational policy revision. Missing future checkpoints are labelled pending;
they are never backfilled or simulated.

## 10. Minimum reliability work

Testing exists to prevent a failed demo, not to become a submission artifact.
There is no automatic GitHub workflow.

The one local command `make demo-check` covers only these invariants:

1. Injection input and unavailable, errored or inconclusive screening never reach
   Gemini.
2. Vendor mismatch reaches `QUARANTINED` with no receipt.
3. Execution before approval is denied.
4. Wrong or expired approval is denied.
5. The clean standby cannot use contaminated context.
6. Duplicate execution returns one stable receipt.
7. Verification cannot pass when warrant, source and receipt disagree.
8. The clean control completes normally.

Before recording, run the flagship end to end until two timed rehearsals complete
cleanly. Report only what was observed; do not claim population accuracy,
guaranteed latency or exhaustive least privilege.

## 11. Four-minute judge experience

- **0:00–0:20 — Hook:** “Would you let an AI agent pay this invoice?” Show the
  altered bank fingerprint and the amount at risk.
- **0:20–0:40 — First defense:** launch the injection fixture; Model Armor blocks
  it before Gemini.
- **0:40–1:15 — The harder attack:** launch the semantic-tamper fixture. Screening
  clears it, the AP agent proposes the wrong destination, and Hisaar quarantines
  it before payment.
- **1:15–2:05 — The fleet recovers:** Raasid observes, Kashif investigates and
  Muslih produces the trusted-source warrant. Keep their outputs to one readable
  sentence each.
- **2:05–2:35 — Governance:** show pre-approval denial, then approve the exact
  warrant as the human commander.
- **2:35–3:05 — Safe completion:** the clean standby completes once; repeat returns
  the same receipt; Shaahid reports `MATCH`; Gate shows `VERIFIED`.
- **3:05–3:35 — Platform proof:** show both Agent Runtime resources, the
  correlated Google Cloud trace and genuine Memory Bank checkpoints available
  at recording time.
- **3:35–4:00 — Close:** restate the business outcome and architecture in one
  sentence: Hisaar does not merely detect a compromised agent; it safely finishes
  the work.

The recording is one continuous normal-speed take. The UI, not a terminal, carries
the story.

## 12. Submission package

Stage One is protected with a simple checklist:

- Correct Fortified Enterprise Fleet category selected.
- Gemini 3.5-or-newer requirement satisfied by the two allowed models.
- Google ADK and Google Cloud usage stated plainly.
- Hosted project URL or clear testing instructions.
- Public repository URL.
- Concise feature/technology/findings write-up.
- Reproducible spin-up instructions in `README.md`.
- Clean architecture diagram.
- Public English video no longer than four minutes with visible Google Cloud
  deployment proof.
- New-project provenance and disclosure of standard libraries/tools.

The optional public build article and social post are created only after the core
submission is complete. They must not delay the product or video.

## 13. Score-preserving cut rule

Before accepting any task, ask:

1. Is it required for eligibility?
2. Will a judge see it in four minutes?
3. Does it materially strengthen one of the 40/30/30 rubric categories?
4. Does it prevent the flagship demo from failing?

If all four answers are no, cut the task.

## 14. Definition of ready

HisaarAI is ready when:

- the two real fixtures visibly produce the promised block and recovery paths;
- the flagship ends with one correct sandbox receipt and replay `MATCH`;
- all six agents have readable, distinct roles and truthful model provenance;
- the command room makes the business value understandable within 30 seconds;
- the video, once publicly recorded, shows an unedited live action and visible
  Google Cloud proof;
- the real continuity checkpoints available by submission time are shown without
  fabrication;
- the repository contains the required diagram and setup instructions; and
- every public claim is narrower than or equal to the demonstrated behavior.

No test-count threshold, SHA ceremony, CI badge or infrastructure breadth is part
of readiness.
