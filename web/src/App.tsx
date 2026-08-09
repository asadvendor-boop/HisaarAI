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
  ["Clean AP", "Standby executor", "Gemini 3.6 Flash", "MEDIUM"],
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

function stateIndex(state?: IncidentState) {
  if (!state) return -1;
  if (state === "BLOCKED") return 1;
  return steps.indexOf(state);
}

function agentStatus(index: number, incident: Incident | null) {
  if (!incident) return "STANDBY";
  const current = stateIndex(incident.state);
  const thresholds = [0, 2, 2, 3, 5, 7];
  if (current < thresholds[index]) return index === 4 ? "ISOLATED" : "STANDBY";
  if (incident.state === "BLOCKED" && index > 0) return "WITHHELD";
  if (index === 4 && current < 5) return "CLEAN / LOCKED";
  return current === thresholds[index] ? "ACTIVE" : "COMPLETE";
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
  const [notice, setNotice] = useState(
    sharedIncidentId
      ? "Read-only hosted evidence loaded. Commander sign-in is required only for new actions."
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
        setNotice(
          nextData.incident.state === "BLOCKED"
            ? "Model Armor blocked the injection before Gemini."
            : "Authenticated event delivered. Hisaar Gate is live.",
        );
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
          : "Security control published. Watching Model Armor.",
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

  const incident = data?.incident ?? null;
  const amount = useMemo(() => {
    if (!incident?.proposal) return "PKR 4.275M";
    return new Intl.NumberFormat("en-PK", {
      style: "currency",
      currency: incident.proposal.currency,
      maximumFractionDigits: 0,
    }).format(incident.proposal.amount_minor / 100);
  }, [incident]);
  const progress = stateIndex(incident?.state);

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
        <section className="hero bastion">
          <div className="hero-copy">
            <p className="eyebrow">GOVERNED MULTI-AGENT RECOVERY / 01</p>
            <h1>The agent was compromised.<br /><em>The payment was not.</em></h1>
            <p className="lede">HisaarAI quarantines a poisoned workflow, reconstructs clean context, obtains one human decision, and safely finishes the work.</p>
            <div className="hero-actions">
              <button className="primary" onClick={() => launch()} disabled={!token || !!busy}>
                <span>{busy === "semantic-tamper" ? "PUBLISHING…" : "RUN FLAGSHIP INCIDENT"}</span>
                <b>↗</b>
              </button>
              <button className="secondary" onClick={() => launch("injection-control")} disabled={!token || !!busy}>
                TEST MODEL ARMOR
              </button>
            </div>
            <p className="notice" aria-live="polite"><span>COMMAND</span> {notice}</p>
          </div>
          <div className="risk-dial" aria-label={`Amount at risk ${amount}`}>
            <div className="dial-ring"><span>PROTECTED</span><strong>{amount}</strong><small>AMOUNT AT RISK</small></div>
            <div className={`state-beacon state-${incident?.state ?? "READY"}`}>
              <i /> {incident?.state ?? "READY"}
            </div>
          </div>
        </section>

        <section className="agent-rail" aria-label="Agent fleet">
          {agents.map(([name, role, model, thinking], index) => {
            const status = agentStatus(index, incident);
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
            <div className="comparison-row unsafe">
              <span>INVOICE DESTINATION</span>
              <code>{incident?.proposal?.bank_fingerprint ?? "PK-ATTACKER-9911"}</code>
              <b>{incident ? "MISMATCH" : "PENDING"}</b>
            </div>
            <div className="comparison-row trusted">
              <span>VENDOR MASTER v{incident?.trusted_vendor?.version ?? 7}</span>
              <code>{incident?.trusted_vendor?.bank_fingerprint ?? "PK-NSTAR-TRUSTED-8842"}</code>
              <b>TRUSTED</b>
            </div>
            <div className="armor-line">
              <span>MODEL ARMOR</span>
              <div><i className={incident?.screening_decision === "CLEAR" ? "clear" : ""} /></div>
              <strong>{incident?.screening_decision ?? "AWAITING INPUT"}</strong>
            </div>
          </article>

          <article className="panel timeline-panel">
            <header><p>LIVE RECOVERY</p><h2>Governed state rail</h2></header>
            <ol className="timeline">
              {steps.map((step, index) => (
                <li className={index < progress ? "done" : index === progress ? "current" : ""} key={step}>
                  <i /><span>{step.replaceAll("_", " ")}</span><small>{incident?.state_history.find((item) => item.state === step) ? new Date(incident.state_history.find((item) => item.state === step)!.at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", second: "2-digit"}) : "LOCKED"}</small>
                </li>
              ))}
            </ol>
          </article>

          <article className="panel warrant-panel bastion">
            <header><p>HUMAN BOUNDARY</p><h2>Recovery warrant</h2></header>
            {incident?.warrant ? (
              <>
                <dl>
                  <div><dt>Correction</dt><dd>Trusted vendor master v{incident.warrant.trusted_vendor_version}</dd></div>
                  <div><dt>Destination</dt><dd><code>{incident.warrant.bank_fingerprint}</code></dd></div>
                  <div><dt>Warrant digest</dt><dd><code>{shortHash(incident.warrant.digest, 20)}</code></dd></div>
                  <div><dt>Memory revision</dt><dd><code>{shortHash(incident.warrant.continuity_revision_name.split("/").at(-1))}</code></dd></div>
                  <div><dt>Expires</dt><dd>{new Date(incident.warrant.expires_at).toLocaleTimeString()}</dd></div>
                </dl>
                <button className="approve" onClick={approve} disabled={!token || incident.state !== "AWAITING_APPROVAL" || !!busy}>
                  {busy === "approve" ? "VERIFYING IDENTITY…" : "APPROVE EXACT WARRANT"}
                </button>
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
                return <div className="finding" key={name}><b>0{index + 1}</b><div><h3>{name}</h3><p>{finding?.summary ?? "Waiting for bounded incident evidence."}</p></div><span>{finding?.thinking_level ?? agents[index + 1][3]}</span></div>;
              })}
            </div>
          </article>
          <article className={`outcome panel ${incident?.state === "VERIFIED" ? "verified" : ""}`}>
            <header><p>FINALITY</p><h2>{incident?.state === "VERIFIED" ? "Work safely completed." : "Unsafe payment remains blocked."}</h2></header>
            <div className="outcome-score"><strong>{incident?.verification ?? "—"}</strong><span>REPLAY VERDICT</span></div>
            <dl>
              <div><dt>Receipt</dt><dd>{data?.receipt?.receipt_id ?? "No mutation"}</dd></div>
              <div><dt>Executed destination</dt><dd>{data?.receipt?.bank_fingerprint ?? "Locked"}</dd></div>
              <div><dt>Shaahid</dt><dd>{incident?.witness_summary ?? "Awaiting deterministic comparison."}</dd></div>
            </dl>
          </article>
        </section>

        <footer className="provenance">
          <span>REAL GOOGLE PROVENANCE</span>
          <a href="https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=hisaarai-agentic-2026" target="_blank">2 AGENT RUNTIMES ↗</a>
          <a href="https://console.cloud.google.com/firestore/databases/hisaarai/data/panel?project=hisaarai-agentic-2026" target="_blank">FIRESTORE AUTHORITY ↗</a>
          <a href="https://console.cloud.google.com/security/model-armor?project=hisaarai-agentic-2026" target="_blank">MODEL ARMOR ↗</a>
          <a href={incident ? `https://console.cloud.google.com/traces/explorer?project=hisaarai-agentic-2026&traceId=${incident.trace_id}` : "https://console.cloud.google.com/traces/explorer?project=hisaarai-agentic-2026"} target="_blank">CORRELATED TRACE ↗</a>
          <span>CONTINUITY {Object.values(continuity).filter(Boolean).length}/4 GENUINE</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
