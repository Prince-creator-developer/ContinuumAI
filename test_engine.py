"""
ContinuumAI - Automated Unit & Integration Test Suite
Validates the 5-Step Core Engine, Temporal Reconciliation Engine, Presidio Sanitizer,
RBAC Projections, and Grounded RAG Assistant.
"""

import pytest
import os
import sys

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

def test_01_raw_source_ingestion():
    """Validates that multi-source digital exhaust is parsed correctly."""
    sources = engine.load_raw_sources()
    assert len(sources["git_commits"]) >= 10, "Should load at least 10 git commits"
    assert len(sources["pull_requests"]) >= 3, "Should load pull requests"
    assert len(sources["slack_channels"]) >= 3, "Should load slack channels"
    assert len(sources["jira_issues"]) >= 5, "Should load jira tasks"

def test_02_presidio_zero_trust_sanitization():
    """Validates that secret API keys, Stripe tokens, and PII are redacted."""
    raw_secret_text = "Stripe secret is sk_mock_stripe_key_999988887777 and email is lead@valerion.dev with salary $150k"
    cleaned, count = sanitizer.sanitize_text(raw_secret_text, role="contractor")
    assert "[REDACTED_STRIPE_SECRET_KEY]" in cleaned
    assert "[REDACTED_EMAIL]" in cleaned
    assert "sk_mock_" not in cleaned
    assert count >= 2

def test_03_temporal_state_reconstruction():
    """Validates chronological event sequencing and implicit ADR extraction."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    assert len(state["timeline"]) >= 15
    assert len(state["architecture_decisions"]) >= 1
    assert any("JWT" in adr["title"] for adr in state["architecture_decisions"])
    assert len(state["active_blockers"]) >= 1
    assert any("OPS-412" == b["key"] for b in state["active_blockers"])

def test_04_tre_contradiction_detection():
    """Validates that cross-source contradictions and knowledge gaps are caught."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)

    assert tre_data["grounded_claim_ratio"] == 1.0, "All claims must be citation-backed"
    assert tre_data["total_conflicts"] >= 1, "Must detect the Redis vs Memcached conflict"
    conflict = tre_data["detected_conflicts"][0]
    assert conflict["status"] == "CONFLICT_DETECTED"
    assert "Memcached" in conflict["statement"]

    assert tre_data["total_gaps"] >= 1, "Must detect the missing salt runbook gap"
    gap = tre_data["knowledge_gaps"][0]
    assert gap["parameter"] == "X_INTERNAL_SYNC_SALT"

def test_05_role_governed_projections():
    """Validates dynamic role filtering (Engineering vs PM vs Contractor)."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)

    eng_view = rbac.get_role_handover("engineering", state, tre_data)
    assert "Tier-1" in eng_view["clearance_level"]
    assert len(eng_view["first_30_days_tasks"]) == 4

    contractor_view = rbac.get_role_handover("contractor", state, tre_data)
    assert "Tier-3" in contractor_view["clearance_level"]
    assert contractor_view["confidential_secrets_hidden"] is True

def test_06_hitl_review_and_cryptographic_signoff():
    """Validates human contradiction resolution and SHA-256 certificate generation."""
    res = ledger.resolve_conflict("conflict_01", "Redis Cluster Retained", "Confirmed by Lead", "Prince Kumar")
    assert res["decision"] == "Redis Cluster Retained"

    note = ledger.add_tacit_note("Prince Kumar", "Check Redlock expiry before restarting sync daemon")
    assert note["author"] == "Prince Kumar"

    cert = ledger.sign_handover("Prince Kumar", "Team Lead & AI Architect")
    assert len(cert["certificate_hash"]) == 64, "SHA-256 hash must be 64 characters"
    assert cert["status"] == "OFFICIALLY_SIGNED_AND_VERIFIED"
    assert "BLOCK-" in cert["audit_ledger_block"]

def test_07_grounded_rag_assistant():
    """Validates strictly grounded Q&A with citations and anti-hallucination refusal."""
    raw = engine.load_raw_sources()
    state = engine.reconstruct_project_state(raw)
    tre_data = tre.verify_and_reconcile(raw, state)
    review_state = ledger.get_review_state()

    # Grounded query
    auth_resp = assistant.answer_query("Why do we use custom auth instead of Supabase?", state, tre_data, review_state)
    assert auth_resp["grounded"] is True
    assert len(auth_resp["citations"]) >= 1
    assert "HIPAA" in auth_resp["answer"]

    # Ungrounded query (Refusal to hallucinate)
    fake_resp = assistant.answer_query("What is the quantum encryption protocol key?", state, tre_data, review_state)
    assert fake_resp["grounded"] is False
    assert "refuses to speculate" in fake_resp["answer"]
    assert len(fake_resp["citations"]) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
