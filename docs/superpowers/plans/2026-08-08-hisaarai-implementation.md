# HisaarAI Implementation Plan

> **SUPERSEDED — DO NOT EXECUTE.** This verification-first plan was retired on
> 2026-08-09 after the product strategy changed to the judge-first lean design in
> `docs/superpowers/specs/2026-08-08-hisaarai-design.md`. A replacement vertical-
> slice implementation plan will be written only after the user reviews that
> specification.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and prove HisaarAI as a real Google Cloud agent-fleet recovery command room that blocks unsafe Accounts Payable actions, isolates influenced execution context, obtains one governed approval, and completes one idempotent sandbox ledger mutation through a clean standby.

**Architecture:** Three ADK Agent Runtime resources host the protected AP primary, the identity-distinct AP standby, and the four-role HisaarAI recovery team. An IAM/OIDC-only event-intake/Gate service handles machine traffic, while a separate IAP-protected command-room BFF handles human reads, challenges and approvals; authenticated Cloud Run tools enforce screening and sandbox ERP idempotency across separately scoped Firestore databases.

**Tech Stack:** Python 3.12, `uv`, Pydantic 2, FastAPI, Google ADK, Google Gen AI SDK, Firestore, Pub/Sub, Model Armor direct API, Agent Runtime, Memory Bank, Agent Registry, Cloud Run, Cloud Trace/OpenTelemetry, Terraform, React 19, TypeScript 5, Vite, Vitest and Playwright.

## Global Constraints

- Build only newly created HisaarAI work in this repository; do not copy code, prompts, fixtures, UI assets or deployment files from CreditLock, MuhafizSRE or CrossPatch.
- The design and this plan share one final model boundary: the submitted runtime may use only `gemini-3.6-flash` and `gemini-3.5-flash-lite`.
- Runtime model routing is immutable for this plan: AP primary and standby use `gemini-3.6-flash` with medium thinking; Raasid uses `gemini-3.5-flash-lite`; Kashif uses `gemini-3.6-flash` with high thinking; Muslih uses `gemini-3.6-flash` with high thinking; Shaahid uses `gemini-3.5-flash-lite`; Hisaar Gate uses no model.
- The exact model-ID allowlist has two members. Do not add any model outside that allowlist, an alias, a suffix substitution or cross-model fallback.
- Use `us-central1` for regional infrastructure and Model Armor. Configure every ADK Runtime explicitly for the `global` Gemini location so both approved model IDs and all thinking routes share one preflighted endpoint. Validate startup environment and record every requested model, actual model, thinking level and endpoint.
- Hisaar Gate is the only transition, approval, execution and release authority. Agent confidence and prose never authorize action.
- All authoritative state changes use Firestore transactions. Transaction callbacks contain Firestore reads and writes only; model, network and tool effects occur after commit.
- Pub/Sub is treated as at least once. Use producer-stable event identifiers, leases with fencing tokens and destination idempotency; never claim end-to-end exactly-once delivery.
- Model Armor is invoked directly on the PDF and on the exact normalized extracted text. Reject files over 4 MB and fail closed on skipped, inconclusive or unavailable screening.
- “Quarantine” means a persisted Hisaar Gate deny rule over principal, agent instance and session. Do not claim Runtime shutdown, credential revocation or platform-managed quarantine.
- The four recovery roles share one Runtime principal. Claim and test role-scoped ADK tool adapters, not separate IAM identities.
- The AP primary, AP standby and Recovery Runtime must have distinct effective cloud principals. The standby receives no source PDF or quarantined memory.
- The command-room web/BFF is IAP protected; Pub/Sub and Runtime callbacks use the separate Cloud Run IAM/OIDC event-intake service. Approval requires verified IAP identity, commander-subject allowlist, exact origin, CSRF token, subject-bound challenge nonce, warrant digest, source revisions and expiry.
- No browser-written authority state, synthetic Model Armor verdict, fake Registry resource, seeded incident progression, fabricated trace, backdated memory or hard-coded metric is permitted.
- All payment data is synthetic. The only side effect is a sandbox ledger document keyed by the original business idempotency key.
- Do not expand UI work until every Section 14 platform proof gate in the design has real evidence.

## Calendar and hard gates

| Date | Exit condition |
| --- | --- |
| Aug 8–9 | Repository skeleton and two-model record complete; project ancestry/policy visibility passes before bootstrap; custodian outreach is complete with a viable independent candidate and eligible source class identified; exact-model/platform spike is green; real Day-0 `AP-CONTINUITY-001` checkpoint created |
| Aug 10–13 | Typed contracts, state machine, transactional store, quarantine, policy and approval invariants green locally and in Firestore emulator |
| Aug 14–16 | Model Armor/extractor pipeline, AP primary/standby and four recovery agents deployed; real Day-7 resumption recorded |
| Aug 17–20 | Hosted end-to-end recovery, IAP approval, idempotent ERP, observability and evidence export green; custodian's eligible five-fixture encrypted-archive commitment recorded by Aug 20 |
| Aug 21–23 | Command room connected only to live backend; Day-14 resumption recorded; Playwright proof green |
| Aug 24–26 | Frozen evaluation suite, concurrency/failure runs, permission negatives and architecture/submission docs complete |
| Aug 27 | Code and prompts frozen; release manifest hash committed |
| Aug 28 | One complete frozen real-service release run preserved and `--phase release-run` passes; three sub-four-minute rehearsals pass |
| Aug 29 after 12:00 UTC | Scheduler-produced Day-21 resumption verified and committed; no final verdict is attempted before this evidence exists |
| Aug 30 | Final continuous video, public article, social proof and Devpost fields complete; only then may `--phase final` run |
| Aug 31 | Submission buffer only; no unmeasured feature work |

## Planned file map

```text
src/hisaarai/
  config.py                    exact model, region and security configuration
  canonical.py                 canonical JSON and SHA-256 digests
  clock.py                     injectable UTC server clock
  contracts/                   typed events, incidents, agents, warrants, receipts
  gate/                        state machine, policy, quarantine, approval, service
  store/                       repository protocol, memory fake, Firestore adapter
  security/                    IAP, CSRF and service-to-service OIDC verification
  integrations/                Model Armor, Agent Runtime, Registry, Memory, tracing
  services/                    FastAPI event intake, command-room BFF, reader, extractor and ERP apps
  evaluation/                  frozen manifest, runner, metrics and evidence export
agent_apps/
  ap_agent/                    primary/standby ADK application
  recovery_agent/              Raasid, Kashif, Muslih, Shaahid and root orchestrator
web/                           React command room
infra/terraform/               APIs, IAM, Firestore, Pub/Sub, Cloud Run, IAP, budgets
deploy/cloud-run/              one Dockerfile per Cloud Run service
scripts/                       spike, deployment, continuity, prewarm, release checks
evaluation/fixtures/           synthetic PDFs, controls and hashed manifest
tests/unit/                    pure deterministic tests
tests/integration/             Firestore emulator and authenticated service tests
tests/contract/                JSON schema and role-tool boundary tests
tests/e2e/                     hosted failure-first and approval flows
docs/evidence/                 secret-free manifests pointing to real Cloud evidence
docs/submission/               architecture, provenance, Devpost and video material
```

---

### Task 1: Greenfield skeleton and compliance gate

**Files:**
- Create: `.python-version`
- Create: `.gitignore`
- Create: `pyproject.toml`
- Create: `Makefile`
- Create: `src/hisaarai/__init__.py`
- Create: `tests/smoke/test_package.py`
- Create: `docs/compliance/model-routing.md`
- Create: `docs/submission/PROVENANCE.md`
- Create: `evaluation/fixtures/HELDOUT_CUSTODY.md`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-08-08-hisaarai-design.md`
- Produces: importable `hisaarai` package, locked Python environment, standard verification commands and compliance record used by every later task

- [ ] **Step 1: Start isolated execution work**

Use `superpowers:using-git-worktrees` to create branch `codex/hisaarai-build`; confirm the worktree contains commit `b46b91c` plus the revised planning commit and that `.DS_Store` remains untouched.

- [ ] **Step 2: Write the failing smoke test**

```python
from hisaarai import __version__


def test_package_version_is_explicit() -> None:
    assert __version__ == "0.1.0"
```

- [ ] **Step 3: Verify the test fails before scaffolding**

Run: `python3.12 -m pytest tests/smoke/test_package.py -q`

Expected: FAIL because `hisaarai` is not importable.

- [ ] **Step 4: Create the package and quality configuration**

Set `.python-version` to `3.12`. Configure `pyproject.toml` with package name `hisaarai`, version `0.1.0`, `src` layout and these dependency groups:

```toml
[project]
name = "hisaarai"
version = "0.1.0"
requires-python = ">=3.12,<3.13"
dependencies = [
  "fastapi>=0.124.1,<1",
  "google-adk[gcp]==2.1.0",
  "google-auth>=2.47,<3",
  "google-cloud-aiplatform[agent_engines,adk]>=1.148.1,<2",
  "google-cloud-firestore>=2.21,<3",
  "google-cloud-logging>=3.12,<4",
  "google-cloud-modelarmor>=0.7,<1",
  "google-cloud-pubsub>=2.31,<3",
  "google-genai>=1.74,<2",
  "httpx>=0.28,<1",
  "opentelemetry-api>=1.36,<2",
  "opentelemetry-exporter-otlp-proto-http>=1.36,<2",
  "opentelemetry-sdk>=1.36,<=1.41.1",
  "pydantic>=2.12,<3",
  "pydantic-settings>=2.10,<3",
  "pypdf>=6,<7",
  "rfc8785>=0.1,<1",
  "structlog>=25,<26",
  "uvicorn>=0.35,<1",
]

[dependency-groups]
dev = [
  "hypothesis>=6.138,<7",
  "mypy>=1.17,<2",
  "pytest>=8.4,<9",
  "pytest-asyncio>=1.1,<2",
  "respx>=0.22,<1",
  "ruff>=0.12,<1",
]
```

Run `uv lock` and commit `uv.lock`; never hand-edit the lockfile. Configure `make test`, `make lint`, `make typecheck` and `make verify` to call `uv run pytest`, `uv run ruff check`, `uv run ruff format --check` and `uv run mypy src tests`.

- [ ] **Step 5: Record the final two-model compliance boundary**

Create `docs/compliance/model-routing.md` with the exact two-member allowlist,
the six role routes, thinking levels and the rule that every invocation records
requested model, actual model, thinking level, endpoint and fallback status.
State explicitly that every identifier outside the two-member allowlist is
prohibited and that both approved identifiers satisfy the hackathon's Gemini
3.5-or-newer floor.
Record the official model-documentation URLs and UTC verification time; a failed
endpoint/quota probe remains a release blocker and never authorizes substitution.

- [ ] **Step 6: Secure the independent held-out custodian now**

By 2026-08-12, record a named person who is not implementing HisaarAI, their
written acceptance timestamp, independence statement, confirmed eligible source
class, archive-commitment deadline and post-freeze handoff procedure in
`evaluation/fixtures/HELDOUT_CUSTODY.md`. Store a privacy-safe public identifier
or digest of the acceptance record, not private correspondence. The preferred
exit is written acceptance during Aug 8–9; if it is absent on Aug 12, this
winner-readiness gate is `FAILED` even though unrelated engineering may continue.
Independent custody is an internal evaluation-strengthening control, not a claim
that the hackathon rules require it.

- [ ] **Step 7: Seed truthful provenance**

Create `docs/submission/PROVENANCE.md` with the audited statement from design Section 15, the root commit date, an empty-but-explicit “Pre-existing work incorporated: none” table, dependency-license section and AI-assistant disclosure.

- [ ] **Step 8: Verify and commit**

Run: `uv sync --all-groups && make verify`

Expected: smoke test PASS; Ruff and mypy exit 0.

```bash
git add .python-version .gitignore pyproject.toml uv.lock Makefile src tests/smoke docs/compliance docs/submission/PROVENANCE.md evaluation/fixtures/HELDOUT_CUSTODY.md
git commit -m "chore: scaffold greenfield HisaarAI project"
```

---

### Task 2: Exact configuration, contracts and canonical digests

**Files:**
- Create: `src/hisaarai/config.py`
- Create: `src/hisaarai/canonical.py`
- Create: `src/hisaarai/clock.py`
- Create: `src/hisaarai/contracts/common.py`
- Create: `src/hisaarai/contracts/events.py`
- Create: `src/hisaarai/contracts/incidents.py`
- Create: `src/hisaarai/contracts/agents.py`
- Create: `src/hisaarai/contracts/warrants.py`
- Create: `src/hisaarai/contracts/verification.py`
- Test: `tests/unit/test_config.py`
- Test: `tests/unit/test_canonical.py`
- Test: `tests/contract/test_json_schemas.py`

**Interfaces:**
- Consumes: environment variables prefixed `HISAAR_`
- Produces: `Settings`, `canonical_bytes(model)`, `sha256_digest(model)`, every typed contract and JSON schema used by agents, Gate, tools, Firestore and frontend

- [ ] **Step 1: Write exact-routing and canonicalization failures**

```python
def test_locked_model_routes(settings: Settings) -> None:
    assert settings.model_ap_primary == "gemini-3.6-flash"
    assert settings.model_ap_standby == "gemini-3.6-flash"
    assert settings.model_raasid == "gemini-3.5-flash-lite"
    assert settings.model_kashif == "gemini-3.6-flash"
    assert settings.model_muslih == "gemini-3.6-flash"
    assert settings.model_shaahid == "gemini-3.5-flash-lite"
    assert settings.thinking_ap == "MEDIUM"
    assert settings.thinking_kashif == "HIGH"
    assert settings.thinking_muslih == "HIGH"
    assert {
        settings.model_ap_primary,
        settings.model_ap_standby,
        settings.model_raasid,
        settings.model_kashif,
        settings.model_muslih,
        settings.model_shaahid,
    } == {"gemini-3.6-flash", "gemini-3.5-flash-lite"}


def test_warrant_digest_is_order_independent(warrant: RecoveryWarrant) -> None:
    raw = warrant.model_dump(mode="json")
    reversed_raw = dict(reversed(list(raw.items())))
    assert sha256_digest(raw) == sha256_digest(reversed_raw)
```

Also test that changing the Kashif mapping, adding an alias such as `-001`, using a naive datetime, omitting a schema version or serializing money as a float raises validation failure.

- [ ] **Step 2: Run the focused tests and observe failure**

Run: `uv run pytest tests/unit/test_config.py tests/unit/test_canonical.py tests/contract/test_json_schemas.py -q`

Expected: collection/import failures for undefined contracts.

- [ ] **Step 3: Implement immutable settings and shared primitives**

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HISAAR_", frozen=True)
    gcp_region: Literal["us-central1"] = "us-central1"
    gemini_location: Literal["global"] = "global"
    model_armor_location: Literal["us-central1"] = "us-central1"
    use_enterprise_genai: Literal[True] = True
    model_ap_primary: Literal["gemini-3.6-flash"] = "gemini-3.6-flash"
    model_ap_standby: Literal["gemini-3.6-flash"] = "gemini-3.6-flash"
    model_raasid: Literal["gemini-3.5-flash-lite"] = "gemini-3.5-flash-lite"
    model_kashif: Literal["gemini-3.6-flash"] = "gemini-3.6-flash"
    model_muslih: Literal["gemini-3.6-flash"] = "gemini-3.6-flash"
    model_shaahid: Literal["gemini-3.5-flash-lite"] = "gemini-3.5-flash-lite"
    thinking_ap: Literal["MEDIUM"] = "MEDIUM"
    thinking_kashif: Literal["HIGH"] = "HIGH"
    thinking_muslih: Literal["HIGH"] = "HIGH"
    warrant_ttl_seconds: Literal[600] = 600
    execution_lease_seconds: Literal[60] = 60
    max_document_bytes: Literal[4194304] = 4_194_304
```

Use timezone-aware UTC datetimes, `Decimal` serialized as strings, schema version `1`, strict Pydantic models (`extra="forbid"`) and RFC 8785 canonical JSON before SHA-256.

- [ ] **Step 4: Define all boundary models**

Include `InvoiceReceived`, `ScreeningEnvelope`, `ActionProposal`, `IncidentState`, `IncidentEvent`, `IncidentObservation`, `EvidenceAcquisitionRequest`, `BlastRadiusReport`, `RecoveryWarrantDraft`, Gate-owned `RecoveryWarrant`, `WarrantApproval`, `ExecutionLease`, Gate-derived `ExecutionRequest`, `MutationReceipt`, `DeterministicCheck`, and `VerificationReport`. The execution request schema exposes the server-derived identifier and canonical digest but never accepts either as caller authority. Export all JSON schemas to `docs/contracts/*.schema.json` in a deterministic test.

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest tests/unit/test_config.py tests/unit/test_canonical.py tests/contract/test_json_schemas.py -q && make verify`

Expected: all contract/config tests PASS and exported schemas are stable on a second run.

```bash
git add src/hisaarai/config.py src/hisaarai/canonical.py src/hisaarai/clock.py src/hisaarai/contracts tests/unit tests/contract docs/contracts
git commit -m "feat: define locked models and typed authority contracts"
```

---

### Task 3: Google platform spike and genuine Day-0 evidence

**Files:**
- Create: `spikes/agent_apps/probe/agent.py`
- Create: `scripts/preflight_project_hierarchy.py`
- Create: `scripts/platform_spike.py`
- Create: `scripts/build_runtime_role.py`
- Create: `scripts/create_continuity_checkpoint.py`
- Create: `scripts/record_continuity_resume.py`
- Create: `infra/bootstrap/enable_apis.sh`
- Create: `infra/bootstrap/bootstrap_spike.sh`
- Create: `infra/bootstrap/schedule_continuity.sh`
- Create: `spikes/event_intake_bootstrap/main.py`
- Create: `spikes/event_intake_bootstrap/Dockerfile`
- Create: `src/hisaarai/integrations/memory_bank.py`
- Create: `src/hisaarai/continuity.py`
- Create: `infra/bootstrap/runtime-permission-allowlist.yaml`
- Generate: `infra/bootstrap/runtime-role-discovery.json`
- Generate: `infra/bootstrap/runtime-role-final.json`
- Create: `docs/evidence/platform-spike/manifest.schema.json`
- Generate: `docs/evidence/platform-spike/project-hierarchy.json`
- Generate: `docs/evidence/platform-spike/manifest.json`
- Generate: `docs/evidence/continuity/day-00.json`
- Test: `tests/unit/test_platform_evidence_manifest.py`
- Test: `tests/unit/test_project_hierarchy_preflight.py`

**Interfaces:**
- Consumes: `Settings`, authorized Google ADC, `HISAAR_PROJECT_ID`, `HISAAR_BILLING_ACCOUNT_ID` and an IAM-evidence principal with visibility appropriate to the project's actual ancestry
- Produces: a Day-1 ancestry/policy-visibility decision, then minimally bootstrapped staging/Artifact Registry/Firestore/IAM/Registry/Scheduler resources plus a secret-free manifest containing exact remote-Runtime model responses, Runtime/Registry references, principals, Memory Revision, Trace ID, Model Armor response evidence and real Day-0 lineage `AP-CONTINUITY-001`

- [ ] **Step 1: Write hierarchy and manifest validation first**

```python
def test_project_hierarchy_preflight_is_terminal(preflight: dict) -> None:
    assert preflight["status"] == "PASS"
    assert preflight["topology"] in {"TOP_LEVEL_PROJECT", "ORGANIZATION_BACKED"}
    assert preflight["ancestors_complete"] is True
    assert set(preflight["policy_class_coverage"]) == {"allow", "deny", "principal_set"}
    assert set(preflight["policy_class_coverage"].values()) <= {"VISIBLE", "ABSENT"}
    assert preflight["unknown_results"] == []
