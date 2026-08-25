# HisaarAI Final Rubric Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Do not use
> parallel workers because the proof IDs, documentation and hosted deployment
> are sequentially coupled.

**Goal:** Correct the two remaining provenance claims, make the hosted proof
judge-first, align the story truthfully with Google's August 25 Financial
Services announcement, and produce one continuous submission-ready demo.

**Architecture:** Preserve the current Cloud Run, ADK Agent Runtime, Model Armor,
Firestore, Pub/Sub and deterministic Gate design. Make one backward-compatible
receipt-field addition, presentation-only frontend changes, precise documentation
corrections and one fresh hosted proof cycle. Gemini Enterprise for Financial
Services remains narrative context rather than a runtime dependency.

**Tech Stack:** Python 3.13, Pydantic, FastAPI, Firestore, Google ADK, Vertex AI,
React, TypeScript, Vite, SVG, Cloud Run and Playwright/browser verification.

## Global constraints

- Keep only Gemini 3.6 Flash and Gemini 3.5 Flash-Lite in the approved core.
- Hisaar Gate remains the only component allowed to persist finality.
- Do not add MCP, A2A, Agent Gateway, Financial Research Agent, an ERP connector,
  customer data, real-money mutation or anonymous commander authority.
- Do not add CI/CD, SHA matching, a broad test matrix or a new release verifier.
- Keep committed lockfiles; group work into a small number of local commits and
  push once after the hosted proof is verified.
- Use one continuous live workflow in the video. AI voiceover and explanatory
  overlays are allowed; workflow cuts, splicing and rearrangement are forbidden.
- All measurements remain `observed hosted run / n=1` and all financial records
  remain synthetic enterprise-shaped sandbox data.
- Do not wait for Day 21 before recording or submission.

**Execution order:** Complete Tasks 1–6, then Task 8. Task 7 is an optional
branch: run its access-only spike before Task 6 if the user explicitly chooses
to pursue Gemma; otherwise skip it without delaying the mandatory sequence.

---

### Task 1: Correct receipt provenance without breaking old receipts

**Files:**
- Modify: `src/hisaarai/contracts.py`
- Modify: `src/hisaarai/sandbox_erp.py`
- Modify: `src/hisaarai/governance.py`
- Modify: `src/hisaarai/store.py`
- Modify: `web/src/App.tsx`
- Test: `tests/test_task5_governance.py`
- Test: `tests/test_task2_gate.py`

**Interfaces:**
- `SandboxReceipt.executor_identity` remains a required string and now records
  the actual persistence actor.
- `SandboxReceipt.reasoning_runtime_identity: str | None = None` records the
  Recovery Runtime model identity and preserves compatibility with older
  Firestore documents.
- `SandboxERP.execute(..., executor_identity: str,
  reasoning_runtime_identity: str | None = None) -> SandboxReceipt` persists
  both identities.

- [ ] **Step 1: Add the failing governance assertion**

  Extend `test_one_human_decision_completes_once_and_replay_is_stable` with:

  ```python
  assert receipt.executor_identity == settings().app_service_account
  assert (
      receipt.reasoning_runtime_identity
      == settings().recovery_runtime_service_account
  )
  ```

- [ ] **Step 2: Verify the targeted test fails for the current misattribution**

  Run:

  ```bash
  PYTHONPATH=src uv run pytest -q \
    tests/test_task5_governance.py::test_one_human_decision_completes_once_and_replay_is_stable
  ```

  Expected: failure because `executor_identity` is the Recovery Runtime and the
  second field does not exist.

- [ ] **Step 3: Add the backward-compatible receipt field**

  In `SandboxReceipt`, keep `executor_identity: str` and add:

  ```python
  reasoning_runtime_identity: str | None = None
  ```

  Add the same field to `_receipt_binding()` after `executor_identity` so a
  replay cannot silently substitute a different reasoning identity.

- [ ] **Step 4: Pass both real identities at execution**

  Extend `SandboxERP.execute` with the optional keyword argument, copy it into
  `SandboxReceipt`, and change `GovernedRecovery.execute_and_verify` to call:

  ```python
  receipt = self.erp.execute(
      request,
      executor_identity=self.settings.app_service_account,
      reasoning_runtime_identity=(
          self.settings.recovery_runtime_service_account
      ),
  )
  ```

