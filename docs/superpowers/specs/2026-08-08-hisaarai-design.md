# HisaarAI Product Design

**Status:** Approved product direction; revised after technical review
**Date:** 2026-08-08  
**Hackathon:** All Things Agentic  
**Primary category:** The Fortified Enterprise Fleet  
**Primary prize target:** Fortified Enterprise Fleet  
**Fallback prize routes:** Best Architectural Design, Individual/Hobbyist, Grand Prize, Honorable Mention

## 1. Product thesis

**HisaarAI — The Agent Fleet Recovery Command Room**

**Tagline:** Contain the agent. Preserve the mission.

HisaarAI is an enterprise-agent recovery control plane. When a business agent
encounters unsafe content, HisaarAI blocks unsafe action, places the affected
principal, instance and session under a Hisaar Gate execution quarantine,
reconstructs trusted context, and resumes the interrupted business workflow with
a clean agent under one governed human approval.

Most agent-security products stop an unsafe execution. HisaarAI differentiates
itself by providing **safe continuity**: it contains the incident and still
finishes the authorized business task with one idempotently unique sandbox
mutation.

The reference workflow is sandbox accounts payable and uses two deliberately
separate fixtures through the same pipeline:

1. A security-control PDF contains an approved prompt-injection test signal.
   Direct Model Armor screening must block it before any agent consumes it.
2. The flagship recovery PDF contains no injection language but carries a
   synthetic remittance-profile identifier that conflicts with the versioned
   vendor master. Model Armor must pass the content-security check, the protected
   AP agent must propose the influenced action, and Hisaar Gate must deny that
   action before mutation, apply its execution quarantine to the affected session
   and recover the business task through a clean standby.

The first fixture proves perimeter screening; it is never presented as agent
recovery. The second proves the differentiator: deterministic business authority
can contain unsafe context that a content-security control is not designed to
classify, then complete one correct sandbox ERP mutation.

## 2. Judging strategy

HisaarAI is designed against both the selectable **Fortified Enterprise Fleet**
category and the binding rules' older **Multi-Agent Nexus** language.

### Innovation and operational utility — 40%

- The system starts from an event, not a chat prompt.
- Agents perform detection triage, investigation, recovery planning and
  verification autonomously.
- The human supplies one bounded approval rather than conducting the diagnosis.
- The protected business workflow finishes safely instead of remaining stopped.
- Stored evaluation runs measure containment, continuity, duplicate prevention
  and trusted-context integrity.

### Architectural discipline and technology — 30%

- Distinct ADK agents have separate roles, role-scoped tool adapters and typed
  outputs. Because the four roles share one Recovery Runtime identity, the design
  claims application-level tool separation, not four different IAM principals.
- A deterministic state machine is the sole execution and release authority.
- Model Armor, Agent Runtime, Memory Bank, Agent Registry, scoped identity,
  Pub/Sub, Firestore and Cloud observability are used as real services when
  claimed.
- All event handling and business mutation are idempotent.
- Invalid schemas, stale approvals, unavailable security controls and verification
  mismatches fail closed.

### Demo and production readiness — 30%

- The core video sequence is one continuous live run.
- Every command-room state is backed by a persisted backend event.
- The video visibly shows a real Model Armor verdict, Google Cloud deployment,
  Registry entry, trace correlation, Firestore state and replay result.
- The repository contains reproducible setup, deployment and evaluation
  instructions.

## 3. Scope

### In scope

- One protected Accounts Payable agent version with a primary deployment and a
  pre-provisioned clean standby deployment.
- One HisaarAI recovery orchestrator containing four specialized agents.
- One registered, authenticated Cloud Run sandbox ERP JSON API exposed as a typed
  ADK tool; MCP is not required for the reference workflow.
- One invoice-received Pub/Sub event.
- One approved prompt-injection security fixture, one semantic-tamper flagship
  fixture and a stored clean-control set.
- One governed recovery approval.
- One idempotently unique sandbox ledger mutation.
- One evidence replay and one command-room UI.

### Explicitly out of scope

- A generic enterprise-security platform.
- A large agent marketplace.
- Real payment execution or real financial data.
- Multiple business domains before the reference workflow passes.
- Simulated weeks of memory or fabricated production history.
- LLM-controlled authorization, identity grants or release decisions.
- Decorative traces, metrics, Registry entries or Model Armor verdicts.
- Custom substitutes presented as Google Agent Gateway, Agent Identity or Agent
  Registry.
- Preview-only Google platform services as dependencies of the core recovery
  path. The user-approved `gemini-3.1-pro-preview` investigator is the one explicit
  model exception and must pass deployment preflight.
- CreditLock code, assets or workflows.

## 4. Deployment topology

Use one Google Cloud project with regional infrastructure in `us-central1`.
Every locked Gemini request uses explicitly validated ADK/Gen AI `global`
configuration so the three-model route has one tested model endpoint;
`gemini-3.6-flash` and
`gemini-3.5-flash-lite` also support the `us` and `eu` multi-regions, while
`gemini-3.1-pro-preview` currently supports only `global`. Runtime, Memory, Model
Armor, Firestore, Pub/Sub and Cloud Run location metadata remain explicit in
provenance.

### Managed agent runtimes

1. **Protected AP Primary Runtime**
   - Processes the sandbox invoice workflow.
   - Uses Gemini 3.6 Flash with medium thinking.
   - Has access only to the registered invoice reader and sandbox ERP proposal
     tool.
   - Cannot bypass Hisaar Gate for business mutation.

2. **Protected AP Standby Runtime**
   - Is deployed before the release run; deployment is never part of the hot
     recovery path.
   - Runs the same AP agent version with a different runtime resource, service
     identity, session namespace and memory namespace.
   - Starts each recovery in a fresh session and receives only the Gate-approved
     clean recovery package, never the source PDF or quarantined session memory.
   - Remains unable to mutate the sandbox ledger directly.

3. **HisaarAI Recovery Runtime**
   - Contains Raasid, Kashif, Muslih and Shaahid as specialized ADK agents.
   - Exposes typed recovery skills.
   - Uses Memory Bank only for explicitly trusted cross-session context.

All three Runtime resources must be visible as real Agent Registry entries. The
sandbox ERP Cloud Run API is registered as a typed ADK tool. The design does not
create four separate recovery runtimes merely to make the four recovery roles
look distributed.

### Supporting services

- **Cloud Run:** hosts five services: an IAM/OIDC-only event-intake/Gate machine
  API, an IAP-protected command-room web/BFF for human reads and approvals, the
  screened invoice reader, the isolated document extractor and the sandbox ERP.
  Pub/Sub and Runtime callbacks never traverse the IAP-protected service.
