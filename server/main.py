"""
ContinuumAI - Backend Engine Microservice (Vercel Service: server)
Exposes all analytical, reconstruction, verification, and audit endpoints.
"""

import os
import sys
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
