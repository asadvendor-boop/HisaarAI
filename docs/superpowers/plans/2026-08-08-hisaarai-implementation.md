# HisaarAI — Lean Rubric-First Build Plan

> **Historical planning artifact.** The final runtime and submission truth are
> defined by `README.md`, `docs/DEVPOST.md` and the August 25 final-rubric
> polish design. Do not use conflicting earlier demo or continuity wording.

**Date:** 2026-08-09
**Status:** Approved for implementation
**Design:** `docs/superpowers/specs/2026-08-08-hisaarai-design.md`
**Track:** Fortified Enterprise Fleet
**Goal:** Ship the strongest four-minute product story with the least machinery.

## 0. Build rules

This plan replaces every earlier HisaarAI implementation plan.

- Build one memorable journey: compromised AP agent → blocked payment → clean
  recovery fleet → one human decision → correct sandbox payment exactly once.
- Use only `gemini-3.6-flash` and `gemini-3.5-flash-lite`.
- Use Google Sign-In ID tokens for the commander. Do not build IAP.
- Use exactly three user-managed service accounts: `hisaar-app`,
  `hisaar-ap-runtime`, and `hisaar-recovery-runtime`. Never deploy on the default
  Compute Engine service account.
- Keep Model Armor fail-closed. A conclusive match becomes
  `BLOCKED/MODEL_ARMOR_MATCH`; an error or inconclusive outcome becomes
  `BLOCKED/SCREENING_UNAVAILABLE`. Neither reaches Gemini.
- Keep dependency lockfiles because they make clean installation reliable.
- Do not build GitHub Actions, push-triggered deployment, Terraform, SHA release
  matching, freeze manifests, benchmark suites, IAM-forensics reports, held-out
  fixture custody or statistical claims.
- Deploy manually when a judge-visible slice is ready. A documentation edit must
  never redeploy the app or start a test farm.
- Verification lives inside each product task. The only final local gate is
  `make demo-check`, containing eight business invariants.
- Stop any task once its judge-visible outcome works. Polish only what appears in
  the four-minute recording.

## Calendar-sensitive bootstrap — completed first

The irreversible continuity clock started before the rest of this plan was
written.

- Calendar timezone: `Asia/Karachi`
- Day 0: 2026-08-09
- Day 7: 2026-08-16
- Day 14: 2026-08-23
- Day 21: 2026-08-30
- Google Cloud project: `hisaarai-agentic-2026`
- Final-named Recovery Runtime:
  `projects/957109932069/locations/us-central1/reasoningEngines/6980660236528910336`
- Day-0 Memory:
  `projects/957109932069/locations/us-central1/reasoningEngines/6980660236528910336/memories/6243621652144324608`
- Immutable MemoryRevision:
  `projects/957109932069/locations/us-central1/reasoningEngines/6980660236528910336/memories/6243621652144324608/revisions/2389586264371232768`
- Evidence: `docs/evidence/day-0-continuity.json`

The same Runtime is updated with the complete recovery fleet. Do not replace it
with a fresh resource. The truthful claim is “an application checkpoint backed
by an exact immutable Google MemoryRevision.”

## Task 1 — Finish the real Google Cloud spine

**Rubric:** Architecture and Production Readiness
**Target:** Aug 10–11

Create only the resources needed by the visible journey:

- `src/hisaarai/app.py`: minimal FastAPI app with health, browser and internal
  route groups.
- `src/hisaarai/auth.py`: route-specific Google token verification.
- `src/hisaarai/continuity/`: reuse the deployed Recovery Runtime and create the
  Day-7/14/21 checkpoint job. Cloud Scheduler publishes a date-keyed event to
  Pub/Sub; `/internal/pubsub/events` makes checkpoint creation idempotent by
  calendar date.
- `scripts/deploy_app.sh` and `scripts/deploy_runtimes.py`: explicit manual
  deployments using the three named service accounts.
- One Firestore database, one event Pub/Sub topic/subscription and one Cloud Run
  service. The single push endpoint accepts a strict discriminated envelope for
  `invoice.received`, `continuity.checkpoint` and `recovery.execute`, each with
  its own idempotency key. Create the Protected AP Runtime; retain the existing
  Recovery Runtime.
- Manually create and read back one Google Identity Services OAuth Web client,
  register the exact `.run.app` JavaScript origin, configure its public client
  ID, and capture the allowlisted commander `sub` from one verified login. No
  client secret or IAP is required.
- Configure authenticated Pub/Sub push with the exact app audience and
  `hisaar-app` token identity. Grant the Pub/Sub service agent Token Creator on
  that identity and the subscription creator `actAs`; use the same boundary for
  continuity events.
- Deploy and read back both callable Runtime resource names and their separate
  runtime identities.
- Mirror the Day-0 checkpoint into Firestore, preserving its real server time
  and MemoryRevision name. Schedule the remaining checkpoint dates against the
  final app endpoint.

