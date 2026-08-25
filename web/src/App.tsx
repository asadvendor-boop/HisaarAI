import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type IncidentState =
  | "DETECTED"
  | "QUARANTINED"
  | "INVESTIGATING"
  | "PLAN_READY"
  | "AWAITING_APPROVAL"
  | "APPROVED"
  | "COMPLETED"
  | "VERIFIED"
  | "BLOCKED";

type Finding = {
  agent: string;
  summary: string;
  actual_model: string;
  thinking_level: string;
};

type Warrant = {
  digest: string;
  bank_fingerprint: string;
  expires_at: string;
  trusted_vendor_version: number;
  continuity_revision_name: string;
};

type Incident = {
  incident_id: string;
  invoice_id: string;
  trace_id: string;
  state: IncidentState;
  reason: string | null;
  proposal: {
    amount_minor: number;
    currency: string;
    bank_fingerprint: string;
    actual_model: string;
    thinking_level: string;
  } | null;
  trusted_vendor: {
    display_name: string;
    bank_fingerprint: string;
    version: number;
  } | null;
  findings: Finding[];
  warrant: Warrant | null;
  verification: string | null;
  witness_summary: string | null;
  screening_decision: string | null;
  gemini_invocations: number;
  state_history: { state: IncidentState; at: string; reason: string | null }[];
};

type Receipt = {
  receipt_id: string;
  bank_fingerprint: string;
  executor_identity: string;
  reasoning_runtime_identity: string | null;
  created_at: string;
};

type IncidentResponse = { incident: Incident; receipt: Receipt | null };

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (element: HTMLElement, config: Record<string, unknown>) => void;
        };
      };
    };
  }
}

const agents = [
  ["Protected AP", "Invoice proposal", "Gemini 3.6 Flash", "MEDIUM"],
  ["Raasid", "Observer", "Gemini 3.5 Flash-Lite", "DEFAULT"],
  ["Kashif", "Investigator", "Gemini 3.6 Flash", "HIGH"],
  ["Muslih", "Recovery planner", "Gemini 3.6 Flash", "HIGH"],
  ["Clean AP", "Standby validator", "Gemini 3.6 Flash", "MEDIUM"],
  ["Shaahid", "Witness", "Gemini 3.5 Flash-Lite", "DEFAULT"],
] as const;

const steps: IncidentState[] = [
  "DETECTED",
  "QUARANTINED",
  "INVESTIGATING",
  "PLAN_READY",
  "AWAITING_APPROVAL",
  "APPROVED",
  "COMPLETED",
  "VERIFIED",
];

const publicProofs = [
  ["VERIFIED RECOVERY", "inc-invoice-1f8fa7d20b0e49b2"],
  ["BLOCK BEFORE GEMINI", "inc-invoice-5d86da12456b4796"],
  ["CLEAN CONTROL", "inc-invoice-473fbd809fca4195"],
] as const;

function stateIndex(state?: IncidentState) {
  if (!state) return -1;
  if (state === "BLOCKED") return 1;
  return steps.indexOf(state);
}

