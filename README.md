# ContinuumAI: Intelligent Knowledge Handover & Continuity Engine

<div align="center">

![ContinuumAI Banner](https://img.shields.io/badge/ContinuumAI-Round%202%20Operational%20Build-2563eb?style=for-the-badge)
[![Round 2: The Build](https://img.shields.io/badge/Hackathon-Round%202%3A%20The%20Build%20(100%20Pts)-10b981?style=for-the-badge)](./ContinuumAI_Knowledge_Handover_Round2_Build_Dossier.pdf)
[![Tests Passing](https://img.shields.io/badge/Tests-7%2F7%20Passing%20(100%25)-059669?style=for-the-badge)](./test_engine.py)
[![Track](https://img.shields.io/badge/Track-We%20Code%20Coders-7c3aed?style=for-the-badge)](#team-valerion-coders)
[![License: MIT](https://img.shields.io/badge/License-MIT-0891b2?style=for-the-badge)](./LICENSE)

**Prevent Critical Knowledge From Leaving With People**  
*Autonomous Project State Reconstruction from Disparate Digital Exhaust with Permission-Aware Evidence Graphs and Human-in-the-Loop Verification.*

[📄 View Round 2 Build Dossier (PDF)](./ContinuumAI_Knowledge_Handover_Round2_Build_Dossier.pdf) • [🌐 Launch Web Dashboard (HTML)](./templates/index.html) • [🧪 Run Automated Test Suite (pytest)](./test_engine.py)

</div>

---

## 🚀 Quickstart for Hackathon Judges (Run in Under 60 Seconds)

ContinuumAI is engineered as a unified, high-performance web service with zero complex multi-terminal setup:

```bash
# 1. Clone repository
git clone https://github.com/Prince-creator-developer/ContinuumAI.git
cd ContinuumAI

# 2. Install dependencies & run test suite
pip install -r requirements.txt
python -m pytest test_engine.py

# 3. Launch the operational server
python app.py
```
> **Open [http://localhost:8000](http://localhost:8000)** in your browser to experience the 5-step handover journey.  
> *(On Windows, you can also simply double-click `run.bat`)*

---

## 👥 Team: Valerion Coders

| Member Name | Official Hackathon Role | Personal Contribution & Workstream |
| :--- | :--- | :--- |
| **Prince Kumar** | **Team Lead & AI Architect** | FastAPI backend architecture, Temporal Reconciliation Engine (TRE), zero-trust Presidio regex sanitizer, Grounded RAG assistant, pytest test suite, and Round 2 Build Dossier. |
| **Yash Sharma** | **Full-Stack & UI/UX Specialist** | Next-style Tailwind CSS dashboard, 5-step interactive stepper, HITL Review & Approval Cockpit, 1-click contradiction resolution UI, role projection filters, and citation pins. |

---

## 🎯 Round 2 Evaluation Highlights (100 Points Rubric)

### 1. Working Core Workflow (30 Points)
The complete 5-stage lifecycle is fully operational from end-to-end without broken central steps:
* **Step 01: Connect & Clean (`/api/sources`)** — Ingests 45 commits, 20 PRs, 80 Slack messages, and 15 Jira tasks. Microsoft Presidio scrubs API keys (`sk_mock_...`), passwords, emails, and executive salaries before embedding.
* **Step 02: Temporal Reconstruct (`/api/reconstruct`)** — Builds chronological timeline, mines implicit Architecture Decision Records (e.g. ADR-002: Custom JWT for HIPAA cookie compliance), and maps directional dependency trees.
* **Step 03: Verify & Reconcile (`/api/verify`)** — Anchors 100% of claims to source line numbers and SHAs. Triggers the **`[CONFLICT_DETECTED]` Circuit Breaker** for cross-source discrepancies (Redis vs Memcached) and exposes undocumented dependencies (`X_INTERNAL_SYNC_SALT`).
* **Step 04: Review & Sign (`/api/sign`)** — Human-in-the-Loop Cockpit allowing the departing lead and manager to resolve contradictions in 1 click, add tacit notes, and sign off with an immutable **SHA-256 cryptographic certificate**.
* **Step 05: Role Handover & Q&A (`/api/handover/{role}`, `/api/ask`)** — Dynamic role projections (Engineering Deep-Dive, PM Overview, Contractor Sandbox) and an interactive, citation-grounded conversational search assistant.

### 2. Technical Depth & Reliability (25 Points)
* **Deterministic State Hierarchy Formula:** Rather than trusting naive LLM probabilistic guesses, ContinuumAI resolves conflicting signals using state durability weighting:
  $$\text{Merged Main Code } (1.0) > \text{Merged PR } (0.85) > \text{Closed Issue } (0.70) > \text{Slack Chat } (0.35)$$
* **Zero-Hallucination Policy:** The Grounded RAG Assistant explicitly declares *"Information not found in project records"* when asked about ungrounded topics, refusing to speculate.
* **100% Grounded Claim Ratio (GCR = 1.0):** Every assertion is mathematically linked to a vector or graph node.

### 3. Progress from Round 1 (20 Points)
* Transitioned from theoretical proposal to **100% functional Python/FastAPI implementation**.
* Built pre-packaged 6-month simulated enterprise corpus containing 3 intentional edge cases to demonstrate live contradiction resolution and gap detection.
* Added tamper-evident SHA-256 certificate hashing for SOC 2 compliance.

### 4. Usability & Human Control (10 Points)
* Clean, responsive Tailwind CSS interface requiring zero user training.
* Interactive query chips on the *"Ask This Handover"* assistant for instant evaluation.
* 1-click contradiction resolution buttons with instant DOM feedback.

---

## 🔮 Three Major Improvements Committed for Round 3 (15 Points)

In accordance with Round 2 guidelines, we commit to three meaningful, non-cosmetic product advancements for Round 3 (The Finish):

1. 🌐 **Live Multi-Source OAuth Ingestion Connectors:**  
   Native GitHub App webhook listener, Slack Bolt app integration, and Jira Cloud OAuth REST connectors for automated, continuous data ingestion from live cloud services.
2. 🤖 **Autonomous Continuous Background Journaling Agent:**  
   A LangGraph cron daemon that periodically reconstructs project memory weekly, detecting documentation drift and resolving technical debt long before an employee departure is announced.
3. 🏛️ **SOC 2 & ISO 27001 Cryptographic Handover Audit Vault:**  
   A publicly verifiable audit portal (`/verify-certificate/{hash}`) with Zero-Knowledge Proof (ZKP) attestation confirming that all confidential secrets and PII were scrubbed before handover.

---

## 📁 Repository Structure

```
ContinuumAI/
├── app.py                                            # Main FastAPI Server & Web App
├── run.bat                                           # 1-Click Windows Local Launcher
├── run.sh                                            # 1-Click Unix Local Launcher
├── requirements.txt                                  # Python Dependencies
├── test_engine.py                                    # Automated Pytest Suite (7/7 Passing)
├── vercel.json                                       # Serverless Cloud Deployment Config
├── ContinuumAI_Knowledge_Handover_Round2_Build_Dossier.pdf # Official Round 2 PDF Dossier
├── ContinuumAI_Knowledge_Handover_Round1_Dossier.pdf # Round 1 Proposal Reference
├── core/
│   ├── sanitizer.py                                  # Presidio PII & Secret Redactor
│   ├── engine.py                                     # Temporal AST & Causal Graph Builder
│   ├── tre.py                                        # Temporal Reconciliation Engine (TRE)
│   ├── rbac.py                                       # Role-Based Access Control Lenses
│   ├── review_ledger.py                              # HITL Review & SHA-256 Signoff Ledger
│   └── grounded_rag.py                               # Cited "Ask This Handover" Assistant
├── data/synthetic_project_dump/
│   ├── git_commits.json                              # 45 Realistic Commits & Diffs
│   ├── pull_requests.json                            # 20 PRs with Architectural Debates
│   ├── slack_channels.json                           # 80 Chat Messages with Conflicts
│   └── jira_issues.json                              # 15 Issues with Blockers
├── templates/
│   └── index.html                                    # Modern Tailwind Web Dashboard
└── README.md
```

---

## 📄 License
Licensed under the MIT License — see the [LICENSE](./LICENSE) file for details.

*Developed with pride for the Hackathon Challenge by **Valerion Coders** (Prince Kumar & Yash Sharma).*
