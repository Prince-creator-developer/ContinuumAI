"""
ContinuumAI - Backend Engine Microservice (Vercel Service: server)
Exposes all analytical, reconstruction, verification, and audit endpoints.
"""

import os
import sys
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Ensure local directories are in python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.sanitizer import sanitizer
from core.engine import engine
from core.tre import tre
from core.rbac import rbac
from core.review_ledger import ledger
from core.grounded_rag import assistant

app = FastAPI(
    title="ContinuumAI Backend Service",
    description="Backend Verification & Temporal Reconciliation Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConflictResolutionRequest(BaseModel):
    conflict_id: str
    decision: str
    notes: str
    approver: str = "Lead Reviewer"

class TacitNoteRequest(BaseModel):
    author: str
    content: str

class SignHandoverRequest(BaseModel):
    signer_name: str
    signer_role: str
    project_name: Optional[str] = "ContinuumAI Core Project"

class AskQueryRequest(BaseModel):
    query: str

# Health / Status
@app.get("/")
@app.get("/status")
@app.get("/api/status")
def get_system_status():
    return {
        "status": "online",
        "service": "ContinuumAI Backend Microservice",
        "round": "Round 2 — The Build",
        "team": "Valerion Coders",
        "core_steps_operational": [
            "01_connect_sanitization",
            "02_temporal_ast_reconstruct",
            "03_tre_verification_conflicts",
            "04_hitl_review_signoff",
            "05_role_governed_handover"
        ]
    }

# Data Sources
@app.get("/sources")
@app.get("/api/sources")
def get_sources_endpoint():
    raw = engine.load_raw_sources()
    total_redactions = 0
    for ch in raw.get("slack_channels", []):
        for msg in ch.get("messages", []):
            _, count = sanitizer.sanitize_text(msg.get("text", ""))
            total_redactions += count

    return {
        "raw_counts": {
            "git_commits": len(raw.get("git_commits", [])),
            "pull_requests": len(raw.get("pull_requests", [])),
            "slack_messages": sum(len(c.get("messages", [])) for c in raw.get("slack_channels", [])),
            "jira_issues": len(raw.get("jira_issues", []))
        },
        "zero_trust_redactions_applied": total_redactions,
        "sources": raw
    }

# Reconstruction
@app.get("/reconstruct")
@app.get("/api/reconstruct")
def reconstruct_endpoint():
    raw = engine.load_raw_sources()
    return engine.reconstruct_project_state(raw)

# Verification & TRE
@app.get("/verify")
@app.get("/api/verify")
def verify_endpoint():
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    return tre.verify_and_reconcile(raw, state)

# Review Ledger
@app.get("/ledger")
@app.get("/api/ledger")
def get_ledger_endpoint():
    return ledger.get_review_state()

@app.post("/resolve_conflict")
@app.post("/api/resolve_conflict")
def resolve_conflict_endpoint(req: ConflictResolutionRequest):
    return ledger.resolve_conflict(req.conflict_id, req.decision, req.notes, req.approver)

@app.post("/add_note")
@app.post("/api/add_note")
def add_note_endpoint(req: TacitNoteRequest):
    return ledger.add_tacit_note(req.author, req.content)

@app.post("/sign")
@app.post("/api/sign")
def sign_handover_endpoint(req: SignHandoverRequest):
    return ledger.sign_handover(req.signer_name, req.signer_role, req.project_name)

# Role Handover
@app.get("/handover/{role}")
@app.get("/api/handover/{role}")
def get_role_handover_endpoint(role: str):
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    return rbac.get_role_handover(role, state, tre_data)

# Grounded RAG Assistant
@app.post("/ask")
@app.post("/api/ask")
def ask_handover_assistant_endpoint(req: AskQueryRequest):
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    ledger_state = ledger.get_review_state()
    return assistant.answer_query(req.query, state, tre_data, ledger_state)

@app.get("/api/verify_cert/{cert_hash}")
def verify_cert_endpoint(cert_hash: str):
    return ledger.verify_certificate(cert_hash)

@app.get("/api/export/{fmt}")
def export_handover_endpoint(fmt: str = "markdown"):
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    review_state = ledger.get_review_state()

    if fmt.lower() == "json":
        return {
            "platform": "ContinuumAI Handover OS",
            "version": "2.0.0 Enterprise",
            "state": state,
            "verification": tre_data,
            "audit_ledger": review_state
        }

    md = []
    md.append("# 🚀 Project Handover & Continuity Briefing")
    md.append("*Generated automatically by ContinuumAI — Enterprise Handover Platform*\n")
    md.append("## 1. Executive Summary")
    md.append(f"- **Total Timeline Milestones:** {len(state.get('timeline', []))}")
    md.append(f"- **Architectural Decisions (ADRs):** {len(state.get('architecture_decisions', []))}")
    md.append(f"- **Active Blockers:** {len(state.get('active_blockers', []))}")
    md.append(f"- **Grounded Claim Veracity Ratio:** {tre_data.get('grounded_claim_ratio', 1.0) * 100}%\n")

    md.append("## 2. First 30 Days Actionable Continuity Checklist")
    role_info = rbac.get_role_handover("engineering", state, tre_data)
    for task in role_info.get("first_30_days_tasks", []):
        md.append(f"- **[{task.get('day')}]**: {task.get('task')}")
    md.append("")

    md.append("## 3. Architecture Decision Records (ADRs)")
    for adr in state.get("architecture_decisions", []):
        md.append(f"### {adr.get('title')} ({adr.get('status')})")
        md.append(f"- **Rationale:** {adr.get('decision')}")
        md.append(f"- **Evidence Pin:** `{adr.get('citation')}`\n")

    md.append("## 4. Active Technical Blockers & Missing Parameters")
    for b in state.get("active_blockers", []):
        md.append(f"- **[{b.get('key')}] {b.get('summary')}** (Assignee: {b.get('assignee')})")
        md.append(f"  - Context: {b.get('notes')}")
    md.append("")

    md.append("## 5. Cryptographic Signoff & Compliance Seal")
    sigs = review_state.get("signatures", [])
    if sigs:
        sig = sigs[-1]
        md.append(f"- **Signer:** {sig.get('signer_name')} ({sig.get('signer_role')})")
        md.append(f"- **Timestamp:** {sig.get('timestamp')}")
        md.append(f"- **Certificate SHA-256:** `{sig.get('certificate_hash')}`")
        md.append(f"- **Ledger Block:** `{sig.get('audit_ledger_block')}`")
    else:
        md.append("- *Status: Ready for two-party cryptographic signoff in Step 4.*")

    return {
        "format": "markdown",
        "content": "\\n".join(md)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
