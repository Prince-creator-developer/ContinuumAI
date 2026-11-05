"""
ContinuumAI - Comprehensive Regressive Test Suite
Exhaustively tests all algorithmic components, API routes, edge cases,
PII redaction, contradiction resolution, RBAC lenses, and anti-hallucination boundaries.
"""

import pytest
import os
import sys
import hashlib

# Compatibility shim for httpx >= 0.28 with Starlette TestClient
import httpx
_orig_httpx_init = httpx.Client.__init__
httpx.Client.__init__ = lambda self, *args, **kwargs: _orig_httpx_init(
    self, *args, **{k: v for k, v in kwargs.items() if k != "app"}
)

from fastapi.testclient import TestClient

# Ensure local imports work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.sanitizer import sanitizer
from core.engine import engine
from core.tre import tre
from core.rbac import rbac
from core.review_ledger import ledger
from core.grounded_rag import assistant
from app import app
import server.main as server_app

client_app = TestClient(app)
client_server = TestClient(server_app.app)

# ============================================================================
# 1. DATA INGESTION & ZERO-TRUST SANITIZATION TESTS
# ============================================================================

def test_01_raw_source_ingestion_schema():
    """Validates multi-source ingestion formats and field completeness."""
    sources = engine.load_raw_sources()
    assert len(sources["git_commits"]) >= 10, "Must have at least 10 commits"
    assert len(sources["pull_requests"]) >= 3, "Must have pull requests"
    assert len(sources["slack_channels"]) >= 3, "Must have slack channels"
    assert len(sources["jira_issues"]) >= 5, "Must have jira issues"

    # Validate commit structure
    first_commit = sources["git_commits"][0]
    for key in ["sha", "timestamp", "author", "message", "branch", "status"]:
        assert key in first_commit, f"Missing required commit key: {key}"

def test_02_presidio_sanitizer_secret_scrubbing_exhaustive():
    """Exhaustively tests redaction of Stripe keys, AWS tokens, passwords, and PII."""
    raw_payloads = [
        ("Secret key is sk_mock_stripe_key_1234567890abcdef", "[REDACTED_STRIPE_SECRET_KEY]"),
        ("Webhook is whsec_938471928374abcdef", "[REDACTED_WEBHOOK_SIGNING_SECRET]"),
        ("AWS token AKIAIOSFODNN7EXAMPLE", "[REDACTED_AWS_ACCESS_KEY]"),
        ("Database password: SuperSecretPassword123!", "[REDACTED_CREDENTIAL]"),
        ("Contact lead at developer.lead@valerion.dev for details", "[REDACTED_EMAIL]"),
        ("Q4 budget is $45,000/mo and salary is $160k", "[REDACTED_FINANCIAL_FIGURE]")
    ]

    for raw, expected_token in raw_payloads:
        cleaned, count = sanitizer.sanitize_text(raw, role="engineering")
        assert expected_token in cleaned, f"Expected {expected_token} in '{cleaned}'"
        assert count >= 1

def test_03_contractor_role_confidential_masking():
    """Validates contractor boundary masking of salaries and executive budget threads."""
    exec_chat = "Confidential executive review: budget is $150k and salary is $120k"
    cleaned, count = sanitizer.sanitize_text(exec_chat, role="contractor")
    assert "[REDACTED_RESTRICTED_ACCESS]" in cleaned or "[REDACTED_FINANCIAL_BUDGET]" in cleaned or "[REDACTED_FINANCIAL_FIGURE]" in cleaned
    assert count >= 1

# ============================================================================
# 2. TEMPORAL STATE RECONSTRUCTION & CAUSAL GRAPH TESTS
# ============================================================================

def test_04_temporal_ordering_and_adr_extraction():
    """Validates chronological ordering and implicit ADR mining."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)

    # Check chronological ordering
    timestamps = [e["timestamp"] for e in state["timeline"]]
    assert timestamps == sorted(timestamps), "Timeline events must be strictly sorted chronologically"

    # Check ADR mining
    assert len(state["architecture_decisions"]) >= 1
    jwt_adr = next((adr for adr in state["architecture_decisions"] if "JWT" in adr["title"]), None)
    assert jwt_adr is not None, "Must extract Custom JWT ADR"
    assert "regulatory" in jwt_adr["decision"] or "HIPAA" in jwt_adr["decision"] or "cookie" in jwt_adr["decision"]

def test_05_causal_dependency_graph_edges():
    """Validates graph node and edge generation between Jira tickets and Git commits."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)

    assert len(state["graph_nodes"]) > 15
    assert len(state["graph_edges"]) >= 2

    # Check that CORE-101 or AUTH-204 links to a commit
    auth_edge = next((e for e in state["graph_edges"] if "AUTH-204" in e["from"]), None)
    assert auth_edge is not None, "AUTH-204 must have a resolves edge"
    assert auth_edge["relation"] == "resolves"

# ============================================================================
# 3. TEMPORAL RECONCILIATION ENGINE (TRE) TESTS
# ============================================================================

