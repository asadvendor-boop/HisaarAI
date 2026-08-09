# HisaarAI Judge-Readiness Repair Design

**Date:** 2026-08-09  
**Status:** Approved by the user on 2026-08-09  
**Scope rule:** Repair judge-visible truth, resilience and scoring clarity only.

## Outcome

HisaarAI must open with one evidence-backed transformation that a finance judge
can repeat after thirty seconds:

> A compromised AP agent proposed an attacker destination for a PKR 4.275M
> sandbox invoice. HisaarAI quarantined it before any receipt, obtained one
> accountable decision, and completed one verified receipt to the trusted
> destination.

The command room may display measured timings only from the loaded incident's
persisted state history and must label them as one observed hosted run (`n=1`).
It must never imply customer deployment, generalized performance or real-money
movement.

## Public-truth repairs

1. Recovery agents receive `amount_display` in major currency units instead of
   raw `amount_minor`; warrant and receipt authority continue using integer minor
   units. Agent narration must not be able to relabel minor units as currency.
2. A Model Armor terminal incident with no proposal or trusted vendor displays
   `NOT REACHED`, not fallback fingerprints or a fabricated mismatch.
3. `BLOCKED` is a distinct terminal state in the state rail and never aliases
   `QUARANTINED`.
4. Shaahid is `COMPLETE` when a `VERIFIED` incident already contains the witness
   summary and deterministic verdict.
5. Public proof links are available from the unsigned-in landing state.

## Governed-action repairs

Approval remains a single authenticated decision. The approval endpoint becomes
idempotently resumable: an exact retry by the same commander with the same
warrant digest republishes the same stable execution event while the incident is
`APPROVED`; `COMPLETED` or `VERIFIED` returns the existing terminal result
without another mutation. Wrong identity or digest still fails closed.

The commander UI exposes rejection while approval is pending. After verification
it exposes an idempotency proof action that calls the existing deterministic
replay path and must return the same receipt identifier. The UI shows
`APPROVAL_REQUIRED` while execution is locked; it does not manufacture a denial
event that did not occur.

## Judge-facing compression

Add a compact `BEFORE / CONTROL / AFTER` strip above the detailed panels. Every
value comes from the loaded incident:

- Before: proposed destination and amount at risk.
- Control: terminal screening block or semantic quarantine; zero unsafe receipt.
- After: trusted executed destination, one receipt and deterministic `MATCH`.

The primary buyer is named as an Accounts Payable Operations leader. Agent
summaries remain evidence, but the first sentence is visually prioritized and
long identifiers do not dominate the four-minute recording.

## Claim calibration and submission

- Public materials claim two callable ADK Agent Runtime resources and, after the
  2026-08-09 official live readback, Agent Registry discovery of exactly those
  two HisaarAI Runtime agents. Registry is catalog proof, not execution authority.
- “Tool boundaries” becomes “typed input and authority boundaries” because the
  fleet is routed through bounded payloads rather than agent-callable tool APIs.
- Devpost explicitly names synthetic PDF fixtures, the Firestore vendor master
  and sandbox ledger as data sources, plus the main implementation learning.
- README contains a complete environment matrix, a no-cloud product-check path
  and a static architecture image.
- No GitHub Actions, SHA manifest, bulk evaluation or new infrastructure layer is
  added. Lockfiles remain for reproducible installation only.

## Acceptance

The repair is ready for recording only after:

1. focused regressions and all eight business invariants pass;
2. the Python suite and production web build pass;
3. a fresh deployed injection control shows `BLOCKED`, zero Gemini and no fake
   authority comparison;
4. a fresh deployed semantic incident shows the correct PKR amount, one exact
   approval, one trusted receipt, replay `MATCH`, Shaahid `COMPLETE` and final
   `VERIFIED`;
5. a fresh hosted clean control completes normally;
6. the public proof links and final Devpost copy match those observed behaviors.