```

```python
def test_platform_manifest_requires_real_resource_names(manifest: dict) -> None:
    assert manifest["project_id"]
    probes = manifest["model_probes"]
    expected_routes = {
        "ap_primary_medium": ("gemini-3.6-flash", "MEDIUM"),
        "ap_standby_medium": ("gemini-3.6-flash", "MEDIUM"),
        "raasid_lite": ("gemini-3.5-flash-lite", "DEFAULT"),
        "kashif_high": ("gemini-3.6-flash", "HIGH"),
        "muslih_high": ("gemini-3.6-flash", "HIGH"),
        "shaahid_lite": ("gemini-3.5-flash-lite", "DEFAULT"),
    }
    assert set(probes) == set(expected_routes)
    for route, (expected_model, expected_thinking) in expected_routes.items():
        assert probes[route]["requested_model"] == expected_model
        assert probes[route]["actual_model"] == expected_model
        assert probes[route]["thinking_level"] == expected_thinking
        assert probes[route]["fallback_status"] == "NONE"
    assert len({r["effective_principal"] for r in manifest["runtimes"]}) == 3
    assert manifest["continuity"]["lineage_id"] == "AP-CONTINUITY-001"
    assert manifest["continuity"]["memory_id"].startswith("projects/")
    assert manifest["continuity"]["memory_revision"].startswith("projects/")
    assert manifest["runtime_role"]["predefined_user_bindings"] == []
    assert manifest["runtime_role"]["discovery_bindings"] == []
    assert manifest["runtime_role"]["remaining_memory_permissions"] == []
    assert manifest["runtime_role"]["administrative_permissions"] == []
    assert manifest["runtime_role"]["final_allowlist_digest"] == manifest["runtime_role"]["effective_role_digest"]
    assert manifest["runtime_role"]["binding_inventory_digest"]
    assert manifest["runtime_role"]["binding_inventory_complete"] is True
    assert manifest["runtime_role"]["policy_troubleshooter_cannot_access_complete"] is True
    assert set(manifest["runtime_role"]["policy_class_coverage"]) == {"allow", "deny", "principal_set"}
    assert set(manifest["runtime_role"]["policy_class_coverage"].values()) <= {"VISIBLE", "ABSENT"}
    assert manifest["runtime_role"]["unsupported_permissions_reviewed"] is True
    assert manifest["runtime_role"]["recovery_scope_positive"] is True
    assert manifest["runtime_role"]["cross_scope_denied"] is True
    assert manifest["artifact_registry"]["repository"].endswith("/hisaar-containers")
    assert manifest["event_intake"]["image_digest"].startswith("sha256:")
```

Reject values containing `mock`, `demo`, `example-resource` or an empty evidence URL.

- [ ] **Step 2: Prove project ancestry and evidence visibility before bootstrap**

Before bulk product API enablement, linking product resources or running the
bootstrap, execute:

```bash
uv run python scripts/preflight_project_hierarchy.py \
  --project "$HISAAR_PROJECT_ID" \
  --output docs/evidence/platform-spike/project-hierarchy.json
```

If a required inspection API is disabled, the only permitted preflight mutation
is enabling the Resource Manager/IAM/Cloud Asset/Policy Troubleshooter inspection
surface and recording that fact; do not create a product resource. Step 3 may
idempotently include those APIs again.

The script records `gcloud projects get-ancestors` output, project number,
effective evidence principal and the applicable policy hierarchy. If ancestry
contains an organization, require an already authorized reviewer with the
official Security Reviewer and Deny Reviewer visibility on that organization,
Browser visibility when principal-set bindings may apply, project-scoped Cloud
Asset visibility and a terminal Policy Troubleshooter probe. Project Owner alone
does not satisfy this branch. If any applicable allow, deny or principal-set
policy cannot be inspected, or any probe is unknown/conditional-unknown, write a
secret-free `FAILED` record and stop before bootstrap.

If ancestry proves the project is top-level, inventory its project allow policy,
project-attached deny policies, project custom roles and project-scoped Cloud
Asset results, and require terminal Policy Troubleshooter results. Prefer a new
dedicated top-level project only when **No organization** is actually available
to the authorized account. Managed Workspace/Cloud Identity users may be forced
into an organization; in that case obtain the visibility above or choose another
authorized project/account before work begins. Never plan to move a populated
project later to repair missing evidence access.

Run `uv run pytest tests/unit/test_project_hierarchy_preflight.py -q`. Task 3 may
continue only when `project-hierarchy.json` is `PASS` and its digest is included
in the platform manifest.

- [ ] **Step 3: Enable only the required APIs**

`infra/bootstrap/enable_apis.sh` must enable:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  agentregistry.googleapis.com \
  artifactregistry.googleapis.com \
  billingbudgets.googleapis.com \
  cloudbuild.googleapis.com \
  cloudasset.googleapis.com \
  cloudresourcemanager.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudtrace.googleapis.com \
  compute.googleapis.com \
  firestore.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  iap.googleapis.com \
  logging.googleapis.com \
  modelarmor.googleapis.com \
  monitoring.googleapis.com \
  pubsub.googleapis.com \
  policytroubleshooter.googleapis.com \
  run.googleapis.com \
  storage.googleapis.com \
  telemetry.googleapis.com \
  --project "$HISAAR_PROJECT_ID"
```

`infra/bootstrap/bootstrap_spike.sh` then creates the versioned staging/build-log
bucket, regional `hisaar-containers` Docker Artifact Registry repository, named
`hisaar-authority` Firestore database, three custom Runtime service accounts,
`hisaar-gate`, `hisaar-pubsub-push` and `hisaar-builder` accounts, Pub/Sub
continuity topic and Agent Registry setup. The push subscription is deliberately
deferred until Step 8 has deployed `event-intake` and read its canonical service
URL. The dedicated builder has
repository-scoped `roles/artifactregistry.writer`, exact-bucket
`roles/storage.objectUser`/`roles/storage.bucketViewer` and only the logging role
actually used by the build; the deployer has `actAs` on that account. Do not rely
on automatic repository creation or the default build identity.

Before the initial Runtime deployment, `scripts/build_runtime_role.py` fetches
the live `roles/aiplatform.user` definition, removes every permission matching
`aiplatform.memories.*` or `aiplatform.memoryRevisions.*`, fails if any other
`aiplatform.*memory*` permission remains unreviewed, queries custom-role support,
and creates temporary `hisaarRuntimeDiscoveryNoMemory`. Persist its source etag,
included, Memory-excluded and unsupported permission lists plus digests in
`infra/bootstrap/runtime-role-discovery.json`. Bind it—not the predefined role—
to the three Runtime identities only for Steps 5–6. This discovery role is broad,
is not called least privilege and may not be used for Memory, Day-0 or release
evidence.

Grant Recovery Runtime
`roles/aiplatform.memoryUser` under a positive `memoryScope` equality condition
that permits only `lineage=AP-CONTINUITY-001`; grant primary and standby no Memory
role. Do not exercise that Memory grant until the discovery binding has been
removed in Step 6. Grant the deployer `roles/iam.serviceAccountUser` on exactly
the accounts it deploys. Before any trace export, grant Recovery Runtime
`roles/telemetry.tracesWriter`; add logging or metrics writer roles only if the
probe directly emits those signal types, and record the exercised writer grants
for Task 13 import. Do not assume the Google-managed Runtime service agent's
telemetry permissions transfer to the custom Runtime identity.

Do not create a custom Scheduler publisher: Pub/Sub-target jobs use Google's
Cloud Scheduler service agent. Task 13 must import/adopt every surviving
bootstrap resource, repository, final custom role and project/repository IAM
binding into Terraform; the removed discovery binding is evidence, not imported
state. Its Runtime deployment script converges the exact
resource-level Runtime IAM policies; neither path may create duplicates.

- [ ] **Step 4: Probe the two exact model IDs and all six role routes**

For the local/deployer probe, use the documented explicit Python constructor
`genai.Client(enterprise=True, project=project_id, location="global",
http_options=HttpOptions(api_version="v1"))`. Fail the spike if that exact
enterprise configuration, API version or endpoint is unavailable rather than
silently switching APIs.
For each of the six locked role routes, request a fixed
`ProbeResult(status: Literal["READY"], role: str)` JSON response and record the
requested model, actual model, effective thinking setting, usage, endpoint,
latency and UTC timestamp. This step is the local/deployer probe; Step 5 repeats
it inside each remotely deployed Runtime. AP primary and standby must send
`GenerateContentConfig(thinking_config=ThinkingConfig(thinking_level="MEDIUM"))`;
Kashif and Muslih must send the same typed configuration with `HIGH`. Raasid and
Shaahid omit `ThinkingConfig`, use the supported default/minimal Flash-Lite
behavior and record the manifest sentinel `DEFAULT` rather than a fabricated API
thinking value. Record resolved request JSON for every route and
assert the set of actual model IDs equals exactly the two-member allowlist. One
same-model retry is permitted; any substitution fails the spike.

- [ ] **Step 5: Deploy three minimal ADK Runtime resources**

Export one probe ADK `root_agent`, wrap it as an Agent Engine ADK application and
deploy `hisaar-ap-primary`, `hisaar-ap-standby` and `hisaar-recovery` through the
Agent Platform SDK `client.agent_engines.create`, each with its custom Runtime
service account in `us-central1`. Do not set Agent Runtime's reserved
`GOOGLE_CLOUD_PROJECT` or `GOOGLE_CLOUD_LOCATION` environment variables and do
not configure Preview Runtime resource controls in the mandatory path. Set only
`GOOGLE_GENAI_USE_ENTERPRISE=True` plus custom
`HISAAR_MODEL_LOCATION=global`. With the pinned ADK 2.x version, implement and
test its `GlobalGemini(Gemini)` pattern: override the cached `api_client` with
`genai.Client(enterprise=True, project=<runtime-project>, location="global",
http_options=HttpOptions(api_version="v1"))`, then construct every agent with
`GlobalGemini(model=<locked-id>)` rather than a bare default string. Record
resolved SDK
versions, resource names, Runtime update timestamps/code digests and Registry
`RuntimeReference`; do not make the Preview Runtime-revisions/traffic feature a
core proof and do not treat an
optional Registry version string as deployment proof.

Invoke the fixed remote probe under each effective Runtime principal and capture
the exact successful API call graph, Cloud Audit evidence where available and
application-level permission observations needed to construct the final role.
This run is permission discovery, not release evidence.

- [ ] **Step 6: Contract to the final reviewed Runtime data-plane role**

Create `runtime-permission-allowlist.yaml` as a no-wildcard list of only the
permissions justified by the exact remote model/session call graph. Every entry
names the consuming call, Runtime role and official API reference. Build
versioned `hisaarAgentRuntimeDataPlaneV1` from that allowlist; reject every
Memory permission and every Runtime/reasoning-engine, endpoint, job, dataset or
IAM create, update, delete and policy-management permission. Persist the final
definition, support levels, justifications and digest in
`runtime-role-final.json`.

Add the final role to each Runtime identity, remove all three discovery-role
bindings, then disable or delete the unbound discovery role. Re-run every remote
model, structured-output and session positive under fresh credentials. Use
three deterministic checks: intersect the fetched final custom-role definition
with the frozen administrative-permission denylist; inventory every direct and
inherited binding that applies to each Runtime principal across the complete
resource hierarchy; and run Policy Troubleshooter for control-plane create
permissions using the exact Vertex AI Location full resource name
`//aiplatform.googleapis.com/projects/PROJECT_NUMBER/locations/us-central1`, plus
update/delete/policy permissions on each verified-existing Runtime full resource
name. Pin the proof to Policy Troubleshooter REST v3 and require exact
`overallAccessState == CANNOT_ACCESS`; reject `UNKNOWN_INFO`,
`UNKNOWN_CONDITIONAL`, unspecified and every other non-terminal state, and record
all allow/deny explanations. Fail if the reviewer cannot view every applicable
policy or custom-role definition. For
endpoint, job and dataset types with no real resource, rely on the exact
permission-set intersection and complete binding inventory rather than an empty
resource check. `testIamPermissions` may corroborate a verified-existing,
supported resource but an empty response is never accepted as denial evidence.
Also prove primary/standby Memory calls fail, Recovery's exact conditional scope
succeeds and its cross-scope call fails. If a positive needs another permission,
add only that individually justified permission, version the allowlist and repeat
the entire contraction. No Memory or Day-0 call may proceed while a discovery
binding remains.

The configured `HISAAR_IAM_EVIDENCE_PRINCIPAL` is a human/release operator, not a
Runtime identity. Revalidate the Day-1 hierarchy record before using it. For an
organization-backed project, verify the current official prerequisites that
apply: `roles/iam.securityReviewer` and `roles/iam.denyReviewer` on the containing
organization; `roles/browser` when service-account principal-set bindings may
apply; `roles/serviceusage.serviceUsageConsumer` on the quota project for gcloud;
and Cloud Asset policy visibility. For a verified top-level project, record the
organization/folder classes as `ABSENT` and instead prove complete project allow,
project-attached deny, project custom-role and project-scoped Cloud Asset
visibility; never fabricate an organization grant.
Use an already authorized reviewer or an equivalent reviewed visibility-only
custom role where possible; do not auto-grant an Organization Admin role merely
to make a hackathon check pass. Record each allow, deny and principal-set policy
class as `VISIBLE` or API-proven `ABSENT`, together with hierarchy and
coverage evidence. Any applicable invisible class or `UNKNOWN*` result blocks the
spike. Pin the core proof to REST v3. A PAB can only further restrict access and
cannot create a forbidden allow, so PAB/v3beta evaluation is optional
informational evidence and never a mandatory core dependency. Do not grant
inspection roles to a product service account.

- [ ] **Step 7: Prove Memory Bank, Trace and Model Armor under the intended identities**

Invoke a typed Recovery Runtime continuity method so the Recovery Runtime
principal—not the deployer or Gate—creates one real session, Memory resource and
immutable Memory Revision for lineage `AP-CONTINUITY-001`, with Memory Revisions
enabled and an explicit request-level `revision_ttl="31536000s"` (365 days).
Re-fetch the revision and record its returned `expire_time`; do not infer
retention from the request alone. Use the stable phase idempotency key
`AP-CONTINUITY-001/day-00`; this exact session, Memory and Revision are the Day-0
candidate that Step 8 must adopt, not a disposable probe. Emit one correlated
tool span through the Recovery Runtime's OTLP/Telemetry exporter, and retrieve
all by API. Create one
committed Model Armor template at regional
endpoint `modelarmor.us-central1.rep.googleapis.com` and run the official benign
direct-PDF sample plus a clean text control. Persist template name, response
digest, correlation ID and timestamp; Model Armor does not provide a durable
verdict resource.

- [ ] **Step 8: Create Day-0 continuity evidence immediately**

Build `spikes/event_intake_bootstrap` with the dedicated builder, capture the
Artifact Registry image digest, and deploy it now as the final-named
`event-intake` Cloud Run service under `hisaar-gate`, not as a sixth temporary
service. It validates Pub/Sub push OIDC, writes the idempotent authority
checkpoint, and invokes only the exact Recovery Runtime continuity method;
Recovery Runtime alone reads/writes Memory Bank. Grant Gate
`roles/datastore.user` with the exact positive `hisaar-authority` database
condition, a custom role containing only `aiplatform.reasoningEngines.query`
bound in the IAM policy of the exact Recovery Runtime resource, and the trace/log
writer roles it actually uses. Prove Gate cannot call
Memory APIs or another Runtime.

After deployment, read the canonical `event-intake` status URL. Only then create
the authenticated push subscription with that exact URL as both endpoint and
OIDC audience, grant the Pub/Sub service agent
`roles/iam.serviceAccountTokenCreator` on `hisaar-pubsub-push`, and grant that
push account `roles/run.invoker` only on `event-intake`. Verify a signed push
reaches the route and a wrong audience is rejected before publishing Day 0.

The Day-0 call uses the same `AP-CONTINUITY-001/day-00` idempotency key as Step
7. Recovery must return the exact existing session, Memory and Revision; it must
not create a second Day-0 revision. `event-intake` then transactionally adopts
those identifiers and digests into the authority checkpoint. A different result
for the same phase key fails the spike.

Run:

```bash
uv run python scripts/create_continuity_checkpoint.py \
  --lineage AP-CONTINUITY-001 \
  --phase day-00 \
  --playbook REMITTANCE_PROFILE_CONFLICT_RECOVERY_V1
```

