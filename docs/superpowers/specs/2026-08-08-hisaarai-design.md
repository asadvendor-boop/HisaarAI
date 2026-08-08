# HisaarAI Product Design

**Status:** Approved product direction; written-spec review pending  
**Date:** 2026-08-08  
**Hackathon:** All Things Agentic  
**Primary category:** The Fortified Enterprise Fleet  
**Primary prize target:** Fortified Enterprise Fleet  
**Fallback prize routes:** Best Architectural Design, Individual/Hobbyist, Grand Prize, Honorable Mention

## 1. Product thesis

**HisaarAI — The Agent Fleet Recovery Command Room**

**Tagline:** Contain the agent. Preserve the mission.

HisaarAI is an enterprise-agent recovery control plane. When a business agent
encounters poisoned content, HisaarAI blocks unsafe action, quarantines the
affected execution, reconstructs trusted context, and resumes the interrupted
business workflow with a clean agent under one governed human approval.

Most agent-security products stop an unsafe execution. HisaarAI differentiates
itself by providing **safe continuity**: it contains the incident and still
finishes the authorized business task exactly once.

The reference workflow is sandbox accounts payable. An incoming invoice PDF
contains an approved security-test signal and payment details that conflict with
the trusted vendor master. HisaarAI must prevent an unsafe ledger mutation,
isolate the affected execution, recover from a trusted checkpoint, and create
one correct sandbox ERP mutation.

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

- Distinct ADK agents have separate roles, tools, permissions and typed outputs.
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

- One protected Accounts Payable agent.
- One HisaarAI recovery orchestrator containing four specialized agents.
- One sandbox ERP tool or MCP endpoint.
- One invoice-received Pub/Sub event.
- One security-test invoice and a stored clean-control set.
- One governed recovery approval.
- One exactly-once sandbox ledger mutation.
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
- Preview-only features as dependencies of the core recovery path.
- CreditLock code, assets or workflows.

## 4. Deployment topology

Use one Google Cloud project and one supported region wherever possible.

### Managed agent runtimes

1. **Protected AP Agent Runtime**
   - Processes the sandbox invoice workflow.
   - Uses Gemini 3.6 Flash with medium thinking.
   - Has access only to the registered invoice reader and sandbox ERP proposal
     tool.
   - Cannot bypass Hisaar Gate for business mutation.

2. **HisaarAI Recovery Runtime**
   - Contains Raasid, Kashif, Muslih and Shaahid as specialized ADK agents.
   - Exposes typed recovery skills.
   - Uses Memory Bank only for explicitly trusted cross-session context.

Both runtimes must be visible as real Agent Registry entries. The sandbox ERP
endpoint is registered as a tool or MCP endpoint. The design does not create four
separate runtimes merely to make the four recovery roles look distributed.

### Supporting services

- **Cloud Run:** hosts the command-room web application, API facade and sandbox
  ERP service.
- **Pub/Sub:** delivers invoice and incident events. Duplicate delivery is an
  expected condition.
- **Firestore:** stores operational state, event history, warrants, approvals,
  business mutations, verification results and evaluation runs.
- **Model Armor:** directly sanitizes the PDF or extracted document content before
  Gemini receives it. The system fails closed if screening does not complete.
- **Memory Bank:** stores trusted semantic context. Firestore checkpoint metadata
  records exactly which memory identifiers are eligible for recovery.
- **Agent Observability:** exports real logs, metrics and trace spans with shared
  correlation identifiers.
- **Agent Identity:** provides a narrowly scoped identity for each deployed
  runtime if the capability is available in the project. Otherwise, separately
  scoped service accounts are used and the product does not claim Agent Identity.
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

There is no automatic cross-model fallback. A transient request may retry the
same model once using the same idempotency and correlation identifiers. A second
failure leaves the workflow blocked. Every invocation records requested model,
actual model, thinking level, attempt number and `fallback=false`.

## 6. Agent contracts

Agents communicate with typed JSON contracts rather than prose handoffs.

### Raasid output: `IncidentObservation`

- Incident and execution identifiers
- Model Armor verdict reference
- Artifact digest and trust classification
- Observed tool, agent and session identifiers
- Detection timestamp and trace identifier
- Proposed severity with bounded enum values

### Kashif output: `BlastRadiusReport`

- Affected execution, sessions, memory identifiers and tools
- Last trusted checkpoint identifier
- Explicitly excluded artifact and context digests
- Evidence references for every conclusion
- Unknowns and abstentions
- Confidence fields used only for display, never authorization

### Muslih output: `RecoveryWarrantDraft`

- Incident identifier and source execution
- Replacement Agent Registry resource and version
- Approved trusted checkpoint and memory identifiers
- Excluded artifacts and context
- Minimum allowed tools and permission scopes
- Expected sandbox business mutation
- Idempotency key
- Expiration timestamp
- Draft digest

