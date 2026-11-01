"""
ContinuumAI - Temporal State Reconstructor & Event Graph Engine
Ingests multi-source digital exhaust and constructs a chronological Project State Graph.
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

class KnowledgeEngine:
    def __init__(self, data_dir: str = None):
        if not data_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data", "synthetic_project_dump")
        self.data_dir = data_dir

    def load_raw_sources(self) -> Dict[str, Any]:
        """Loads and parses raw multi-source files."""
        commits_file = os.path.join(self.data_dir, "git_commits.json")
        prs_file = os.path.join(self.data_dir, "pull_requests.json")
        slack_file = os.path.join(self.data_dir, "slack_channels.json")
        jira_file = os.path.join(self.data_dir, "jira_issues.json")

        commits = []
        prs = []
        slack = []
        jira = []

        if os.path.exists(commits_file):
            with open(commits_file, "r", encoding="utf-8") as f:
                commits = json.load(f)
        if os.path.exists(prs_file):
            with open(prs_file, "r", encoding="utf-8") as f:
                prs = json.load(f)
        if os.path.exists(slack_file):
            with open(slack_file, "r", encoding="utf-8") as f:
                slack = json.load(f)
        if os.path.exists(jira_file):
            with open(jira_file, "r", encoding="utf-8") as f:
                jira = json.load(f)

        return {
            "git_commits": commits,
            "pull_requests": prs,
            "slack_channels": slack,
            "jira_issues": jira
        }

    def reconstruct_project_state(self, sources: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Reconstructs project chronology, extracted ADRs, in-flight branches,
        and directional dependencies from raw sources.
        """
        if sources is None:
            sources = self.load_raw_sources()

        timeline_events = []
        nodes = []
        edges = []

        # 1. Process Git Commits
        for c in sources.get("git_commits", []):
            event = {
                "id": f"commit_{c['sha']}",
                "type": "commit",
                "timestamp": c["timestamp"],
                "title": c["message"],
                "author": c["author"],
                "status": c.get("status", "merged"),
                "source": f"git:commit/{c['sha']}",
                "files": c.get("files_changed", [])
            }
            timeline_events.append(event)
            nodes.append({
                "id": event["id"],
                "label": f"Commit {c['sha'][:7]}",
                "category": "Git Commit",
                "detail": c["message"]
            })

        # 2. Process Pull Requests & ADRs
        adrs = []
        for pr in sources.get("pull_requests", []):
            event = {
                "id": f"pr_{pr['pr_number']}",
                "type": "pull_request",
                "timestamp": pr.get("merged_at") or pr["created_at"],
                "title": f"PR #{pr['pr_number']}: {pr['title']}",
                "author": pr["author"],
                "status": pr["status"],
                "source": f"github:pr/{pr['pr_number']}"
            }
            timeline_events.append(event)
            nodes.append({
                "id": event["id"],
                "label": f"PR #{pr['pr_number']}",
                "category": "Pull Request",
                "detail": pr["title"]
            })

            # Check for implicit ADRs in discussion
            for msg in pr.get("discussion", []):
                if "ADR" in msg["comment"] or "Decided" in msg["comment"] or "regulatory" in msg["comment"]:
                    adrs.append({
                        "id": f"adr_{pr['pr_number']}",
                        "title": pr["title"],
                        "decision": msg["comment"],
                        "citation": f"PR #{pr['pr_number']} @ {msg['timestamp']}",
                        "status": "Accepted & Implemented"
                    })

        # 3. Process Jira Issues
        blockers = []
        for issue in sources.get("jira_issues", []):
            event = {
                "id": f"jira_{issue['key']}",
                "type": "jira_issue",
                "timestamp": issue.get("resolution_date") or "2026-10-20T00:00:00Z",
                "title": f"{issue['key']}: {issue['summary']}",
                "author": issue["assignee"],
                "status": issue["status"],
                "source": f"jira:issue/{issue['key']}"
            }
            timeline_events.append(event)
            nodes.append({
                "id": event["id"],
                "label": issue["key"],
                "category": "Jira Task",
                "detail": issue["summary"]
            })

            if "Blocker" in issue.get("status", "") or issue.get("priority") == "Highest" and not issue.get("resolution_date"):
                blockers.append({
                    "key": issue["key"],
                    "summary": issue["summary"],
                    "notes": issue.get("notes", "No notes"),
                    "assignee": issue["assignee"]
                })

            # Edge connections
            for linked_sha in issue.get("linked_commits", []):
                edges.append({
                    "from": f"jira_{issue['key']}",
                    "to": f"commit_{linked_sha}",
                    "relation": "resolves"
                })

        # Sort timeline chronologically
        timeline_events.sort(key=lambda x: x["timestamp"])

        return {
            "timeline": timeline_events,
            "architecture_decisions": adrs,
            "active_blockers": blockers,
            "graph_nodes": nodes,
            "graph_edges": edges,
            "total_sources_ingested": len(timeline_events)
        }

engine = KnowledgeEngine()