- [ ] **Step 5: Expose both provenance fields in the finality panel**

  Extend the frontend `Receipt` type with:

  ```ts
  executor_identity: string;
  reasoning_runtime_identity: string | null;
  ```

  Add two rows under the receipt destination:

  ```tsx
  <div><dt>Persistence actor</dt><dd>{data?.receipt?.executor_identity ?? "Locked"}</dd></div>
  <div><dt>Recovery runtime</dt><dd>{data?.receipt?.reasoning_runtime_identity ?? "Legacy receipt"}</dd></div>
  ```

  Do not label either value simply as “executor.”

- [ ] **Step 6: Run the narrow provenance and idempotency tests**

  Run:

  ```bash
  PYTHONPATH=src uv run pytest -q \
    tests/test_task5_governance.py \
    tests/test_task2_gate.py
  ```

  Expected: all selected tests pass.

---

### Task 2: Calibrate Memory Bank and Clean AP claims

**Files:**
- Modify: `README.md`
- Modify: `docs/DEVPOST.md`
- Modify: `docs/BUILD_ARTICLE.md`
- Modify: `docs/media/architecture.svg`
- Modify: `docs/superpowers/specs/2026-08-08-hisaarai-design.md`
- Modify: `docs/superpowers/plans/2026-08-08-hisaarai-implementation.md`

**Interfaces:** Documentation must describe the implemented runtime boundary;
no code or cloud API is added in this task.

- [ ] **Step 1: Replace the direct Memory-read claim everywhere public**

  Use this exact sentence in README, Devpost and the article:

  > Recovery consumes a Firestore checkpoint mirror bound to the exact genuine
  > Memory Bank revision resource name; the warrant preserves that binding
  > without adding quarantined invoice text to the clean context.

  Remove wording that says the Recovery Fleet directly “reads” or “uses” the
  latest immutable Memory revision.

- [ ] **Step 2: Correct the Clean AP execution description**

  Use this exact authority wording:

  > Clean AP validates the exact approved request. Hisaar Gate, running under
  > the application persistence identity, commits the idempotent sandbox
  > receipt and performs deterministic verification.

  Replace “Clean AP executes the payment” and analogous claims in public copy.

- [ ] **Step 3: Correct and label the architecture diagram**

  Make these text-only SVG changes without adding new boxes:

  - Protected AP Runtime: `Google ADK • Gemini 3.6 Flash / Vertex AI`.
  - Recovery Fleet Runtime: `Google ADK • Gemini 3.6 + 3.5 Flash-Lite / Vertex AI`.
  - Clean AP role: change `Execute` to `Validate`.
  - Memory Bank: change the body to `Firestore checkpoint mirror • bound to a genuine revision`.
  - Hisaar Gate: add `App persistence identity writes the sandbox receipt`.

- [ ] **Step 4: Mark older design and implementation documents as historical**

  Add this block directly under each old document title:

  > **Historical planning artifact.** The final runtime and submission truth are
  > defined by `README.md`, `docs/DEVPOST.md` and the August 25 final-rubric
  > polish design. Do not use conflicting earlier demo or continuity wording.

- [ ] **Step 5: Export and inspect the architecture upload asset**

  Run:

  ```bash
  rsvg-convert -w 1600 -h 900 \
    docs/media/architecture.svg \
    -o docs/media/architecture.png
  ```

  Inspect the PNG at native size. Expected: Gemini, ADK, Vertex AI, Gate and the
  checkpoint-mirror relationship are readable without zooming.

---

### Task 3: Add the approved Financial Services “why now” alignment

**Files:**
- Modify: `docs/DEVPOST.md`
- Modify: `docs/BUILD_ARTICLE.md`
- Modify: `docs/DEMO_SCRIPT.md`

**Interfaces:** Narrative only. No Gemini Enterprise, MCP, A2A or Financial
Research Agent client is added.

- [ ] **Step 1: Add the sourced Devpost “Why now” paragraph**

  Insert after `What makes it different`:

  > On August 25, Google Cloud introduced Gemini Enterprise for Financial
  > Services around specialized financial skills, secure data connections,
  > acting agents and centralized governance. HisaarAI explores the
  > complementary recovery problem: when a financial agent's context is
  > poisoned, how can the institution contain it, reconstruct trusted context
  > and safely finish the work exactly once? HisaarAI demonstrates aligned
  > design principles; it does not claim integration with the preview product.

  Link “introduced Gemini Enterprise for Financial Services” to:
  `https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-for-financial-services`.