### Shaahid output: `VerificationReport`

- Deterministic check identifiers and returned results
- Expected versus observed business mutation
- Duplicate mutation count
- Trusted-context inclusion and exclusion checks
- Trace and evidence references
- Replay digest and match status
- Missing or contradictory evidence

Shaahid cannot set the overall result. Hisaar Gate derives PASS or BLOCKED from
the deterministic checks.

## 7. Deterministic incident state machine

The allowed incident path is:

`DETECTED -> QUARANTINED -> INVESTIGATING -> PLAN_READY -> AWAITING_APPROVAL -> APPROVED -> REASSIGNED -> COMPLETED -> VERIFIED`

Any nonterminal state before `VERIFIED` can transition to `BLOCKED` when a
non-recoverable error occurs. `VERIFIED` and `BLOCKED` are terminal for that
incident; a retry creates a new recovery attempt with a new identifier.

Hisaar Gate enforces:

- No investigation before quarantine is persisted.
- No plan may include an untrusted artifact, memory or checkpoint.
- Tool scopes may remain equal or shrink during recovery; they may never expand.
- The replacement runtime identity must differ from the quarantined execution.
- Approval must bind the exact current warrant digest and be unexpired.
- The expected business mutation and idempotency key cannot change after
  approval.
- Only one ledger mutation may exist for the idempotency key.
- Verification must match the approved warrant and persisted mutation.
- Failed verification cannot transition to VERIFIED.

## 8. End-to-end recovery flow

1. An `invoice.received` Pub/Sub message supplies an invoice reference and
   idempotency key.
2. The AP workflow retrieves the document through the registered endpoint.
3. Direct Model Armor screening returns a persisted verdict before the document
   can enter Gemini context.
4. A security match or deterministic vendor-master conflict causes Hisaar Gate
   to persist `QUARANTINED`. No sandbox ledger mutation occurs.
5. Raasid converts the security and runtime events into an IncidentObservation.
6. Kashif queries traces, Registry metadata, checkpoints and trusted Memory Bank
   references to produce a BlastRadiusReport.
7. Muslih builds a RecoveryWarrantDraft from trusted sources only.
8. Hisaar Gate validates the draft and derives its canonical digest.
9. An Incident Commander approves that exact digest in the command room.
10. Hisaar Gate validates freshness, identity, scope and idempotency, then launches
    a clean execution.
11. The clean AP execution performs exactly one sandbox ERP ledger mutation.
12. Shaahid invokes deterministic verification and replay tools.
13. Hisaar Gate derives VERIFIED only when every required result passes.

## 9. Firestore data model

Firestore is an operational database, not an immutable ledger. HisaarAI uses
append-only application records and a tamper-evident hash chain without calling
that mechanism cryptographic attestation.

Primary collections:

- `agent_catalog_snapshots`
- `incidents`
- `incident_events`
- `context_checkpoints`
- `recovery_warrants`
- `warrant_approvals`
- `business_mutations`
- `verification_reports`
- `model_invocations`
- `evaluation_runs`

Each incident event contains the previous event digest, canonical payload digest,
correlation identifier, actor or agent identity, timestamp and service evidence
references. Security rules and IAM prevent browser clients from writing authority
records directly.

## 10. Command-room experience

The command room is one connected product experience, not separate dashboards.

### Fleet strip

- Real Agent Registry resources and versions
- Runtime identity and status
- Active, quarantined and recovering counts
- Links to real trace evidence

### Incident topology

- Protected AP execution, registered tools, affected context and replacement
  execution
- Trust-boundary coloring derived from backend state
- Clickable event and evidence references

### Recovery timeline

- Model Armor verdict
- Quarantine
- Raasid observation
- Kashif blast-radius report
- Muslih warrant
- Human approval
- Reassignment, business completion and Shaahid verification

### Recovery warrant panel

- Trusted checkpoint and memory identifiers
- Excluded artifact and context digests
- Replacement identity and allowed tools
- Expected mutation, idempotency key, expiration and warrant digest
- One explicit approval action

### Verification panel

- Unsafe mutations
- Duplicate mutations
- Trusted-context violations
- Expected versus observed mutation
- Replay result
- Model and trace provenance

The frontend never derives authoritative states, injects pre-completed incidents
or offers role simulators that fabricate HTTP or security responses.

## 11. Failure handling

- **Model Armor unavailable or inconclusive:** fail closed before Gemini or tool
  execution.
- **Duplicate Pub/Sub delivery:** return the existing incident or mutation for the
  idempotency key.
- **Agent timeout:** one same-model retry; then persist BLOCKED.
- **Invalid agent schema:** reject the output, record diagnostics and remain in the
  current safe state.