Expected: `docs/evidence/continuity/day-00.json` contains real Memory resource,
immutable Memory Revision, fact digest, revision `expire_time`, session,
checkpoint and trace resource IDs plus server timestamps; no caller-supplied
historical date exists. The evidence records Recovery Runtime as the Memory
caller and `hisaar-gate` as the checkpoint writer.

- [ ] **Step 9: Schedule the remaining genuine resumptions now**

With the bootstrap `event-intake` route proven,
`infra/bootstrap/schedule_continuity.sh` creates one-phase jobs for
2026-08-15, 2026-08-22 and 2026-08-29 at 12:00 UTC. Each publishes lineage
`AP-CONTINUITY-001` plus its phase only; the handler derives server time, refuses
early/backfilled phases and is idempotent by `(lineage_id, phase)`. Scheduler
publishes through
`service-{PROJECT_NUMBER}@gcp-sa-cloudscheduler.iam.gserviceaccount.com`; verify
that Google-managed principal retains `roles/cloudscheduler.serviceAgent`, which
contains the publish permission, rather than granting a custom publisher. Reuse
the already verified authenticated push subscription unchanged. Pause each
recurring job immediately after verified phase export. Task 13 adopts this exact
service, identity, subscription endpoint and OIDC audience, then updates its
image in place without changing the continuity route.

- [ ] **Step 10: Validate the initial access proofs truthfully**

Run: `uv run python scripts/platform_spike.py --verify && uv run pytest tests/unit/test_platform_evidence_manifest.py -q`

Expected: exit 0 only for access facts actually exercised now: exact models,
three distinct Runtime principals under the final reviewed data-plane role, no
discovery binding or administrative permission, Registry, Memory Bank/Day-0 checkpoint, direct Model
Armor and Trace. The manifest labels later implementation proofs `NOT_RUN`; it
must never mark a design note or planned harness as passing evidence. Missing
access is recorded as `FAILED` and never patched with a custom imitation.

- [ ] **Step 11: Commit secret-free evidence pointers**

```bash
git add spikes scripts/platform_spike.py scripts/build_runtime_role.py scripts/create_continuity_checkpoint.py scripts/record_continuity_resume.py infra/bootstrap src/hisaarai/integrations/memory_bank.py src/hisaarai/continuity.py docs/evidence tests/unit/test_platform_evidence_manifest.py
git commit -m "feat: prove Google platform access and start real continuity"
```

---

### Task 4: Deterministic incident state machine

**Files:**
- Create: `src/hisaarai/gate/state_machine.py`
- Test: `tests/unit/gate/test_state_machine.py`
- Test: `tests/property/test_state_machine_invariants.py`

**Interfaces:**
- Consumes: `IncidentState`, current `state_version`, requested transition
- Produces: `TransitionDecision` and `assert_transition(current, target)` used by every Firestore authority write

- [ ] **Step 1: Encode failing transition examples**

```python
@pytest.mark.parametrize(
    ("current", "target"),
    [
        (IncidentState.RECEIVED, IncidentState.SCREENING),
        (IncidentState.AWAITING_APPROVAL, IncidentState.APPROVED),
        (IncidentState.AWAITING_APPROVAL, IncidentState.REJECTED),
        (IncidentState.COMPLETED, IncidentState.VERIFIED),
    ],
)
def test_legal_transition_is_accepted(current, target) -> None:
    assert_transition(current, target)


def test_approval_cannot_skip_plan() -> None:
    with pytest.raises(IllegalTransition):
        assert_transition(IncidentState.QUARANTINED, IncidentState.APPROVED)
```

- [ ] **Step 2: Add property failures**

Generate at least 1,000 transition sequences with Hypothesis. Assert terminal states never leave, `VERIFIED` is reachable only through `COMPLETED`, `APPROVED` only through `AWAITING_APPROVAL`, and ingress blocks never create `SESSION_TAINTED`.

- [ ] **Step 3: Run tests to observe failure**

Run: `uv run pytest tests/unit/gate/test_state_machine.py tests/property/test_state_machine_invariants.py -q`

Expected: import failure for `state_machine`.

- [ ] **Step 4: Implement the explicit adjacency map**

```python
ALLOWED: Final[dict[IncidentState, frozenset[IncidentState]]] = {
    IncidentState.RECEIVED: frozenset({IncidentState.SCREENING, IncidentState.BLOCKED}),
    IncidentState.SCREENING: frozenset({IncidentState.BLOCKED_AT_INGRESS, IncidentState.SCREENED_CLEAR, IncidentState.BLOCKED}),
    IncidentState.SCREENED_CLEAR: frozenset({IncidentState.AGENT_CONSUMED, IncidentState.BLOCKED}),
    IncidentState.AGENT_CONSUMED: frozenset({IncidentState.ACTION_PROPOSED, IncidentState.BLOCKED}),
    IncidentState.ACTION_PROPOSED: frozenset({IncidentState.POLICY_ALLOWED, IncidentState.POLICY_DENIED, IncidentState.BLOCKED}),
    IncidentState.POLICY_ALLOWED: frozenset({IncidentState.COMPLETED, IncidentState.BLOCKED}),
    IncidentState.POLICY_DENIED: frozenset({IncidentState.SESSION_TAINTED, IncidentState.BLOCKED}),
    IncidentState.SESSION_TAINTED: frozenset({IncidentState.QUARANTINED, IncidentState.BLOCKED}),
    IncidentState.QUARANTINED: frozenset({IncidentState.INVESTIGATING, IncidentState.BLOCKED}),
    IncidentState.INVESTIGATING: frozenset({IncidentState.PLAN_READY, IncidentState.BLOCKED}),
    IncidentState.PLAN_READY: frozenset({IncidentState.AWAITING_APPROVAL, IncidentState.BLOCKED}),
    IncidentState.AWAITING_APPROVAL: frozenset({IncidentState.APPROVED, IncidentState.REJECTED, IncidentState.BLOCKED}),
    IncidentState.APPROVED: frozenset({IncidentState.REASSIGNED, IncidentState.BLOCKED}),
    IncidentState.REASSIGNED: frozenset({IncidentState.COMPLETED, IncidentState.BLOCKED}),
    IncidentState.COMPLETED: frozenset({IncidentState.VERIFIED, IncidentState.BLOCKED}),
    IncidentState.BLOCKED_AT_INGRESS: frozenset(),
    IncidentState.REJECTED: frozenset(),
    IncidentState.BLOCKED: frozenset(),
    IncidentState.VERIFIED: frozenset(),
}
```

Do not derive ordering from enum values. The clean path reaches `POLICY_ALLOWED`
without recovery approval only after deterministic vendor/PO checks; the unsafe
path can reach `APPROVED` only through the recovery chain.

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest tests/unit/gate/test_state_machine.py tests/property/test_state_machine_invariants.py -q`

Expected: all examples and at least 1,000 generated sequences PASS.

```bash
git add src/hisaarai/gate/state_machine.py tests/unit/gate tests/property
git commit -m "feat: enforce deterministic recovery state machine"
```

---

### Task 5: Transactional Firestore authority store

**Files:**
- Create: `src/hisaarai/store/protocol.py`
- Create: `src/hisaarai/store/memory.py`
- Create: `src/hisaarai/store/firestore.py`
- Create: `src/hisaarai/gate/event_chain.py`
- Test: `tests/unit/store/test_memory_store.py`
- Test: `tests/integration/store/test_firestore_transactions.py`
- Test: `tests/integration/store/test_event_claim_concurrency.py`

**Interfaces:**
- Consumes: `InvoiceReceived`, `IncidentEvent`, `TransitionDecision`, UTC `Clock`
- Produces: `AuthorityStore.reserve_event()`, `transition()`, `create_successor_attempt()`, `claim_expired_lease()`, `get_incident()`, `append_event()` and `finalize_event()`

- [ ] **Step 1: Write reservation and fencing failures**

```python
async def test_duplicate_event_returns_one_logical_claim(store, invoice_event) -> None:
    results = await asyncio.gather(
        *(store.reserve_event(invoice_event, worker_id=f"w-{i}") for i in range(50))
    )
    assert sum(r.status == ClaimStatus.ACQUIRED for r in results) == 1
    assert len({r.incident_id for r in results}) == 1


async def test_stale_fencing_token_cannot_finalize(store, active_claim) -> None:
    takeover = await store.take_over_expired_claim(active_claim.event_id, worker_id="new")
    with pytest.raises(StaleFencingToken):
        await store.finalize_event(active_claim.event_id, active_claim.fencing_token, result={})
    await store.finalize_event(takeover.event_id, takeover.fencing_token, result={"ok": True})
```

- [ ] **Step 2: Write atomic event-chain failure**

Assert one transaction checks `state_version`, writes the new incident state, creates the next event with `previous_digest`, and advances `chain_head`. A mismatched version must write neither state nor event.
Force one Firestore callback retry and prove that the service-generated
`event_time` and resulting event digest remain identical while the separately
stored server-resolved `committed_at` is not part of the digest payload.
Also test fifty concurrent successor commands against one expired
`AWAITING_APPROVAL` attempt: exactly one transaction marks the old attempt
`BLOCKED`, invalidates its challenges and creates one new `QUARANTINED` attempt;
every caller receives the same successor ID. The successor preserves the incident
ID, execution-quarantine reference and business idempotency key.

- [ ] **Step 3: Run tests against memory store and emulator**

Start the Firestore emulator in Native mode, then run:

`uv run pytest tests/unit/store tests/integration/store -q`

Expected: failure because store implementations do not exist.

- [ ] **Step 4: Define the authority protocol**

```python
class AuthorityStore(Protocol):
    async def reserve_event(self, event: InvoiceReceived, worker_id: str) -> EventClaim: ...
    async def transition(self, command: TransitionCommand) -> IncidentSnapshot: ...
    async def create_successor_attempt(self, command: SuccessorAttemptCommand) -> IncidentSnapshot: ...
    async def take_over_expired_claim(self, event_id: str, worker_id: str) -> EventClaim: ...
    async def finalize_event(self, event_id: str, fencing_token: int, result: dict[str, JsonValue]) -> None: ...
```

`reserve_event` is keyed by producer-stable `event_id`, compares `payload_hash`, creates a 120-second processing lease, starts fencing token `1`, and returns `ACQUIRED`, `BUSY` or `COMPLETED`. Reuse of one event ID with a different payload hash raises `EventIdentityConflict`.

- [ ] **Step 5: Implement Firestore transaction callbacks with no effects**

Use the server Firestore client and transaction decorator. Read every document before writes. Keep transaction callbacks pure; return claim/transition data to callers and make model/tool calls only after the transaction resolves.

- [ ] **Step 6: Scope the hash chain per incident**

Canonical event digest input is exactly:

```python
{
    "schema_version": 1,
    "incident_id": incident_id,
    "sequence": sequence,
    "previous_digest": previous_digest,
    "state_from": state_from,
    "state_to": state_to,
    "actor": actor,
    "payload_digest": payload_digest,
    "evidence_refs": sorted(evidence_refs),
    "event_time": event_time,
}
```

Create `event_time` once, as an aware UTC value, before entering the transaction
callback. Store Firestore `SERVER_TIMESTAMP` separately as `committed_at` on the
event document. Do not digest `committed_at`: its value does not resolve until
commit and therefore cannot be a stable input when Firestore retries the
callback.

- [ ] **Step 7: Verify concurrency and commit**

Run: `uv run pytest tests/unit/store tests/integration/store -q && make verify`

Expected: 50 simultaneous claims yield one owner; stale fencing fails; conflicting transitions leave no partial write; each incident chain replays to its recorded head.

```bash
git add src/hisaarai/store src/hisaarai/gate/event_chain.py tests/unit/store tests/integration/store
git commit -m "feat: add transactional incident authority store"
```

---

### Task 6: Vendor policy and Gate execution quarantine

**Files:**
- Create: `src/hisaarai/gate/policy.py`
- Create: `src/hisaarai/gate/quarantine.py`
- Create: `src/hisaarai/gate/service.py`
- Create: `src/hisaarai/contracts/policy.py`
- Test: `tests/unit/gate/test_vendor_policy.py`
- Test: `tests/integration/gate/test_quarantine_enforcement.py`

**Interfaces:**
- Consumes: `ActionProposal`, `VendorMasterRevision`, `PurchaseOrderRevision`, caller `ExecutionIdentity`
- Produces: `PolicyDecision`, `QuarantineRecord`, `HisaarGate.evaluate_proposal()` and `HisaarGate.authorize_tool_call()`

- [ ] **Step 1: Write the flagship policy failure**

```python
def test_remittance_conflict_denies_before_mutation(gate, proposal, vendor_v42) -> None:
    proposal = proposal.model_copy(update={"remittance_profile_id": "RPF-7731"})
    vendor_v42 = vendor_v42.model_copy(update={"remittance_profile_id": "RPF-4912"})
    decision = gate.evaluate_proposal(proposal, vendor_v42)
    assert decision.code == "PAYMENT_DESTINATION_MUST_MATCH_VENDOR_MASTER_REVISION"
    assert decision.allowed is False
    assert decision.expected_profile_id == "RPF-4912"
```

- [ ] **Step 2: Write the quarantine-boundary failures**

Test exact-match denial for quarantined principal + instance + session, standby success under a different principal/session, stale fencing rejection, and no denial of unrelated sessions. Also assert the response label is `HISAAR_GATE_EXECUTION_QUARANTINE`, never platform shutdown.

- [ ] **Step 3: Run tests and observe failure**

Run: `uv run pytest tests/unit/gate/test_vendor_policy.py tests/integration/gate/test_quarantine_enforcement.py -q`

Expected: missing policy/quarantine modules.

- [ ] **Step 4: Implement deterministic policy**

```python
def evaluate_remittance(
    proposal: ActionProposal,
    vendor: VendorMasterRevision,
) -> PolicyDecision:
    if proposal.vendor_id != vendor.vendor_id:
        return PolicyDecision.deny("VENDOR_REVISION_MISMATCH")
    if proposal.remittance_profile_id != vendor.remittance_profile_id:
        return PolicyDecision.deny(
            "PAYMENT_DESTINATION_MUST_MATCH_VENDOR_MASTER_REVISION",
            expected_profile_id=vendor.remittance_profile_id,
        )
    return PolicyDecision.allow("VENDOR_MASTER_MATCH")
```

No model output, confidence score or document assertion can override this comparison.

- [ ] **Step 5: Persist and enforce quarantine transactionally**

On denial, one transaction moves `ACTION_PROPOSED -> POLICY_DENIED -> SESSION_TAINTED -> QUARANTINED` through explicit commands, records `content_release_at`, creates the deny key `(principal, instance_id, session_id)`, and increments its fencing version. Every protected tool adapter calls `authorize_tool_call` before any effect.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/unit/gate tests/integration/gate -q && make verify`

Expected: all mismatch/quarantine cases PASS; no mutation fixture is touched.

```bash
git add src/hisaarai/gate src/hisaarai/contracts/policy.py tests/unit/gate tests/integration/gate
git commit -m "feat: enforce vendor authority and execution quarantine"
```

---

### Task 7: Structurally unbypassable document-screening pipeline

**Files:**
- Create: `src/hisaarai/integrations/model_armor.py`
- Create: `src/hisaarai/security/oidc.py`
- Create: `src/hisaarai/services/document_extractor/main.py`
- Create: `src/hisaarai/services/invoice_reader/main.py`
- Create: `deploy/cloud-run/document-extractor.Dockerfile`
- Create: `deploy/cloud-run/invoice-reader.Dockerfile`
- Test: `tests/unit/integrations/test_model_armor.py`
- Test: `tests/unit/services/test_extractor.py`
- Test: `tests/integration/services/test_invoice_reader.py`

**Interfaces:**
- Consumes: PDF bytes, caller identity, incident/event IDs, `ModelArmorClient`, Gate authorization client and extractor HTTP client
- Produces: a typed `ScreeningEnvelope` response with raw PDF digest, normalized-text digest, template/config reference, PDF verdict, text verdict and exact releasable text; the reader itself has no Firestore client

- [ ] **Step 1: Write fail-closed screening tests**

```python
@pytest.mark.parametrize("result", ["EXECUTION_SKIPPED", "INCONCLUSIVE", "UNAVAILABLE"])
async def test_non_pass_result_never_releases_text(invoice_reader, result) -> None:
    invoice_reader.model_armor.pdf_result = result
    response = await invoice_reader.read_pdf(b"%PDF-1.7 safe fixture")
    assert response.released_text is None
    assert response.status == "BLOCKED"


async def test_pdf_over_four_mb_is_rejected_before_model_armor(invoice_reader) -> None:
    with pytest.raises(DocumentTooLarge):
        await invoice_reader.read_pdf(b"x" * (4_194_304 + 1))
    assert invoice_reader.model_armor.calls == []
```

Also test PDF match prevents local extraction, PDF pass followed by text match
blocks release, the exact released text hashes to the returned envelope digest,
embedded images are never marked screened, the security fixture matches the
`pi_and_jailbreak` filter specifically, and the AP Runtime cannot call the
extractor directly.

- [ ] **Step 2: Write extractor-isolation tests**

Send a small synthetic PDF and assert deterministic Unicode normalization, page
separators, maximum extracted characters and no Firestore/Gemini/ERP client or
credential-bearing dependency in the extractor image. The live infrastructure
test in Task 13 must additionally prove that outbound network access fails.

- [ ] **Step 3: Run focused tests to observe failure**

Run: `uv run pytest tests/unit/integrations/test_model_armor.py tests/unit/services/test_extractor.py tests/integration/services/test_invoice_reader.py -q`

Expected: missing clients/apps.

- [ ] **Step 4: Implement the Model Armor adapter**

Define:

```python
class ModelArmorClient(Protocol):
    async def sanitize_pdf(self, *, content: bytes, template: str) -> ArmorVerdict: ...
    async def sanitize_text(self, *, content: str, template: str) -> ArmorVerdict: ...
```