- **Typed tool boundary:** the screened invoice reader and sandbox ERP are
  authenticated Cloud Run JSON services surfaced as explicit ADK tools. Runtime
  callers use Google-signed OIDC service tokens; Cloud Run grants invocation at
  service scope, while each receiving app verifies the caller and enforces its
  route allowlist. There is no undecided MCP branch.
- **Pub/Sub:** pushes only to the IAM/OIDC event-intake service. Delivery is
  treated as at least once; equivalent publishes, redelivery and out-of-order
  arrival are expected conditions.
- **Firestore:** uses one named authority database written only by Hisaar Gate and
  one named sandbox-ERP database written only by the ERP principal. Authority
  state includes event history, processing leases, warrants, approvals, consumed
  nonces, execution leases, verification and evaluation; the ERP database holds
  business mutations and receipts. Project IAM bindings use exact positive
  `resource.name` conditions for each database because server clients bypass
  Firestore Security Rules; cross-database calls are live negative tests.
- **Document extractor:** runs as a separate, non-root, resource-bounded Cloud Run
  service with a minimally privileged identity, no Firestore, Gemini or ERP
  access, an ephemeral filesystem and all egress routed through a dedicated VPC
  subnet with deny rules and no NAT. A live denial test supports the network-
  isolation claim. It returns normalized text plus raw-file and extracted-text
  digests.
- **Model Armor:** is structurally embedded in the only invoice-reader service the
  agents can call. The reader submits original PDF bytes with `byteDataType=PDF`,
  then screens the exact normalized extracted text that would be released to
  Gemini. Uploads over 4 MB, `EXECUTION_SKIPPED`, inconclusive results and service
  failures all fail closed. It returns a typed envelope to Gate for persistence;
  the reader has no Firestore write role. Embedded PDF images are explicitly
  outside the screening claim.
- **Memory Bank:** stores contextual facts while authority metadata pins the exact
  immutable Memory Revision name, fact digest, checkpoint label, creation time and
  returned expiration. Revisions use an explicit 365-day TTL and lineage/phase
  labels. “Gate-certified” is HisaarAI application status, not a claimed native
  Google verification state.
- **Agent Observability:** exports real logs, metrics and trace spans with shared
  correlation identifiers.
- **Runtime identity:** the core direct-Cloud-Run path always uses three distinct
  custom Runtime service accounts and ordinary service-account ID tokens. A
  broad no-Memory custom role derived from `roles/aiplatform.user` may be bound
  only during the initial permission-discovery spike; it is explicitly not a
  least-privilege proof and is removed before Memory, Day-0 or product evidence.
  The core and release use a versioned, reviewed data-plane allowlist containing
  only permissions proven necessary by the exact remote model/session call graph.
  It excludes all Memory permissions and Runtime, endpoint, job, dataset and IAM
  administration. Exact role-permission intersection, a complete direct and
  inherited binding inventory, Policy Troubleshooter results on real project and
  Runtime resources, and live data-plane positives prove the boundary;
  `testIamPermissions` is optional corroboration, never authorization evidence.
  Only Recovery Runtime additionally receives conditional
  `roles/aiplatform.memoryUser` for the exact continuity scope. Agent Identity is
  considered only with an optional, separately proven Agent Gateway mTLS/DPoP
  path and is never treated as interchangeable with Google-JWKS OIDC.
- **Commander authentication:** the command-room Cloud Run service is protected
  by Identity-Aware Proxy. The backend verifies the signed IAP assertion's
  issuer, Cloud Run resource audience, expiration and subject, then requires that
  stable subject in the Incident Commander allowlist. State-changing requests
  also require an origin-bound CSRF token and exact allowed origin; wildcard CORS
  is forbidden. First use in a no-organization project is bootstrapped through
  Google's required Console/custom-OAuth flow and then adopted by Terraform;
  invalid audience/expiry proofs use IAP's own `SECURE_TOKEN_TEST` assertions,
  not client-injected headers.
- **Agent Gateway:** target enhancement for the registered sandbox ERP route. It
  is introduced only after the core direct Model Armor path works. If the project
  or region cannot support it reliably, it is omitted and not imitated.

## 5. Agent model routing and authority

Only the following model identifiers may appear in HisaarAI runtime code,
configuration, tests, documentation and claims:

- `gemini-3.6-flash`
- `gemini-3.5-flash-lite`
- `gemini-3.1-pro-preview`

| Component | Model | Configuration | Authority boundary |
| --- | --- | --- | --- |
| Protected AP Agent | `gemini-3.6-flash` | Medium thinking | Proposes tool actions; cannot mutate the ledger directly |
| Raasid — Observer | `gemini-3.5-flash-lite` | Default/minimal | Creates structured incident observations only |
| Kashif — Investigator | `gemini-3.1-pro-preview` | Default | Only Pro stage; produces a read-only blast-radius report |
| Muslih — Recovery Planner | `gemini-3.6-flash` | High thinking | Drafts a recovery warrant; cannot approve or execute it |
| Shaahid — Witness | `gemini-3.5-flash-lite` | Default/minimal | Reports deterministic verification-tool results |
| Hisaar Gate | None | Deterministic code | Sole transition, execution and release authority |

Raasid, Kashif, Muslih and Shaahid share the Recovery Runtime's effective cloud
principal. Their least-privilege boundary is therefore enforced by the ADK agent
tool registry, typed input capabilities and Hisaar Gate policy rather than
misrepresented as per-agent IAM. Tests must prove that each role cannot resolve
or invoke another role's adapter. Primary AP, standby AP and Recovery Runtime do
retain distinct cloud principals.

The identifiers live in one validated release configuration rather than role
code or test literals:

- `MODEL_AP_PRIMARY=gemini-3.6-flash`
- `MODEL_AP_STANDBY=gemini-3.6-flash`
- `MODEL_RAASID=gemini-3.5-flash-lite`
- `MODEL_KASHIF=gemini-3.1-pro-preview`
- `MODEL_MUSLIH=gemini-3.6-flash`
- `MODEL_SHAAHID=gemini-3.5-flash-lite`
- `THINKING_AP=MEDIUM`
- `THINKING_MUSLIH=HIGH`

Startup validation rejects missing values, unapproved identifiers or a role
mapping different from this table. The release manifest records the configuration
digest. Model aliases or regional suffixes are not silently substituted: the
platform spike must prove these exact identifiers, features, quota and endpoint
availability in the target project. A failed check stops the release and requires
an explicit user decision.

There is no automatic cross-model fallback. A transient request may retry the
same model once using the same idempotency and correlation identifiers. A second
failure leaves the workflow blocked. Every invocation records requested model,
actual model, thinking level, attempt number and `fallback=false`.