- **Kashif abstains:** Muslih cannot produce an executable warrant.
- **Untrusted or missing memory:** exclude it; never reconstruct from convenience.
- **Stale approval:** reject and require approval of a newly digested warrant.
- **Gateway unavailable:** use the already proven direct Model Armor path and do
  not claim Gateway enforcement.
- **Sandbox ERP transient error:** safely retry with the same idempotency key.
- **Verification mismatch:** remain BLOCKED and retain all evidence.
- **Trace export delay:** business safety remains enforced; submission readiness
  fails until the trace is visible and linked.

## 12. Evaluation and release gates

Evaluation uses committed, stored scenarios and reports measured results. It does
not hardcode metrics or generate expected results from the implementation.

### Scenario groups

- Approved security-test invoice fixtures
- Clean invoice controls
- Vendor-master conflict controls
- Duplicate Pub/Sub deliveries
- Agent timeout and invalid-schema injections
- Missing or tainted memory cases
- Stale and mutated approval cases
- Sandbox ERP transient failure
- Verification mismatch and evidence-tamper cases

### Required gates

- Security-test fixture block rate: 100%
- Clean-control allow rate: at least 95%
- Unsafe sandbox business mutations: 0
- Duplicate business mutations: 0
- Untrusted context included in recovery: 0
- Valid recovery completion rate: 100% for the frozen release set
- Warrant schema and deterministic validation pass rate: 100%
- Approval-to-warrant digest match: 100%
- Evidence replay match rate: 100%
- Model-provenance completeness: 100%
- Trace correlation completeness: 100%
- P95 containment latency: no more than 5 seconds in the recorded environment
- P95 approved-recovery latency: no more than 60 seconds in the recorded
  environment

After implementation stabilizes, code and prompts are frozen before a new
fixture-only release set is committed. That release set is executed once with
real services. The report is preserved whether it passes or fails.

## 13. Four-minute demonstration

The core execution is recorded continuously at normal speed.

- **0:00–0:20:** The problem and promise: contain the agent, preserve the mission.
- **0:20–0:40:** Hosted command room plus real Google Cloud deployment and Registry
  resources.
- **0:40–1:05:** Publish the invoice event; show the real Model Armor verdict and
  zero business mutations.
- **1:05–1:45:** Watch Raasid, Kashif and Muslih progress through persisted events;
  show excluded context and the recovery warrant.
- **1:45–2:05:** Approve the exact warrant digest.
- **2:05–2:35:** Clean reassignment completes the sandbox ERP mutation exactly
  once, including a duplicate delivery attempt.
- **2:35–3:05:** Shaahid verification and deterministic Hisaar Gate result.
- **3:05–3:35:** Replay, Cloud Trace, Firestore and model provenance.
- **3:35–4:00:** Measured utility, architecture summary and closing value.

## 14. Platform proof gates before UI expansion

The following facts must be proven in a narrow spike before significant UI work:

1. Both ADK runtimes deploy successfully.
2. Real Registry entries are visible and retrievable.
3. Memory Bank persists and returns a real memory identifier.
4. Direct Model Armor returns a real document-screening verdict.
5. Cloud Trace displays a correlated agent or tool execution.
6. Pub/Sub duplicate delivery is safely deduplicated in Firestore.
7. Scoped runtime identities cannot perform unauthorized writes.

Agent Gateway is attempted only after these seven facts pass.

## 15. Submission package

- Hosted command-room URL and testing credentials if required
- Public or judge-accessible repository containing only newly created project work
- Reproducible local and Google Cloud setup instructions
- Infrastructure and deployment instructions
- Architecture diagram
- Threat and trust-boundary diagram
- Stored evaluation fixtures and immutable run reports
- Model-routing and provenance documentation
- Four-minute public English demonstration video
- Public build article created for the hackathon
- Qualifying social post using `#AllThingsAgenticHackathon`

No additional Google AI model is added merely for bonus points. Gemma, Veo, Lyria
or another model requires separate user approval and a genuine bounded product
role. HisaarAI's submitted runtime remains restricted to the three approved Gemini
model identifiers.

## 16. Definition of winner-ready

HisaarAI is winner-ready only when:

- Every mandatory submission requirement is satisfied.
- The reference workflow passes all release gates using real services.
- The hosted command room displays only backend-derived state.
- The unedited core demo can be reproduced from a clean environment.
- Google Cloud, model, identity, Registry, Model Armor and trace claims match the
  deployed implementation exactly.
- Known preview or unavailable capabilities are omitted from claims.
- The repository, video, architecture and metrics tell the same failure-first
  story without contradictions.

These conditions maximize scoring potential but do not guarantee a prize; judging
and competing submissions remain outside the team's control.