The real adapter calls the regional endpoint
`modelarmor.us-central1.rep.googleapis.com`, invokes `SanitizeUserPrompt` with a
`DataItem.byte_item` whose `byteDataType=PDF` for the document and a
`DataItem.text` for normalized text, and records the raw response digest. `PASS`
requires `response.sanitization_result.invocation_result == SUCCESS`,
`response.sanitization_result.filter_match_state == NO_MATCH_FOUND`, and a
typed `execution_state == EXECUTION_SUCCESS` in every enabled nested entry under
`sanitization_result.filter_results`. The calibration assertion checks the
`pi_and_jailbreak` result's own typed match state. Missing, skipped, failed,
unknown or matched filter results fail closed. Only the invoice-reader principal receives
`roles/modelarmor.user` and `roles/modelarmor.viewer` on the template project.

- [ ] **Step 5: Implement the isolated extractor**

Run as non-root UID `65532`, accept authenticated internal requests only, use
`pypdf` inside the dedicated Cloud Run extractor service with a 5-second request
deadline, 256 MiB memory limit, one-request concurrency, 20-page limit and
100,000-character output cap. Mount a size-limited 16 MiB in-memory volume at
`/tmp/extract`, set `TMPDIR` to it, keep parser inputs there only when unavoidable,
and delete them in `finally`; application tests fail on writes outside that mount.
Do not claim the ordinary Cloud Run root filesystem is read-only. Normalize text
with Unicode NFKC and `\n\f\n` page separators. The extractor service account receives no
project role or data-store permission; Task 13 routes all egress through its
no-NAT, Private-Google-Access-disabled subnet and proves denial live.

- [ ] **Step 6: Implement the invoice-reader enforcement order**

1. Verify Google-signed OIDC caller and Gate quarantine.
2. Enforce MIME and 4 MB byte limit.
3. Hash exact PDF bytes.
4. Direct-PDF Model Armor call; stop on any non-pass.
5. Call isolated extractor.
6. Hash exact normalized text.
7. Model Armor text call; stop on any non-pass.
8. Return the typed `ScreeningEnvelope` and exact text to event-intake/Gate; do
   not write Firestore from the reader.
9. Event-intake/Gate persists that envelope in the authority database and only
   then releases the envelope-bound exact text to the AP Runtime. A failed
   authority write releases nothing.

- [ ] **Step 7: Run real template proof and commit**

Use the committed approved security-control PDF, semantic-tamper PDF and one clean PDF. Expected: security control matches before local extraction; semantic and clean fixtures pass both calls; service IDs/digests are stored.

Run: `uv run pytest tests/unit/integrations tests/unit/services tests/integration/services/test_invoice_reader.py -q && make verify`

```bash
git add src/hisaarai/integrations/model_armor.py src/hisaarai/security/oidc.py src/hisaarai/services/document_extractor src/hisaarai/services/invoice_reader deploy/cloud-run tests
git commit -m "feat: enforce isolated dual document screening"
```

---

### Task 8: Protected AP primary and clean standby ADK agent

**Files:**
- Create: `agent_apps/ap_agent/__init__.py`
- Create: `agent_apps/ap_agent/agent.py`
- Create: `agent_apps/ap_agent/prompts.py`
- Create: `agent_apps/ap_agent/tools.py`
- Create: `src/hisaarai/contracts/recovery_package.py`
- Test: `tests/unit/agents/test_ap_agent.py`
- Test: `tests/contract/test_ap_tool_boundary.py`

**Interfaces:**
- Consumes: `ScreeningEnvelope` for primary runs or `CleanRecoveryPackage` for standby runs, typed invoice-reader and proposal adapters
- Produces: one `ActionProposal`; never writes the ledger directly

- [ ] **Step 1: Write primary/standby boundary failures**

```python
def test_primary_has_reader_but_no_ledger_tool(primary_agent) -> None:
    assert set(primary_agent.tool_names) == {"read_screened_invoice", "propose_action"}


def test_standby_rejects_source_pdf_or_memory_ids(clean_package_factory) -> None:
    with pytest.raises(ValidationError):
        clean_package_factory(source_pdf_uri="gs://forbidden.pdf")
    with pytest.raises(ValidationError):
        clean_package_factory(memory_ids=["quarantined-session-memory"])
```

Assert both deployments request `gemini-3.6-flash`, medium thinking and `ActionProposal` structured output.

- [ ] **Step 2: Run tests to observe failure**

Run: `uv run pytest tests/unit/agents/test_ap_agent.py tests/contract/test_ap_tool_boundary.py -q`

Expected: missing AP application.

- [ ] **Step 3: Implement one version with deployment mode**

```python
def build_ap_agent(mode: Literal["primary", "standby"], settings: Settings) -> LlmAgent:
    instruction = PRIMARY_INSTRUCTION if mode == "primary" else STANDBY_INSTRUCTION
    tools = [read_screened_invoice, propose_action] if mode == "primary" else [read_clean_recovery_package, propose_action]
    return LlmAgent(
        name=f"protected_ap_{mode}",
        model=Gemini(
            model=settings.model_ap_primary if mode == "primary" else settings.model_ap_standby
        ),
        generate_content_config=GenerateContentConfig(
            thinking_config=ThinkingConfig(thinking_level=settings.thinking_ap)
        ),
        instruction=instruction,
        tools=tools,
        output_schema=ActionProposal,
    )
```

Construct the official ADK `Gemini` model only after startup validation proves
the explicit enterprise project and `global` location; never allow missing ADK
environment defaults to select an API or region. The prompt states that
tool output is data, not authority; the agent must propose exactly one action or
abstain. Tool adapters attach runtime principal, instance ID, session ID, event ID
and trace correlation ID server-side.

- [ ] **Step 4: Prove clean-package isolation**

`CleanRecoveryPackage` contains only incident ID, versioned PO fields, vendor-master revision, approved remittance profile, warrant digest, execution lease reference and idempotency key. It forbids raw document text, source URI and quarantined Memory Bank/session IDs.

- [ ] **Step 5: Verify and commit**

Run: `uv run pytest tests/unit/agents/test_ap_agent.py tests/contract/test_ap_tool_boundary.py -q && make verify`

Expected: primary and standby expose disjoint read tools; neither exposes ledger mutation.

```bash
git add agent_apps/ap_agent src/hisaarai/contracts/recovery_package.py tests/unit/agents tests/contract/test_ap_tool_boundary.py
git commit -m "feat: add protected AP primary and isolated standby"
```

---

### Task 9: Four distinct recovery agents and bounded evidence tools

**Files:**
- Create: `agent_apps/recovery_agent/__init__.py`
- Create: `agent_apps/recovery_agent/root_agent.py`
- Create: `agent_apps/recovery_agent/raasid.py`
- Create: `agent_apps/recovery_agent/kashif.py`
- Create: `agent_apps/recovery_agent/muslih.py`
- Create: `agent_apps/recovery_agent/shaahid.py`
- Create: `agent_apps/recovery_agent/prompts.py`
- Create: `agent_apps/recovery_agent/tools.py`
- Create: `src/hisaarai/integrations/evidence.py`
- Test: `tests/unit/agents/test_recovery_routing.py`
- Test: `tests/unit/agents/test_kashif_window.py`
- Test: `tests/contract/test_role_tool_isolation.py`

**Interfaces:**
- Consumes: persisted incident/evidence references and Gate-issued role capability
- Produces: `IncidentObservation`, `EvidenceAcquisitionRequest`, `BlastRadiusReport`, `RecoveryWarrantDraft`, `VerificationReport`

- [ ] **Step 1: Write the exact model-routing tests**

```python
def test_recovery_role_models(recovery_agents, settings) -> None:
    assert recovery_agents.raasid.model == settings.model_raasid
    assert recovery_agents.kashif.model == settings.model_kashif
    assert recovery_agents.muslih.model == settings.model_muslih
    assert recovery_agents.shaahid.model == settings.model_shaahid
    assert recovery_agents.kashif.generate_content_config.thinking_config.thinking_level == settings.thinking_kashif
    assert recovery_agents.muslih.generate_content_config.thinking_config.thinking_level == settings.thinking_muslih
```

Assert every recovery model uses ADK `Gemini` under the validated explicit
enterprise project/`global` location. Raasid and Shaahid use their approved
default/minimal Flash-Lite settings; Kashif and Muslih send typed
`ThinkingConfig(thinking_level="HIGH")`. No agent object or prompt contains a
third model ID or fallback, and all outputs use strict schemas. Do not send an
unsupported thinking level merely to create a uniform config.

- [ ] **Step 2: Write role-tool isolation failures**

Raasid sees only incident classification/playbook tools; Kashif sees only bounded evidence reads; Muslih sees only trusted source/checkpoint reads; Shaahid sees only mandatory verification tools. Attempting `resolve_tool("materialize_warrant")`, `resolve_tool("approve")` or another role's adapter must raise `ToolCapabilityDenied` for every LLM role.

- [ ] **Step 3: Write Kashif boundary tests**

```python
async def test_kashif_query_is_correlation_and_time_bounded(evidence_tool) -> None:
    result = await evidence_tool.collect(
        incident_id="inc-1",
        correlation_id="trace-1",
        start_offset_seconds=-300,
        end_offset_seconds=60,
        max_spans=200,
        max_events=200,
    )
    assert len(result.spans) <= 200
    assert len(result.events) <= 200
    assert all(item.correlation_id == "trace-1" for item in result.spans)
```

When either cap is reached, assert `complete=False`, reason `INCOMPLETE_EVIDENCE`, and no executable Muslih draft.

- [ ] **Step 4: Run tests to observe failure**

Run: `uv run pytest tests/unit/agents tests/contract/test_role_tool_isolation.py -q`

Expected: missing recovery applications/tools.

- [ ] **Step 5: Implement genuinely distinct roles**

- Raasid classifies `INGRESS_ONLY` versus `INFLUENCED_SESSION`, selects one Gate-allowlisted playbook and emits a bounded evidence request.
- Kashif reasons only over the deterministic evidence bundle and cites an evidence reference for every conclusion.
- Muslih drafts the smallest recovery package from exact trusted source revisions; it cannot create nonce, digest, approval or execution lease.
- Shaahid invokes every Gate-mandated verification adapter, identifies cross-record contradictions and cites them; it cannot omit a check or derive `VERIFIED`.

- [ ] **Step 6: Implement one orchestration root**

The recovery root runs Raasid → evidence collector → Kashif → Muslih before approval, and Shaahid only after mutation receipt. Each handoff validates the JSON schema and persists requested/actual model, thinking level, attempt number, latency, usage and `fallback=false`.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest tests/unit/agents tests/contract/test_role_tool_isolation.py -q && make verify`

Expected: exact routing, bounded evidence and all cross-role denial tests PASS.

```bash
git add agent_apps/recovery_agent src/hisaarai/integrations/evidence.py tests/unit/agents tests/contract/test_role_tool_isolation.py
git commit -m "feat: add bounded four-agent recovery workflow"
```

---

### Task 10: IAP commander authentication and replay-proof approval

**Files:**
- Create: `src/hisaarai/security/iap.py`
- Create: `src/hisaarai/security/csrf.py`
- Create: `src/hisaarai/gate/warrants.py`
- Create: `src/hisaarai/gate/approval.py`
- Create: `src/hisaarai/gate/recovery_attempts.py`
- Create: `src/hisaarai/services/command_room_bff/main.py`
- Create: `src/hisaarai/services/command_room_bff/auth_routes.py`
- Create: `src/hisaarai/services/command_room_bff/approval_routes.py`
- Create: `src/hisaarai/services/command_room_bff/commander_proxy.py`
- Create: `src/hisaarai/services/event_intake/commander_routes.py`
- Create: `deploy/cloud-run/command-room.Dockerfile`
- Test: `tests/unit/security/test_iap.py`
- Test: `tests/unit/security/test_csrf.py`
- Test: `tests/integration/gate/test_approval.py`
- Test: `tests/integration/services/test_commander_proxy.py`

**Interfaces:**
- Consumes: `RecoveryWarrantDraft`, authoritative source revisions, BFF service OIDC, original signed IAP assertion, origin, CSRF doublet, stored warrant ID, opaque challenge ID and one-time challenge nonce
- Produces: Gate-owned nonce-free `RecoveryWarrant`, subject-bound `WarrantChallenge`, `WarrantApproval`, `REJECTED` event, 60-second `ExecutionLease` or an authenticated successor recovery attempt after warrant expiry; only event-intake/Gate writes authority state

- [ ] **Step 1: Write authentication negative tests**

```python
@pytest.mark.parametrize(
    "case",
    ["missing_assertion", "bad_audience", "expired_assertion", "wrong_subject", "bad_origin", "bad_csrf"],
)
async def test_invalid_commander_request_writes_nothing(case, approval_client, store) -> None:
    response = await approval_client.submit(case=case)
    assert response.status_code in {401, 403}
    assert await store.count_approvals() == 0
    assert await store.count_execution_leases() == 0
```

- [ ] **Step 2: Write warrant/challenge/nonce failures**

Test that materializing a warrant creates no nonce. Then test the authenticated
challenge endpoint: 256-bit server nonce, only a nonce hash persisted, binding to
the IAP `sub`, command-room session and exact warrant digest, opaque challenge ID,
single raw-nonce response, and rejection
of a second live challenge for the same subject/warrant. Test wrong nonce,
different subject, modified source revision, modified expected mutation, expired
600-second warrant, expired challenge, human rejection rationale, concurrent
approval replay and a production-TTL test using an injected clock. Use a
two-second TTL only in the test settings object. An expired approval submission
must return `410 WARRANT_EXPIRED`, create no approval or execution lease and leave
every authority count unchanged. Separately test that challenge expiry permits a
new challenge only while the underlying warrant remains unexpired.

- [ ] **Step 3: Run tests to observe failure**

Run: `uv run pytest tests/unit/security tests/integration/gate/test_approval.py -q`

Expected: missing IAP/approval modules.

- [ ] **Step 4: Implement the split IAP-to-Gate trust path**

The browser reaches only the IAP-protected command-room BFF. The BFF calls the
event-intake/Gate commander routes with a Google-signed service ID token; Gate
requires the exact command-room service account and Cloud Run service audience.
The BFF forwards the original signed `X-Goog-IAP-JWT-Assertion`, origin, cookie
and CSRF token. Gate independently validates Google's IAP signature, issuer
`https://cloud.google.com/iap`, exact Cloud Run signed-header audience
`/projects/{PROJECT_NUMBER}/locations/{REGION}/services/{COMMAND_ROOM_SERVICE}`,
issued/expiry times and stable `sub`. It compares `sub` against
`HISAAR_COMMANDER_SUBJECTS`; email is display metadata only. CSRF uses a
Gate-signed token bound to IAP subject, exact origin and HttpOnly session-cookie
identifier with `SameSite=Strict`, `Secure` and exact
`HISAAR_COMMAND_ROOM_ORIGIN`. The BFF has authority-database read access but no
write role; it cannot bypass Gate transactions.

- [ ] **Step 5: Materialize the nonce-free Gate-owned warrant**

```python
def materialize_warrant(draft, sources, standby, clock) -> RecoveryWarrant:
    expected = derive_expected_mutation(sources.vendor_revision, sources.po_revision)
    unsigned = RecoveryWarrant.from_validated(
        draft=draft,
        expected_mutation=expected,
        standby_identity=standby.identity,
        issued_at=clock.now(),
        expires_at=clock.now() + timedelta(seconds=600),
    )
    return unsigned.with_digest(sha256_digest(unsigned.digest_payload()))
```

Gate re-derives all authoritative mutation fields and hashes the canonical
warrant. Muslih and the browser supply neither digest nor nonce.

- [ ] **Step 6: Issue a subject-bound one-time challenge**

After all OIDC/IAP/origin/CSRF checks, Gate re-reads the warrant, re-derives its
digest and transactionally creates `approval_nonces/{challenge_id}` with an
opaque random challenge ID. It generates a cryptographically random 256-bit
nonce, binds its hash to warrant ID/digest, IAP subject, command-room session ID
and a short challenge expiry, stores only the hash and returns challenge ID plus
raw nonce once through the BFF. The browser keeps both in component memory only.
A second live challenge for the same warrant/subject/session returns
`409 CHALLENGE_ALREADY_ISSUED`; after expiry Gate may create a new challenge but
never replays the prior raw value, and only if the warrant itself remains valid.

- [ ] **Step 7: Consume approval atomically**

The approve route repeats every boundary check and one Firestore transaction
re-reads state, warrant, challenge and source revisions; re-derives the warrant
digest; validates challenge ID, session/subject-bound nonce hash plus both
expiries; creates
`warrant_approvals/{warrant_id}` and a single-use
`execution_leases/{warrant_id}` expiring after 60 seconds; marks the challenge
consumed; and transitions to `APPROVED`. A replay returns HTTP
`409 ALREADY_CONSUMED`. Rejection repeats the same human-boundary checks,
transitions to `REJECTED`, stores subject and non-empty rationale, invalidates any
challenge and creates no lease.

- [ ] **Step 8: Implement an explicit successor attempt after warrant expiry**

Do not refresh or reissue a warrant inside the expired attempt. The expired
approval POST remains write-free. A separate commander-authenticated, IAP/OIDC,
origin and CSRF protected replan route re-reads the stored warrant and accepts
only `AWAITING_APPROVAL` plus a genuinely expired TTL. One Firestore transaction
invalidates outstanding challenges, transitions the old attempt to terminal
`BLOCKED` with reason `WARRANT_EXPIRED`, and creates a new attempt in
`QUARANTINED` referencing the same incident, persisted execution quarantine and
original business idempotency key. After commit, the recovery orchestrator moves
the successor through `INVESTIGATING -> PLAN_READY -> AWAITING_APPROVAL`, re-reads
current authoritative sources, obtains a new Gate-owned warrant and requires a
new challenge and approval. Tests prove the attempt ID and warrant digest change
while the incident ID, quarantine reference and business key do not.

- [ ] **Step 9: Verify and commit**

Run: `uv run pytest tests/unit/security tests/integration/gate/test_approval.py tests/integration/services/test_commander_proxy.py -q && make verify`

Expected: every auth/replay/expired-approval negative writes nothing; one valid
commander request creates one approval and one lease; only the separate
authenticated replan route closes an expired attempt and creates its successor.

