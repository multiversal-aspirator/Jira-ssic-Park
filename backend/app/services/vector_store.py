import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from pathlib import Path
from datetime import datetime, timezone
from app.utils.logger import get_logger

# Suppress the noisy "No ONNX providers provided" debug warning from ChromaDB's
# default embedding function — it fires once per upsert/query otherwise.
logging.getLogger("chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2").setLevel(logging.WARNING)

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

    def _normalize_pr(self, repo: str, pr: dict) -> tuple[str, str, dict]:
        """Return (doc_id, text, metadata) from a GitHub PR dict."""
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
        return doc_id, text, metadata

    def ingest_pr(self, repo: str, pr: dict):
        """Ingest a single PR. Prefer ingest_prs_batch for multiple PRs."""
        doc_id, text, metadata = self._normalize_pr(repo, pr)
        self.pull_requests.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_prs_batch(self, repo: str, prs: list[dict]):
        """Ingest multiple GitHub PRs in a single ChromaDB call."""
        if not prs:
            return
        ids, documents, metadatas = [], [], []
        for pr in prs:
            doc_id, text, metadata = self._normalize_pr(repo, pr)
            ids.append(doc_id)
            documents.append(text)
            metadatas.append(metadata)
        self.pull_requests.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"[VectorStore] Batch-ingested {len(ids)} PRs for repo {repo}")

    def _normalize_jira_issue_fields(self, project_key: str, issue: dict) -> tuple[str, str, dict]:
        """Return (doc_id, text, metadata) from either a raw or normalized Jira issue dict."""
        key = issue.get("key", "")
        if isinstance(issue.get("fields"), dict):
            fields = issue["fields"]
            summary = fields.get("summary", "") or ""
            status = (fields.get("status") or {}).get("name", "Unknown") or "Unknown"
            assignee = ((fields.get("assignee") or {}).get("displayName")) or "Unassigned"
            priority = ((fields.get("priority") or {}).get("name")) or "None"
        else:
            summary = issue.get("summary", "") or ""
            status = issue.get("status", "Unknown") or "Unknown"
            assignee = issue.get("assignee", "Unassigned") or "Unassigned"
            priority = issue.get("priority", "None") or "None"

        doc_id = f"{project_key}:{key}"
        text = f"[{key}] {summary} | Status: {status} | Assignee: {assignee} | Priority: {priority}"
        metadata = {
            "project": project_key,
            "key": key,
            "status": str(status),
            "assignee": str(assignee),
            "priority": str(priority),
            "type": "jira_issue",
        }
        return doc_id, text, metadata

    def ingest_jira_issue(self, project_key: str, issue: dict):
        """Ingest a single Jira issue. Prefer ingest_jira_issues_batch for multiple issues."""
        doc_id, text, metadata = self._normalize_jira_issue_fields(project_key, issue)
        self.jira_tickets.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_jira_issues_batch(self, project_key: str, issues: list[dict]):
        """Ingest multiple Jira issues in a single ChromaDB call (much faster than N individual upserts)."""
        if not issues:
            return
        # Deduplicate by doc_id (last write wins for same key)
        seen: dict[str, tuple[str, dict]] = {}
        for issue in issues:
            doc_id, text, metadata = self._normalize_jira_issue_fields(project_key, issue)
            seen[doc_id] = (text, metadata)
        ids = list(seen.keys())
        documents = [v[0] for v in seen.values()]
        metadatas = [v[1] for v in seen.values()]
        self.jira_tickets.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"[VectorStore] Batch-ingested {len(ids)} Jira issues for project {project_key}")

    def _normalize_teams_message(self, channel: str, message: dict) -> tuple[str, str, dict]:
        """Return (doc_id, text, metadata) from a Teams message dict."""
        msg_id = message.get("id") or f"{message.get('day','')}-{message.get('timestamp','')}-{message.get('speaker','')}"
        doc_id = f"{channel}:{msg_id}"

        if "body" in message and isinstance(message.get("body"), dict):
            body = message["body"].get("content", "")
        elif "content" in message:
            body = message["content"]
        else:
            body = str(message.get("body", ""))

        if "from" in message and isinstance(message.get("from"), dict):
            sender = message["from"].get("user", {}).get("displayName", "Unknown")
        elif "speaker" in message:
            sender = message["speaker"]
        else:
            sender = "Unknown"

        text = f"[Teams:{channel}] {sender}: {body[:1000]}"
        metadata = {
            "channel": channel,
            "sender": sender,
            "created": message.get("createdDateTime", message.get("created", "")),
            "type": "teams_message",
        }
        return doc_id, text, metadata

    def ingest_teams_message(self, channel: str, message: dict):
        """Ingest a single Teams message. Prefer ingest_teams_messages_batch for multiple messages."""
        doc_id, text, metadata = self._normalize_teams_message(channel, message)
        self.teams_messages.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def ingest_teams_messages_batch(self, channel: str, messages: list[dict]):
        """Ingest multiple Teams messages in a single ChromaDB call."""
        if not messages:
            return
        ids, documents, metadatas = [], [], []
        for message in messages:
            doc_id, text, metadata = self._normalize_teams_message(channel, message)
            ids.append(doc_id)
            documents.append(text)
            metadatas.append(metadata)
        self.teams_messages.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"[VectorStore] Batch-ingested {len(ids)} Teams messages for channel {channel}")

    def ingest_teams_transcript(self, channel: str, transcript: dict):
        """Ingest a meeting transcript into the vector store."""
        transcript_id = transcript.get("transcript_id", str(datetime.now(timezone.utc).timestamp()))
        content = transcript.get("content", "")

        # Split long transcripts into chunks for better retrieval
        chunks = self._chunk_text(content, max_chars=1500)
        for i, chunk in enumerate(chunks):
            doc_id = f"{channel}:transcript:{transcript_id}:chunk-{i}"
            text = f"[Teams Transcript:{channel}] {chunk}"
            metadata = {
                "channel": channel,
                "transcript_id": transcript_id,
                "source_file": transcript.get("source_file", ""),
                "created": transcript.get("created", ""),
                "chunk_index": i,
                "type": "teams_transcript",
            }
            self.meeting_notes.upsert(ids=[doc_id], documents=[text], metadatas=[metadata])

    def _chunk_text(self, text: str, max_chars: int = 1500) -> list[str]:
        """Split text into chunks by line boundaries."""
        lines = text.split("\n")
        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > max_chars and current:
                chunks.append(current.strip())
                current = ""
            current += line + "\n"
        if current.strip():
            chunks.append(current.strip())
        return chunks if chunks else [text[:max_chars]]

    def ingest_report(self, project_key: str, report_type: str, content: str):
        doc_id = f"{project_key}:{report_type}:{datetime.now(timezone.utc).isoformat()}"
        metadata = {
            "project": project_key,
            "report_type": report_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "type": "report",
        }
        self.reports.upsert(ids=[doc_id], documents=[content], metadatas=[metadata])

    def search(self, query: str, collection_name: str | None = None, n_results: int = 10) -> list[dict]:
        """Semantic search across one or all collections."""
        results = []

        if collection_name:
            try:
                collections = [self.client.get_collection(collection_name)]
            except Exception:
                logger.warning(f"[VectorStore] Collection '{collection_name}' not found — returning empty results")
                return []
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
