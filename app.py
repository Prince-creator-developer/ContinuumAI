"""
ContinuumAI - Frontend & Gateway Service (Vercel Service: app)
Serves the web dashboard and delegates backend state to the bound `server` service.
"""

import os
import sys
import hashlib
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
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

# Vercel Service Binding: Target internal URL for the "server" service
SERVER_SERVICE_URL = os.environ.get("SERVER_URL", "").rstrip("/")

app = FastAPI(
    title="ContinuumAI — Frontend Service",
    description="Web Dashboard and Gateway Service",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
templates_dir = os.path.join(CURRENT_DIR, "templates")
templates = Jinja2Templates(directory=templates_dir)

static_dir = os.path.join(CURRENT_DIR, "static")
if os.path.isdir(static_dir):
    try:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    except Exception as e:
        pass

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

class CustomIngestRequest(BaseModel):
    commits_text: Optional[str] = ""
    slack_text: Optional[str] = ""
    jira_text: Optional[str] = ""
    profile_preset: Optional[str] = None

# In-memory session store for custom ingested data
SESSION_CUSTOM_SOURCES: Dict[str, Any] = {}

# ----------------- WEB FRONTEND ROUTE -----------------
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main interactive Next/Tailwind style dashboard."""
    try:
        raw_sources = engine.load_raw_sources()
        state = engine.reconstruct_project_state(raw_sources)
        tre_data = tre.verify_and_reconcile(raw_sources, state)
        review_state = ledger.get_review_state()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "request": request,
                "state": state,
                "tre": tre_data,
                "review": review_state,
                "version": "2.0.0 (Round 2 Multi-Service Build)",
                "server_bound": True
            }
        )
    except Exception as e:
        import traceback
        return HTMLResponse(
            content=f"<h1>ContinuumAI Service Error</h1><pre>{traceback.format_exc()}</pre>",
            status_code=500
        )

# ----------------- GATEWAY API FALLBACK ROUTES -----------------
# When public rewrites route /api/* to the server service, client requests hit server directly.
# These routes are retained in app as proxies or local fallbacks.

@app.get("/api/status")
def get_system_status():
    if SERVER_SERVICE_URL:
        try:
            return requests.get(f"{SERVER_SERVICE_URL}/api/status", timeout=3).json()
        except Exception:
            pass
    return {
        "status": "online",
        "service": "ContinuumAI Frontend Gateway",
        "server_binding": SERVER_SERVICE_URL or "local_embedded",
        "round": "Round 2 — The Build",
        "team": "Valerion Coders"
    }

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

@app.get("/api/reconstruct")
def reconstruct_endpoint():
    raw = engine.load_raw_sources()
    return engine.reconstruct_project_state(raw)

@app.get("/api/verify")
def verify_endpoint():
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    return tre.verify_and_reconcile(raw, state)

@app.get("/api/ledger")
def get_ledger_endpoint():
    return ledger.get_review_state()

@app.post("/api/resolve_conflict")
def resolve_conflict_endpoint(req: ConflictResolutionRequest):
    return ledger.resolve_conflict(req.conflict_id, req.decision, req.notes, req.approver)

@app.post("/api/add_note")
def add_note_endpoint(req: TacitNoteRequest):
    return ledger.add_tacit_note(req.author, req.content)

@app.post("/api/sign")
def sign_handover_endpoint(req: SignHandoverRequest):
    return ledger.sign_handover(req.signer_name, req.signer_role, req.project_name)

@app.get("/api/handover/{role}")
def get_role_handover_endpoint(role: str):
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    return rbac.get_role_handover(role, state, tre_data)

@app.post("/api/ask")
def ask_handover_assistant_endpoint(req: AskQueryRequest):
    raw = SESSION_CUSTOM_SOURCES.get("active") or engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    ledger_state = ledger.get_review_state()
    return assistant.answer_query(req.query, state, tre_data, ledger_state)

@app.post("/api/ingest_custom")
def ingest_custom_endpoint(req: CustomIngestRequest):
    """Parses and redacts custom uploaded activity, then reconstructs the state."""
    raw = engine.load_raw_sources()
    
    # Custom commits
    custom_commits = list(raw.get("git_commits", []))
    total_redacted = 0
    
    if req.commits_text and req.commits_text.strip():
        for line in req.commits_text.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            sanitized_line, count = sanitizer.sanitize_text(line)
            total_redacted += count
            custom_commits.insert(0, {
                "sha": hashlib.sha256(line.encode()).hexdigest()[:7],
                "timestamp": "2026-11-05T12:00:00Z",
                "author": "Current User",
                "message": sanitized_line,
                "branch": "feature/custom-handover",
                "status": "active"
            })

    # Custom slack messages
    custom_slack = list(raw.get("slack_channels", []))
    if req.slack_text and req.slack_text.strip():
        new_msgs = []
        for line in req.slack_text.strip().splitlines():
            if not line.strip():
                continue
            sanitized_line, count = sanitizer.sanitize_text(line)
            total_redacted += count
            new_msgs.append({
                "id": f"msg_user_{len(new_msgs)+1:03d}",
                "timestamp": "2026-11-05T14:30:00Z",
                "user": "CurrentUser",
                "text": sanitized_line
            })
        custom_slack.insert(0, {
            "channel": "custom-team-chat",
            "messages": new_msgs
        })

    custom_sources = {
        "git_commits": custom_commits,
        "pull_requests": raw.get("pull_requests", []),
        "slack_channels": custom_slack,
        "jira_issues": raw.get("jira_issues", [])
    }
    SESSION_CUSTOM_SOURCES["active"] = custom_sources

    new_state = engine.reconstruct_project_state(custom_sources)
    new_tre = tre.verify_and_reconcile(custom_sources, new_state)

    return {
        "status": "success",
        "redactions_applied": total_redacted,
        "total_commits": len(custom_commits),
        "total_slack_channels": len(custom_slack),
        "state": new_state,
        "tre": new_tre
    }

@app.get("/api/verify_cert/{cert_hash}")
def verify_cert_endpoint(cert_hash: str):
    return ledger.verify_certificate(cert_hash)

@app.get("/api/export/{fmt}")
def export_handover_endpoint(fmt: str = "markdown"):
    raw = SESSION_CUSTOM_SOURCES.get("active") or engine.load_raw_sources()
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

    # Generate Structured Markdown Briefing
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
    print("=" * 70)
    print("  ContinuumAI - Frontend Service starting on http://127.0.0.1:8000")
    print(f"  Bound Server Service: {SERVER_SERVICE_URL or 'Local In-Process'}")
    print("=" * 70)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
