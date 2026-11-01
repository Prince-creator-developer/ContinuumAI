"""
ContinuumAI - Frontend & Gateway Service (Vercel Service: app)
Serves the web dashboard and delegates backend state to the bound `server` service.
"""

import os
import sys
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
static_dir = os.path.join(CURRENT_DIR, "static")

if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)

if os.path.exists(static_dir):
    try:
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    except Exception as e:
        print(f"Notice: Static mount skipped: {e}")

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

def fetch_from_server_or_local(endpoint: str, local_fallback_fn):
    """Fetches data from bound Vercel service or falls back to local direct call."""
    if SERVER_SERVICE_URL:
        try:
            resp = requests.get(f"{SERVER_SERVICE_URL}/{endpoint.lstrip('/')}", timeout=4)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"Notice: Call to bound server {SERVER_SERVICE_URL} failed, falling back to local: {e}")
    return local_fallback_fn()

# ----------------- WEB FRONTEND ROUTE -----------------
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main interactive Next/Tailwind style dashboard."""
    raw_sources = engine.load_raw_sources()
    
    state = fetch_from_server_or_local(
        "api/reconstruct",
        lambda: engine.reconstruct_project_state(raw_sources)
    )
    tre_data = fetch_from_server_or_local(
        "api/verify",
        lambda: tre.verify_and_reconcile(raw_sources, state)
    )
    review_state = fetch_from_server_or_local(
        "api/ledger",
        lambda: ledger.get_review_state()
    )

    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": state,
        "tre": tre_data,
        "review": review_state,
        "version": "2.0.0 (Round 2 Multi-Service Build)",
        "server_bound": bool(SERVER_SERVICE_URL)
    })

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
    return fetch_from_server_or_local("api/reconstruct", lambda: engine.reconstruct_project_state())

@app.get("/api/verify")
def verify_endpoint():
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    return fetch_from_server_or_local("api/verify", lambda: tre.verify_and_reconcile(raw, state))

@app.get("/api/ledger")
def get_ledger_endpoint():
    return fetch_from_server_or_local("api/ledger", lambda: ledger.get_review_state())

@app.post("/api/resolve_conflict")
def resolve_conflict_endpoint(req: ConflictResolutionRequest):
    if SERVER_SERVICE_URL:
        try:
            return requests.post(f"{SERVER_SERVICE_URL}/api/resolve_conflict", json=req.dict(), timeout=3).json()
        except Exception:
            pass
    return ledger.resolve_conflict(req.conflict_id, req.decision, req.notes, req.approver)

@app.post("/api/add_note")
def add_note_endpoint(req: TacitNoteRequest):
    if SERVER_SERVICE_URL:
        try:
            return requests.post(f"{SERVER_SERVICE_URL}/api/add_note", json=req.dict(), timeout=3).json()
        except Exception:
            pass
    return ledger.add_tacit_note(req.author, req.content)

@app.post("/api/sign")
def sign_handover_endpoint(req: SignHandoverRequest):
    if SERVER_SERVICE_URL:
        try:
            return requests.post(f"{SERVER_SERVICE_URL}/api/sign", json=req.dict(), timeout=3).json()
        except Exception:
            pass
    return ledger.sign_handover(req.signer_name, req.signer_role, req.project_name)

@app.get("/api/handover/{role}")
def get_role_handover_endpoint(role: str):
    if SERVER_SERVICE_URL:
        try:
            return requests.get(f"{SERVER_SERVICE_URL}/api/handover/{role}", timeout=3).json()
        except Exception:
            pass
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    return rbac.get_role_handover(role, state, tre_data)

@app.post("/api/ask")
def ask_handover_assistant_endpoint(req: AskQueryRequest):
    if SERVER_SERVICE_URL:
        try:
            return requests.post(f"{SERVER_SERVICE_URL}/api/ask", json=req.dict(), timeout=3).json()
        except Exception:
            pass
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    ledger_state = ledger.get_review_state()
    return assistant.answer_query(req.query, state, tre_data, ledger_state)

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("  ContinuumAI - Frontend Service starting on http://127.0.0.1:8000")
    print(f"  Bound Server Service: {SERVER_SERVICE_URL or 'Local In-Process'}")
    print("=" * 70)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