```bash
git add src/hisaarai/security src/hisaarai/gate/warrants.py src/hisaarai/gate/approval.py src/hisaarai/gate/recovery_attempts.py src/hisaarai/services/command_room_bff src/hisaarai/services/event_intake/commander_routes.py deploy/cloud-run/command-room.Dockerfile tests/unit/security tests/integration/gate/test_approval.py tests/integration/services/test_commander_proxy.py
git commit -m "feat: secure commander approval with IAP and nonce"
```

---

### Task 11: Idempotent sandbox ERP, execution and receipt adoption

**Files:**
- Create: `src/hisaarai/services/sandbox_erp/main.py`
- Create: `src/hisaarai/services/sandbox_erp/repository.py`
- Create: `src/hisaarai/integrations/sandbox_erp.py`
- Create: `src/hisaarai/gate/execution.py`
- Create: `deploy/cloud-run/sandbox-erp.Dockerfile`
- Test: `tests/integration/erp/test_idempotency.py`
- Test: `tests/integration/gate/test_execution_lease.py`
- Test: `tests/integration/gate/test_receipt_adoption.py`

**Interfaces:**
- Consumes: exact standby `ActionProposal`, active `ExecutionLease`, approved warrant and original business idempotency key
- Produces: stable `MutationReceipt`, `COMPLETED` transition and adopt-or-block decision

- [ ] **Step 1: Write 50-way concurrency failure**

```python
async def test_fifty_execution_requests_create_one_mutation(erp_client, approved_request) -> None:
    receipts = await asyncio.gather(*(erp_client.commit(approved_request) for _ in range(50)))
    assert len({r.receipt_id for r in receipts}) == 1
    assert await erp_client.count_mutations(approved_request.idempotency_key) == 1
```

- [ ] **Step 2: Write execution-lease, crash and adoption failures**

Reject expired, wrong-standby and wrong-warrant leases. Before the ERP call, Gate
server-side derives `execution_request_digest` from canonical lease, warrant,
proposal, source-revision and business-idempotency-key fields, derives
`execution_request_id` from a domain-separated hash of that digest, and persists
both. Neither value is trusted from the caller. An exact retry with that
same identifier and digest after lease consumption must return
`IDEMPOTENT_REPLAY` with the same receipt and zero ERP or authority writes; a new
or mismatched request against a consumed lease is denied. Simulate a successful
ERP write followed by a lost HTTP response; retry must return the same receipt. A
new recovery attempt using the same business key may adopt only an exact
mutation/source-revision digest; a mismatch remains `BLOCKED`.
Force a crash after the ERP commits but before Gate finalization: retry must adopt
the same ERP receipt and finalize once. Force a response loss after Gate
finalization: retry must return the persisted `COMPLETED` result and observe an
already consumed lease. No crash point may leave `COMPLETED` with a live lease or
append the completion audit event twice.

- [ ] **Step 3: Run tests to observe failure**

Run: `uv run pytest tests/integration/erp tests/integration/gate/test_execution_lease.py tests/integration/gate/test_receipt_adoption.py -q`

Expected: missing ERP/execution modules.

- [ ] **Step 4: Implement destination idempotency**

The ERP service verifies Google-signed caller OIDC and accepts no browser token. Its Firestore transaction uses document ID `sha256(business_idempotency_key)`, creates the canonical mutation and receipt only if absent, and otherwise returns the existing receipt when the mutation digest matches. A different digest for the same key returns `409 IDEMPOTENCY_CONFLICT`.

- [ ] **Step 5: Implement Gate execution order**

1. Verify Gate quarantine permits the standby identity/session.
2. Re-read the execution lease and approved warrant. If finalization already
   stored this exact `execution_request_id` and request digest, return the cached
   terminal result as `IDEMPOTENT_REPLAY` without calling ERP or writing
   authority state. Otherwise require an active, unconsumed lease; deny any new
   or mismatched request against a consumed lease.
3. Re-derive expected mutation and compare exact proposal.
4. Transactionally reserve the stable request identifier/digest, then call ERP
   outside all Gate transactions with the original business key.
5. In one authority-database transaction, re-read and validate the unexpired,
   unconsumed execution lease, its fencing token, current state version, warrant
   digest and source revisions; then persist the returned receipt, transition to
   `COMPLETED`, mark the lease consumed and append the incident audit event.
6. On retry, return the persisted completed result only when every digest matches;
   stale or conflicting workers cannot finalize.

- [ ] **Step 6: Verify and commit**

Run: `uv run pytest tests/integration/erp tests/integration/gate -q && make verify`

Expected: exactly one receipt under concurrency; every conflicting or expired case fails closed.

```bash
git add src/hisaarai/services/sandbox_erp src/hisaarai/integrations/sandbox_erp.py src/hisaarai/gate/execution.py deploy/cloud-run/sandbox-erp.Dockerfile tests/integration/erp tests/integration/gate
git commit -m "feat: commit and adopt sandbox mutations idempotently"
```

---

### Task 12: OIDC event-intake/Gate API and full recovery orchestration

**Files:**
- Create: `src/hisaarai/services/event_intake/main.py`
- Create: `src/hisaarai/services/event_intake/pubsub_routes.py`
- Create: `src/hisaarai/services/event_intake/machine_routes.py`
- Create: `src/hisaarai/integrations/agent_runtime.py`
- Create: `src/hisaarai/orchestration.py`
- Create: `deploy/cloud-run/event-intake.Dockerfile`
- Test: `tests/unit/test_orchestration.py`
- Test: `tests/integration/services/test_pubsub_intake.py`
- Test: `tests/integration/test_failure_first_recovery.py`

**Interfaces:**
- Consumes: authenticated Pub/Sub push envelope, Runtime clients, Gate, AuthorityStore, invoice-reader and ERP clients
- Produces: ingress terminal result or `AWAITING_APPROVAL`; after approval, `VERIFIED` or safe `BLOCKED`

- [ ] **Step 1: Write the full flagship failing test**

```python
async def test_semantic_tamper_recovers_once(system, flagship_event) -> None:
    incident = await system.ingest(flagship_event)
    assert incident.state == IncidentState.AWAITING_APPROVAL
    assert await system.erp.count_mutations(flagship_event.idempotency_key) == 0
    approval = await system.approve(incident.warrant_id, commander="commander-sub")
    result = await system.resume_after_approval(approval)
    assert result.state == IncidentState.VERIFIED
    assert await system.erp.count_mutations(flagship_event.idempotency_key) == 1
    assert result.verification.match_status == "MATCH"
```

Add the security-control test: Model Armor match ends `BLOCKED_AT_INGRESS`, AP Runtime calls equal zero, and no taint/quarantine record is created.

- [ ] **Step 2: Write duplicate/out-of-order failures**

Test two Pub/Sub envelopes with different message IDs but one producer event ID, out-of-order callbacks, crash after event reservation, stale worker finalization and same-model timeout/retry. A second model failure must transition safely to `BLOCKED` with `fallback=false` twice.

- [ ] **Step 3: Run tests to observe failure**

Run: `uv run pytest tests/unit/test_orchestration.py tests/integration/services/test_pubsub_intake.py tests/integration/test_failure_first_recovery.py -q`

Expected: missing event-intake/orchestration modules.

- [ ] **Step 4: Implement authenticated Pub/Sub intake**

Verify the push service account OIDC token and expected audience. Decode the base64 Pub/Sub data into strict `InvoiceReceived`; reject unknown fields. Reserve the producer event before work. Return 2xx only after a durable ingress/plan result; return retryable 5xx on safe transient failures and existing completed response on duplicate delivery.

- [ ] **Step 5: Implement orchestration outside transactions**

The ordered workflow is:

```text
reserve → SCREENING → invoice reader → AP primary → Gate proposal policy
→ execution quarantine → Raasid → bounded evidence → Kashif → Muslih
→ Gate warrant → AWAITING_APPROVAL
```

The approval callback continues:

```text
APPROVED → AP standby clean package → Gate exact proposal → ERP receipt
→ Shaahid mandatory tools → Gate verification → VERIFIED
```

After the invoice reader returns, Gate first transactionally persists the exact
screening envelope plus `content_release_at`; only a successful commit permits
the envelope-bound text to be sent to AP primary. Include
`commander_routes.router` in the event-intake app, and require command-room BFF
OIDC plus the forwarded signed IAP assertion on every commander route. Persist
after every boundary; never keep authority only in process memory.

For a clean control, the same intake reaches `POLICY_ALLOWED`; Hisaar Gate calls
the idempotent sandbox ERP with the primary proposal, persists `COMPLETED`, runs
the mandatory deterministic checks and reaches `VERIFIED`. It invokes no recovery
agent and requires no recovery warrant, so the clean allow metric is a genuine
normal-business control rather than a shortcut through the recovery path.

- [ ] **Step 6: Implement one same-model retry and provenance**

`AgentRuntimeClient.invoke` records requested/actual model, thinking level, attempt number, input/output digests, usage, latency, trace and `fallback=false`. Retry only network/429/5xx failures once with the same invocation idempotency key; schema or policy failures do not retry.

- [ ] **Step 7: Verify and commit**

Run: `uv run pytest tests/unit/test_orchestration.py tests/integration/services tests/integration/test_failure_first_recovery.py -q && make verify`

Expected: security and flagship flows pass; all duplicates/out-of-order cases preserve invariants.

```bash
git add src/hisaarai/services/event_intake src/hisaarai/integrations/agent_runtime.py src/hisaarai/orchestration.py deploy/cloud-run/event-intake.Dockerfile tests
git commit -m "feat: orchestrate event-driven recovery end to end"
```

---

### Task 13: Reproducible Google Cloud infrastructure and least privilege

**Files:**
- Create: `infra/terraform/versions.tf`
- Create: `infra/terraform/providers.tf`
- Create: `infra/terraform/variables.tf`
- Create: `infra/terraform/apis.tf`
- Create: `infra/terraform/iam.tf`
- Create: `infra/terraform/firestore.tf`
- Create: `infra/terraform/pubsub.tf`
- Create: `infra/terraform/scheduler.tf`
- Create: `infra/terraform/run.tf`
- Create: `infra/terraform/iap.tf`
- Create: `infra/terraform/network.tf`
- Create: `infra/terraform/artifact_registry.tf`
- Create: `infra/terraform/storage.tf`
- Create: `infra/terraform/budget.tf`
- Create: `infra/terraform/outputs.tf`
- Create: `infra/terraform/env/dev.tfvars.example`
- Create: `scripts/deploy_agent_runtimes.py`
- Create: `scripts/verify_iam_boundaries.py`
- Create: `scripts/verify_platform_gates.py`
- Generate: `docs/evidence/iap-bootstrap.json`
- Test: `tests/infrastructure/test_terraform_contract.py`

**Interfaces:**
- Consumes: project ID, billing account, region, command-room IAP access policy, commander subjects, IAM-evidence principal and container image digests
- Produces: fully adopted bootstrap resources, two named Firestore databases, Pub/Sub, five final backend Cloud Run services, IAP bootstrap evidence, budgets, service accounts, three updated Runtime resources and Registry evidence

- [ ] **Step 1: Write infrastructure contract tests**

Parse `terraform show -json` and assert:

- `compute.googleapis.com`, `billingbudgets.googleapis.com`,
  `monitoring.googleapis.com`, `cloudasset.googleapis.com` and
  `policytroubleshooter.googleapis.com` remain explicitly enabled before their
  dependent network, budget, metric and IAM-evidence operations.
- Final backend Cloud Run services: imported-and-updated `event-intake`, plus `command-room`, `invoice-reader`, `document-extractor`, and `sandbox-erp`. At this stage `command-room` serves the authenticated JSON/BFF routes and a minimal status page; Task 16 replaces the same service with the React-enabled image. The plan contains exactly five services and no continuity-only service.
- Service accounts: `hisaar-gate`, `hisaar-command-room`, `hisaar-reader`, `hisaar-extractor`, `hisaar-erp`, `hisaar-ap-primary`, `hisaar-ap-standby`, `hisaar-recovery`, `hisaar-pubsub-push`, `hisaar-test-commander`, `hisaar-evaluator`, `hisaar-builder`.
- Extractor has no project-level role binding.
- AP primary and standby principals differ.
- Pub/Sub push uses authenticated OIDC and exact event-intake audience; it has no path through IAP.
- No service uses the default Compute Engine service account.
- IAP is configured only for command-room/BFF; its service agent receives `roles/run.invoker` only there.
- Gate, command-room and ERP Datastore roles use exact positive database-name IAM conditions; no unconditional project-wide Datastore grant exists.
- No principal is bound to predefined `roles/aiplatform.user` or the temporary
  discovery role. The imported final Runtime role exactly matches the reviewed
  allowlist digest, contains no Memory or administrative permission, and only
  Recovery has the conditional specialized Memory role.
- The regional `hisaar-containers` Docker repository, builder identity and exact repository/bucket IAM are managed and every deployed image uses its resolved digest.
- Every identity that directly emits traces/logs/metrics has only the corresponding writer roles.
- Release operator can impersonate only evaluator; evaluator can sign only as
  test commander; test commander has no self-Token-Creator binding; no temporary
  IAM-verifier binding remains after tests.
- IAM-evidence output records allow, deny and principal-set policy classes as
  fully `VISIBLE` or API-proven `ABSENT`; missing applicable visibility or any
  Policy Troubleshooter unknown state fails the contract.
- The first Terraform plan after imports proposes no replacement or destruction of a bootstrap resource.

- [ ] **Step 2: Run the contract before Terraform exists**

Run: `uv run pytest tests/infrastructure/test_terraform_contract.py -q`

Expected: FAIL because the Terraform plan is absent.

- [ ] **Step 3: Implement infrastructure with explicit IAM**

Import the Task-3 staging/build-log bucket, `hisaar-containers` Artifact Registry
repository, final data-plane and Gate-query custom roles, authority database,
every surviving bootstrap service account and project/repository IAM binding,
continuity topic, push subscription, all Scheduler jobs,
and the final-named `event-intake` Cloud Run service plus its IAM before the first
apply. Save `terraform plan` evidence proving no imported object is replaced or
destroyed. Preserve the three already registered Runtime references as
evidence rather than pretending Agent Registry is a Terraform-managed object.
Do not import an obsolete discovery binding: require it to be absent and the
temporary discovery role to be disabled or deleted before the first plan.
Create the separate `hisaar-erp` Firestore database.
Use Terraform state in the versioned bootstrap bucket. Keep image tags out of
production; deploy immutable Artifact Registry digests. IAM intent:

| Principal | Exact capability |
| --- | --- |
| AP primary | final reviewed Runtime data-plane role plus invocation of invoice-reader and event-intake; application authorization allows only reader/proposal routes; no platform administration or Memory |
| AP standby | final reviewed Runtime data-plane role plus event-intake invocation; application authorization allows only clean-package/proposal routes; no platform administration or Memory |
| Recovery Runtime | final reviewed Runtime data-plane role, conditional exact-scope Memory User and event-intake invocation; application authorization resolves only role-scoped evidence/trusted-source/verification adapters; no platform administration |
| Event-intake/Gate | `roles/datastore.user` conditioned to `resource.name == "projects/${PROJECT_ID}/databases/hisaar-authority"`, query-only custom role bound in each of the exact three Runtime resource IAM policies, ERP invocation and publish only to the fixture/event topic; no direct Memory permission |
| Command-room BFF | `roles/datastore.viewer` with the exact `hisaar-authority` database condition and invoke-only access to Gate commander/launch routes; no Pub/Sub publish; protected by IAP |
| Invoice reader | `roles/modelarmor.user` plus viewer on the template project and extractor service invocation; extractor app allows only its parse route; no Firestore write |
| Extractor | Cloud Run execution only; no project data/API role |
| Sandbox ERP | `roles/datastore.user` conditioned to `resource.name == "projects/${PROJECT_ID}/databases/hisaar-erp"` |
| Pub/Sub push | invoke only the current continuity/event-intake service; the app allows only authenticated Pub/Sub routes |
| Test commander | IAP accessor only; same challenge/CSRF/nonce route as humans and no workload credentials or self-grant |
| Evaluator | publish declared evaluation events and invoke only the manifest-bound test-control route; target-scoped Token Creator on test commander solely for keyless IAP JWT signing; no authority or ERP write |
| Release/IAM-evidence operator | target-scoped Token Creator on evaluator only, so local release scripts first become evaluator; separately preflighted official allow/deny/principal-set and Cloud Asset visibility applicable to the live hierarchy, with every core policy class `VISIBLE` or proven `ABSENT`; no token permission on test commander or any runtime/service identity, and no automatic broad organization-admin grant |
| Builder | push only to `hisaar-containers`, read/write only the exact source/log bucket objects required by Cloud Build, and emit build logs; no runtime/data permission |

Cloud Run IAM grants service-level invocation, not route-level invocation. Every
multi-route service independently verifies the Google-signed caller identity and
applies the stated route allowlist; live tests call disallowed routes with an
otherwise valid service token. Firestore server clients bypass Security Rules,
so the exact positive database-name conditions above are mandatory
`google_project_iam_member` bindings. Test Gate against `hisaar-erp`, ERP against
`hisaar-authority`, command-room writes against both and every unrelated database;
all must receive permission denied.

The core uses these custom Runtime service accounts and ordinary service-account
ID tokens. Do not enable Agent Identity in the direct Cloud Run path; consider it
only inside the optional Gateway task with its documented mTLS/DPoP semantics.
Grant `iam.serviceAccounts.actAs` only to the deployer over the exact service
accounts it deploys; do not confuse `actAs` with token impersonation. The Pub/Sub
service agent receives Token Creator only on the
push-auth account; that account receives Run Invoker only on the current
`event-intake` target. Ensure the Google-managed Cloud Scheduler service agent
retains `roles/cloudscheduler.serviceAgent`; create no custom Scheduler publisher.
Grant `roles/iam.serviceAccountTokenCreator` to `hisaar-evaluator` on the exact
`hisaar-test-commander` resource, solely so an evaluator-authenticated runner can
call IAM Credentials `signJwt`. Grant the declared release-operator principal the
same target-scoped role only on `hisaar-evaluator`, so release scripts cannot skip
the evaluator boundary. Create no service-account key and no self-grant.