Cloud Run is publicly reachable because browser Google Sign-In tokens have the
OAuth client as their audience. Application code protects every state-changing
route. Every Google token must pass signature, issuer, expiry, exact route
audience and expected subject or service-account-email checks:

- `/api/commander/*`: Google web-client audience plus allowlisted human `sub`.
- `/internal/pubsub/events`: Pub/Sub push audience plus `hisaar-app` identity and
  one of the three allowed event types.
- Protected AP Runtime invocation: typed bounded input under
  `hisaar-ap-runtime`.
- Recovery Fleet Runtime invocation: typed bounded input under
  `hisaar-recovery-runtime`.

**Done when:** the `.run.app` health page works, both Runtime resource names are
real, Day 0 is visible from Memory Bank and Firestore, and future checkpoints are
scheduled—not fabricated.

## Task 2 — Build Hisaar Gate and the sandbox money boundary

**Rubric:** Innovation plus Architecture
**Target:** Aug 12–13

Implement the smallest authoritative backend:

- `src/hisaarai/contracts.py`: typed incident, proposal, warrant and receipt
  payloads.
- `src/hisaarai/gate.py`: legal state transitions and version checks.
- `src/hisaarai/store.py`: Firestore reads and short transactions.
- `src/hisaarai/sandbox_erp.py`: trusted vendor master and sandbox receipt.

Rules that remain non-negotiable:

- Gemini and network calls run outside Firestore transaction callbacks.
- Only Gate changes incident state or releases execution.
- A mismatch can reach `QUARANTINED` without any receipt.
- The receipt document is keyed by the stable invoice business key.
- Duplicate execution adopts and returns the existing receipt.
- A source/warrant/receipt disagreement can never become `VERIFIED`.

Add focused tests for legal/illegal transitions, no pre-approval receipt, one
idempotent receipt and verification disagreement. Do not add a generated state
sequence campaign.

**Done when:** one backend-driven semantic incident is quarantined with no
receipt, and ten concurrent calls against one approved business key still leave
one stable sandbox receipt.

## Task 3 — Make the protected AP path real

**Rubric:** Innovation and Operational Utility
**Target:** Aug 14–15

Add three small committed text-PDF fixtures:

1. Injection control: Model Armor blocks it before Gemini.
2. Semantic tamper: Model Armor clears the exact extracted text, the AP agent
   proposes the altered fingerprint, and Gate catches the vendor-master mismatch.
3. Clean control: the proposed destination matches the trusted vendor record.

Implement Pub/Sub intake, bounded PDF text extraction, direct Model Armor
screening and the Protected AP ADK agent. Persist the requested/actual model and
thinking level with each run.

Model Armor releases text only if the API call succeeds, invocation is
`SUCCESS`, required filters execute successfully and the relevant result is
`NO_MATCH_FOUND`. A successful `MATCH_FOUND` result persists `BLOCKED` with
reason `MODEL_ARMOR_MATCH`. Error, unavailable, partial, skipped, malformed or
unknown outcomes persist `BLOCKED/SCREENING_UNAVAILABLE`. Both branches make
zero Gemini calls and create zero receipts. Return a terminal 2xx to Pub/Sub
after persisting either state so it does not retry forever.

**Done when:** the three fixtures visibly produce block-before-Gemini,
semantic quarantine and clean behavior on the hosted stack.

## Task 4 — Assemble the clean recovery fleet

**Rubric:** Multi-agent complexity plus Architectural Discipline
**Target:** Aug 16–18

Update the existing Recovery Runtime with five distinct ADK roles:

- Raasid — `gemini-3.5-flash-lite`, default/minimal thinking.
- Kashif — `gemini-3.6-flash`, high thinking.
- Muslih — `gemini-3.6-flash`, high thinking.
- Clean AP Standby — `gemini-3.6-flash`, medium thinking.
- Shaahid — `gemini-3.5-flash-lite`, default/minimal thinking.

Keep outputs typed and short. Raasid reads persisted events and the latest exact
MemoryRevision. One bounded, non-authoritative continuity policy field selects
the recovery playbook; its MemoryRevision name is persisted on the incident and
warrant and shown in the UI. Kashif receives only bounded correlated evidence;
Muslih drafts but cannot approve; the standby gets trusted vendor data and the
approved warrant but no raw invoice or contaminated session; Shaahid narrates
deterministic checks but cannot change verdicts.

Give every recovery role a bounded timeout and strict output validation. A
timeout, invalid schema or missing required evidence persists terminal `BLOCKED`,
creates no warrant or receipt, and appears as a backend-derived blocked state.
This is product behavior, not a separate fault-testing campaign.

Gate re-reads trusted sources and materializes the authoritative warrant with a
ten-minute expiry. Agent output cannot become authority merely because its JSON
is valid.

**Done when:** the hosted semantic incident reaches `AWAITING_APPROVAL` with
three readable specialist findings and a Gate-owned warrant, while the standby
request contains no contaminated context identifiers or invoice text.