function agentStatus(index: number, incident: Incident | null, receipt: Receipt | null) {
  if (!incident) return "STANDBY";
  const cleanPath = !!incident.proposal
    && !!incident.trusted_vendor
    && incident.proposal.bank_fingerprint === incident.trusted_vendor.bank_fingerprint
    && !incident.state_history.some((event) => event.state === "QUARANTINED")
    && incident.findings.length === 0;
  if (cleanPath) {
    if (index === 0) return "COMPLETE";
    if (index >= 1 && index <= 3) return "NOT NEEDED";
    if (index === 4) {
      if (receipt) return "COMPLETE";
      return incident.state === "APPROVED" || incident.state === "COMPLETED"
        ? "ACTIVE"
        : "CLEAN / LOCKED";
    }
    if (incident.witness_summary) return "COMPLETE";
    return incident.state === "COMPLETED" ? "ACTIVE" : "STANDBY";
  }
  if (incident.state === "BLOCKED") {
    if (index === 0) {
      if (incident.reason === "PROTECTED_AP_FAILED") return "FAILED";
      return incident.proposal ? "COMPLETE" : "WITHHELD";
    }
    if (index >= 1 && index <= 3) {
      return incident.findings.some((finding) => finding.agent === agents[index][0])
        ? "COMPLETE"
        : "WITHHELD";
    }
    if (index === 4) {
      if (incident.reason === "STANDBY_OUTPUT_DISAGREEMENT") return "FAILED";
      return receipt ? "COMPLETE" : "ISOLATED";
    }
    if (incident.reason?.startsWith("WITNESS_")) return "FAILED";
    return incident.witness_summary ? "COMPLETE" : "WITHHELD";
  }
  const current = stateIndex(incident.state);
  const thresholds = [0, 2, 2, 3, 5, 6];
  if (current < thresholds[index]) return index === 4 ? "ISOLATED" : "STANDBY";
  if (index === 4 && current < 5) return "CLEAN / LOCKED";
  return current === thresholds[index] ? "ACTIVE" : "COMPLETE";
}

function elapsedLabel(start?: string, end?: string) {
  if (!start || !end) return null;
  const elapsed = new Date(end).getTime() - new Date(start).getTime();
  if (!Number.isFinite(elapsed) || elapsed < 0) return null;
  if (elapsed < 1000) return `${elapsed} MS`;
  if (elapsed < 10000) return `${(elapsed / 1000).toFixed(2)} SEC`;
  return `${(elapsed / 1000).toFixed(1)} SEC`;
}

export function phaseTimingLabels(history: Incident["state_history"]) {
  const at = (state: IncidentState) => history.find((item) => item.state === state)?.at;
  const detected = at("DETECTED");
  const awaitingApproval = at("AWAITING_APPROVAL");
  const approved = at("APPROVED");
  const verified = at("VERIFIED");
  return {
    quarantine: elapsedLabel(detected, at("QUARANTINED")),
    automatedPlanning: elapsedLabel(detected, awaitingApproval),
    humanReview: elapsedLabel(awaitingApproval, approved),
    approvedExecution: elapsedLabel(approved, verified),
    total: elapsedLabel(detected, verified),
  };
}

export function missingTimelineStepLabel(
  step: IncidentState,
  cleanTrustedPath: boolean,
) {
  if (
    cleanTrustedPath
    && (step === "QUARANTINED" || step === "INVESTIGATING")
  ) {
    return "NOT NEEDED";
  }
  return "PENDING";
}

export function modelArmorLabel(decision: string | null, blocked: boolean) {
  if (blocked && decision === "MATCH") return "INJECTION MATCH / BLOCKED";
  return decision ?? "AWAITING INPUT";
}

function firstSentence(summary: string) {
  const match = summary.match(/^.*?[.!?](?:\s|$)/);
  const lead = match?.[0] ?? summary;
  return [lead, summary.slice(lead.length)] as const;
}

function shortHash(value?: string | null, length = 16) {
  return value ? `${value.slice(0, length)}…` : "—";
}

const sharedIncidentId = new URLSearchParams(window.location.search).get("incident") ?? "";