The mandatory stack rule requires Gemini 3.5 or newer; HisaarAI substantially
uses 3.5 Flash-Lite and 3.6 Flash and therefore implements that required stack.
The rules do not expressly prohibit an additional older model, but using 3.1 Pro
Preview in a required stage creates interpretation risk. Written organizer
clarification is a pre-freeze compliance gate. Until then, Kashif remains on the
user-locked model and the risk is reported rather than hidden or silently routed
away.

## 6. Agent contracts

Agents communicate with typed JSON contracts rather than prose handoffs.

### Raasid output: `IncidentObservation`

- Incident and execution identifiers
- Model Armor verdict reference
- Artifact digest and trust classification
- Observed tool, agent and session identifiers
- Exact content-release timestamp and source-session taint boundary
- Detection timestamp and trace identifier
- Proposed severity with bounded enum values
- One allowlisted recovery-playbook class
- A bounded `EvidenceAcquisitionRequest` naming the exact evidence classes Kashif
  should receive

Raasid does more than reformat events: it distinguishes ingress-only containment
from influenced-session recovery and chooses a fixed playbook/evidence-request
shape. Hisaar Gate rejects unknown playbooks, query expansion and uncited input.

### Kashif output: `BlastRadiusReport`

- Affected execution, sessions, memory identifiers and tools
- Last trusted checkpoint identifier
- Explicitly excluded artifact and context digests
- Evidence references for every conclusion
- Query window, event count and whether the evidence cap was reached
- Unknowns and abstentions
- Confidence fields used only for display, never authorization

Kashif receives a deterministic evidence bundle rather than project-wide search
access. It is restricted to the incident correlation identifier, source session,
invoice and tool-call chain, from five minutes before the unsafe proposal through
sixty seconds after quarantine, with at most 200 trace spans and 200 Firestore
events. Direct checkpoint lookups by exact identifier do not expand that window.
If either cap is reached or required evidence is missing, Kashif returns
`INCOMPLETE_EVIDENCE` and Muslih cannot create an executable plan.

### Muslih output: `RecoveryWarrantDraft`

- Incident identifier and source execution
- Replacement Agent Registry resource and version
- Approved trusted checkpoint and memory identifiers
- Excluded artifacts and context
- Minimum allowed tools and permission scopes
- Expected sandbox business mutation
- Idempotency key
- Authoritative vendor-master and purchase-order revision identifiers
- Clean recovery-package manifest

Muslih does not generate security tokens or the authoritative digest. After
validating the draft, Hisaar Gate materializes a `RecoveryWarrant` containing the
canonical digest, server issue time and ten-minute expiration. It also recomputes
the expected mutation from the versioned authoritative records rather than
trusting the draft. A nonce is issued only later through an authenticated
commander challenge.

### Shaahid output: `VerificationReport`

- Deterministic check identifiers and returned results
- The mandatory verification suite selected from a fixed Gate-owned allowlist
- Expected versus observed business mutation
- Duplicate mutation count
- Trusted-context inclusion and exclusion checks
- Trace and evidence references
- Replay digest and match status
- Missing or contradictory evidence

Shaahid invokes every Gate-mandated verification tool, searches the returned
cross-service records for contradictions and cites each finding. It cannot omit a
mandatory check or invent a new authority check. Hisaar Gate independently
derives PASS or BLOCKED from the persisted deterministic outputs. Shaahid's
report is a bounded judge-facing explanation; it cannot change or override a
check.

## 7. Deterministic incident state machine

The security-control intake path is:

`RECEIVED -> SCREENING -> BLOCKED_AT_INGRESS`

`BLOCKED_AT_INGRESS` means the content was stopped before agent consumption. It
does not create a fictitious tainted session or recovery claim.

The flagship recovery path is:

`RECEIVED -> SCREENING -> SCREENED_CLEAR -> AGENT_CONSUMED -> ACTION_PROPOSED -> POLICY_DENIED -> SESSION_TAINTED -> QUARANTINED -> INVESTIGATING -> PLAN_READY -> AWAITING_APPROVAL -> APPROVED -> REASSIGNED -> COMPLETED -> VERIFIED`

The clean-control path is:

`RECEIVED -> SCREENING -> SCREENED_CLEAR -> AGENT_CONSUMED -> ACTION_PROPOSED -> POLICY_ALLOWED -> COMPLETED -> VERIFIED`

`POLICY_ALLOWED` is available only when Hisaar Gate's deterministic authoritative
source checks pass. It does not let the AP agent self-authorize, and it never
passes through a recovery approval state.

Human rejection follows `AWAITING_APPROVAL -> REJECTED`. The approval transaction
stores the authenticated commander, non-empty rationale, warrant digest and
server timestamp. Any nonterminal state before `VERIFIED` can transition to
`BLOCKED` on a non-recoverable error. `BLOCKED_AT_INGRESS`, `REJECTED`, `BLOCKED`
and `VERIFIED` are terminal for that intake or recovery attempt.

`QUARANTINED` means a Hisaar Gate execution quarantine: a persisted deny record
keyed by runtime principal, agent-instance identifier and session identifier with
a fencing version. Every protected invoice-reader, proposal and ERP tool call
checks that deny record before work. It does not claim that Google Agent Runtime
was shut down, credentials were revoked or a platform-managed identity was
disabled unless a separately proven platform control is added later.

A later attempt uses a new recovery-attempt identifier but preserves the incident
identifier and the original business idempotency key. It may never mint a new
business key to bypass an existing mutation.

Hisaar Gate enforces:

- No investigation before quarantine is persisted.
- No plan may include an untrusted artifact, memory or checkpoint.
- Tool scopes may remain equal or shrink during recovery; they may never expand.
- The replacement runtime identity must differ from the quarantined execution.
- Approval must bind the exact current warrant digest, authenticated commander,
  source revisions, unconsumed nonce and unexpired warrant.
- The expected business mutation and idempotency key cannot change after
  approval.
- Only one ledger mutation may exist for the idempotency key.
- Verification must match the approved warrant and persisted mutation.
- Failed verification cannot transition to VERIFIED.

### Transaction and side-effect rules

Every authoritative transition is a Firestore compare-and-set transaction over
the current state and monotonically increasing `state_version`. The same
transaction appends the next incident-scoped hash-chain event. Firestore may
retry a transaction callback, so callbacks contain only Firestore reads and
writes: no Gemini call, Model Armor call, tool call or other external effect may
run inside one.

Inbound messages carry a producer-stable `event_id`, `payload_hash` and business
idempotency key. An admission transaction returns an existing completed result,
reports a live claim as busy, or atomically creates/takes over a processing lease
with a random lease token, expiration and incremented fencing token. Work occurs
after commit; finalization verifies the fencing token before persisting the
result. Out-of-order transitions are rejected, not reordered by an LLM.