def test_06_tre_contradiction_detection_and_citations():
    """Validates TRE detection of the Redis vs Memcached contradiction and citation pinning."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)

    assert tre_data["grounded_claim_ratio"] == 1.0, "All assertions must be citation-backed"
    assert tre_data["total_conflicts"] >= 1, "Must detect the Redis vs Memcached conflict"

    conflict = tre_data["detected_conflicts"][0]
    assert conflict["status"] == "CONFLICT_DETECTED"
    assert "Memcached" in conflict["statement"]
    assert "slack" in conflict["citation_a"]["source"]
    assert "pr" in conflict["citation_b"]["source"]

def test_07_tre_knowledge_gap_surfacing():
    """Validates detection of undocumented parameters as missing evidence gaps."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)

    assert tre_data["total_gaps"] >= 1
    gap = tre_data["knowledge_gaps"][0]
    assert gap["parameter"] == "X_INTERNAL_SYNC_SALT"
    assert gap["status"] == "MISSING_EVIDENCE"
    assert gap["severity"] == "CRITICAL_BLOCKER"

# ============================================================================
# 4. HUMAN-IN-THE-LOOP (HITL) REVIEW & CRYPTOGRAPHIC LEDGER TESTS
# ============================================================================

def test_08_hitl_conflict_resolution_and_notes():
    """Validates binding human conflict resolution and personal tacit context capture."""
    record = ledger.resolve_conflict(
        conflict_id="conflict_01",
        decision="Redis Cluster Confirmed",
        notes="Spike proved Memcached had no distributed locking",
        approver="Prince Kumar"
    )
    assert record["decision"] == "Redis Cluster Confirmed"
    assert "conflict_01" in ledger.resolved_conflicts

    note = ledger.add_tacit_note("Prince Kumar", "Staging DB sync salt must be placed in Vault")
    assert note["author"] == "Prince Kumar"
    assert any(n["id"] == note["id"] for n in ledger.tacit_notes)

def test_09_tamper_evident_sha256_signoff():
    """Validates SHA-256 certificate generation and cryptographic uniqueness."""
    cert1 = ledger.sign_handover("Prince Kumar", "Team Lead & AI Architect", "ContinuumAI Project")
    assert len(cert1["certificate_hash"]) == 64
    assert cert1["status"] == "OFFICIALLY_SIGNED_AND_VERIFIED"
    assert "BLOCK-" in cert1["audit_ledger_block"]

    # Verify that different signer produces different hash
    cert2 = ledger.sign_handover("Yash Sharma", "Full-Stack Specialist", "ContinuumAI Project")
    assert cert1["certificate_hash"] != cert2["certificate_hash"]

# ============================================================================
# 5. ROLE-BASED ACCESS CONTROL (RBAC) PROJECTIONS
# ============================================================================

def test_10_rbac_role_lenses():
    """Validates dynamic projection generation across Engineering, PM, and Contractor."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)

    # 1. Engineering
    eng_view = rbac.get_role_handover("engineering", state, tre_data)
    assert "Tier-1" in eng_view["clearance_level"]
    assert len(eng_view["first_30_days_tasks"]) == 4
    assert eng_view["confidential_secrets_hidden"] is False

    # 2. Product Manager
    pm_view = rbac.get_role_handover("product", state, tre_data)
    assert "Tier-2" in pm_view["clearance_level"]
    assert pm_view["confidential_secrets_hidden"] is True

    # 3. External Contractor
    con_view = rbac.get_role_handover("contractor", state, tre_data)
    assert "Tier-3" in con_view["clearance_level"]
    assert con_view["confidential_secrets_hidden"] is True

    # 4. Unknown fallback role defaults to contractor restricted view
    fallback_view = rbac.get_role_handover("unknown_external_role", state, tre_data)
    assert fallback_view["confidential_secrets_hidden"] is True

# ============================================================================
# 6. GROUNDED RAG ASSISTANT & ANTI-HALLUCINATION BOUNDARY
# ============================================================================

def test_11_grounded_rag_cited_answers():
    """Validates accurate cited answers for ground-truth architectural queries."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    review_state = ledger.get_review_state()

    # Query 1: Custom Auth
    res_auth = assistant.answer_query("Why do we use custom auth instead of Supabase?", state, tre_data, review_state)
    assert res_auth["grounded"] is True
    assert res_auth["confidence"] >= 0.95
    assert len(res_auth["citations"]) >= 1
    assert "HIPAA" in res_auth["answer"]

    # Query 2: Redis vs Memcached
    res_cache = assistant.answer_query("Why was Memcached dropped for Redis?", state, tre_data, review_state)
    assert res_cache["grounded"] is True
    assert "Redlock" in res_cache["answer"] or "locking" in res_cache["answer"]

    # Query 3: Sync salt
    res_salt = assistant.answer_query("What is the sync salt blocker?", state, tre_data, review_state)
    assert res_salt["grounded"] is True
    assert "X_INTERNAL_SYNC_SALT" in res_salt["answer"]

