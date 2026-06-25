import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "vector_db"


class VectorStore:
    """ChromaDB-backed vector store for project knowledge."""

    def __init__(self):
        DB_PATH.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(DB_PATH),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._ensure_collections()

    def _ensure_collections(self):
        self.commits = self.client.get_or_create_collection("github_commits")
        self.pull_requests = self.client.get_or_create_collection("github_prs")
        self.jira_tickets = self.client.get_or_create_collection("jira_tickets")
        self.teams_messages = self.client.get_or_create_collection("teams_messages")
        self.meeting_notes = self.client.get_or_create_collection("meeting_notes")
        self.reports = self.client.get_or_create_collection("generated_reports")

    def ingest_commit(self, repo: str, commit: dict):
        doc_id = f"{repo}:{commit.get('sha', '')[:8]}"
        text = f"[{repo}] {commit.get('commit', {}).get('message', '')}"
        metadata = {
            "repo": repo,
            "author": commit.get("commit", {}).get("author", {}).get("name", ""),
            "date": commit.get("commit", {}).get("author", {}).get("date", ""),
            "sha": commit.get("sha", ""),
            "type": "commit",
        }
        self.commits.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_pr(self, repo: str, pr: dict):
        doc_id = f"{repo}:pr-{pr.get('number', 0)}"
        text = f"[{repo}] PR #{pr.get('number')}: {pr.get('title', '')} - {pr.get('body', '')[:500]}"
        metadata = {
            "repo": repo,
            "number": pr.get("number", 0),
            "state": pr.get("state", ""),
            "author": pr.get("user", {}).get("login", ""),
            "created_at": pr.get("created_at", ""),
            "type": "pull_request",
        }
        self.pull_requests.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_jira_issue(self, project_key: str, issue: dict):
        key = issue.get("key", "")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")
        status = fields.get("status", {}).get("name", "")
        assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
        priority = (fields.get("priority") or {}).get("name", "")

        doc_id = f"{project_key}:{key}"
        text = f"[{key}] {summary} | Status: {status} | Assignee: {assignee} | Priority: {priority}"
        metadata = {
            "project": project_key,
            "key": key,
            "status": status,
            "assignee": assignee,
            "priority": priority,
            "type": "jira_issue",
        }
        self.jira_tickets.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_teams_message(self, channel: str, message: dict):
        msg_id = message.get("id", str(datetime.utcnow().timestamp()))
        doc_id = f"{channel}:{msg_id}"
        body = message.get("body", {}).get("content", "") if isinstance(message.get("body"), dict) else str(message.get("body", ""))
        sender = message.get("from", {}).get("user", {}).get("displayName", "Unknown") if isinstance(message.get("from"), dict) else "Unknown"

        text = f"[Teams:{channel}] {sender}: {body[:1000]}"
        metadata = {
            "channel": channel,
            "sender": sender,
            "created": message.get("createdDateTime", ""),
            "type": "teams_message",
        }
        self.teams_messages.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_report(self, project_key: str, report_type: str, content: str):
        doc_id = f"{project_key}:{report_type}:{datetime.utcnow().isoformat()}"
        metadata = {
            "project": project_key,
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "type": "report",
        }
        self.reports.upsert(ids=[doc_id], documents=[content], metadatas=[metadata])

    def search(self, query: str, collection_name: str | None = None, n_results: int = 10) -> list[dict]:
        """Semantic search across one or all collections."""
        results = []

        if collection_name:
            collections = [self.client.get_collection(collection_name)]
        else:
            collections = [
                self.commits, self.pull_requests, self.jira_tickets,
                self.teams_messages, self.meeting_notes, self.reports,
            ]

        for col in collections:
            try:
                if col.count() == 0:
                    continue
                res = col.query(query_texts=[query], n_results=min(n_results, col.count()))
                for i, doc in enumerate(res["documents"][0]):
                    results.append({
                        "document": doc,
                        "metadata": res["metadatas"][0][i] if res["metadatas"] else {},
                        "distance": res["distances"][0][i] if res.get("distances") else None,
                        "collection": col.name,
                    })
            except Exception as e:
                logger.warning(f"Search failed on {col.name}: {e}")

        # Sort by distance (lower = more relevant)
        results.sort(key=lambda x: x.get("distance") or 999)
        return results[:n_results]

    def get_project_context(self, project_key: str, n_results: int = 20) -> str:
        """Get all relevant context for a project as a single string for RAG."""
        results = self.search(project_key, n_results=n_results)
        return "\n".join(r["document"] for r in results)

    def clear_all(self):
        """Delete all data from all collections."""
        for col in [self.commits, self.pull_requests, self.jira_tickets,
                    self.teams_messages, self.meeting_notes, self.reports]:
            ids = col.get()["ids"]
            if ids:
                col.delete(ids=ids)
        logger.info("[VectorStore] All collections cleared")

    def clear_project(self, project_key: str):
        """Delete all data for a specific project."""
        for col in [self.commits, self.pull_requests, self.jira_tickets,
                    self.teams_messages, self.meeting_notes, self.reports]:
            try:
                results = col.get(where={"project": project_key})
                if results["ids"]:
                    col.delete(ids=results["ids"])
            except Exception:
                # Collection may not have 'project' metadata field
                pass
        logger.info(f"[VectorStore] Cleared data for project: {project_key}")

    def get_stats(self) -> dict:
        """Get collection counts."""
        return {
            "commits": self.commits.count(),
            "pull_requests": self.pull_requests.count(),
            "jira_tickets": self.jira_tickets.count(),
            "teams_messages": self.teams_messages.count(),
            "meeting_notes": self.meeting_notes.count(),
            "reports": self.reports.count(),
            "total": sum([
                self.commits.count(), self.pull_requests.count(),
                self.jira_tickets.count(), self.teams_messages.count(),
                self.meeting_notes.count(), self.reports.count(),
            ]),
        }


_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