- [ ] **Step 2: Add the four-principle mapping to the public article**

  Add the exact table from the approved design after the Google-stack paragraph.
  Precede it with: `HisaarAI demonstrates the same governed design principles in
  a bounded AP recovery scenario:`.

- [ ] **Step 3: Add the five-second narration line**

  Add this to the architecture segment of the demo script:

  > “Google Cloud is bringing governed agents into financial workflows.
  > HisaarAI answers the next question: how do you safely recover one when its
  > context is poisoned?”

- [ ] **Step 4: Run a prohibited-claim scan**

  Run:

  ```bash
  rg -n "built on Gemini Enterprise for Financial Services|integrat(e|ed|ion).*Financial Research|uses Gemini Enterprise for Financial Services" \
    README.md docs
  ```

  Expected: no matches.

---

### Task 4: Make the signed-out judge path outcome-first

**Files:**
- Modify: `web/src/App.tsx`
- Modify: `web/src/styles.css`
- Test: `web/src/App.timeline.test.mjs`

**Interfaces:** Existing authenticated launch endpoints and commander policy do
not change. Public actions remain read-only GET navigation and replay.

- [ ] **Step 1: Replace the signed-out primary action**

  When there is no commander token, render a primary anchor to the verified
  incident instead of a disabled flagship button:

  ```tsx
  <a className="primary proof-cta" href={`/?incident=${publicProofs[0][1]}`}>
    <span>VIEW VERIFIED RECOVERY</span><b>↗</b>
  </a>
  ```

  Authenticated commanders continue to see `RUN FLAGSHIP INCIDENT`.

- [ ] **Step 2: Replace misleading unloaded states**

  For a shared incident that has not returned yet, display `LOADING PROOF…`.
  For a Model Armor `MODEL_ARMOR_MATCH` with no proposal, display
  `NO PROPOSAL — BLOCKED PRE-GEMINI`. For an idle authenticated root, display
  `READY`; never show `NOT LOADED` to a judge.

- [ ] **Step 3: Bring the outcome strip into the first proof viewport**

  Add a `proof-hero` class when `sharedIncidentId` is present and use a compact
  shared-proof hero at desktop widths. At 1440x900, the headline, amount/state
  and the complete three-cell outcome strip must all be visible before scroll.
  Do not reduce the public body font below its current size.

- [ ] **Step 4: Clarify public versus project-restricted provenance**

  Change the footer heading to `GOOGLE CLOUD PROVENANCE / PROJECT ACCESS
  REQUIRED FOR CONSOLE`. Add visible public links beside it for the current
  incident JSON, public replay when verified, and repository evidence. Do not
  remove the existing Cloud Console links.

- [ ] **Step 5: Run frontend checks**

  Run:

  ```bash
  node --test web/src/App.timeline.test.mjs
  npm run build --prefix web
  ```

  Expected: two frontend tests pass and Vite exits successfully.

- [ ] **Step 6: Inspect signed-out desktop views**

  Inspect root, verified, Model Armor and clean-control URLs at 1440x900 without
  Google authentication. Expected:

  - Root has an active `VIEW VERIFIED RECOVERY` primary action.
  - Verified proof shows the full before/control/after strip in the first viewport.
  - Model Armor says `NO PROPOSAL — BLOCKED PRE-GEMINI`.
  - Public replay remains a GET-only action and returns `MATCH`.

---

### Task 5: Replace the edited-demo instructions with one continuous run

**Files:**
- Rewrite: `docs/DEMO_SCRIPT.md`
- Modify: `docs/SUBMISSION_CHECKLIST.md`
- Modify: `docs/DEVPOST.md`

**Interfaces:** This task defines the human recording procedure; it does not
alter runtime behavior.

- [ ] **Step 1: Change the demo contract**

  Title the script `HisaarAI — continuous live demo under four minutes` and open
  with:

  > Record one continuous genuine screen capture. Do not cut, splice, reorder
  > or hide any workflow stage. Add accurate AI voiceover, subtitles and
  > explanatory overlays after recording. If uniform speed-up is necessary,
  > apply it to the entire capture and label the speed on screen.

