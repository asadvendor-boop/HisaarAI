# The agent was compromised. The payment was not.

I created this article for the purpose of entering the All Things Agentic Hackathon.

Enterprise agent systems usually stop at detection: an unsafe request is flagged,
an operator sees a red alert, and the business task remains unfinished. HisaarAI
asks a harder question: can an agent fleet contain a compromised execution,
reconstruct the task from trusted context, obtain one human decision, and finish
the work safely?

HisaarAI demonstrates that journey with a sandbox accounts-payable incident. A
committed invoice passes through two real Model Armor checks. A prompt-injection
fixture stops before Gemini. A subtler banking-detail tamper clears content
screening, reaches the Protected AP agent, and is caught by Hisaar Gate when the
proposal disagrees with the trusted vendor master.

The recovery fleet then separates responsibility across named agents: Raasid
observes persisted evidence, Kashif bounds the blast radius, Muslih drafts the
smallest recovery action, a clean AP standby executes only an approved warrant,
and Shaahid narrates the deterministic verification result. Gemini never grants
authority. Hisaar Gate owns the state machine, reloads trusted sources, creates
the expiring warrant, and requires an allowlisted Google identity to approve its
exact digest.

The implementation uses Gemini 3.6 Flash and Gemini 3.5 Flash-Lite through Google
ADK, two callable Agent Runtime resources with separate runtime identities,
Agent Registry, Memory Bank, Model Armor, Pub/Sub, Cloud Run, Firestore, Cloud
Logging, and Cloud Trace. The official Registry readback discovers exactly the
two HisaarAI Runtime agents and their separate deployed identities; it is catalog
proof rather than an execution boundary. Agents receive typed bounded inputs;
deterministic Gate code and the commander retain authority. The latest observed
warrant binds a genuine Day-14 Memory revision in a Day-0 → Day-7 → Day-14
predecessor chain. The Day-7 and Day-14 jobs fired on schedule but initially
failed a Vertex API validation change; their real August 25 recovery timestamps
remain visible rather than being backdated. Day-21 remains `PENDING`.

The command room compresses the architecture into one judge-readable screen:
the altered and trusted bank fingerprints, live agent roles, the Gate-owned
warrant, the authenticated human decision, one sandbox receipt, replay status,
and Google Cloud provenance. The core claim stays deliberately narrow: HisaarAI
is a sandbox recovery demonstration using committed fixtures, not a production
payment processor and not a statistical security benchmark.

The data is equally bounded: synthetic PDF fixtures provide invoice evidence, a
Firestore vendor master supplies the trusted bank fingerprint, and a Firestore
sandbox ledger holds the receipt. In one observed hosted run (`n=1`), the system
transformed an attacker-destination proposal into one verified sandbox receipt
at the trusted destination. That observation is not customer validation or a
claim about production-money impact.

The result is not another incident dashboard. It is a governed recovery product:
contain the agent, preserve the business outcome, and prove exactly what happened.
