# HisaarAI Final Rubric Polish Design

**Status:** Approved on 2026-08-25 for planning. This design supersedes the
presentation and demo-format instructions in earlier planning documents where
they conflict.

## Goal

Finish HisaarAI as a truthful, judge-first Fortified Enterprise Fleet
submission without adding a broad feature, cloud service, agent, authority path,
or release ceremony. The final package must make one business transformation
obvious in the first ten seconds: attacker-directed PKR 4.275M proposal,
quarantine before mutation, trusted reconstruction, one accountable decision,
one receipt, and deterministic replay `MATCH`.

## Global decisions

- The flagship footage is one continuous genuine workflow. AI voiceover,
  subtitles and explanatory overlays are allowed; workflow cuts, splicing,
  rearrangement and concealed failures are not.
- Gemini Enterprise for Financial Services is narrative alignment only. HisaarAI
  must not claim to use, integrate with, or run on that preview solution.
- The submitted core continues to use Gemini 3.7 Flash and Gemini 3.5
  Flash-Lite through Google ADK. No MCP, A2A, Agent Gateway, Financial Research
  Agent, production ERP, bank connector, customer data or real-money mutation is
  added.
- Gemma is a separate optional bonus decision. It is not part of this approved
  core design and cannot delay the flagship proof, video or submission.
- Hisaar Gate remains the only recovery authority. Models may interpret,
  validate or narrate; they may not approve, persist `VERIFIED`, or decide that
  a receipt matches.
- No SHA lock ceremony, CI/CD expansion, broad benchmark, held-out custodian or
  exhaustive test suite is added. Keep lockfiles and run only targeted tests,
  the eight business invariants, the frontend build and live signed-out proof.
- Public claims remain bounded to synthetic enterprise-shaped records, a
  sandbox ledger and observed run `n=1`.

## 1. Correct receipt provenance

The Recovery Runtime genuinely performs the bounded model-validation step, but
the Cloud Run application service account owns the Firestore client and persists
the sandbox receipt. New receipts must therefore expose both facts:

- `executor_identity`: the actual persistence actor, `hisaar-app@...`.
- `reasoning_runtime_identity`: the Recovery Runtime identity that validated the
  approved request before persistence.

The schema must remain backward compatible with already-persisted receipts that
lack `reasoning_runtime_identity`. The primary judge link must be replaced with
a fresh incident generated after this correction.

## 2. Calibrate Memory Bank wording

HisaarAI has genuine Memory Bank revisions. Runtime recovery consumes the
Firestore checkpoint mirror and binds the exact genuine Memory revision resource
name into the warrant; it does not directly reread the Memory API in the
recovery path. README, Devpost, article, diagram and narration must use that
precise claim. No late Memory API dependency is added.

Clean AP must be described as validating the exact approved request. Hisaar
Gate, running under the application persistence actor, commits the idempotent
sandbox receipt.

## 3. Judge-first hosted experience

For signed-out visitors, the primary hero action becomes `VIEW VERIFIED
RECOVERY`. The verified proof URL becomes the Devpost hosted-project URL. At
1440x900 the verified page must show the headline and the complete
`BEFORE / HISAAR CONTROL / AFTER` strip in the first viewport.

The root and proof states must avoid confusing `NOT LOADED` language. The Model
Armor proof says `NO PROPOSAL — BLOCKED PRE-GEMINI`. Cloud Console links are
labelled `PROJECT ACCESS REQUIRED`, while public incident, replay and evidence
links remain visibly available without authentication.

## 4. Architecture and current Google Cloud alignment

The detailed architecture remains intact but explicitly labels Google ADK,
Gemini 3.7 Flash, Gemini 3.5 Flash-Lite and Vertex AI inside the two Runtime
boxes. Its Memory Bank label states that recovery uses a Firestore checkpoint
mirror bound to a genuine Memory revision. Clean AP is labelled as validation,
not the Firestore writer. A 1600x900 PNG export is created for Devpost.

Devpost, the public build article and five seconds of narration add this truthful
“why now” statement:

> On August 25, Google Cloud introduced Gemini Enterprise for Financial Services
> around specialized financial skills, secure data connections, acting agents
> and centralized governance. HisaarAI explores the complementary recovery
> problem: when a financial agent's context is poisoned, how can the institution
> contain it, reconstruct trusted context and safely finish the work exactly once?

The article maps Google's four design principles to existing HisaarAI evidence:

| Google Cloud design principle | HisaarAI evidence |
| --- | --- |
| Purpose-built financial skills | Bounded AP recovery playbook and specialist instructions |
| Secure connections | Scoped vendor-master and sandbox-ledger tools |
| Agents that act | Quarantine, reconstruction, warrant preparation and verified completion |
| Governed control plane | Hisaar Gate, commander approval, Model Armor, identities, traces and immutable receipt |

Every use of this comparison must say “aligned with” or “demonstrates the same
design principles,” never “built on Gemini Enterprise for Financial Services.”

## 5. Continuous demo and final submission

The video opens on the outcome, then launches one fresh flagship incident in the
same uninterrupted screen capture. While the asynchronous workflow runs, the
narration explains specialization and deterministic authority. The commander
approves the exact warrant once; the recording shows one receipt and public
replay `MATCH`, then navigates to the persisted Model Armor proof, simplified
architecture and public Google provenance.

The voiceover uses this positioning:

> HisaarAI autonomously moves an untrusted invoice from arrival to an
> approval-ready recovery warrant. An accounts-payable operator—not a SOC
> engineer—makes one exact, policy-required decision, while deterministic
> Hisaar Gate permits only one verified sandbox mutation.

The close states the limitation: synthetic enterprise-shaped records, sandbox
mutation and observed run `n=1`. The video is public, English, under four
minutes, and linked from README, Devpost and the submission form.

## Success criteria

1. New receipt truthfully separates recovery reasoning identity from Firestore
   persistence identity.
2. No public artifact claims direct Memory API consumption during recovery.
3. Signed-out judges reach a complete verified before/control/after story in
   one click and one viewport.
4. Architecture visibly names Gemini, ADK, Vertex AI and the correct authority
   boundaries.
5. Financial Services alignment is current, sourced and explicitly not an
   integration claim.
6. One continuous live workflow is recorded with accurate AI narration and no
   workflow cuts.
7. Targeted local checks, fresh hosted proof and signed-out replay pass before
   the public video is recorded.
8. Article and social bonuses are pursued only after the core entry is safe.