Pub/Sub delivery is never described as end-to-end exactly once. The push path is
duplicate-tolerant, and the sandbox ERP independently creates or returns the
single mutation document keyed by the business idempotency key. A lost response
therefore retries safely and returns the existing receipt.

Each intentional sandbox launch has a server-issued `sandbox_run_id`. For a
human launch, the IAP BFF asks Gate to issue a short-lived opaque launch token
bound to the commander subject, command-room session and allowlisted fixture;
Gate generates it and stores only its hash. The launch transaction consumes or
reuses that token atomically:
the first submit creates the run, while a browser retry or double-click returns
the same run. A deliberate rehearsal or final take requests a new token and gets
a new run without deleting earlier evidence. Gate derives the event ID, synthetic
invoice ID and business idempotency key from `sandbox_run_id`; the client cannot
supply them. Frozen evaluation `run_id` values use the same reservation rule under
the evaluator identity, so a retried declared run is adopted rather than duplicated.

### Approval and execution rules

After IAP, allowlist, origin and CSRF verification, an authenticated warrant-
challenge endpoint reloads the current warrant and transactionally issues a
server-generated 256-bit nonce plus opaque challenge identifier bound to the
commander subject, command-room session and warrant digest. It stores only the
nonce hash and returns the raw nonce once to that session.

The approval API accepts that stored warrant identifier, challenge identifier and
one-time nonce, not an authoritative client-supplied digest. It repeats the
human-boundary checks,
reloads the warrant, re-derives its digest and verifies the challenge binding.
One transaction verifies the ten-minute warrant TTL, consumes the nonce exactly
once, writes the authenticated subject into the approval, moves the attempt to
`APPROVED` and creates a single-use sixty-second execution lease. Only the nonce
digest and consumption result remain as audit evidence.

The standby submits an exact mutation proposal during that execution lease.
Hisaar Gate validates it against the warrant and authoritative source revisions;
before calling the ERP, Gate server-side derives and persists a stable
`execution_request_digest` from canonical lease, warrant, proposal, source-
revision and business-idempotency-key fields, then derives
`execution_request_id` from a domain-separated hash of that digest. Neither value
is trusted from the caller. That request identity is part of the single-use lease
record.
The sandbox ERP's own transaction writes one mutation or returns its existing
receipt. After that external call, one authority-database transaction revalidates
the lease, fencing token, state version, warrant and sources, then atomically
persists the receipt, transitions to `COMPLETED`, consumes the lease and appends
the audit event. A crash before that transaction safely re-adopts the ERP receipt;
a canonical-equivalent retry that re-derives the same request identifier and
digest after that
transaction returns `IDEMPOTENT_REPLAY` with the persisted completed result and
performs no ERP or authority write. A new or mismatched request presented against
the consumed lease is denied. If verification later fails, a new attempt may
adopt that existing receipt only when the business
key, mutation digest and source revisions match exactly, then run fresh
verification. Ambiguous or conflicting persisted mutations remain `BLOCKED` for
manual remediation.

### Context-taint and trust rules

The invoice reader returns an envelope-bound `content_release_at` proposal with
the screened text; Hisaar Gate transactionally persists the screening envelope
and release boundary before the orchestrator sends that exact text to the
protected agent. All plans, tool proposals, memories and checkpoints written by
that source execution at or after first artifact contact are excluded
from recovery by default. The semantic-tamper document is described as causing
`SESSION_TAINTED_UNSAFE_PROPOSAL`; HisaarAI does not claim that the agent binary,
credentials or whole fleet were compromised.

Trusted recovery inputs are limited to versioned ERP and purchase-order records,
a prior checkpoint produced by an execution that terminated clean, and
explicitly allowlisted Memory Bank identifiers with verified lineage. Memory
Bank may inform recovery context or playbook selection but never supplies the
authoritative remittance profile, amount, mutation or release decision. Standby
outputs remain candidate context until the recovery reaches `VERIFIED`.

## 8. End-to-end recovery flow

1. An allowlisted launch creates or reuses a server-issued `sandbox_run_id`; Gate
   derives the synthetic invoice reference, producer-stable event identifier,
   payload hash and business idempotency key before publishing `invoice.received`.
2. The admission transaction reserves or returns the existing intake before any
   slow work begins.
3. The only registered invoice-reader tool submits the original PDF bytes to
   direct Model Armor PDF screening. Model Armor screens document text; HisaarAI
   does not claim byte-level malware or embedded-image inspection.
4. If the PDF verdict is a security match, the security-control path persists
   `BLOCKED_AT_INGRESS`; extraction and Gemini consumption never occur.
5. If clear, the isolated extractor returns normalized text plus the raw-file and
   extracted-text digests. The invoice reader screens that exact normalized text
   with Model Armor and persists a screening envelope containing both digests,
   template/configuration reference and both verdicts.
6. Only the exact text bound to a passing screening envelope can enter Gemini.
   The flagship fixture must pass both checks; this is a valid content-security
   result, not a Model Armor miss.
7. The protected AP agent proposes synthetic remittance profile `RPF-7731`, while
   versioned vendor-master revision `V42` authorizes `RPF-4912` for vendor
   `ACME-017`.
8. Hisaar Gate applies `PAYMENT_DESTINATION_MUST_MATCH_VENDOR_MASTER_REVISION`,
   denies the proposal, persists the content-release taint boundary and creates
   the execution-quarantine deny record for the affected principal, agent
   instance and session. No sandbox mutation occurs.
9. Raasid converts the persisted security, policy and runtime events into an
   `IncidentObservation`.
10. Kashif receives the bounded evidence bundle and produces a cited
    `BlastRadiusReport` without project-wide search authority.
11. Muslih builds a `RecoveryWarrantDraft` from authoritative sources and
    eligible trusted context only.
12. Hisaar Gate validates the draft, recomputes the expected mutation and
    materializes the canonical warrant, digest and expiration.
13. The authenticated command room requests a subject-bound one-time challenge,
    then the Incident Commander approves that exact stored warrant; execution
    before approval returns `APPROVAL_REQUIRED`.
14. Hisaar Gate consumes approval once and assigns the already deployed standby
    Runtime under its distinct scoped identity and clean session.
15. The standby receives a clean structured recovery package, proposes the
    approved action and never sees the source PDF or quarantined memory.
16. Hisaar Gate authorizes the sandbox ERP tool to create or return exactly one
    mutation for the original business idempotency key.
17. Shaahid invokes deterministic verification and replay tools, and Hisaar Gate
    derives `VERIFIED` only when every persisted result passes.