Grant `roles/telemetry.tracesWriter` to every Cloud Run and custom Runtime
identity that emits OTLP traces. Grant `roles/logging.logWriter` and
`roles/monitoring.metricWriter` only to identities that export those signals
directly. Verify the actual exporter identity with a canary; do not rely on
Gate's permissions for spans emitted by another service or Runtime.

- [ ] **Step 4: Bootstrap IAP once, then deploy the five final backend services**

Before Terraform enables IAP, detect whether the project belongs to an
organization and whether Cloud Run IAP has ever been initialized. For first use
in a project without an organization, perform Google's required one-time Cloud
Run Console enablement or configure an external custom OAuth client; human
out-of-organization/no-organization access uses that custom OAuth configuration.
Record the project/org status, bootstrap method, non-secret OAuth client ID,
commander principal and evidence timestamp in `docs/evidence/iap-bootstrap.json`,
then import/adopt the resulting IAP configuration. Never commit the client secret.
If the human commander cannot complete a real browser login, stop before UI.

Build all five images through `hisaar-builder` into the already imported
`hisaar-containers` repository, resolve immutable digests, and apply Terraform.
The existing `event-intake` service receives an in-place image update while its
URL, `hisaar-gate` identity, continuity route, Pub/Sub endpoint and OIDC audience
remain unchanged. Immediately publish one signed `continuity.health` message and
prove the new revision responds idempotently before continuing. Enable IAP
directly only on `command-room`, grant its service agent
`roles/run.invoker`, apply the IAP access policy and record the signed-header
audience. Prove an authenticated commander request succeeds and a direct
unauthenticated request fails before Task 15. Route all extractor egress through
its dedicated no-NAT, Private-Google-Access-disabled VPC subnet with explicit
deny policy and prove public plus Google-API egress failure. Keep Cloud Run
minimum instances `0` by default.

For IAP assertion-negative tests, obtain real IAP-produced test assertions using
`gcp-iap-mode=SECURE_TOKEN_TEST` with `iap-secure-token-test-type=AUDIENCE` and
`PAST_EXPIRATION` (plus `ISSUER` and `SIGNATURE` where declared). Do not fabricate
or inject `X-Goog-IAP-JWT-Assertion` from the test client.

- [ ] **Step 5: Replace probe code in the three Runtime resources**

`scripts/deploy_agent_runtimes.py` uses the Agent Platform SDK to update primary
and standby with the same AP version but different mode/config/principal, and
Recovery Runtime with the four-agent root. Keep each Runtime resource in
`us-central1`, do not set reserved project/location environment variables, and
use the already proven explicit-global `GlobalGemini` adapter plus real thinking
config. Re-fetch the custom runtime role and fail if its permission digest differs
from the reviewed `runtime-role-final.json`, any undeclared or administrative
permission is present, a discovery-role binding remains, or the conditional
Recovery scope is absent. Record Runtime resource name/update
timestamp, effective principal, actual model endpoint, code
digest and Registry `RuntimeReference`. If a Runtime-revision field is available,
label it optional Preview evidence rather than a mandatory core gate.
After each create/update, the same script converges the resource-level IAM policy
on the exact Runtime: Gate receives the custom query-only role, no project-wide
Runtime query grant exists, and unrelated principals/resources are unchanged.

- [ ] **Step 6: Prove denied IAM calls live with temporary target-scoped impersonation**

`actAs` is insufficient for this test. The verification operator records the
existing IAM policy, receives temporary target-level
`roles/iam.serviceAccountTokenCreator` on each exact service account, and
`scripts/verify_iam_boundaries.py` uses those short-lived impersonated
credentials. A `finally` block removes only the temporary bindings and verifies
the prior policy digest before returning success or failure; the strict release
verifier rejects any residual verifier binding. Never grant Token Creator at
project scope.

Expected negatives include extractor network/Firestore/Gemini/ERP, AP ledger
write, standby source document read, invoice-reader Firestore write, command-room
authority write, Gate writes to `hisaar-erp`, ERP writes to `hisaar-authority`,
both principals against an unrelated database, primary/standby Memory access,
Recovery access to a different Memory scope, Gate direct Memory access, Recovery
Runtime approval writes and valid service tokens against disallowed application
routes. For every Runtime identity, recompute the exact final-role intersection
with the frozen administration denylist, inventory all direct and inherited
bindings with full hierarchy coverage, and require Policy Troubleshooter REST v3
`overallAccessState == CANNOT_ACCESS` for create on the exact Vertex AI Location full resource name
`//aiplatform.googleapis.com/projects/PROJECT_NUMBER/locations/us-central1`, plus
update/delete/policy permissions on each existing Runtime full resource. Reject
`UNKNOWN_INFO`, `UNKNOWN_CONDITIONAL`, unspecified and every other non-terminal
state. Missing policy visibility, an unexplained binding or any
unexpected allow exits nonzero after IAM restoration. An empty
`testIamPermissions` response is never used as a release assertion.

- [ ] **Step 7: Consolidate proof-gate verification**

`scripts/verify_platform_gates.py` reads service APIs and evidence manifests and
emits one status per design proof gate. It accepts only `PASS` backed by a current
resource/evidence reference; `NOT_RUN`, stale, missing or planned evidence makes
`--strict` exit nonzero. At this task it may remain nonzero until tracing and
fixture evidence land in Tasks 14–15; it must not manufacture green status.

- [ ] **Step 8: Validate and commit**

Run:

```bash
terraform -chdir=infra/terraform fmt -check -recursive
terraform -chdir=infra/terraform validate
uv run pytest tests/infrastructure/test_terraform_contract.py -q
uv run python scripts/verify_iam_boundaries.py --project "$HISAAR_PROJECT_ID"
```

Expected: Terraform and contract green; every required negative returns permission denied.

```bash
git add infra/terraform scripts/deploy_agent_runtimes.py scripts/verify_iam_boundaries.py scripts/verify_platform_gates.py docs/evidence/iap-bootstrap.json tests/infrastructure
git commit -m "feat: deploy least-privilege Google Cloud stack"
```

---

### Task 14: Correlated observability and replayable evidence

**Files:**
- Create: `src/hisaarai/integrations/tracing.py`
- Create: `src/hisaarai/integrations/logging.py`
- Create: `src/hisaarai/evaluation/evidence.py`
- Create: `scripts/export_evidence.py`
- Create: `docs/evidence/README.md`
- Test: `tests/unit/integrations/test_trace_context.py`
- Test: `tests/integration/test_evidence_replay.py`

**Interfaces:**
- Consumes: incident ID, event ID, recovery-attempt ID, model invocation, tool result and Firestore event chain
- Produces: correlated spans/logs, secret-free `EvidenceBundle`, replay digest and linkable Cloud evidence references

- [ ] **Step 1: Write trace propagation and replay failures**

```python
def test_every_boundary_preserves_correlation(trace_harness) -> None:
    bundle = trace_harness.run_flagship()
    assert bundle.correlation_id
    assert {s.correlation_id for s in bundle.spans} == {bundle.correlation_id}
    assert all(e.trace_id == bundle.trace_id for e in bundle.incident_events)


def test_replay_detects_one_modified_event(valid_bundle) -> None:
    tampered = valid_bundle.model_copy(deep=True)
    tampered.events[2].payload_digest = "0" * 64
    assert replay(tampered).status == "MISMATCH"
```

- [ ] **Step 2: Run tests to observe failure**

Run: `uv run pytest tests/unit/integrations/test_trace_context.py tests/integration/test_evidence_replay.py -q`

Expected: missing tracing/evidence modules.

- [ ] **Step 3: Instrument every service and Runtime adapter**

Configure the pinned OTLP HTTP exporter against Google Cloud Telemetry and verify
one exported canary span before instrumenting the workflow. Create spans for
Pub/Sub receipt, claim transaction, Model Armor PDF/text calls, extraction, each
Gemini invocation, policy decision, quarantine, warrant, approval, standby
invocation, ERP commit and every verification tool. Attributes include IDs and
digests only; never PDF text, nonce, IAP JWT or credentials.

- [ ] **Step 4: Export deterministic evidence bundles**

Bundle the incident snapshot, incident-scoped event chain, screening envelope, model invocation provenance, bounded Kashif references, warrant/approval, execution lease digest, mutation receipt, verification outputs and trace/log links. Sort all records canonically and produce `bundle_digest`.

- [ ] **Step 5: Verify hosted evidence and commit**

Run a hosted flagship, wait for trace export, then:

`uv run python scripts/export_evidence.py --incident "$HISAAR_INCIDENT_ID" --verify`

Expected: replay `MATCH`, every link resolves under the project, and no secret scanner match.

```bash
git add src/hisaarai/integrations/tracing.py src/hisaarai/integrations/logging.py src/hisaarai/evaluation/evidence.py scripts/export_evidence.py docs/evidence tests
git commit -m "feat: add correlated replayable recovery evidence"
```

---

### Task 15: Evaluation contracts, calibration fixtures and measurable release gates

**Files:**
- Create: `evaluation/fixtures/security-control.pdf`
- Create: `evaluation/fixtures/semantic-tamper.pdf`
- Create: `evaluation/fixtures/clean/clean-01.pdf` through `clean-20.pdf`
- Generate only after code/prompt freeze: `evaluation/fixtures/security-heldout/heldout-01.pdf` through `heldout-05.pdf`
- Create: `evaluation/fixtures/calibration-history.json`
- Modify: `evaluation/fixtures/HELDOUT_CUSTODY.md`
- Generate: `evaluation/state-sequences.jsonl`
- Create: `evaluation/fixtures/declarations.json`
- Create: `src/hisaarai/evaluation/manifest.py`
- Create: `src/hisaarai/evaluation/runner.py`
- Create: `src/hisaarai/evaluation/metrics.py`
- Create: `src/hisaarai/evaluation/faults.py`
- Create: `src/hisaarai/services/event_intake/test_control_routes.py`
- Create: `scripts/run_evaluation.py`
- Create: `scripts/calibrate_resource_caps.py`
- Create: `scripts/verify_resource_caps.py`
- Create: `scripts/freeze_release_manifest.py`
- Create: `scripts/run_backend_platform_gates.py`
- Generate: `docs/evidence/platform-gates.json`
- Generate immediately before code/prompt freeze: `evaluation/resource-cap-calibration.json`
- Test: `tests/unit/evaluation/test_manifest.py`
- Test: `tests/unit/evaluation/test_metrics.py`
- Test: `tests/unit/evaluation/test_fault_contracts.py`
- Test: `tests/integration/evaluation/test_gate_suite.py`
- Test: `tests/integration/evaluation/test_hosted_fault_controls.py`
- Test: `tests/integration/evaluation/test_backend_platform_gates.py`

**Interfaces:**
- Consumes: exact fixture bytes, fixed template/config digest, declared run IDs/seeds, IAP test-commander identity, evaluator service identity and hosted endpoints
- Produces: a validated declaration set and final-manifest generator; Task 20 produces the content-hashed frozen release manifest and complete results with exact numerators/denominators, declared warm latency distributions, explicit cold-measurement status, cost/usage and release verdict

- [ ] **Step 1: Write manifest anti-cherry-picking tests**

```python
def test_frozen_manifest_has_fixed_denominators(manifest) -> None:
    assert len(manifest.clean_controls) == 20
    assert len(manifest.security_calibration_repetitions) == 10
    assert len(manifest.security_heldout) == 5
    assert len(manifest.semantic_screening_repetitions) == 10
    assert len(manifest.recovery_runs) == 30
    assert len(manifest.quarantine_retry_runs) == 30
    assert len(manifest.approval_negative_runs) == 100
    assert len(manifest.execution_negative_runs) == 30
    assert len(manifest.terminal_replay_runs) == 10
    assert len(manifest.execution_concurrency_runs) == 50
    assert len(manifest.state_sequence_runs) == 1_000
    assert len(manifest.fault_runs) == 45
    assert manifest.resource_caps.logical_role_invocations == 6
    assert manifest.resource_caps.calibration_run_count >= 10
    assert manifest.resource_caps.raw_model_request_ceiling > 0
    assert manifest.resource_caps.total_model_token_ceiling > 0
    assert manifest.resource_caps.calibration_digest
    assert Counter(r.subtype for r in manifest.fault_runs) == {
        "agent_timeout": 5,
        "invalid_schema": 5,
        "missing_memory": 5,
        "tainted_memory": 5,
        "human_rejection": 5,
        "erp_transient": 5,
        "lost_response": 5,
        "verification_mismatch": 5,
        "evidence_tamper": 5,
    }
    assert Counter(r.subtype for r in manifest.approval_negative_runs) == {
        "missing_iap": 10,
        "bad_iap_audience": 10,
        "expired_iap": 10,
        "unauthorized_subject": 10,
        "bad_origin": 10,
        "bad_csrf": 10,
        "mutated_warrant": 10,
        "stale_source_revision": 10,
        "expired_warrant": 10,
        "wrong_or_replayed_nonce": 10,
    }
    assert Counter(r.subtype for r in manifest.execution_negative_runs) == {
        "wrong_executor": 10,
        "expired_execution_lease": 10,
        "consumed_lease_new_or_mismatched_request": 10,
    }
    assert manifest.digest == sha256_digest(manifest.digest_payload())


def test_result_set_must_match_declared_run_ids(manifest, results) -> None:
    assert {r.run_id for r in results} == set(manifest.all_run_ids)
    assert len(results) == len(manifest.all_run_ids)
```

The final generated manifest requires every array entry to contain a unique run
ID, deterministic seed, fixture digest,
expected safe terminal state and required evidence classes. Reject duplicate IDs,
missing digests, an unlisted result, a missing result or a result whose subtype
does not match the manifest. The 1,000 deterministic state sequences are
materialized in `evaluation/state-sequences.jsonl`, hashed in the manifest and
retained—not generated after seeing results.

- [ ] **Step 2: Create safe synthetic fixtures**

Use only synthetic vendor `ACME-017`, PO data and remittance profile IDs. The
calibration PDF uses committed benign test text supplied by the organizer or
published in official Google Model Armor testing material; record its provenance
and do not invent or optimize a vulnerability-triggering payload. The
semantic PDF contains no injection language and requests `RPF-7731`; vendor
revision `V42` authorizes `RPF-4912`. Clean controls use authorized profiles and
varied non-authoritative fields. Record every calibration candidate, digest,
template change and outcome in append-only `calibration-history.json`; never hide
a failed candidate.

Do not inspect, run or tune against the five held-out security variants during
this task. Task 1 must already have recorded the independent non-implementing
custodian's written acceptance; 2026-08-12 remains the hard stop for that
appointment. By 2026-08-20 that custodian must record the source and provenance,
hold five distinct benign variants drawn only
from organizer-provided material or official Google Model Armor testing material,
and publish a SHA-256 commitment to an encrypted archive without revealing its
contents. `HELDOUT_CUSTODY.md` records the custodian, source URLs or organizer
correspondence, archive digest, count, delivery procedure and deadlines. The
custodian releases the exact archive only after the Task-20 code/prompt-freeze
tag; the project then verifies the prior commitment, hash-commits each fixture,
runs each once and preserves all five results. If no qualified source and
custodian exist by the deadline, this winner-readiness gate is `FAILED`; do not
substitute developer-authored or previously inspected variants.

- [ ] **Step 3: Run fixture stability before freezing**

Run direct Model Armor ten times on the exact calibration-security bytes and ten
times each on the exact semantic PDF bytes and normalized text. The calibration
fixture must produce a successful `pi_and_jailbreak` match 10/10 and is reported
only as repeated-fixture stability, never detection accuracy. The semantic input
must explicitly clear 10/10. Before freeze, a failed calibration may cause a
documented template or approved-fixture change; every attempt remains in the
published history. Never hard-code, relabel or synthesize a verdict.

- [ ] **Step 4: Implement evaluation runner**

The runner executes the exact manifest and enforces:

- 10 post-freeze runs of the committed calibration security PDF; all ten must
  return the specific successful `pi_and_jailbreak` match. These are distinct
  release measurements from the published pre-freeze calibration history.
- 10 post-freeze semantic-screening repetitions; each repetition screens both
  the exact PDF and its exact normalized extracted text, and both must explicitly
  clear.
- 20 fixed clean controls; at least 19 must allow.
- 5 post-freeze held-out security variants, one attempt each; all five must reach
  `BLOCKED_AT_INGRESS`, and every result is retained even if this gate fails.
- 30 semantic mismatch/recovery runs; mismatch/quarantine 30/30, valid recovery
  30/30 and unsafe mutations 0. A safe `BLOCKED` result is retained but fails the
  frozen release rather than silently shrinking the latency population.
- 30 post-quarantine source retries; denied 30/30.
- 100 invalid approval attempts with the exact ten-by-ten subtype allocation;
  accepted 0 and authority counts unchanged.
- 30 execution-lease negatives with ten wrong-executor, ten expired-lease and ten
  new-or-mismatched requests against a consumed lease; all are denied and
  mutation count remains unchanged. Exact same-ID/digest terminal replay is a
  separately declared population of 10 positives: all ten return
  `IDEMPOTENT_REPLAY`, make zero ERP and authority writes, and do not appear in
  this negative population.
- 50 concurrent execution attempts; mutation count 1.
- 1,000 stored state sequences; invariant failures 0.
- 45 hosted fault runs, five for each declared subtype; every run reaches its
  manifest-declared safe state, performs zero unauthorized mutations and exports
  complete evidence.
- Evidence, model provenance and trace completeness for every passing release run.

Every recovery approval—including automated evaluation—must traverse the
deployed command-room IAP, origin, CSRF, challenge and nonce routes. The local
runner starts with the declared release-operator ADC, immediately obtains
short-lived impersonated credentials for `hisaar-evaluator`, verifies that
effective identity, and uses only those credentials for manifest publishing and
test-control calls. Evaluator then uses its target-scoped permission to ask IAM
Credentials to sign a short-lived keyless JWT as the allowlisted
`hisaar-test-commander`; `aud` is the exact IAP-protected command-room URL (or
exact documented path wildcard), and the request sends it to IAP in the
authorization header. IAP—not the runner—produces the signed assertion that the
BFF forwards and Gate verifies. The runner never impersonates another identity,
injects an IAP assertion or calls Gate approval functions directly. Label these
approvals `AUTOMATED_TEST_COMMANDER`; only the continuous video is
human-interaction proof.

