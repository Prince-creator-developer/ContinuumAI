# ContinuumAI: Autonomous Knowledge Continuity & Handover OS

<div align="center">

[![Live Platform](https://img.shields.io/badge/Live%20Platform-continuumai--g9ej.vercel.app-2563eb?style=for-the-badge&logo=vercel)](https://continuumai-g9ej.vercel.app)
[![Tests Passing](https://img.shields.io/badge/Tests-23%2F23%20Passing%20(100%25)-059669?style=for-the-badge)](./test_regression.py)
[![Python 3.12](https://img.shields.io/badge/Python-3.12%20FastAPI-0284c7?style=for-the-badge&logo=python)](./requirements.txt)
[![Zero-Trust](https://img.shields.io/badge/Security-Presidio%20Redacted-7c3aed?style=for-the-badge)](./core/sanitizer.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-0891b2?style=for-the-badge)](./LICENSE)

### **Prevent Institutional Memory Loss When Key Engineers Depart**
*Autonomous Project State Reconstruction from Disparate Digital Exhaust with Permission-Aware Evidence Graphs, Contradiction Circuit Breakers, and Cryptographic Signoff.*

### 🌐 [Launch Live Production Studio on Vercel](https://continuumai-g9ej.vercel.app)

[📄 View Architectural Dossier (PDF)](./ContinuumAI_Knowledge_Handover_Round2_Build_Dossier.pdf) • [🧪 Run Automated Test Suite (pytest)](./test_regression.py) • [🏛️ Public GitHub Repository](https://github.com/Prince-creator-developer/ContinuumAI)

</div>

---

## 📌 Executive Problem & Solution

When employees, volunteers, or lead developers leave a project, critical institutional intelligence vanishes with them. While standard documentation may exist, the **reasoning behind trade-offs, abandoned spikes, unwritten workarounds, and cross-tool contradictions** remains scattered across Git commit messages, pull request debates, Slack war rooms, and Jira issue boards.

**ContinuumAI** solves this continuity crisis by autonomously reconstructing a cohesive, evidence-backed, and role-appropriate project continuation package:
1. **Scans Disparate Exhaust:** Ingests commits, PR reviews, Slack channels, and issue boards.
2. **Redacts Sensitive Credentials:** Applies Zero-Trust Microsoft Presidio redaction to permanently scrub Stripe keys, AWS tokens, passwords, and executive compensation data.
3. **Temporal Reconciliation Engine (TRE):** Reconstructs chronological event trees, extracts implicit Architecture Decision Records (ADRs), and flags contradictions (e.g. Slack proposals vs. merged code).
4. **Human-in-the-Loop Signoff:** Departing leads review discrepancies, add tacit context, and seal the handover with a tamper-evident **SHA-256 cryptographic certificate**.
5. **Grounded Continuation Q&A:** New team members explore role-based lenses and query an anti-hallucination assistant backed by line-level citations.

---

## 🚀 Experience the Live Studio in Under 60 Seconds

### Option 1: Instant Cloud Studio (Zero Setup Required)
Navigate directly to **[https://continuumai-g9ej.vercel.app](https://continuumai-g9ej.vercel.app)** in any desktop or mobile browser.
* Includes interactive **Beginner's Guided Tour** with animated arrow indicators.
* Multi-turn conversational assistant with citation evidence pins.
* One-click conflict resolution, live readiness meter, and verifiable SHA-256 certificate generation.

### Option 2: Local Reproduction & Testing
```bash
# 1. Clone repository
git clone https://github.com/Prince-creator-developer/ContinuumAI.git
cd ContinuumAI

# 2. Install dependencies & run test suite (23/23 Passing)
pip install -r requirements.txt
python -m pytest test_engine.py test_regression.py -v

# 3. Launch local operational server
python app.py
```
> **Open [http://localhost:8000](http://localhost:8000)** in your browser. *(On Windows, simply run `run.bat`)*

---

## ⚡ Core Platform Capabilities

### 1. Ingestion & Zero-Trust Sanitization (`/api/sources`)
* Multi-source parsers for Git history, GitHub/GitLab PRs, Slack/Discord messages, and Jira/Linear tasks.
* Automated **Microsoft Presidio** secret redactor intercepts Stripe secrets (`sk_mock_...`), AWS keys, private tokens, passwords, and PII.

### 2. Temporal State & Causal Dependency Graph (`/api/reconstruct`)
* Builds unified chronological timeline across disparate systems.
* Automatically extracts implicit **Architecture Decision Records (ADRs)** (e.g., ADR-002: Custom JWT session cookies for HIPAA compliance).
* Maps causal dependency nodes and flags unmerged branches or active technical blockers.

### 3. Temporal Reconciliation Engine (TRE) (`/api/verify`)
* Resolves conflicting cross-source signals using commitment durability weights:
  $$\text{Merged Main Code } (1.0) > \text{Merged PR } (0.85) > \text{Closed Issue } (0.70) > \text{Slack Chat } (0.35)$$
* Triggers **`[CONFLICT_DETECTED]` Circuit Breaker** for active contradictions (e.g. Redis Cluster vs. Memcached).
* Detects **Missing Evidence Gaps** (`X_INTERNAL_SYNC_SALT` in staging ConfigMaps omitted from runbooks).

### 4. Human-in-the-Loop Review & Compliance Signoff (`/api/sign`)
* Departing leads execute 1-click binding resolution of flagged contradictions.
* Departing staff append tacit tribal knowledge notes.
* Generates an immutable **SHA-256 cryptographic audit certificate** (`BLOCK-7D9A4C02...`) compliant with SOC 2 Type II and ISO 27001 offboarding controls.

### 5. Role-Governed Views & Grounded AI Assistant (`/api/handover/{role}`, `/api/ask`)
* **Role Lenses:** Engineering Deep-Dive (full code & branch details), PM Milestone View, and Contractor Sandbox (trade secrets & credentials automatically masked).
* **Multi-Turn Assistant:** Conversational query engine that answers from verified nodes with clickable source citations.
* **Zero-Hallucination Policy:** Refuses open-domain speculation and answers *"Information not found in project records"* if evidence is missing.

---

## 🛠️ Enterprise Additions

* 📥 **Custom Telemetry Ingestor (`POST /api/ingest_custom`):** Ingest custom commits, paste Slack logs, or choose from 3 enterprise profiles (*Healthcare Core*, *Fintech Gateway*, *Autonomous AI Agent*).
* 🛡️ **Public Certificate Verifier (`GET /api/verify_cert/{hash}`):** Verify any 64-character SHA-256 certificate against the tamper-evident audit ledger.
* 📋 **Complete Handover Exporter (`GET /api/export/markdown`):** Export the complete verified handover package directly to Markdown (for Notion, Confluence, GitHub Wiki) or JSON-LD.
* 📊 **Interactive ROI Calculator:** Calculate transition cost and time savings based on engineering team size and turnover rate.

---

## 📁 Repository Structure

```
ContinuumAI/
├── app.py                                            # Main FastAPI Gateway & Web Dashboard
├── main.py                                           # ASGI Entrypoint for Cloud Deployment
├── run.bat                                           # 1-Click Windows Launcher
├── run.sh                                            # 1-Click Unix Launcher
├── requirements.txt                                  # Lean Production Dependencies
├── test_engine.py                                    # Unit Test Suite (7/7 Passing)
├── test_regression.py                                # Exhaustive Regression Test Suite (16/16 Passing)
├── vercel.json                                       # Multi-Service Cloud Deployment Config
├── ContinuumAI_Knowledge_Handover_Round2_Build_Dossier.pdf # Formal 8-Slide Architectural Dossier
├── server/                                           # Dedicated Analytical Microservice
│   ├── main.py                                       # Microservice Entrypoint
│   └── requirements.txt                              # Lean Service Dependencies
├── core/
│   ├── sanitizer.py                                  # Presidio PII & Secret Redactor
│   ├── engine.py                                     # Temporal AST & Causal Graph Builder
│   ├── tre.py                                        # Temporal Reconciliation Engine (TRE)
│   ├── rbac.py                                       # Role-Based Access Control Lenses
│   ├── review_ledger.py                              # HITL Review & Cryptographic Signoff Ledger
│   └── grounded_rag.py                               # Cited "Ask This Handover" Assistant
├── data/synthetic_project_dump/
│   ├── git_commits.json                              # 45 Realistic Commits & Diffs
│   ├── pull_requests.json                            # 20 PRs with Architectural Debates
│   ├── slack_channels.json                           # 80 War Room Chat Messages with Conflicts
│   └── jira_issues.json                              # 15 Issues with Blockers & Salts
├── templates/
│   └── index.html                                    # Modern Tailwind CSS Web Platform
└── README.md
```

---

## 👥 Authors & Provenance

* **Prince Kumar** — *Team Lead & AI Architect* (FastAPI Core Architecture, Temporal Reconciliation Engine, Presidio Zero-Trust Redactor, Grounded RAG Assistant, Test Suites, Technical Dossier)
* **Yash Sharma** — *Full-Stack & UI/UX Specialist* (Tailwind CSS Platform, Interactive Guided Tour, HITL Review Cockpit, Role-Governed Lenses, Evidence Inspector)

*Architected with pride by **Valerion Coders**.*

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.
