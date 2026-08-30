# The agent was compromised. The payment was not.

I created this article for the purpose of entering the All Things Agentic Hackathon.

Enterprise agent systems usually stop at detection: an unsafe request is flagged,
an operator sees a red alert, and the business task remains unfinished. HisaarAI
asks a harder question: can an agent fleet contain a compromised execution,
reconstruct the task from trusted context, obtain one human decision, and finish
the work safely?

Protocols are making agents easier to connect. HisaarAI addresses the next
production question: what are those connected agents actually allowed to cause?

HisaarAI demonstrates that journey with a sandbox accounts-payable incident. A
committed invoice passes through two real Model Armor checks. A prompt-injection
fixture stops before Gemini. A subtler banking-detail tamper clears content
screening, reaches the Protected AP agent, and is caught by Hisaar Gate when the
proposal disagrees with the trusted vendor master.

The recovery fleet then separates responsibility across named agents: Raasid
observes persisted evidence, Kashif bounds the blast radius, Muslih drafts the
smallest recovery action, Clean AP validates the exact approved request, and
Shaahid narrates the deterministic verification result. Gemini never grants
authority. Hisaar Gate owns the state machine, reloads trusted sources, creates
the expiring warrant, requires an allowlisted Google identity to approve its
exact digest, and persists the idempotent sandbox receipt under the application
identity.

The implementation uses Gemini 3.7 Flash and Gemini 3.5 Flash-Lite through Google
ADK, two callable Agent Runtime resources with separate runtime identities,
Agent Registry, Memory Bank, Model Armor, Pub/Sub, Cloud Run, Firestore, Cloud
Logging, and Cloud Trace. The official Registry readback discovers exactly the
two HisaarAI Runtime agents and their separate deployed identities; it is catalog
proof rather than an execution boundary. Agents receive typed bounded inputs;
deterministic Gate code and the commander retain authority. The latest observed
warrant binds the exact genuine Day-21 Memory revision resource name in a Day-0
→ Day-7 → Day-14 → Day-21 predecessor chain. Runtime recovery consumes its Firestore
checkpoint mirror; it does not reread the Memory API in the recovery path. The
Day-7 and Day-14 jobs fired on schedule but initially failed a Vertex API
validation change; their real August 25 recovery timestamps remain visible
rather than being backdated. The scheduled Day-21 delivery succeeded on August
30 and points to the Day-14 revision as its predecessor.

On August 25, Google Cloud [introduced Gemini Enterprise for Financial
Services](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-for-financial-services)
around specialized financial skills, secure data connections, acting agents and
centralized governance. HisaarAI explores the complementary recovery problem:
when a financial agent's context is poisoned, how can the institution contain
it, reconstruct trusted context and safely finish the work exactly once?
HisaarAI demonstrates the same governed design principles in a bounded AP
recovery scenario; it does not claim integration with the preview product.

| Google Cloud design principle | HisaarAI evidence |
| --- | --- |
| Purpose-built financial skills | Bounded AP recovery playbook and specialist instructions |
| Secure connections | Scoped vendor-master and sandbox-ledger tools |
| Agents that act | Quarantine, reconstruction, warrant preparation and verified completion |
| Governed control plane | Hisaar Gate, commander approval, Model Armor, identities, traces and immutable receipt |

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