## Task 5 — Complete governed recovery after one human decision

**Rubric:** Innovation and Production Readiness
**Target:** Aug 19–20

Implement Google Identity Services callback mode. Keep the ID token in browser
memory and send it as a bearer token. The backend validates Google signature,
issuer, expiry, exact OAuth web-client audience and allowlisted stable `sub`;
email is display-only.

Approval reloads the current warrant and trusted source, rejects wrong identity
without changing incident state, and atomically changes a valid current warrant
`AWAITING_APPROVAL → APPROVED`. Human rejection records the commander, rationale
and server time and terminates as `BLOCKED/HUMAN_REJECTED` without execution. An
expired current warrant becomes `BLOCKED/WARRANT_EXPIRED`; a retry begins a new
attempt from quarantine, keeps the launch-scoped business idempotency key and creates a
fresh warrant.

After approval, publish the clean execution request and return immediately; the
UI polls persisted state. The standby creates or adopts the one sandbox receipt.
Deterministic code compares receipt, warrant and source before Gate persists
`VERIFIED`; Shaahid supplies only the readable narrative.

**Done when:** one live journey shows pre-approval denial, one accountable human
approval, completion by the clean standby, the same receipt on replay and final
`VERIFIED`. An expired approval must remain denied.

## Task 6 — Build the one-screen command room

**Rubric:** Demo and Production Readiness
**Target:** Aug 20–23

Use a React/Vite frontend built into and served by the FastAPI container. Keep
only two lockfiles: `uv.lock` and `web/package-lock.json`.

Above the fold must communicate within 30 seconds:

- “The agent was compromised. The payment was not.”
- Amount at risk and current incident state.
- Six distinct agent cards with name, role, model and backend-driven status.
- One flagship launch action.

The main view shows invoice versus vendor fingerprint, the live recovery
timeline and the authoritative warrant/approval panel. The outcome shows unsafe
payment blocked, trusted payment completed once, receipt, replay `MATCH`,
Shaahid’s summary and real proof links for both Runtime resources, Memory Bank
and the correlated Trace.

Do not add extra pages, fake log streams, invented scores, generic analytics or
configuration screens. Meet responsive layout, keyboard focus and readable
contrast because judges may watch on a laptop or compressed video.

**Done when:** a non-technical viewer can explain the before/after outcome after
30 seconds, and the full live journey runs without a terminal.

## Task 7 — Bind just enough proof for a reliable recording

**Rubric:** Architecture and Production Readiness
**Target:** Aug 24–28

Add one correlated trace/log path through Pub/Sub, Model Armor, both Runtimes,
Gate and Firestore. Surface real resource names and currently available
continuity dates in the UI; future dates remain `PENDING`.

Create `make demo-check` with exactly these eight checks:

1. Injection and non-clear Model Armor results never reach Gemini.
2. Vendor mismatch reaches `QUARANTINED` with no receipt.
3. Execution before approval is denied.
4. Wrong or expired approval is denied.
5. Clean standby input excludes contaminated context.
6. Duplicate execution returns one stable receipt.
7. Verification fails when warrant, source and receipt disagree.
8. Clean control completes normally.

These are focused business checks, not a benchmark. Run two timed continuous
dress rehearsals against the candidate deployment. Fix only failures that can
break the judge story.

**Done when:** all eight checks pass once against the candidate build and two
four-minute rehearsals complete cleanly.

## Task 8 — Ship the submission

**Rubric:** Demo and Production Readiness plus Stage-One eligibility
**Target:** Aug 29–31

- Capture genuine Day 21 on Aug 30 and show Day 0/7/14/21 with their actual
  dates. Never backfill a missed checkpoint.
- Perform one intentional image-digest deployment of the candidate app. The
  digest proves what was deployed at that moment; later documentation commits do
  not need to match it and do not trigger redeployment.
- Verify a clean lockfile install, run `make demo-check`, then stop engineering.
- Write the concise README, setup steps, architecture diagram, limitations and
  Devpost fields.
- Record one continuous, normal-speed English video no longer than four minutes.
- Confirm the public repository, hosted URL and video tell the same narrow story.
- Work on the optional article/social bonus only after the core submission is
  complete.

**Done when:** the hosted app, repository and video all demonstrate the same
business outcome, every public claim is no broader than observed behavior, and
the Devpost eligibility checklist is complete.

## Definition of winning-ready

Winning-ready does not mean exhaustive proof. It means a judge can see, in one
continuous four-minute experience, that HisaarAI:

1. catches both obvious prompt injection and harder semantic tampering;
2. quarantines the compromised agent and its context before money moves;
3. uses a real specialized Google agent fleet to reconstruct the safe action;
4. obtains one clear human governance decision;
5. finishes the business process correctly and exactly once; and
6. proves the story with real Google Cloud resources and honest multi-week
   memory.

Anything else is optional and cut first.
