# HisaarAI Judge-Readiness Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task-by-task.

**Goal:** Correct every identified judge-visible truth defect, make governed
execution safely resumable, compress the live business transformation, align
public claims with evidence, and produce fresh hosted proof.

**Architecture:** Preserve the current single Cloud Run application, two ADK
Agent Runtimes, Firestore authority, Pub/Sub delivery and React command room.
Make bounded changes at the recovery payload, approval route, UI presentation
and documentation layers; do not add services or release machinery.

**Tech Stack:** Python 3.13, FastAPI, Pydantic, Firestore, Pub/Sub, Google ADK,
Gemini 3.6 Flash, Gemini 3.5 Flash-Lite, React, TypeScript and Vite.

## Global Constraints

- CreditLock, MuhafizSRE and CrossPatch remain out of scope.
- Only `gemini-3.6-flash` and `gemini-3.5-flash-lite` are allowed.
- Hisaar Gate alone owns state, approval release and deterministic verification.
- Public claims must be no broader than the loaded persisted evidence.
- Financial effects remain confined to the Firestore sandbox ledger.
- No GitHub Actions, SHA ceremony, bulk evaluation, Agent Gateway, new database
  or new microservice.
- Retain dependency lockfiles.

---

### Task 1: Correct recovery amount semantics and resumable approval

**Files:**
- Modify: `src/hisaarai/recovery_flow.py`
- Modify: `src/hisaarai/agents/recovery_fleet.py`
- Modify: `src/hisaarai/app_factory.py`
- Modify: `tests/test_task4_recovery.py`
- Modify: `tests/test_task1_spine.py`

**Interfaces:**
- Planning payload exposes `proposal.amount_display`, never
  `proposal.amount_minor`.
- `POST /api/commander/incidents/{incident_id}/approve` accepts an exact retry
  in `APPROVED`, returns terminal results in `COMPLETED/VERIFIED`, and publishes
  stable event ID `execute-{attempt_id}` only while execution is pending.
- `POST /api/commander/incidents/{incident_id}/replay` returns
  `{state, receipt_id, replay: "MATCH"}` only for a verified stable receipt.

- [ ] Add focused regression coverage for major-unit planning input and ensure
      the test fails against the existing raw-minor payload.
- [ ] Add a route regression where the first execution publish fails after
      approval, the exact approval retry republishes safely, and a terminal
      retry does not publish again.
- [ ] Implement the minimal amount and approval/replay changes.
- [ ] Run the focused tests and the eight-invariant `make demo-check` command.

### Task 2: Repair and compress the judge-facing command room

**Files:**
- Modify: `web/src/App.tsx`
- Modify: `web/src/styles.css`

**Interfaces:**
- `BLOCKED` has an explicit terminal rail row.
- Missing proposal/vendor evidence renders `NOT REACHED` and cannot render a
  mismatch.
- `VERIFIED` renders Shaahid `COMPLETE`.
- Landing state links to both public persisted proofs.
- Outcome strip derives only from incident state/history, proposal, trusted
  vendor and receipt.
- Commander rejection is available only in `AWAITING_APPROVAL`; replay proof is
  available only in `VERIFIED` and reports the returned receipt ID.

- [ ] Implement the state/presentation repairs without changing the established
      industrial bastion aesthetic.
- [ ] Add the above-fold buyer line and `BEFORE / CONTROL / AFTER` evidence strip.
- [ ] Add proof navigation, rejection and replay interactions with accessible
      focus, labels and responsive layout.
- [ ] Run `npm run build --prefix web` and inspect the local app at desktop and
      mobile widths.

### Task 3: Align every public claim and submission artifact

**Files:**
- Modify: `README.md`
- Modify: `docs/DEVPOST.md`
- Modify: `docs/DEMO_SCRIPT.md`
- Modify: `docs/BUILD_ARTICLE.md`
- Modify: `docs/SUBMISSION_CHECKLIST.md`
- Modify: `docs/superpowers/specs/2026-08-08-hisaarai-design.md`
- Modify: `docs/superpowers/plans/2026-08-08-hisaarai-implementation.md`
- Create: `docs/media/architecture.svg`

**Interfaces:**
- Public materials say “two callable Agent Runtime resources” and “typed input
  and authority boundaries.” After official live readback, they may also claim
  Agent Registry discovery of exactly those two Runtime agents, but no
  agent-callable tool layer or Registry execution authority.
- Devpost names the three data sources and one implementation learning.
- README documents every required environment variable and the no-cloud
  `make demo-check` path.
- Demo opens outcome-first, states the observed `n=1` transformation, shows
  cloud proof before the final minute and remains under four minutes.

- [x] Calibrate Registry and tool-boundary claims everywhere; after the official
      readback, add only the bounded two-agent discovery proof.
- [ ] Add the outcome-first buyer/data-source/learnings copy and static diagram.
- [ ] Update setup and public testing instructions without adding release
      ceremony.
- [ ] Search for stale claims and verify every referenced link/path exists.

### Task 4: Verify, deploy and bind fresh hosted proof

**Files:**
- Modify after live readback: `README.md`
- Modify after live readback: `docs/DEVPOST.md`
- Modify after live readback: `docs/evidence/hosted-judge-path.json`
- Modify after live readback: `docs/SUBMISSION_CHECKLIST.md`

**Interfaces:**
- The same final deployment produces fresh injection, semantic and clean
  incident IDs.
- Public read-only links load without authentication.
- Evidence records only observed resource names, states, receipt IDs and trace
  IDs; it does not require a repository hash manifest.

- [ ] Run fresh full Python tests, `make demo-check`, frontend build and
      `git diff --check`.
- [ ] Deploy once with the existing user-managed app service account.
- [ ] Run and inspect fresh injection, signed semantic, replay and clean-control
      flows on the deployed candidate.
- [ ] Update the public proof IDs/evidence and deploy the final documentation/UI
      candidate if those IDs changed after the first deployment.
- [ ] Perform desktop/mobile browser inspection and two timed continuous
      rehearsals; leave recording/upload/submission as explicit human actions.

