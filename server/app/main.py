"""
ContinuumAI - Knowledge Handover & Organizational Continuity Engine
FastAPI Core Entrypoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ContinuumAI Knowledge Handover Engine",
    description="Autonomous Project State Reconstruction from Disparate Digital Exhaust with Permission-Aware Evidence Graphs.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ContinuumAI Core Engine",
        "round": "Round 1 - The Plan (Validated)",
        "team": "Valerion Coders",
        "workflow": [
            "01_connect",
            "02_reconstruct",
            "03_verify",
            "04_review",
            "05_handover"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "temporal_reconciliation_engine": "ready"}