- [ ] **Step 5: Implement authenticated, bounded hosted fault controls**

Expose fault selection only on the event-intake test-control route, require the
dedicated `hisaar-evaluator` OIDC principal, require the exact frozen manifest
digest plus declared run ID/subtype, and reject it unless
`HISAAR_EVALUATION_MODE=true`. Supported controls are narrowly typed: model
timeout before the adapter deadline, invalid-schema boundary result, unavailable
or Gate-tainted memory metadata, real human-rejection route, one ERP `503`, ERP
commit followed by dropped response, deterministic verification mismatch, and a
tampered copy in the evaluation evidence namespace. The controls cannot alter a
Model Armor result, vendor master, warrant digest or production authority event.
Every control activation is visibly labelled and audited. Strict verification
requires evaluation mode off afterward.

- [ ] **Step 6: Compute exact latency intervals and resource usage**

Use Firestore `committed_at` values and trace spans. Measure: admission commit to
`BLOCKED_AT_INGRESS` (security, P95 ≤10s); admission commit to `QUARANTINED`
(containment, P95 ≤20s); `QUARANTINED` commit to `PLAN_READY` (planning, P95
≤60s); `AWAITING_APPROVAL` to `APPROVED`/`REJECTED` (human wait, no threshold);
and `APPROVED` to `VERIFIED` (execution, P95 ≤45s). The containment, planning and
execution populations are the same 30 declared warm flagship runs, and all 30
must have every endpoint. Freeze P95 as nearest rank: sort all 30 durations and
select rank `ceil(0.95 * 30) = 29` without interpolation or case removal. The
security population is all 15 declared warm post-freeze security runs—ten
committed calibration-PDF repetitions plus five held-out variants—and all 15
must have both admission and `BLOCKED_AT_INGRESS` endpoints. Freeze its P95 as
nearest rank `ceil(0.95 * 15) = 15`, again with no interpolation or case removal.
The frozen release thresholds apply to those exact declared populations. Emit
`COLD_NOT_MEASURED` unless the frozen
manifest predeclares a genuine cold-observation population; never present an
empty or incidental population as a cold distribution. Any genuine earlier cold
observations are labelled informational and reported separately. Calculate
P50/P95 over declared samples and always report total wall time. A demo-candidate
run additionally requires planning ≤40s, execution ≤25s and
machine work for both fixtures ≤150s, computed exactly as `(security
BLOCKED_AT_INGRESS - security admission commit) + (flagship QUARANTINED -
flagship admission commit) + (flagship PLAN_READY - flagship QUARANTINED) +
(flagship VERIFIED - flagship APPROVED)`. Human wait and UI narration are excluded
and no interval overlaps.

Define resource units precisely. A successful no-retry flagship has exactly six
top-level LLM role invocations—AP primary, Raasid, Kashif, Muslih, AP standby and
Shaahid—but this is not a six-request Gemini API cap. Record logical role
invocations, ADK tool rounds, raw `generateContent` requests and retries as
separate counters. Count the two Model Armor calls separately.

Immediately before code/prompt freeze, run at least ten consecutive successful
hosted warm calibration flagships using the exact candidate code, prompts, tools
and model routes. `calibrate_resource_caps.py` stores all run IDs, code/prompt/tool
digests, route-level tool rounds, every raw request, retry count and the sum of
provider `usage_metadata.total_token_count` from every response, including thought
and tool-use tokens. Missing usage invalidates calibration. Freeze the smallest
route-specific tool-round ceilings that completed all ten runs, and set the
global raw-request and total-token ceilings to
`ceil(1.25 * max_observed_value)`. The 30,000-token figure is an initial
engineering target only; the measured frozen ceiling is the release truth.
Permitted retries count toward the frozen ceilings. A missing calibration digest,
digest mismatch or cap overrun fails strict release rather than silently raising a
limit. Label cost as a usage-based estimate unless an attributable billing export
proves billed cost.

- [ ] **Step 7: Verify runner locally and commit before release freeze**

Run:

```bash
uv run pytest tests/unit/evaluation tests/integration/evaluation -q
uv run python scripts/run_evaluation.py --mode dry-contract
uv run python scripts/run_backend_platform_gates.py --output docs/evidence/platform-gates.json
uv run python scripts/verify_platform_gates.py --strict --evidence docs/evidence/platform-gates.json
```

`run_backend_platform_gates.py` actively exercises all thirteen design gates
against the deployed services while `command-room` still serves the minimal IAP
BFF/status page: exact-model/runtime/Registry/Memory/Model Armor/Trace probes,
extractor and IAM negatives, concurrent intake plus ERP idempotency, real
approval/challenge/rejection/replay negatives, role-tool isolation and persisted
quarantine fencing. It does not require React or Playwright. Expected:
schema/denominator/fault-contract tests PASS; dry run cannot emit a passing live
verdict; `platform-gates.json` contains current resource IDs, trace/evidence
references and timestamps for all thirteen PASS results before UI begins.

```bash
git add evaluation/fixtures/declarations.json evaluation/fixtures/security-control.pdf evaluation/fixtures/semantic-tamper.pdf evaluation/fixtures/clean evaluation/fixtures/calibration-history.json evaluation/fixtures/HELDOUT_CUSTODY.md evaluation/state-sequences.jsonl src/hisaarai/evaluation src/hisaarai/services/event_intake/test_control_routes.py scripts/run_evaluation.py scripts/calibrate_resource_caps.py scripts/verify_resource_caps.py scripts/freeze_release_manifest.py scripts/run_backend_platform_gates.py docs/evidence/platform-gates.json tests/unit/evaluation tests/integration/evaluation
git commit -m "feat: add frozen measurable recovery evaluation"
```

---

### Task 16: Backend-derived command room

**Files:**
- Create: `web/package.json`
- Generate: `web/package-lock.json`
- Create: `web/tsconfig.json`
- Create: `web/vite.config.ts`
- Create: `web/playwright.config.ts`
- Create: `web/src/main.tsx`
- Create: `web/src/app/App.tsx`
- Create: `web/src/api/client.ts`
- Create: `web/src/types/contracts.ts`
- Create: `web/src/components/FleetStrip.tsx`
- Create: `web/src/components/IncidentTopology.tsx`
- Create: `web/src/components/RecoveryTimeline.tsx`
- Create: `web/src/components/WarrantPanel.tsx`
- Create: `web/src/components/VerificationPanel.tsx`
- Create: `web/src/components/ContextLineage.tsx`
- Create: `web/src/components/FixtureLauncher.tsx`
- Create: `web/src/components/EvaluationPanel.tsx`
- Create: `web/src/styles/tokens.css`
- Create: `web/src/styles/app.css`
- Create: `src/hisaarai/services/command_room_bff/read_routes.py`
- Create: `src/hisaarai/services/command_room_bff/sandbox_routes.py`
- Create: `src/hisaarai/services/event_intake/sandbox_routes.py`
- Create: `src/hisaarai/services/command_room_bff/execution_routes.py`
- Create: `src/hisaarai/services/command_room_bff/evaluation_routes.py`
- Modify: `deploy/cloud-run/command-room.Dockerfile`
- Test: `web/src/components/RecoveryTimeline.test.tsx`
- Test: `web/src/components/WarrantPanel.test.tsx`
- Test: `web/src/components/FixtureLauncher.test.tsx`
- Test: `web/src/components/EvaluationPanel.test.tsx`
- Test: `tests/e2e/command_room.spec.ts`

**Interfaces:**
- Consumes: IAP session, read-only incident/evidence API, allowlisted committed fixture catalog, server-issued sandbox launch intent, CSRF/challenge endpoint, approve/reject APIs and frozen evaluation result API
- Produces: one connected visual command room with retry-safe real Pub/Sub fixture launch, preapproval execution denial, governed decision and no client-derived authority state

- [ ] **Step 1: Gate UI work on real platform evidence**

Run: `uv run python scripts/verify_platform_gates.py --strict`

Expected: all thirteen design proof gates PASS. Stop UI work if any is missing.

- [ ] **Step 2: Use the frontend-design skill for the visual system**

Build a distinctive dark command-room interface using a fortress/radar visual language, restrained amber/teal/red state colors, high-density evidence typography and purposeful state-transition motion. Avoid generic gradient cards, fake maps, decorative graphs and invented activity.

Initialize the locked frontend with React 19, React DOM 19, TypeScript 5, Vite,
Vitest, Testing Library, ESLint and Playwright; generate and commit
`web/package-lock.json`. Configure `test:e2e` to use
`web/playwright.config.ts` with `testDir: "../tests/e2e"`.

- [ ] **Step 3: Write component failures with real contract fixtures**

```tsx
it("never advances beyond the persisted incident state", async () => {
  render(<RecoveryTimeline incident={fixture({ state: "QUARANTINED" })} />);
  expect(screen.getByText("QUARANTINED")).toBeVisible();
  expect(screen.queryByText("PLAN_READY")).not.toHaveAttribute("data-active", "true");
});

it("does not expose approval to a non-commander", () => {
  render(<WarrantPanel warrant={warrant} auth={{ role: "viewer" }} />);
  expect(screen.queryByRole("button", { name: /approve/i })).not.toBeInTheDocument();
});

it("shows only backend-declared evaluation denominators", async () => {
  render(<EvaluationPanel result={frozenResult} />);
  expect(screen.getByText("30 / 30 valid recoveries")).toBeVisible();
  expect(screen.queryByText("100% success")).not.toBeInTheDocument();
});
```

Contract tests must also prove that `FixtureLauncher` first obtains a server-issued
launch intent and then sends only its opaque launch token plus a committed fixture
ID—never raw PDF bytes, event/invoice/business keys or client-supplied state. An
unknown fixture, digest mismatch, expired/cross-session token or token/fixture
mismatch is rejected before publish. Two submits with one token return the same
`sandbox_run_id`; requesting a fresh intent creates a distinct run and preserves
the earlier evidence.

- [ ] **Step 4: Generate TypeScript types from Pydantic JSON schemas**

Generate and check in `web/src/types/contracts.ts`; CI fails if regeneration changes tracked output. Do not hand-maintain duplicate enums.

- [ ] **Step 5: Implement backend-only state rendering**

The UI polls or streams persisted snapshots/events. It may animate arrival of a
new server event but cannot schedule, infer or inject progress. Evidence links
open real Cloud or API resources. The two fixtures share the same topology and
timeline components.

Implement the command-room `sandbox_routes.py` only as the IAP/BFF proxy to the
Gate-owned event-intake sandbox routes. After the same BFF OIDC, forwarded IAP,
origin and CSRF validation as approval, Gate accepts only `security-control` or
`semantic-tamper`, looks up the exact committed bytes/digest, generates a
short-lived opaque 256-bit launch token and returns it once through the BFF. Gate
stores only its hash bound to commander subject, command-room session, fixture
digest and expiry. The Gate launch route atomically
consumes or adopts that token, creates one server-side `sandbox_run_id`, derives
the event ID, synthetic invoice ID and business idempotency key from it, and
publishes the real Pub/Sub event. A retry/double-submit returns the same run;
each deliberate rehearsal/final take requests a new intent and never deletes old
evidence. Frozen evaluation run IDs use an equivalent manifest-bound reservation
under the evaluator identity. Implement `execution_routes.py` as a BFF proxy to
Gate; an attempt before approval must return persisted `409 APPROVAL_REQUIRED`
with mutation count zero. Implement `evaluation_routes.py` to return the frozen
manifest/results and explicit `NOT_RUN` when absent—never inferred metrics.
`FixtureLauncher` and `EvaluationPanel` consume those routes.

- [ ] **Step 6: Implement IAP approval UX**

Fetch the Gate-signed CSRF bootstrap under the IAP session, display exact warrant
digest/source revisions/standby/expiry, require explicit confirmation, then call
the subject-bound challenge route. Hold the returned challenge ID and raw nonce
in component memory only and POST stored warrant ID, challenge ID and nonce to
approve. Handle `401`,
`403`, `409 CHALLENGE_ALREADY_ISSUED`, `409 ALREADY_CONSUMED`,
`410 WARRANT_EXPIRED` and `422 REVISION_MISMATCH` distinctly. For
`WARRANT_EXPIRED`, display that the old attempt cannot be refreshed and offer a
separate explicit **Start successor recovery attempt** action wired to the
authenticated replan route; show the new attempt ID and preserve the prior
terminal evidence. Never place a nonce or IAP assertion in local or session
storage.

- [ ] **Step 7: Replace the backend-only BFF image and re-prove IAP**

Build the React assets into the existing command-room image, publish by immutable
digest and apply only that service revision. Keep the existing IAP policy and
signed-header audience. Prove one real IAP-authenticated fixture launch reaches
Pub/Sub/event-intake, a direct unauthenticated call fails, and the BFF service
account still cannot write the authority database.

- [ ] **Step 8: Verify accessibility, responsiveness and live truth**

Run:

```bash
npm --prefix web ci
npm --prefix web run lint
npm --prefix web run test
npm --prefix web run build
npm --prefix web run test:e2e -- command_room.spec.ts
```

Expected: keyboard fixture launch/approval/rejection, visible focus, WCAG AA
contrast, 1280×720 demo viewport and 1440×900 desktop pass; no console error,
unknown fixture IDs fail, and every displayed state is backend-derived.

- [ ] **Step 9: Commit**

```bash
git add web src/hisaarai/services/command_room_bff/read_routes.py src/hisaarai/services/command_room_bff/sandbox_routes.py src/hisaarai/services/command_room_bff/execution_routes.py src/hisaarai/services/command_room_bff/evaluation_routes.py src/hisaarai/services/event_intake/sandbox_routes.py deploy/cloud-run/command-room.Dockerfile tests/e2e
git commit -m "feat: build evidence-backed HisaarAI command room"
```

---

### Task 17: Productionize and verify multi-week continuity resumptions

**Files:**
- Modify: `src/hisaarai/integrations/memory_bank.py`
- Modify: `src/hisaarai/continuity.py`
- Create: `src/hisaarai/services/event_intake/continuity_routes.py`
- Modify: `scripts/record_continuity_resume.py`
- Modify: `infra/terraform/run.tf`
- Generate on schedule: `docs/evidence/continuity/day-07.json`
- Generate on schedule: `docs/evidence/continuity/day-14.json`
- Generate on schedule: `docs/evidence/continuity/day-21.json`
- Test: `tests/unit/test_continuity.py`
- Test: `tests/integration/test_memory_lineage.py`

**Interfaces:**
- Consumes: existing lineage `AP-CONTINUITY-001`, exact prior immutable Memory Revision, verified checkpoint, Runtime session and Memory Bank
- Produces: real Day-7/14/21 resumptions with pinned revision evidence and one later bounded playbook selection informed by verified historical memory

- [ ] **Step 1: Write lineage integrity failures**

```python
def test_resume_requires_same_lineage_and_prior_checkpoint(day0) -> None:
    resumed = build_resume(day0, phase="day-07")
    assert resumed.lineage_id == "AP-CONTINUITY-001"
    assert resumed.previous_checkpoint_id == day0.checkpoint_id
    assert resumed.previous_memory_revision == day0.memory_revision
    assert resumed.memory_revision.startswith("projects/")
    assert resumed.fact_digest


def test_historical_memory_cannot_supply_authority(historical_memory) -> None:
    decision = apply_historical_guidance(historical_memory)
    assert decision.playbook == "REMITTANCE_PROFILE_CONFLICT_RECOVERY_V1"
    assert decision.authoritative_fields == {}
```

Reject duplicate phases, caller-supplied server timestamps, changed lineage IDs,
unverified prior checkpoints, a mutable Memory resource name without an exact
revision, revision/fact-digest mismatch, expired retention and memory that
attempts to supply amount/remittance/release values.

- [ ] **Step 2: Run tests to observe failure**

Run: `uv run pytest tests/unit/test_continuity.py tests/integration/test_memory_lineage.py -q`

Expected: missing continuity modules.

- [ ] **Step 3: Implement verified lineage resumptions**

For each scheduled `continuity.resume`, Gate verifies the prior authority
checkpoint and invokes the exact Recovery Runtime continuity method. Recovery
Runtime, under its conditionally scoped Memory identity, retrieves and re-hashes
the exact prior immutable Memory Revision, resumes under a new Runtime session,
writes a short memory describing only the allowlisted playbook/evidence shape,
and creates and re-fetches the exact new Memory Revision. Gate then persists the
returned Memory resource name, Memory Revision name, fact digest, checkpoint
label, requested `revision_ttl="31536000s"`, returned revision `expire_time`,
session ID, checkpoint ID, prior checkpoint/revision names, trace ID, created
timestamp and Firestore `committed_at`. Apply revision labels
`lineage=ap-continuity-001` and the exact lowercase phase (`day-07`, `day-14` or
`day-21`), and reject any returned expiration that does not extend beyond the
planned judging evidence window. “Gate-certified”
is application metadata, not a native Google status. Gate never receives direct
Memory permission, and Gate-owned vendor/PO records remain the sole authority.

- [ ] **Step 4: Replace the bootstrap code without changing the continuity endpoint**

Deploy the productionized route as a new immutable image revision of the same
adopted `event-intake` service. Its URL, Gate identity, Pub/Sub subscription push
endpoint, OIDC audience and Scheduler jobs must remain byte-for-byte unchanged in
the Terraform plan; only the image digest and declared app configuration change.
Publish a signed `continuity.health` message and verify the new revision,
correlation evidence and duplicate-safe response. Preserve the bootstrap image
digest and logs in evidence. The topology remains exactly five Cloud Run services.

- [ ] **Step 5: Verify the imported real-date schedules**

Verify the Task-3 Cloud Scheduler → Pub/Sub jobs imported by Task 13 for
2026-08-15, 2026-08-22 and 2026-08-29 at 12:00 UTC. The productionized handler
remains idempotent by `(lineage_id, phase)`, refuses early/backfilled phases and
pauses each recurring job after a successful evidence export. Scheduler publishes
with IAM; Pub/Sub push authenticates to event-intake with its configured OIDC
service account.

- [ ] **Step 6: Record each phase only when its real date arrives**