Clean controls share steps 1–7. When the proposal matches the authoritative
vendor and PO revisions, Hisaar Gate records `POLICY_ALLOWED`, invokes the same
idempotent sandbox ERP tool, runs deterministic checks and reaches `VERIFIED`
without recovery agents or a recovery approval.

## 9. Firestore data model

Firestore is an operational database, not an immutable ledger. HisaarAI uses
append-only application records and a tamper-evident hash chain without calling
that mechanism cryptographic attestation.

Primary collections:

- `agent_catalog_snapshots`
- `sandbox_launch_intents`
- `sandbox_runs`
- `incidents`
- `incidents/{incident_id}/events`
- `event_claims`
- `processing_leases`
- `context_checkpoints`
- `recovery_warrants`
- `warrant_approvals`
- `approval_nonces`
- `execution_leases`
- `business_mutations`
- `verification_reports`
- `model_invocations`
- `evaluation_runs`

Each incident event contains the incident-local previous event digest, canonical
payload digest, correlation identifier, actor or agent identity, service-generated
UTC `event_time`, Firestore-resolved `committed_at` and service evidence references.
The digest binds `event_time`; `committed_at` is excluded because its server value
does not exist until commit. The incident document stores the chain head and state
version, so a transition transaction can update both without a global write
hotspot. The mechanism is called a tamper-evident application hash chain, not an
immutable ledger or cryptographic attestation.

Security rules and IAM prevent browser clients from writing authority records
directly. Approval nonces, execution leases and processing leases are created and
consumed only by Hisaar Gate's service principal.

## 10. Command-room experience

The command room is one connected product experience, not separate dashboards.

### Fleet strip

- Real Agent Registry resources and versions
- Primary AP, standby AP and recovery Runtime identity and status
- Active, quarantined and recovering counts
- Links to real trace evidence

### Incident topology

- Protected AP execution, registered tools, affected context and replacement
  execution
- Trust-boundary coloring derived from backend state
- Clickable event and evidence references

### Recovery timeline

- Security-control `BLOCKED_AT_INGRESS` without a recovery claim
- Flagship PDF and extracted-text Model Armor pass envelopes
- AP proposal, deterministic policy denial and Gate execution quarantine
- Raasid observation
- Kashif blast-radius report
- Muslih warrant
- Human approval or rejection
- Reassignment, business completion and Shaahid verification

### Recovery warrant panel

- Trusted checkpoint and memory identifiers
- Excluded artifact and context digests
- Replacement identity and allowed tools
- Expected mutation, idempotency key, expiration and warrant digest
- Nonce status without exposing a reusable client authority payload
- Explicit approve and reject actions

### Verification panel

- Unsafe mutations
- Duplicate mutations
- Trusted-context violations
- Expected versus observed mutation
- Replayed request result and mutation count
- Model and trace provenance

### Context lineage

- Real Memory Bank and checkpoint identifiers with server timestamps
- Exact immutable Memory Revision names and fact digests
- Trusted, candidate, tainted and revoked status
- Source execution and verification lineage
- Earliest and latest genuine retained context, with no simulated elapsed time

The frontend never derives authoritative states, injects pre-completed incidents
or offers role simulators that fabricate HTTP or security responses.

## 11. Failure handling

- **Model Armor unavailable, oversized, skipped or inconclusive:** fail closed
  before content release or tool execution; only an explicit passing result is
  treated as clear.
- **Duplicate or equivalent Pub/Sub delivery:** the producer-stable event claim
  returns the existing busy or completed intake; Pub/Sub message ID alone is not
  the business key.
- **Expired processing lease:** a transaction may take over with a higher fencing
  token; a stale worker cannot finalize.
- **Firestore contention:** rely on bounded SDK transaction retries and return a
  safe retriable error when exhausted; never run side effects in the callback.
- **Agent timeout:** one same-model retry; then persist BLOCKED.
- **Locked model unavailable, unauthorized or wrong endpoint:** fail the platform
  or release preflight; do not swap a model alias or cross-model fallback.
- **Invalid agent schema:** reject the output, record diagnostics and remain in the
  current safe state.
- **Kashif abstains or reaches an evidence cap:** Muslih cannot produce an
  executable warrant, and the UI states the bounded scope of the investigation.
- **Untrusted or missing memory:** exclude it; never reconstruct from convenience.
- **Human rejection:** persist `REJECTED`, authenticated identity and rationale;
  no execution lease exists.
- **Unauthenticated, wrong-role, expired-IAP or cross-site approval:** reject
  before warrant lookup and write no authority record.
- **Stale approval or nonce replay:** reject and require a newly validated warrant;
  a consumed nonce never becomes usable again.
- **Standby unavailable or not identity-distinct:** fail before reassignment.
- **Gateway unavailable:** use the already proven direct Model Armor path and do
  not claim Gateway enforcement.
- **Sandbox ERP transient error or lost response:** safely retry with the original
  business idempotency key and adopt the existing matching receipt.
- **Verification mismatch after mutation:** block the attempt, retain all evidence
  and allow only exact receipt adoption plus fresh verification; never create a
  second mutation key.
- **Trace export delay:** business safety remains enforced; submission readiness
  fails until the trace is visible and linked.

## 12. Evaluation and release gates

Evaluation uses committed, stored scenarios and reports measured results. It does
not hardcode metrics or generate expected results from the implementation.

### Scenario groups

- Approved prompt-injection security fixture
- Semantic remittance-profile conflict flagship fixture
- Clean invoice controls using synthetic remittance profiles
- Duplicate Pub/Sub deliveries
- Agent timeout and invalid-schema injections
- Missing or tainted memory cases
- Human rejection, stale, mutated and replayed approval cases
- Sandbox ERP transient failure
- Verification mismatch and evidence-tamper cases

### Required gates

#### Screening and policy

- The preselected calibration security PDF and committed Model Armor template
  produce a successful prompt-injection-filter match in 10 of 10 runs. This is
  reported as repeated-fixture stability, not detection accuracy; the complete
  selection/calibration history is published.
- Five benign held-out security variants from organizer-provided or official
  Google Model Armor testing material are held by a named independent custodian,
  with source provenance and an encrypted-archive digest committed before code
  freeze. They are released and individually hash-committed only after code and
  prompt freeze, then run once each without fixture tuning; all five must reach
  `BLOCKED_AT_INGRESS`, and every result remains published if this gate fails.
- The exact flagship PDF bytes and exact normalized extracted text produce
  explicit clear results in 10 of 10 preflight runs. The fixed set of 20 clean
  controls allows at least 19 of 20; no skipped result counts as clear.
- The template resource name, region, enabled filters, relevant thresholds, both
  content digests, Model Armor response digest, correlation identifier and
  timestamp are stored for every run; no durable Google verdict resource is
  claimed.