function App() {
  const [token, setToken] = useState("");
  const [incidentId, setIncidentId] = useState(sharedIncidentId);
  const [data, setData] = useState<IncidentResponse | null>(null);
  const [continuity, setContinuity] = useState<Record<string, unknown>>({});
  const [busy, setBusy] = useState("");
  const [replayEvidence, setReplayEvidence] = useState<{ receiptId: string; verdict: string } | null>(null);
  const [notice, setNotice] = useState(
    sharedIncidentId
      ? "Loading read-only hosted evidence. Commander sign-in is required only for new actions."
      : "Sign in as Incident Commander to begin.",
  );
  const signInRef = useRef<HTMLDivElement>(null);
  const pendingLaunchRef = useRef(false);
  const refreshSequenceRef = useRef(0);

  const api = useCallback(
    async (url: string, init: RequestInit = {}) => {
      const headers = new Headers(init.headers);
      if (token) headers.set("Authorization", `Bearer ${token}`);
      if (init.body) headers.set("Content-Type", "application/json");
      const response = await fetch(url, { ...init, headers });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || `Request failed: ${response.status}`);
      return body;
    },
    [token],
  );

  useEffect(() => {
    fetch("/api/config")
      .then((response) => response.json())
      .then((config) => {
        const render = () => {
          if (!window.google || !signInRef.current) return false;
          window.google.accounts.id.initialize({
            client_id: config.google_oauth_client_id,
            callback: (credential: { credential: string }) => {
              setToken(credential.credential);
              fetch("/api/identity", {
                headers: { Authorization: `Bearer ${credential.credential}` },
              })
                .then((response) => response.json())
                .then((identity) => setNotice(`Google identity verified: ${identity.email ?? identity.subject}`))
                .catch(() => setNotice("Google identity received; backend verification is pending."));
            },
          });
          window.google.accounts.id.renderButton(signInRef.current, {
            type: "standard",
            theme: "filled_black",
            size: "large",
            shape: "rectangular",
            text: "signin_with",
          });
          return true;
        };
        if (!render()) {
          const timer = window.setInterval(() => render() && window.clearInterval(timer), 250);
          window.setTimeout(() => window.clearInterval(timer), 8000);
        }
      })
      .catch(() => setNotice("Commander sign-in configuration is unavailable."));
    fetch("/api/continuity")
      .then((response) => response.json())
      .then(setContinuity)
      .catch(() => undefined);
  }, []);

  const refresh = useCallback(async () => {
    if (!incidentId) return;
    const requestSequence = ++refreshSequenceRef.current;
    try {
      const nextData = await api(`/api/incidents/${incidentId}`);
      if (requestSequence !== refreshSequenceRef.current) return;
      const wasPendingLaunch = pendingLaunchRef.current;
      pendingLaunchRef.current = false;
      setData(nextData);
      if (wasPendingLaunch) {
        if (nextData.incident.state !== "BLOCKED") {
          setNotice("Authenticated event delivered. Hisaar Gate is live.");
        } else if (
          nextData.incident.reason === "MODEL_ARMOR_MATCH"
          && nextData.incident.screening_decision === "MATCH"
        ) {
          setNotice("Model Armor matched the injection and blocked it before Gemini.");
        } else if (nextData.incident.reason === "SCREENING_UNAVAILABLE") {
          setNotice("Screening was unavailable. Hisaar Gate failed closed before Gemini.");
        } else {
          setNotice(`Hisaar Gate failed closed: ${nextData.incident.reason?.replaceAll("_", " ") ?? "BLOCK REASON UNAVAILABLE"}.`);
        }
      } else if (sharedIncidentId) {
        setNotice("Read-only hosted evidence loaded. Commander sign-in is required only for new actions.");
      }
    } catch (error) {
      if (requestSequence !== refreshSequenceRef.current) return;
      if (
        error instanceof Error
        && error.message === "Incident not found"
        && pendingLaunchRef.current
      ) {
        setNotice("Event accepted. Waiting for authenticated Pub/Sub delivery.");
        return;
      }
      setNotice(error instanceof Error ? error.message : "Incident read failed");
    }
  }, [api, incidentId]);

  useEffect(() => {
    if (!incidentId) return;
    refresh();
    const timer = window.setInterval(refresh, 1600);
    return () => window.clearInterval(timer);
  }, [incidentId, refresh]);

  useEffect(() => setReplayEvidence(null), [incidentId]);

  const launch = async (fixture = "semantic-tamper") => {
    setBusy(fixture);
    setData(null);
    try {
      const result = await api("/api/commander/launch", {
        method: "POST",
        body: JSON.stringify({ fixture }),
      });
      pendingLaunchRef.current = true;
      setIncidentId(result.incident_id);
      setNotice(
        fixture === "semantic-tamper"
          ? "Invoice event published. Watching the protected path."
          : fixture === "injection-control"
            ? "Security control published. Watching Model Armor."
            : "Clean invoice published. Watching the normal governed path.",
      );
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Launch failed");
    } finally {
      setBusy("");
    }
  };

  const approve = async () => {
    if (!data?.incident.warrant) return;
    setBusy("approve");
    try {
      await api(`/api/commander/incidents/${data.incident.incident_id}/approve`, {
        method: "POST",
        body: JSON.stringify({ warrant_digest: data.incident.warrant.digest }),
      });
      setNotice("Exact warrant approved. Clean standby execution released.");
      await refresh();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Approval failed");
    } finally {
      setBusy("");
    }
  };

  const reject = async () => {
    if (!data?.incident.warrant) return;
    setBusy("reject");
    try {
      await api(`/api/commander/incidents/${data.incident.incident_id}/reject`, {
        method: "POST",
        body: JSON.stringify({ rationale: "Commander rejected this recovery warrant." }),
      });
      setNotice("Recovery warrant rejected. Execution remains blocked.");
      await refresh();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Rejection failed");
    } finally {
      setBusy("");
    }
  };

  const replay = async () => {
    if (!data?.receipt || data.incident.state !== "VERIFIED") return;
    setBusy("replay");
    try {
      const result = await api(`/api/incidents/${data.incident.incident_id}/replay`);
      if (result.replay !== "MATCH" || result.receipt_id !== data.receipt.receipt_id) {
        throw new Error("Replay did not return the bound receipt.");
      }
      setReplayEvidence({ receiptId: result.receipt_id, verdict: result.replay });
      setNotice(`One-receipt replay matched ${result.receipt_id}.`);
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Replay failed");
    } finally {
      setBusy("");
    }
  };

  const incident = data?.incident ?? null;
  const amount = useMemo(() => {
    if (!incident?.proposal) {
      if (incident?.reason === "MODEL_ARMOR_MATCH") return "BLOCKED PRE-GEMINI";
      if (incident?.reason === "SCREENING_UNAVAILABLE") return "SCREENING FAILED CLOSED";
      return sharedIncidentId && !data ? "LOADING PROOF…" : "READY";
    }
    return new Intl.NumberFormat("en-PK", {
      style: "currency",
      currency: incident.proposal.currency,
      maximumFractionDigits: 0,
    }).format(incident.proposal.amount_minor / 100);
  }, [incident]);
  const timelineSteps = useMemo(() => {
    if (incident?.state !== "BLOCKED") return steps;
    return incident.state_history.reduce<IncidentState[]>((observed, item) => (
      observed.includes(item.state) ? observed : [...observed, item.state]
    ), []);
  }, [incident]);
  const observedStates = useMemo(
    () => new Set(incident?.state_history.map((item) => item.state) ?? []),
    [incident],
  );
  const detectedAt = incident?.state_history.find((item) => item.state === "DETECTED")?.at;
  const quarantinedAt = incident?.state_history.find((item) => item.state === "QUARANTINED")?.at;
  const phaseTiming = phaseTimingLabels(incident?.state_history ?? []);
  const modelArmorBlock = incident?.state === "BLOCKED"
    && incident.reason === "MODEL_ARMOR_MATCH"
    && incident.screening_decision === "MATCH"
    && incident.gemini_invocations === 0
    && !incident.proposal
    && !data?.receipt;
  const screeningUnavailable = incident?.state === "BLOCKED"
    && incident.reason === "SCREENING_UNAVAILABLE"
    && incident.screening_decision === "UNAVAILABLE"
    && incident.gemini_invocations === 0
    && !incident.proposal
    && !data?.receipt;
  const cleanTrustedPath = !!incident?.proposal
    && !!incident.trusted_vendor
    && incident.screening_decision === "CLEAR"
    && incident.proposal.bank_fingerprint === incident.trusted_vendor.bank_fingerprint
    && !quarantinedAt;
  const trustedExecution = incident?.state === "VERIFIED"
    && incident.verification === "MATCH"
    && !!data?.receipt
    && data.receipt.bank_fingerprint === incident.trusted_vendor?.bank_fingerprint;

  return (
    <div className="shell">
      <div className="grain" aria-hidden="true" />
      <header className="topbar">
        <div className="brand"><span className="brand-mark">H</span><strong>HISAAR<span>AI</span></strong></div>
        <div className="system-strip">
          <span><i className="pulse" /> GOOGLE CLOUD / LIVE</span>
          <span>FORTIFIED ENTERPRISE FLEET</span>
          <span className="clock">UTC+05 / KARACHI</span>
        </div>
        <div className="signin" ref={signInRef} aria-label="Google commander sign in" />
      </header>

      <main id="main">
        <section className={`hero bastion ${sharedIncidentId ? "proof-hero" : ""}`}>
          <div className="hero-copy">
            <p className="buyer">FOR ACCOUNTS PAYABLE OPERATIONS</p>
            <p className="eyebrow">GOVERNED MULTI-AGENT RECOVERY / 01</p>
            <h1>The agent was compromised.<br /><em>The payment was not.</em></h1>
            <p className="lede">HisaarAI quarantines a poisoned workflow, reconstructs clean context, obtains one human decision, and safely finishes the work.</p>
            <div className="hero-actions">
              {token ? (
                <>
                  <button className="primary" onClick={() => launch()} disabled={!!busy}>
                    <span>{busy === "semantic-tamper" ? "PUBLISHING…" : "RUN FLAGSHIP INCIDENT"}</span>
                    <b>↗</b>
                  </button>
                  <button className="secondary" onClick={() => launch("injection-control")} disabled={!!busy}>
                    TEST MODEL ARMOR
                  </button>
                  <button className="secondary" onClick={() => launch("clean-control")} disabled={!!busy}>
                    {busy === "clean-control" ? "PUBLISHING…" : "RUN CLEAN CONTROL"}
                  </button>
                </>
              ) : (
                <a className="primary proof-cta" href={`/?incident=${publicProofs[0][1]}`}>
                  <span>VIEW VERIFIED RECOVERY</span><b>↗</b>
                </a>
              )}
            </div>
            <p className="notice" aria-live="polite"><span>COMMAND</span> {notice}</p>
            {!token && (
              <nav className="public-proof-links" aria-label="Public read-only proof">
                <span>NO SIGN-IN REQUIRED</span>
                {publicProofs.map(([label, proofId]) => (
                  <a href={`/?incident=${proofId}`} key={proofId}>{label} ↗</a>
                ))}
              </nav>
            )}
          </div>
          <div className="risk-dial" aria-label={`Amount at risk ${amount}`}>
            <div className="dial-ring"><span>PROTECTED</span><strong>{amount}</strong><small>AMOUNT AT RISK</small></div>
            <div className={`state-beacon state-${incident?.state ?? "READY"}`}>
              <i /> {incident?.state ?? "READY"}
            </div>
          </div>
        </section>

        <section className="outcome-strip" aria-label="Incident before, control and after outcome">
          <article>
            <span>BEFORE</span>
            <strong>{incident?.proposal
              ? `${incident.proposal.bank_fingerprint} / ${amount}`
              : modelArmorBlock
                ? "NO PROPOSAL — BLOCKED PRE-GEMINI"
                : screeningUnavailable
                  ? "NO PROPOSAL — SCREENING FAILED CLOSED"
                  : sharedIncidentId && !data
                    ? "LOADING PROOF…"
                    : "NO PROPOSAL"}</strong>
            <p>{incident?.proposal
              ? "Persisted proposed destination and amount."
              : modelArmorBlock
                ? "Model Armor blocked the exact model input before inference."
                : "Awaiting persisted incident evidence."}</p>
          </article>
          <article className="control-cell">
            <span>HISAAR CONTROL</span>
            <strong>{modelArmorBlock
              ? "BLOCKED BEFORE GEMINI"
              : screeningUnavailable
                ? "SCREENING_UNAVAILABLE / FAIL CLOSED"
                : quarantinedAt
                  ? "QUARANTINED BEFORE UNSAFE RECEIPT"
                  : cleanTrustedPath
                    ? "TRUSTED SOURCE MATCH / GOVERNED APPROVAL"
                    : "CONTROL NOT REACHED"}</strong>
            <p>{modelArmorBlock || screeningUnavailable
              ? `${incident.gemini_invocations} GEMINI CALLS / ${data?.receipt ? 1 : 0} MUTATIONS`
              : phaseTiming.quarantine
                ? `QUARANTINE ${phaseTiming.quarantine}${phaseTiming.automatedPlanning ? ` / PLAN READY ${phaseTiming.automatedPlanning}` : ""}`
                : cleanTrustedPath
                  ? "MODEL ARMOR CLEAR / NO QUARANTINE REQUIRED"
                  : "No observed control timing yet."}</p>
            {(modelArmorBlock || screeningUnavailable || phaseTiming.quarantine || cleanTrustedPath) && <small>OBSERVED RUN / n=1</small>}
          </article>
          <article className={trustedExecution ? "after-cell verified" : "after-cell"}>
            <span>AFTER</span>
            <strong>{trustedExecution
              ? `${data.receipt!.bank_fingerprint} / ONE RECEIPT`
              : incident?.state === "BLOCKED" && !data?.receipt
                ? "WORKFLOW SAFELY STOPPED"
                : "OUTCOME NOT REACHED"}</strong>
            <p>{trustedExecution
              ? `MATCH${phaseTiming.approvedExecution ? ` / EXECUTION ${phaseTiming.approvedExecution}` : ""}`
              : incident?.state === "BLOCKED" && !data?.receipt
                ? "NO RECEIPT / NO MUTATION"
                : "Awaiting persisted receipt and verification."}</p>
            {trustedExecution
              ? <small>HUMAN REVIEW {phaseTiming.humanReview ?? "—"} / TOTAL {phaseTiming.total ?? "—"} / OBSERVED RUN n=1</small>
              : (modelArmorBlock || screeningUnavailable) && <small>OBSERVED RUN / n=1</small>}
          </article>
        </section>

        <section className="agent-rail" aria-label="Agent fleet">
          {agents.map(([name, role, model, thinking], index) => {
            const status = agentStatus(index, incident, data?.receipt ?? null);
            return (
              <article className={`agent-card ${status === "ACTIVE" ? "active" : ""}`} key={name}>
                <div className="agent-index">0{index + 1}</div>
                <div><h2>{name}</h2><p>{role}</p></div>
                <div className="agent-meta"><span>{model}</span><span>{thinking}</span></div>
                <div className="agent-status"><i />{status}</div>
              </article>
            );
          })}
        </section>

        <section className="command-grid">
          <article className="panel comparison bastion">
            <header><p>AUTHORITY CHECK</p><h2>Invoice vs. trusted source</h2></header>
            {incident?.proposal && incident.trusted_vendor ? (
              <>
                <div className="comparison-row unsafe">
                  <span>INVOICE DESTINATION</span>
                  <code>{incident.proposal.bank_fingerprint}</code>
                  <b>{incident.proposal.bank_fingerprint === incident.trusted_vendor.bank_fingerprint ? "MATCH" : "MISMATCH"}</b>
                </div>
                <div className="comparison-row trusted">
                  <span>VENDOR MASTER v{incident.trusted_vendor.version}</span>
                  <code>{incident.trusted_vendor.bank_fingerprint}</code>
                  <b>TRUSTED</b>
                </div>
              </>
            ) : (
              <div className="authority-empty">
                <b>NOT REACHED</b><span>NO PROPOSAL</span>
                <p>Authority comparison waits for persisted proposal and trusted-vendor evidence.</p>
              </div>
            )}
            <div className="armor-line">
              <span>MODEL ARMOR</span>
              <div><i className={incident?.screening_decision === "CLEAR" ? "clear" : ""} /></div>
              <strong>{modelArmorLabel(incident?.screening_decision ?? null, modelArmorBlock)}</strong>
            </div>
          </article>

          <article className="panel timeline-panel">
            <header><p>LIVE RECOVERY</p><h2>Governed state rail</h2></header>
            <ol className="timeline">
              {timelineSteps.map((step) => {
                const event = incident?.state_history.find((item) => item.state === step);
                return (
                <li className={incident?.state === step ? "current" : observedStates.has(step) ? "done" : ""} key={step}>
                  <i /><span>{step.replaceAll("_", " ")}</span><small>{event ? new Date(event.at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", second: "2-digit"}) : missingTimelineStepLabel(step, cleanTrustedPath)}</small>
                </li>
                );
              })}
            </ol>
          </article>

          <article className="panel warrant-panel bastion">
            <header><p>HUMAN BOUNDARY</p><h2>Recovery warrant</h2></header>
            {incident?.warrant ? (
              <>
                {incident.state === "AWAITING_APPROVAL" && <div className="execution-gate">EXECUTION GATE: <strong>APPROVAL_REQUIRED</strong></div>}
                {incident.state === "APPROVED" && <div className="execution-gate">EXECUTION GATE: <strong>PUBLISH_RETRY_AVAILABLE</strong></div>}
                <dl>
                  <div><dt>Correction</dt><dd>Trusted vendor master v{incident.warrant.trusted_vendor_version}</dd></div>
                  <div><dt>Destination</dt><dd><code>{incident.warrant.bank_fingerprint}</code></dd></div>
                  <div><dt>Warrant digest</dt><dd><code>{shortHash(incident.warrant.digest, 20)}</code></dd></div>
                  <div><dt>Memory revision</dt><dd><code>{shortHash(incident.warrant.continuity_revision_name.split("/").at(-1))}</code></dd></div>
                  <div><dt>Expires</dt><dd>{new Date(incident.warrant.expires_at).toLocaleTimeString()}</dd></div>
                </dl>
                <div className="approval-actions">
                  <button className="approve" onClick={approve} disabled={!token || !["AWAITING_APPROVAL", "APPROVED"].includes(incident.state) || !!busy}>
                    {busy === "approve"
                      ? "VERIFYING IDENTITY…"
                      : incident.state === "APPROVED"
                        ? "RETRY EXECUTION PUBLISH"
                        : "APPROVE EXACT WARRANT"}
                  </button>
                  {incident.state === "AWAITING_APPROVAL" && (
                    <button className="reject" onClick={reject} disabled={!token || !!busy}>
                      {busy === "reject" ? "REJECTING…" : "REJECT WARRANT"}
                    </button>
                  )}
                </div>
              </>
            ) : <div className="warrant-empty"><span>⌁</span><p>Warrant remains sealed until the clean recovery plan is ready.</p></div>}
          </article>
        </section>

        <section className="lower-grid">
          <article className="findings panel">
            <header><p>SPECIALIST OUTPUTS</p><h2>Three agents. Three bounded decisions.</h2></header>
            <div className="finding-list">
              {["Raasid", "Kashif", "Muslih"].map((name, index) => {
                const finding = incident?.findings.find((item) => item.agent === name);
                const summary = finding?.summary ?? "Waiting for bounded incident evidence.";
                const [lead, rest] = firstSentence(summary);
                return <div className="finding" key={name}><b>0{index + 1}</b><div><h3>{name}</h3><p><strong>{lead}</strong>{rest}</p></div><span>{finding?.thinking_level ?? agents[index + 1][3]}</span></div>;
              })}
            </div>
          </article>
          <article className={`outcome panel ${incident?.state === "VERIFIED" ? "verified" : ""}`}>
            <header><p>FINALITY</p><h2>{incident?.state === "VERIFIED" ? "Work safely completed." : incident?.state === "BLOCKED" ? "Workflow safely stopped." : "Awaiting persisted outcome."}</h2></header>
            <div className="outcome-score"><strong>{incident?.verification ?? "—"}</strong><span>VERIFICATION VERDICT</span></div>
            <dl>
              <div><dt>Receipt</dt><dd>{data?.receipt?.receipt_id ?? "No mutation"}</dd></div>
              <div><dt>Executed destination</dt><dd>{data?.receipt?.bank_fingerprint ?? "Locked"}</dd></div>
              <div><dt>Persistence actor</dt><dd>{data?.receipt?.executor_identity ?? "Locked"}</dd></div>
              <div><dt>Recovery runtime</dt><dd>{data?.receipt?.reasoning_runtime_identity ?? "Legacy receipt"}</dd></div>
              <div><dt>Shaahid</dt><dd>{incident?.witness_summary ?? "Awaiting deterministic comparison."}</dd></div>
            </dl>
            {incident?.state === "VERIFIED" && data?.receipt && (
              <div className="replay-control">
                <button className="replay" onClick={replay} disabled={!!busy}>
                  {busy === "replay" ? "VERIFYING RECEIPT…" : "VERIFY ONE-RECEIPT REPLAY"}
                </button>
                <p aria-live="polite">{replayEvidence
                  ? `${replayEvidence.verdict} / ${replayEvidence.receiptId}`
                  : `ONE RECEIPT BOUND / ${data.receipt.receipt_id} / REPLAY NOT YET RUN`}</p>
              </div>
            )}
          </article>
        </section>

        <footer className="provenance">
          <span>GOOGLE CLOUD PROVENANCE / CONSOLE REQUIRES PROJECT ACCESS</span>
          {incident && <a href={`/api/incidents/${incident.incident_id}`} target="_blank" rel="noreferrer">PUBLIC INCIDENT JSON ↗</a>}
          {incident?.state === "VERIFIED" && <a href={`/api/incidents/${incident.incident_id}/replay`} target="_blank" rel="noreferrer">PUBLIC REPLAY ↗</a>}
          <a href="https://github.com/asadvendor-boop/HisaarAI/tree/main/docs/evidence" target="_blank" rel="noreferrer">PUBLIC EVIDENCE ↗</a>
          <a href="https://console.cloud.google.com/agent-platform/agent-registry?project=hisaarai-agentic-2026" target="_blank">AGENT REGISTRY ↗</a>
          <a href="https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=hisaarai-agentic-2026" target="_blank">2 AGENT RUNTIMES ↗</a>
          <a href="https://console.cloud.google.com/firestore/databases/hisaarai/data/panel?project=hisaarai-agentic-2026" target="_blank">FIRESTORE AUTHORITY ↗</a>
          <a href="https://console.cloud.google.com/security/model-armor?project=hisaarai-agentic-2026" target="_blank">MODEL ARMOR ↗</a>
          <a href={incident ? `https://console.cloud.google.com/traces/explorer?project=hisaarai-agentic-2026&traceId=${incident.trace_id}` : "https://console.cloud.google.com/traces/explorer?project=hisaarai-agentic-2026"} target="_blank">CORRELATED TRACE ↗</a>
          <details className="continuity-proof">
            <summary>CONTINUITY {Object.values(continuity).filter(Boolean).length}/4 GENUINE</summary>
            <div>
              {[
                ["day_0", "DAY 0", "2026-08-09"],
                ["day_7", "DAY 7", "2026-08-16"],
                ["day_14", "DAY 14", "2026-08-23"],
                ["day_21", "DAY 21", "2026-08-30"],
              ].map(([key, label, date]) => {
                const checkpoint = continuity[key] as Record<string, unknown> | null | undefined;
                const revision = typeof checkpoint?.memory_revision_name === "string"
                  ? checkpoint.memory_revision_name.split("/").at(-1)
                  : null;
                return (
                  <p className={checkpoint ? "recorded" : "pending"} key={key}>
                    <b>{label}</b><time>{date}</time><span>{checkpoint ? `RECORDED / ${shortHash(revision, 10)}` : "PENDING"}</span>
                  </p>
                );
              })}
            </div>
          </details>
        </footer>
      </main>
    </div>
  );
}

export default App;