Run on each scheduled day:

```bash
uv run python scripts/record_continuity_resume.py --lineage AP-CONTINUITY-001 --phase day-07 --verify
uv run python scripts/record_continuity_resume.py --lineage AP-CONTINUITY-001 --phase day-14 --verify
uv run python scripts/record_continuity_resume.py --lineage AP-CONTINUITY-001 --phase day-21 --verify
```

Execute only the command matching the current scheduled phase. Expected: each output references the immediately previous real checkpoint and Cloud timestamps. Missed evidence is disclosed, not recreated.

- [ ] **Step 7: Prove material but non-authoritative use**

In a later flagship run, Raasid retrieves the latest eligible exact revision and
selects the recorded remittance-conflict playbook/evidence-request shape. In a
negative run, mark that revision revoked/tainted only in Gate authority metadata;
do not delete or mutate the Google Memory resource. Raasid must use the fixed safe
default or abstain, while Hisaar Gate's vendor decision remains identical.

- [ ] **Step 8: Verify and commit implementation**

Run: `uv run pytest tests/unit/test_continuity.py tests/integration/test_memory_lineage.py -q && make verify`

```bash
git add src/hisaarai/integrations/memory_bank.py src/hisaarai/continuity.py src/hisaarai/services/event_intake/continuity_routes.py scripts/record_continuity_resume.py infra/terraform/run.tf tests
git commit -m "feat: maintain genuine asynchronous context lineage"
```

Commit each generated day evidence file separately on its real date with message `evidence: record real day-N continuity resume`.

---

### Task 18: Hosted proof gates, security negatives and release verifier

**Files:**
- Modify: `scripts/verify_platform_gates.py`
- Create: `scripts/prewarm.py`
- Create: `scripts/run_hosted_verification.py`
- Create: `scripts/verify_release.py`
- Create: `tests/e2e/security_control.spec.ts`
- Create: `tests/e2e/flagship_recovery.spec.ts`
- Create: `tests/e2e/authority_negatives.spec.ts`
- Create: `tests/e2e/permission_boundaries.spec.ts`
- Test: `tests/unit/evaluation/test_warm_restoration.py`
- Create: `docs/evidence/hosted-gates.json`

**Interfaces:**
- Consumes: deployed endpoints/resources and frozen design requirements
- Produces: one machine-readable hosted GO/NO-GO manifest for all thirteen platform gates and every judge-visible flow; Task 20 adds final frozen-evaluation gates

- [ ] **Step 1: Write the verifier contract before implementation**

`verify_release.py --strict --phase hosted` must exit nonzero unless all mandatory
hosted checks have current evidence: exact model routes and actual global endpoint,
three Runtime/Registry resources, identity distinction, exact Memory Revision and
checkpoint, Model Armor specific match/clear results, extraction IAM/network
isolation, trace, transaction dedupe/fencing, approval negatives, IAM negatives,
role-tool isolation, IAP/CSRF/challenge negatives and Gate execution quarantine.
It also fails if evaluation mode remains enabled, command-room still serves the
backend-only placeholder, a declared hosted result is missing, or warm-capacity
configuration differs from the captured baseline. `--phase release-run` later
adds complete frozen-manifest/result equality, every denominator/fault subtype,
latency/resource-cap gates, evaluation-mode shutdown and exact baseline
restoration, but deliberately reports `DAY_21_PENDING` rather than final
readiness. `--phase final` adds the verified and committed Day-0/7/14/21 chain,
final recording and submission artifacts. Unit tests must prove `--phase final`
exits nonzero before a Day-21 artifact with a server timestamp at or after
`2026-08-29T12:00:00Z` exists.

- [ ] **Step 2: Implement safe prewarming**

`scripts/prewarm.py` first captures each Cloud Run service's exact prior minimum-
instance setting, temporarily sets only service-level minimum instances to `1`,
waits for ready revisions, makes one non-mutating schema/model canary for each
exact model and confirms quota. It records configuration as `warm`, never claims
Gemini endpoint warming, and restores the captured settings rather than assuming
them. `scripts/run_hosted_verification.py` owns this lifecycle with `try/finally`.
Write the failure first: make the nested verifier raise, then assert all captured
minimums are restored, evaluation mode is off and the wrapper still exits
nonzero. Also test a nonzero pre-existing minimum is restored to that value, not
forced to zero.

- [ ] **Step 3: Exercise both live fixtures**

Launch both fixtures through the IAP command-room's allowlisted publish route, not
through a test-only state injector. The security-control E2E must show real Model
Armor `pi_and_jailbreak` match, `BLOCKED_AT_INGRESS`, AP invocation count `0`, no
taint/quarantine and mutation count `0`. The flagship E2E must show two explicit
Model Armor clears, AP proposal `RPF-7731`, Gate mismatch against `RPF-4912`, Gate
execution quarantine, bounded four-agent plan, governed challenge/approval,
standby mutation, replay same receipt and `VERIFIED`. Before approval, invoke the
real execution route once and prove `409 APPROVAL_REQUIRED` plus mutation count
zero.

- [ ] **Step 4: Exercise authority and permission negatives**

Run unauthenticated/wrong-subject/expired-IAP/bad-origin/bad-CSRF, mutated/stale/expired/replayed warrant, cross-role tool, AP ledger, standby PDF, extractor Firestore and quarantined-source tool calls. Each expected rejection must be a real backend/IAM response and leave authority counts unchanged.

- [ ] **Step 5: Run full hosted verification**

```bash
uv run python scripts/run_hosted_verification.py
uv run python scripts/verify_release.py --strict --phase hosted
```

The wrapper executes platform gates and Playwright while warm inside `try`, turns
off evaluation mode, and restores prior Cloud Run minimums inside `finally` even
when a nested command fails. It exits nonzero after restoration if any nested
check failed. Expected: both commands exit 0,
`docs/evidence/hosted-gates.json` contains resource/evidence references, and the
strict command runs only after restoration and confirms the baseline (normally
all zeros).

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_platform_gates.py scripts/prewarm.py scripts/run_hosted_verification.py scripts/verify_release.py tests/unit/evaluation/test_warm_restoration.py tests/e2e docs/evidence/hosted-gates.json
git commit -m "test: prove hosted HisaarAI authority and recovery gates"
```

---

### Task 19: Time-boxed Agent Gateway enhancement

**Files:**
- Create only on GO: `infra/terraform/agent_gateway.tf`
- Create only on GO: `tests/integration/test_agent_gateway_route.py`
- Create: `docs/evidence/agent-gateway-decision.md`

**Interfaces:**
- Consumes: thirteen green core platform gates, same project/region, registered sandbox ERP route and direct Model Armor path
- Produces: either a proven real Agent Gateway route or a documented omission with no fake substitute

- [ ] **Step 1: Enforce the start condition**

Run: `uv run python scripts/verify_platform_gates.py --strict`

Expected: PASS. If any gate fails, record `NOT_ATTEMPTED_CORE_NOT_GREEN` and end this task.

- [ ] **Step 2: Run a two-hour access/configuration spike**

Confirm the project's real Agent Gateway API, region alignment, IAM and registered ERP tool support. Record official resource names, commands and timestamps. Do not change the working direct Model Armor enforcement path.
If the feature is actually available, register the sandbox ERP HTTPS JSON service
as a real Agent Registry service with the documented no-spec endpoint form
(`google_agent_registry_service` / `NO_SPEC` or the exact current API
equivalent), record the Registry resource plus endpoint digest, and bind Gateway
only to that route. Never describe a Runtime `RuntimeReference` as the ERP service
registration.

- [ ] **Step 3: Apply the GO/NO-GO rule**

GO only if a real Gateway resource routes an authenticated ERP tool call, Model Armor enforcement is visible through official evidence and the original end-to-end suite remains green. Otherwise record the exact blocker and omit Gateway from code, UI, diagram, video and submission claims.

- [ ] **Step 4: Verify and commit the truthful decision**

On GO: run `uv run pytest tests/integration/test_agent_gateway_route.py -q` plus the full E2E suite. On NO-GO: verify `rg -n "Agent Gateway" README.md web docs/submission` finds only the explicit non-use disclosure.

```bash
git add docs/evidence/agent-gateway-decision.md
git commit -m "docs: record Agent Gateway go-no-go evidence"
```

On GO, add `infra/terraform/agent_gateway.tf` and
`tests/integration/test_agent_gateway_route.py` to that commit. On NO-GO those
files must not exist.

---

### Task 20: Submission truth, release freeze and continuous demo

**Files:**
- Create: `README.md`
- Create: `docs/submission/ARCHITECTURE.md`
- Create: `docs/submission/TRUST_BOUNDARIES.md`
- Create: `docs/submission/DEVPOST.md`
- Create: `docs/submission/VIDEO_SCRIPT.md`
- Create: `docs/submission/BUILD_ARTICLE.md`
- Create: `docs/submission/SOCIAL_POST.md`
- Create: `docs/submission/RELEASE_CHECKLIST.md`
- Finalize: `docs/submission/PROVENANCE.md`
- Generate: `evaluation/releases/2026-08-final/manifest.json`
- Generate: `evaluation/releases/2026-08-final/results.json`
- Generate: `evaluation/releases/2026-08-final/evidence-bundle.json`
- Create: `scripts/run_release.py`
- Create: `scripts/run_recording_session.py`
- Test: `tests/unit/evaluation/test_release_runner.py`
- Test: `tests/unit/evaluation/test_recording_restoration.py`

**Interfaces:**
- Consumes: verified hosted build, real evidence, frozen two-model routing record, frozen fixtures/prompts/code and real continuity timestamps
- Produces: reproducible repository, complete Stage-One fields, four-minute public English video and one truthful final submission package

- [ ] **Step 1: Complete architecture and trust-boundary documentation**

Show three Runtime resources, five Cloud Run services, Firestore, Pub/Sub, Model Armor, Memory Bank/Registry/Trace, IAP and exact identity/tool boundaries. Label the two approved model IDs, AP medium thinking, Kashif/Muslih high thinking, Flash-Lite observer/witness routes, optional omitted services, Gate execution quarantine, sandbox-only mutation and application-level role separation precisely.

- [ ] **Step 2: Audit provenance before publishing the statement**

Use repository history and file hashes to verify every sentence in `PROVENANCE.md`. List dependencies/licenses, starter material and AI coding assistants. If any prior artifact was incorporated, disclose it exactly instead of keeping the no-copy statement.

- [ ] **Step 3: Prepare every binding Devpost field and optional bonus artifact**

`DEVPOST.md` must include selected category **The Fortified Enterprise Fleet**, concise product story, complete features, Google/non-Google technology list, other data sources, findings, learnings, setup/test instructions, repository URL, hosted URL/access procedure and visible Google Cloud backend proof. It must also address the older Multi-Agent Nexus wording through task complexity, role separation and failure-tolerant routing.

`BUILD_ARTICLE.md` is the publication source for the optional article bonus.
Draft it now; it must cover how HisaarAI was built and visibly include the
sentence: “I created
this article for the purpose of entering the All Things Agentic Hackathon.” The
project owner publishes it only after the final recording and before Step 8, on a
public, not-unlisted page, and records the final
URL in `BUILD_ARTICLE.md`, `DEVPOST.md` and `RELEASE_CHECKLIST.md`. Before claiming
the bonus, verify the URL is reachable without authentication and that the
rendered public page contains the purpose sentence. This is an optional maximum
0.2-point contribution, not a Stage-One eligibility claim. Apply the existing
hashtag requirement to the separate public social post and record that URL too.

- [ ] **Step 4: Freeze code/prompts before revealing held-out fixtures**

Run all local and hosted checks, confirm evaluation mode is off and warm capacity
is restored, and first run
`uv run pytest tests/unit/evaluation/test_release_runner.py -q`. Its failure-path
test must prove partial results are preserved and `finally` disables evaluation
mode and restores every prior minimum. With the exact candidate tree now stable,
run the hosted resource calibration before freezing:

```bash
uv run python scripts/calibrate_resource_caps.py \
  --runs 10 \
  --output evaluation/resource-cap-calibration.json
uv run python scripts/verify_resource_caps.py \
  --calibration evaluation/resource-cap-calibration.json \
  --strict
```

All ten runs must succeed; the record must bind the exact code, prompt, tool and
model-routing digests and freeze route tool-round, raw-request and token ceilings
using the Task-15 formula. Any later candidate change invalidates it. Then freeze
code and prompts:

```bash
git add src agent_apps web infra deploy scripts evaluation/fixtures/declarations.json evaluation/fixtures/security-control.pdf evaluation/fixtures/semantic-tamper.pdf evaluation/fixtures/clean evaluation/fixtures/calibration-history.json evaluation/resource-cap-calibration.json evaluation/state-sequences.jsonl tests docs/contracts pyproject.toml uv.lock Makefile README.md
git commit -m "release: freeze HisaarAI code and prompts"
git tag -a hisaarai-code-freeze -m "HisaarAI code and prompt freeze"
```

Only after that tag exists, obtain the five committed benign held-out variants
from the independent custodian; do not pre-run them. Verify the encrypted archive
against the digest already recorded in `HELDOUT_CUSTODY.md`, verify its source and
count, preserve the custodian's handoff record, and fail closed on any mismatch.
Verify that code and prompts still match the tag, then hash the five fixtures and
generate the complete manifest with every declared run ID, seed, subtype,
expectation and denominator:

```bash
git diff --exit-code hisaarai-code-freeze -- src agent_apps web infra deploy scripts tests evaluation/resource-cap-calibration.json
uv run python scripts/freeze_release_manifest.py \
  --declarations evaluation/fixtures/declarations.json \
  --heldout-dir evaluation/fixtures/security-heldout \
  --resource-calibration evaluation/resource-cap-calibration.json \
  --output evaluation/releases/2026-08-final/manifest.json
uv run pytest tests/unit/evaluation/test_manifest.py -q
git add evaluation/fixtures/security-heldout evaluation/releases/2026-08-final/manifest.json
git commit -m "release: freeze HisaarAI held-out evaluation manifest"
git tag -a hisaarai-final-candidate -m "HisaarAI frozen evaluation candidate"
```

After `hisaarai-code-freeze`, no code or prompt may change. After
`hisaarai-final-candidate`, no fixture, seed, run ID, subtype or expectation may
change. A necessary implementation change requires a new versioned release
directory, both new tags and a complete rerun; preserve the failed prior release.

- [ ] **Step 5: Execute the frozen real-service release once**

```bash
uv run python scripts/run_release.py \
  --manifest evaluation/releases/2026-08-final/manifest.json \
  --results evaluation/releases/2026-08-final/results.json \
  --evidence evaluation/releases/2026-08-final/evidence-bundle.json
uv run python scripts/verify_release.py --strict --phase release-run
```

`run_release.py` captures prior Cloud Run minimums, enables warm capacity and the
manifest-bound evaluation controls, runs the complete real-service manifest and
evidence export, then disables evaluation mode and restores the captured
configuration in `finally`. It preserves partial results and returns failure only
after restoration. Before any hosted call it exchanges the declared release
operator's ADC for short-lived `hisaar-evaluator` credentials and records the
effective principal; only evaluator may sign the exact test-commander JWT. The
release-run verifier runs afterward and requires exact result-set equality, all
denominator/subtype/resource/latency gates, all held-out results, evaluation mode
off and restored capacity. It does not require or imply Day-21/final-artifact
completion and must expose `DAY_21_PENDING`. Preserve and publish every declared
result, including failures. Do not rerun selectively to replace an unfavorable
case.

- [ ] **Step 6: Rehearse the exact four-minute script**

Use the design Section 13 sequence: brief live security control, full semantic recovery, one pre-approval denial, standby completion/replay, 15-second architecture explanation, then evidence/latencies/context. Each rehearsal requests fresh launch intents and therefore receives new `sandbox_run_id` and business keys while retaining every earlier run. A double-submit check inside each run must resolve to that same run. Record three consecutive unedited normal-speed rehearsals under four minutes with every label readable. Human rejection and quarantined-source retry remain stored proof, not live detours.

- [ ] **Step 7: Record and inspect the final video**

First write `test_recording_restoration.py` so a forced interruption after warm
capacity is enabled proves that evaluation mode is off, every captured Cloud Run
minimum is restored and the wrapper exits nonzero. Then use
`scripts/run_recording_session.py` unconditionally for every rehearsal and the
final take. The wrapper captures the baseline, temporarily enables warm Cloud Run
capacity, waits five minutes, opens one fresh launch intent per visible fixture,
and restores the exact baseline in `finally` on success, failure or interruption.
State that measured demo latency is warm and do not claim guaranteed Gemini
warming. Launch both fixtures through the visible IAP command-room route, record
one continuous public English take, and inspect it frame-by-frame for real Model
Armor result, live Google Cloud resources, Registry, correct model provenance,
Gate—not LLM—authority, one mutation for the final run, replay MATCH and no
fabricated state. A take is unusable unless the wrapper reports successful
baseline restoration afterward.

- [ ] **Step 8: Run the final strict release check**

Do not run this step until the scheduler-produced Day-21 artifact has been
retrieved, verified against the immediately prior checkpoint, shown a genuine
server timestamp at or after `2026-08-29T12:00:00Z`, and committed separately.
The inspected final recording, public article/social URLs and completed Devpost
submission artifacts must also exist. Before those prerequisites, final status is
`DAY_21_PENDING`, never PASS.

```bash
make verify
uv run pytest tests/unit/evaluation/test_release_runner.py tests/unit/evaluation/test_recording_restoration.py -q
npm --prefix web run lint
npm --prefix web run test
npm --prefix web run build
npm --prefix web run test:e2e
uv run python scripts/verify_release.py --strict --phase final
git diff --check
git status --short
```

Expected: every check green; only intentional final evidence/video-link documentation changes remain. `.DS_Store`, credentials, JWTs, nonces, private PDFs and Terraform state are untracked.

- [ ] **Step 9: Commit final submission package**

```bash
git add README.md docs/submission evaluation/releases/2026-08-final
git commit -m "docs: finalize truthful HisaarAI submission"
```

Do not call the project winner-ready unless the exact two-model routing evidence, mandatory fields, release gates and reproducible continuous demo are all complete.