- The semantic remittance mismatch is denied and placed under Gate execution
  quarantine in 30 of 30 runs.
  Requests from the quarantined instance remain denied in 30 of 30 runs.
- Unsafe sandbox business mutations: 0. Tainted context included in recovery: 0.

#### State, approval and idempotency

- All enumerated illegal transitions are rejected, and the frozen set of 1,000
  explicitly stored deterministic transition sequences preserves invariants.
- Exactly 100 committed approval negatives use ten cases each for missing IAP,
  bad IAP audience, expired IAP, unauthorized subject, bad origin, bad CSRF,
  mutated warrant, stale source revision, expired warrant and wrong/replayed
  nonce. They produce zero approvals and no authority-count change.
- Exactly 30 wrong-executor, expired-lease and consumed-lease/new-request calls
  use ten cases per subtype in a separate committed execution-negative suite and
  produce no ERP mutation. Exactly ten separately declared exact terminal replays
  are idempotency positives and must return the cached result with zero writes.
- Automated recovery evaluation obtains a challenge and approval through the
  deployed IAP/CSRF/nonce path using one disclosed, allowlisted test-commander
  principal and Google's keyless service-account JWT flow with an exact target-URL
  audience. The runner cannot inject the downstream IAP assertion. It is labelled
  automated approval; the continuous demo alone proves human commander interaction.
- Human-rejected warrants produce zero execution leases and preserve the stated
  rationale.
- Fifty simultaneous valid mutation attempts with one business idempotency key
  produce one mutation document and one stable receipt.
- A lost-response replay returns the same receipt. A post-mutation recovery
  attempt either adopts that exact receipt or blocks; it never writes a duplicate.

#### Recovery and evidence

- The frozen manifest predeclares the exact fixtures, run identifiers, seeds and
  denominators for screening, clean controls, recovery, quarantine retry,
  approval-negative subtypes, concurrency, stored state sequences and fault
  subtypes and is content-hashed before the release run. All 30 declared warm
  flagship runs must reach valid recovery with zero unsafe mutations; any safe
  `BLOCKED` result remains published but fails winner-readiness for that release.
- The frozen fault suite contains five hosted cases each for agent timeout,
  invalid schema, missing memory, tainted memory, human rejection, ERP transient
  failure, lost response, verification mismatch and evidence tamper. Each must
  reach its declared safe state with zero unauthorized mutation and complete
  evidence. Test-only fault controls require the evaluator service identity,
  frozen manifest digest and declared run ID, are visibly labelled, cannot alter
  Model Armor/vendor/warrant authority and are disabled after the suite.
- Every recovery uses the pre-provisioned identity-distinct standby, a fresh
  session and a clean recovery package with no source PDF or tainted memory.
- Every material Kashif statement has at least one resolvable bounded evidence
  reference. Reaching a query cap returns `INCOMPLETE_EVIDENCE`.
- Warrant schema and deterministic validation, approval-to-warrant digest,
  evidence replay, model provenance and trace correlation are complete for 100%
  of passing release cases.
- Shaahid reports `MATCH` only when the deterministic plan, approval, source
  revisions, ledger receipt and replay checks agree; Hisaar Gate alone derives
  `VERIFIED`.

#### Auditable latency and cost

All latency uses Firestore `committed_at` values and trace spans. Security-ingress
latency uses all 15 predeclared warm post-freeze security observations: ten
committed calibration-PDF runs plus five held-out variants. All 15 must reach
`BLOCKED_AT_INGRESS`; P95 is nearest-rank 15 of 15, with no interpolation or case
removal. The containment, planning and execution populations are the same 30
predeclared warm flagship runs, all of which must reach `VERIFIED`; their P95 is
the frozen nearest-rank estimator at rank `ceil(0.95 * 30) = 29`. Unless the frozen
manifest declares a genuine cold-observation population, report
`COLD_NOT_MEASURED`; incidental or empty samples never become a claimed cold
distribution. Never label human-excluded time as total recovery time.

- Security ingress: admission transaction committed to `BLOCKED_AT_INGRESS`, P95
  no more than 10 seconds.
- Flagship containment: admission committed to `QUARANTINED`, P95 no more than 20
  seconds.
- Automated recovery planning: `QUARANTINED` commit to `PLAN_READY` commit, P95
  no more than 60 seconds.
- Human decision: `AWAITING_APPROVAL` commit to `APPROVED` or `REJECTED` commit,
  reported separately with no system-performance threshold.
- Automated execution: `APPROVED` commit to `VERIFIED` commit, P95 no more than
  45 seconds.
- Demo readiness is stricter than release P95: the chosen warm run must reach
  `PLAN_READY` within 40 seconds of quarantine, `VERIFIED` within 25 seconds of
  approval and complete machine work for both fixtures within 150 seconds. The
  machine-work value is exactly `(security BLOCKED_AT_INGRESS - security
  admission commit) + (flagship QUARANTINED - flagship admission commit) +
  (flagship PLAN_READY - flagship QUARANTINED) + (flagship VERIFIED - flagship
  APPROVED)`; human wait and UI narration are excluded and no interval overlaps.
- Total wall-clock time from admission to terminal state is always displayed.
- A successful flagship run uses at most six Gemini calls and two Model Armor
  calls before retries, targets at most 30,000 combined model tokens, and records
  actual API calls, tokens and Cloud usage. Cost is labelled a usage-based estimate
  unless an attributable billing export proves billed cost.
- Strict release verification fails on a missing declared result, latency or
  resource-cap violation, incomplete Day-0/7/14/21 chain or un-restored warm
  capacity, and while evaluation fault controls remain enabled.

After implementation stabilizes, code and prompts are frozen before the complete
fixture-and-run manifest is hashed and committed. That manifest is executed once
with real services. Every declared result, including failures, is published in
the content-addressed report; no post-run case selection is allowed.

## 13. Four-minute demonstration

The core execution is recorded continuously at normal speed through one shared
pipeline. The security fixture is a short control beat; the flagship receives the
full recovery story.

- **0:00–0:15:** Show the live sandbox label, authoritative `RPF-4912` profile and
  promise: contain the agent, preserve the mission.
- **0:15–0:35:** Show the three real Runtime/Registry resources and publish the
  security PDF. Display the real Model Armor match and `BLOCKED_AT_INGRESS`; state
  explicitly that no agent consumed it.
- **0:35–0:55:** Complete the security-control result, then publish the semantic-
  tamper PDF.
- **0:55–1:25:** Show both Model Armor clear envelopes, the protected AP agent
  proposing `RPF-7731`, and Hisaar Gate denying it against vendor-master revision
  `V42` before mutation.