- [ ] **Step 2: Use the final continuous timeline**

  Implement this recording order:

  1. `0:00–0:15`: start on the persisted final before/control/after proof.
  2. `0:15–0:45`: navigate to the signed-in root, launch one fresh PKR 4.275M
     semantic-tamper incident and explain the risk.
  3. `0:45–1:25`: while the real recovery runs, explain specialized roles,
     bounded evidence and deterministic authority.
  4. `1:25–1:55`: show the exact warrant and approve once immediately when ready.
  5. `1:55–2:20`: show one receipt, both provenance identities and replay `MATCH`.
  6. `2:20–2:45`: navigate to the persisted Model Armor proof and show zero
     Gemini calls and no receipt.
  7. `2:45–3:15`: show the simplified architecture, real Google Cloud proof and
     the five-second Financial Services “why now” line.
  8. `3:15–3:30`: close on synthetic enterprise-shaped data, sandbox mutation
     and observed run `n=1`.

- [ ] **Step 3: Use the rubric positioning sentence**

  Include exactly:

  > “HisaarAI autonomously moves an untrusted invoice from arrival to an
  > approval-ready recovery warrant. An accounts-payable operator—not a SOC
  > engineer—makes one exact, policy-required decision, while deterministic
  > Hisaar Gate permits only one verified sandbox mutation.”

- [ ] **Step 4: Remove expensive narration**

  Do not narrate every agent biography, the continuity recovery postmortem,
  every Cloud service, CI/testing mechanics, or Day 21. Show the Day-0/7/14
  continuity chip briefly and leave Day 21 visibly pending.

- [ ] **Step 5: Correct upload metadata and checklist**

  Replace “edited live-product demo” with “continuous live-product demo.” Remove
  every checklist instruction to record clips or use jump cuts. Require a public
  YouTube/Vimeo upload under four minutes and one full playback of the uploaded
  copy.

---

### Task 6: Run the lean release check and deploy once

**Files:**
- Modify after observation: `docs/evidence/hosted-judge-path.json`
- Modify after observation: `README.md`
- Modify after observation: `docs/DEVPOST.md`
- Modify after observation: `docs/DEMO_SCRIPT.md`
- Modify after observation: `docs/SUBMISSION_CHECKLIST.md`
- Modify after observation: `web/src/App.tsx`
- Replace after observation: `docs/media/command-room.png`

**Interfaces:** The deployment must preserve the existing Cloud Run URL,
commander allowlist, Pub/Sub audience, Agent Runtime names and Model Armor
template.

- [ ] **Step 1: Run only the agreed local checks**

  Run:

  ```bash
  PYTHONPATH=src uv run pytest -q
  make demo-check
  node --test web/src/App.timeline.test.mjs
  npm run build --prefix web
  git diff --check
  ```

  Expected: all Python tests pass, all eight business invariants pass, two
  frontend tests pass, Vite builds and `git diff --check` is silent.

- [ ] **Step 2: Review the diff before cloud mutation**

  Confirm the diff contains only the approved provenance, wording, architecture,
  judge-path, demo and checklist changes. It must contain no new model, service,
  anonymous mutation route, MCP/A2A client or customer-data claim.

- [ ] **Step 3: Deploy the existing Cloud Run service once**

  Run the existing deployment script with the already-configured commander
  environment:

  ```bash
  scripts/deploy_app.sh
  ```

  Expected: a new healthy revision on the existing `.run.app` URL.

- [ ] **Step 4: Run one fresh authenticated flagship incident**

  Sign in as the allowlisted commander, launch the semantic-tamper fixture,
  approve the current exact warrant once, and wait for `VERIFIED`. Record the
  actual incident ID, receipt ID, observed phase timings, app persistence actor,
  Recovery Runtime identity, trusted fingerprint and continuity revision.

- [ ] **Step 5: Verify the new proof without authentication**

  Run:

  ```bash
  read -r -p "Paste the observed flagship incident ID: " hisaar_incident_id
  test -n "$hisaar_incident_id"
  curl -fsS "https://hisaarai-2wkruw66na-uc.a.run.app/health"
  curl -fsS "https://hisaarai-2wkruw66na-uc.a.run.app/api/incidents/$hisaar_incident_id"
  curl -fsS "https://hisaarai-2wkruw66na-uc.a.run.app/api/incidents/$hisaar_incident_id/replay"
  ```

  Expected: health is healthy; incident is `VERIFIED`; receipt persistence actor
  is `hisaar-app@...`; reasoning identity is `hisaar-recovery-runtime@...`; replay
  returns the same receipt and `MATCH`.