def test_12_grounded_rag_refuses_hallucination():
    """Validates strict refusal to hallucinate when asked about unrecorded facts."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    review_state = ledger.get_review_state()

    ungrounded_query = "What is the Bitcoin cold storage private seed phrase?"
    res_fake = assistant.answer_query(ungrounded_query, state, tre_data, review_state)
    assert res_fake["grounded"] is False
    assert res_fake["confidence"] == 0.0
    assert len(res_fake["citations"]) == 0
    assert "refuses to speculate" in res_fake["answer"]

# ============================================================================
# 7. FASTAPI GATEWAY & MICROSERVICE ENDPOINT INTEGRATION TESTS
# ============================================================================

def test_13_app_gateway_http_endpoints():
    """Validates all HTTP routes on the main app gateway."""
    # GET / (HTML Dashboard)
    res_home = client_app.get("/")
    assert res_home.status_code == 200
    assert "ContinuumAI" in res_home.text
    assert "VALERION CODERS" in res_home.text.upper()

    # GET /api/status
    res_status = client_app.get("/api/status")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "online"

    # GET /api/sources
    res_sources = client_app.get("/api/sources")
    assert res_sources.status_code == 200
    assert res_sources.json()["raw_counts"]["git_commits"] >= 10

    # GET /api/reconstruct
    res_recon = client_app.get("/api/reconstruct")
    assert res_recon.status_code == 200
    assert len(res_recon.json()["timeline"]) > 10

    # GET /api/verify
    res_verify = client_app.get("/api/verify")
    assert res_verify.status_code == 200
    assert res_verify.json()["grounded_claim_ratio"] == 1.0

    # POST /api/resolve_conflict
    res_conflict = client_app.post("/api/resolve_conflict", json={
        "conflict_id": "conflict_01",
        "decision": "Redis Confirmed",
        "notes": "Verified by Lead",
        "approver": "Prince Kumar"
    })
    assert res_conflict.status_code == 200

    # POST /api/add_note
    res_note = client_app.post("/api/add_note", json={
        "author": "Yash Sharma",
        "content": "Verify UI stepper before release"
    })
    assert res_note.status_code == 200

    # POST /api/sign
    res_sign = client_app.post("/api/sign", json={
        "signer_name": "Prince Kumar",
        "signer_role": "Lead Architect"
    })
    assert res_sign.status_code == 200
    assert "certificate_hash" in res_sign.json()

    # GET /api/handover/engineering
    res_role = client_app.get("/api/handover/engineering")
    assert res_role.status_code == 200
    assert "Tier-1" in res_role.json()["clearance_level"]

    # POST /api/ask
    res_ask = client_app.post("/api/ask", json={"query": "Why custom auth?"})
    assert res_ask.status_code == 200
    assert res_ask.json()["grounded"] is True

def test_14_server_microservice_direct_endpoints():
    """Validates that the server microservice runs standalone on Vercel."""
    res_status = client_server.get("/api/status")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "online"

    res_verify = client_server.get("/api/verify")
    assert res_verify.status_code == 200
    assert res_verify.json()["total_conflicts"] >= 1

    res_ask = client_server.post("/api/ask", json={"query": "Why was Memcached dropped?"})
    assert res_ask.status_code == 200
    assert "Redlock" in res_ask.json()["answer"] or "locking" in res_ask.json()["answer"]

def test_15_enterprise_export_and_cert_verification():
    """Validates markdown handover export and public SHA-256 certificate verification."""
    # Test Markdown Export
    res_exp_md = client_app.get("/api/export/markdown")
    assert res_exp_md.status_code == 200
    assert "Project Handover & Continuity Briefing" in res_exp_md.json()["content"]
    assert "First 30 Days Actionable Continuity Checklist" in res_exp_md.json()["content"]

    # Test JSON Export
    res_exp_json = client_app.get("/api/export/json")
    assert res_exp_json.status_code == 200
    assert "ContinuumAI Handover OS" in res_exp_json.json()["platform"]

    # Test Sign and Verify Cert
    res_sign = client_app.post("/api/sign", json={
        "signer_name": "Prince Kumar",
        "signer_role": "Team Lead & AI Architect"
    })
    cert_hash = res_sign.json()["certificate_hash"]
    
    res_verify = client_app.get(f"/api/verify_cert/{cert_hash}")
    assert res_verify.status_code == 200
    assert res_verify.json()["valid"] is True
    assert "Prince Kumar" in res_verify.json()["signature"]["signer_name"]

def test_16_custom_telemetry_ingestion_and_sanitization():
    """Validates custom user telemetry ingestion with Presidio secret scrubbing."""
    custom_payload = {
        "commits_text": "feat(secret): test sk_mock_stripe_key_111122223333 commit",
        "slack_text": "Lead: Our confidential client is Alex"
    }
    res_ingest = client_app.post("/api/ingest_custom", json=custom_payload)
    assert res_ingest.status_code == 200
    assert res_ingest.json()["status"] == "success"
    assert res_ingest.json()["redactions_applied"] >= 1

if __name__ == "__main__":
    pytest.main(["-v", __file__])