- **1:25–2:10:** Show the persisted execution quarantine, Raasid's playbook and
  bounded evidence request, Kashif's cited findings and Muslih's clean
  recovery warrant from backend events.
- **2:10–2:30:** Attempt execution before approval and show the real
  `APPROVAL_REQUIRED` response, then display the exact warrant digest and expiry.
- **2:30–3:00:** The authenticated commander approves; the identity-distinct
  standby receives the clean package and Hisaar Gate records one sandbox mutation.
- **3:00–3:25:** Replay the request, show the same receipt and mutation count one,
  then show Shaahid's deterministic `MATCH` and Gate-derived `VERIFIED`.
- **3:25–3:40:** Show the architecture and trust-boundary diagram, identifying
  Gemini/ADK, Model Armor, the deterministic Gate and Google Cloud services.
- **3:40–3:55:** Show trace correlation, genuine context-lineage timestamps,
  evaluation run ID, numerators/denominators and separate latency intervals.
- **3:55–4:00:** Close: HisaarAI turns one unsafe agent session into a contained,
  recoverable incident, not a claimed fleet-wide compromise.

Human rejection and retry denial from the quarantined source identity are proven
in stored evaluation evidence rather than consuming extra live calls in the
four-minute video. The script is frozen only after three consecutive unedited,
normal-speed rehearsals finish below four minutes with every proof readable.

## 14. Platform proof gates before UI expansion

The following facts must be proven in a narrow spike before significant UI work:

1. The exact three locked model identifiers respond with required structured
   output/tool behavior in the configured endpoints and quota.
2. Primary AP, standby AP and HisaarAI ADK runtimes deploy successfully; primary
   and standby have different effective principals.
3. All three real Registry entries are visible and retrievable.
4. Memory Bank persists and returns a real memory identifier linked to a real
   checkpoint and server timestamp.
5. With one committed template, direct Model Armor flags the exact security PDF
   and passes the exact flagship PDF and normalized text; skipped/oversized cases
   fail closed.
6. The isolated extractor cannot write Firestore, call Gemini or call the sandbox
   ERP, and the AP identities cannot retrieve documents except through the
   screened invoice reader.
7. Cloud Trace displays a correlated agent or tool execution.
8. Concurrent duplicate events reserve one logical intake in Firestore, stale
   fencing tokens cannot finalize, and fifty matching mutations yield one receipt.
9. Approval replay, expiration, rejection and wrong-identity cases fail through
   real backend calls.
10. Scoped runtime identities cannot perform unauthorized writes.
11. Each recovery role resolves only its registered ADK tool adapters; attempted
    cross-role invocation is denied and no per-agent IAM claim is made.
12. The IAP/CSRF approval boundary rejects unauthenticated, wrong-subject,
    expired-assertion and disallowed-origin requests before authority records are
    read or written.
13. A protected tool call from a Gate-quarantined principal/instance/session is
    denied by the persisted fencing rule while the standby principal succeeds.

Written organizer clarification for the required-path 3.1 Pro Preview role is a
separate compliance proof gate. Agent Gateway is attempted only after these
thirteen technical facts pass.

For recording, Cloud Run services are health-checked five minutes beforehand and
may temporarily use service-level minimum instances of one. A non-mutating model
and schema canary validates quota and warms application paths; this is not called
guaranteed Gemini prewarming. Recorded latency is labelled warm. Cloud Run minimum
instances return to their captured prior values after rehearsals (normally zero).
Mandatory Agent Runtime deployments use
the platform's default scaling because custom Runtime resource controls are
Preview. A `min_instances=0` experiment is permitted only as a separately labelled
optional cost optimization after core proof; it cannot gate release or support a
scale-to-zero claim. Budget monitoring governs deployment duration.

## 15. Submission package

- Selected category: **The Fortified Enterprise Fleet**
- Devpost description covering product features, Google and non-Google
  technologies, all other data sources, findings and learnings
- Hosted command-room URL and testing credentials if required
- Public or judge-accessible repository containing only newly created project work
- Reproducible local and Google Cloud setup instructions
- Infrastructure and deployment instructions
- Architecture diagram
- Threat and trust-boundary diagram
- Stored evaluation fixtures and content-addressed run reports
- Model-routing and provenance documentation
- Four-minute public English demonstration video with visible proof that the
  backend is deployed on Google Cloud
- Public build article created for the hackathon
- Qualifying social post using `#AllThingsAgenticHackathon`

No additional Google AI model is added merely for bonus points. Gemma, Veo, Lyria
or another model requires separate user approval and a genuine bounded product
role. HisaarAI's submitted runtime remains restricted to the three approved Gemini
model identifiers.

### New-project provenance

`PROVENANCE.md` must state, after a repository audit:

> HisaarAI was created during the All Things Agentic submission period. No source
> code, UI assets, datasets, test fixtures, prompts, deployment configuration or
> architecture diagrams were copied from CreditLock, MuhafizSRE or CrossPatch.
> Prior work contributed conceptual lessons only. All incorporated frameworks,
> starter material and third-party dependencies are identified below.

The statement is published only if repository history and file provenance support
every word. The package includes the first-commit date, dependency and license
manifest, starter-template disclosures and AI coding assistants used. Previous
projects are discussed in provenance, not in the product hero or demo story.

### Genuine multi-week context evidence

The platform spike creates Day 0 of stable lineage `AP-CONTINUITY-001` immediately,
then genuine resumptions update that same lineage around days 7, 14 and 21. Each
resume records a real Memory Bank resource, exact immutable Memory Revision name,
fact digest, returned revision expiration, Firestore checkpoint, Runtime session
and correlated server timestamp.
A minimal final-named `event-intake` route exists from Day 0 under the Gate
identity and is updated in place as the application grows; the Pub/Sub endpoint
and OIDC audience never move. Gate writes only the authority checkpoint and has
no Memory permission. It invokes the exact Recovery Runtime method, and Recovery
Runtime is the only caller allowed to read or write the conditionally scoped
Memory lineage.
A later flagship run retrieves a prior Gate-certified revision that selects the
allowlisted remittance-conflict recovery playbook and evidence-request shape;
Hisaar Gate still derives all authoritative values and decisions independently.

The demo may claim only the actual elapsed duration visible in server timestamps.
No fixture date, fake clock or backfilled record counts as evidence of
asynchronous context maintenance. Revisions are requested with a 365-day TTL;
the returned expiration and trust-status policy are documented, and a missed
scheduled resumption is disclosed rather than recreated.

## 16. Definition of winner-ready

HisaarAI is winner-ready only when:

- Every mandatory submission requirement is satisfied.
- The reference workflow passes all release gates using real services.
- The hosted command room displays only backend-derived state.
- The unedited core demo can be reproduced from a clean environment.
- Google Cloud, model, identity, Registry, Model Armor and trace claims match the
  deployed implementation exactly.