- [ ] **Step 6: Bind every primary link to the observed incident**

  Replace the previous flagship ID and receipt ID in README, Devpost, demo,
  checklist, hosted evidence and `publicProofs`. Do not change the injection and
  clean-control IDs unless their live evidence changed.

- [ ] **Step 7: Replace the stale command-room screenshot**

  Capture the new verified proof at 1440x900 after public replay returns `MATCH`.
  Replace `docs/media/command-room.png` and visually confirm that its timings,
  identities, receipt and destination agree with the live incident.

- [ ] **Step 8: Commit and push the verified package once**

  Create one local commit for the approved final polish, push it to the public
  repository, then confirm the public GitHub commit contains the updated README,
  architecture PNG, evidence and demo instructions. Do not add a new CI
  workflow or SHA gate.

---

### Task 7: Make the Gemma bonus a strict optional decision gate

**Files:** None in the approved core plan.

**Interfaces:** A Gemma integration requires a separate approved mini-design.
It must remain read-only and post-verification; it may never influence Gate,
approval, execution or the receipt comparison.

- [ ] **Step 1: Decide before the final video—not during core repair**

  Verify whether the existing Google Cloud project can invoke an organizer-
  eligible Gemma model with acceptable quota and latency. Time-box this access
  check to 30 minutes and make no repository change during the check.

- [ ] **Step 2: Apply the go/no-go rule**

  - `GO` only if one real hosted call succeeds reliably and the organizer's
    bonus wording clearly accepts that model.
  - `NO-GO` on entitlement, deployment, quota, latency or model-identifier
    uncertainty.

  On `GO`, pause and obtain explicit approval for a separate design that uses
  Gemma only for Shaahid's optional post-verification regulatory brief. On
  `NO-GO`, continue directly to recording. Never add Veo or Lyria.

---

### Task 8: Record, publish and close Stage One

**Files:**
- Modify after upload: `README.md`
- Modify after upload: `docs/DEVPOST.md`
- Modify after publication: `docs/SOCIAL_POST.md`
- Modify: `docs/SUBMISSION_CHECKLIST.md`

**Interfaces:** Human-owned YouTube/Vimeo, Devpost and social accounts. The code
agent may prepare text and verify public URLs but may not impersonate the entrant
or accept legal declarations.

- [ ] **Step 1: Record the continuous flagship footage**

  Use the final script, 16:9 at 1440x900 or 1920x1080, signed in before capture,
  notifications silenced and no live typing. Keep the raw workflow continuous.

- [ ] **Step 2: Add accurate AI narration and overlays**

  Preserve every workflow frame in order. Add only narration, subtitles,
  highlights and explanatory labels. If the capture exceeds four minutes,
  uniformly speed the complete capture and display `CONTINUOUS LIVE EXECUTION —
  UNIFORMLY SPED UP — NO CUTS OR SPLICING`.

- [ ] **Step 3: Upload publicly and verify the uploaded copy**

  Publish to YouTube or Vimeo as public, not unlisted. Confirm duration is under
  four minutes, English narration/subtitles are audible/readable, 1080p playback
  works and the description links the hosted app and repository.

- [ ] **Step 4: Replace every video `PENDING` marker**

  Put the exact public video URL in README, Devpost, social copy and the Devpost
  submission form. Search:

  ```bash
  rg -n "VIDEO_URL|Demo video: `PENDING`|video remains \*\*PENDING\*\*" README.md docs
  ```

  Expected: no unresolved public-video placeholder remains.

- [ ] **Step 5: Publish the explicit scoring bonuses**

  Publish `BUILD_ARTICLE.md` on a public accepted platform with its required
  hackathon-purpose sentence. Publish the social post with
  `#AllThingsAgenticHackathon`. Add both public URLs to Devpost. Do not delay the
  core submission for Gemma.

- [ ] **Step 6: Close the human Devpost checklist**

  Confirm eligibility, roster acceptance, asset permissions, Fortified category,
  hosted verified-proof URL, public repository, architecture PNG, SDK/start
  date, testing instructions and pre-existing-code disclosure. Submit, reopen
  the form, and confirm every field and link persisted.

- [ ] **Step 7: Perform the final signed-out judge check**

  In a signed-out browser, open the submitted app, verified proof, replay,
  repository, architecture, video, article and social post. Expected: all public
  assets load, the replay returns the same receipt with `MATCH`, and privileged
  launch/approval remain commander-only.