- The explicit 3.1 Pro Preview dependency has passed endpoint/quota preflight and
  written organizer clarification confirms that its additional use is compatible
  with the mandatory 3.5-or-newer requirement. Without that clarification, the
  project may proceed only with explicit user risk acceptance and is not called
  eligibility-clear or winner-ready; no other preview capability is critical.
- The repository, video, architecture and metrics tell the same failure-first
  story without contradictions.

These conditions maximize scoring potential but do not guarantee a prize; judging
and competing submissions remain outside the team's control.

## 17. Verified implementation constraints

Checked against official sources on 2026-08-08:

- [Hackathon rules](https://allthingsagentichackathon.devpost.com/rules): Gemini
  3.5 or newer, an approved Google agent framework and a Google Cloud service are
  mandatory; newly created work and pre-existing-work disclosure are required.
- [Firestore transactions](https://firebase.google.com/docs/firestore/manage-data/transactions):
  writes are atomic and transaction callbacks may rerun after concurrent edits.
- [Firestore per-database access](https://docs.cloud.google.com/firestore/native/docs/manage-databases#configure_per-database_access_permissions):
  named-database isolation is enforced with positive project-IAM
  `resource.name` conditions, not browser Security Rules.
- [Pub/Sub exactly-once delivery](https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery):
  the guarantee is limited to regional pull/StreamingPull delivery and does not
  make publish retries or business effects exactly once.
- [Model Armor overview](https://docs.cloud.google.com/model-armor/overview) and
  [sanitization API](https://docs.cloud.google.com/model-armor/sanitize-prompts-responses):
  direct PDF input is supported, document text is screened, input is limited to
  4 MB and embedded document images are outside the document-screening claim;
  verdict fields are read from the nested `sanitization_result` and typed filter
  results rather than assumed at the response top level.
- [Gemini 3.6 Flash](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-6-flash),
  [Gemini 3.5 Flash-Lite](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash-lite)
  and [Gemini 3.1 Pro](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-1-pro):
  the first two are GA and support global plus `us` and `eu`; 3.1 Pro is Public
  Preview and currently supports only global. HisaarAI deliberately validates all
  three through one explicit global model configuration.
- [Google Gen AI SDK overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/sdks/overview)
  and [Python SDK reference](https://googleapis.github.io/python-genai/): local
  enterprise setup supports an explicit project/global-location client with
  `HttpOptions(api_version="v1")`; deployed Runtime code uses that explicit client
  rather than overriding Runtime-reserved project/location environment variables.
- [Agent Runtime identity](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/agent-identity):
  core Runtime deployments use separately scoped custom service accounts; Agent
  Identity token semantics are reserved for a separately proven Gateway path.
- [Agent Platform roles](https://docs.cloud.google.com/iam/docs/roles-permissions/aiplatform):
  predefined `roles/aiplatform.user` spans broad Agent Platform administration
  and contains Memory permissions. HisaarAI may use its no-Memory derivative only
  for temporary discovery, then removes that binding and runs on a reviewed
  data-plane allowlist; the specialized conditional Memory role is added only to
  Recovery Runtime.
- [Policy Troubleshooter v3](https://docs.cloud.google.com/policy-intelligence/docs/reference/policytroubleshooter/rest/v3/iam/troubleshoot):
  evaluates a principal, permission and full resource name against visible allow
  and deny policies; release evidence requires complete policy-view coverage,
  exact `CANNOT_ACCESS` results and rejection of every unknown or unspecified
  result. Principal access boundaries can restrict but cannot create an
  administrative allow, so preview PAB evaluation is not a core proof.
- [Google `testIamPermissions` reference](https://cloud.google.com/secret-manager/docs/reference/rest/v1/projects.locations.secrets/testIamPermissions):
  this method is for permission-aware clients, may fail open and can return empty
  for a nonexistent resource, so HisaarAI never treats an empty result as a deny.
- [Agent Runtime deployment](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/deploy-an-agent)
  and [Agent Registry registration](https://docs.cloud.google.com/agent-registry/register-agents):
  deploy through `client.agent_engines.create`; SDK-deployed Runtime agents
  register automatically, while Preview Runtime traffic revisions and custom
  resource controls are not core proofs; reserved project/location environment
  variables are not overridden.
- [Cloud Scheduler Pub/Sub targets](https://docs.cloud.google.com/scheduler/docs/creating):
  scheduled publishes use Google's Scheduler service agent; the separate
  Pub/Sub push-auth account authenticates delivery to Cloud Run.
- [Artifact Registry with Cloud Build](https://docs.cloud.google.com/artifact-registry/docs/configure-cloud-build)
  and [user-specified build identities](https://docs.cloud.google.com/build/docs/securing-builds/configure-user-specified-service-accounts):
  a regional repository and least-privilege builder exist before the first image
  build; deployed revisions reference resolved image digests.
- [Memory revisions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/revisions):
  each memory mutation creates an immutable revision; HisaarAI pins and re-fetches
  that exact revision, requests the documented 365-day TTL, records returned
  expiration and does not delete the parent during negative testing.
- [Memory Bank IAM conditions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/iam-conditions):
  Recovery Runtime receives the specialized Memory User role only for the
  positive `AP-CONTINUITY-001` scope.
- [Cloud Run service-to-service authentication](https://docs.cloud.google.com/run/docs/authenticating/service-to-service),
  [service-account impersonation](https://docs.cloud.google.com/iam/docs/service-account-impersonation),
  [IAP programmatic authentication](https://docs.cloud.google.com/iap/docs/authentication-howto)
  and [IAP signed headers](https://docs.cloud.google.com/iap/docs/signed-headers-howto):
  typed tool services use Google-signed OIDC identity tokens, while commander
  authorization validates the signed IAP assertion and application role; the
  automated test commander reaches IAP with a keyless service-account JWT.
- [Cloud Run IAP setup](https://docs.cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run)
  and [IAP verification tests](https://docs.cloud.google.com/iap/docs/query-parameters-and-headers-howto):
  no-organization first use requires Console/custom-OAuth bootstrap, and hosted
  bad-audience/expired-token checks use IAP-produced test assertions.
- [Cloud Run container contract](https://docs.cloud.google.com/run/docs/container-contract):
  the ordinary root filesystem is writable in-memory, so extraction uses a
  bounded temporary volume and cleanup rather than a false read-only-root claim.
- [Cloud Run minimum instances](https://docs.cloud.google.com/run/docs/configuring/min-instances):
  warm capacity reduces cold starts but is best-effort and billable, not a
  no-cold-start guarantee.
