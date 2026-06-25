"""RAG-powered Q&A endpoint — answers project questions using vector store context."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.vector_store import get_vector_store
from app.services.llm_service import get_chat_model, parse_llm_json
from app.services.event_processor import get_event_log, get_queue_status
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["intelligence"])


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Natural language question about the project")
    project_key: str | None = Field(None, description="Optional project key to scope the search")


class QuestionResponse(BaseModel):
    answer: str
    sources: list[dict]
    confidence: str


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a natural language question about your project. Uses RAG over the vector store."""
    logger.info(f"[RAG] Question: {request.question}")

    store = get_vector_store()

    # Semantic search for relevant context
    query = request.question
    if request.project_key:
        query = f"{request.project_key}: {request.question}"

    results = store.search(query, n_results=15)

    if not results:
        return QuestionResponse(
            answer="I don't have enough project data to answer this question. "
                   "Please ensure data has been ingested via webhooks or manual sync.",
            sources=[],
            confidence="low",
        )

    # Build RAG context
    context_docs = "\n---\n".join(r["document"] for r in results)

    # Ask LLM with context
    llm = get_chat_model()
    prompt = f"""You are a project intelligence assistant. Answer the user's question based ONLY on the project data provided below.

If the data doesn't contain enough information to answer confidently, say so.

PROJECT DATA:
{context_docs}

QUESTION: {request.question}

Respond with a clear, concise answer. Reference specific tickets, PRs, or messages when relevant."""

    response = await llm.ainvoke(prompt)

    return QuestionResponse(
        answer=response.content,
        sources=[{"document": r["document"][:200], "collection": r["collection"]} for r in results[:5]],
        confidence="high" if len(results) >= 5 else "medium" if len(results) >= 2 else "low",
    )


@router.post("/sync")
async def manual_sync(project_key: str, github_repo: str | None = None, teams_channel: str | None = None):
    """Manually trigger a full sync of project data into the vector store."""
    logger.info(f"[Sync] Manual sync triggered for {project_key}")

    store = get_vector_store()
    synced = {"jira": 0, "github": 0, "teams": 0}

    # Sync Jira
    try:
        from app.services.jira_service import JiraService
        jira = JiraService()
        data = await jira.get_sprint_issues(project_key)
        for issue in data.get("issues", []):
            store.ingest_jira_issue(project_key, issue)
            synced["jira"] += 1
    except Exception as e:
        logger.warning(f"[Sync] Jira sync failed: {e}")

    # Sync GitHub
    if github_repo:
        try:
            from app.services.github_service import GitHubService
            gh = GitHubService()
            prs = await gh.get_open_prs(github_repo)
            for pr in prs:
                store.ingest_pr(github_repo, pr)
                synced["github"] += 1
        except Exception as e:
            logger.warning(f"[Sync] GitHub sync failed: {e}")

    # Sync Teams
    if teams_channel:
        try:
            from app.services.teams_service import TeamsService
            teams = TeamsService()
            messages = await teams.get_channel_messages(teams_channel, limit=50)
            for msg in messages:
                store.ingest_teams_message(teams_channel, msg)
                synced["teams"] += 1
        except Exception as e:
            logger.warning(f"[Sync] Teams sync failed: {e}")

    return {"status": "sync_complete", "ingested": synced}


@router.get("/events")
async def get_events(limit: int = 50):
    """Get recent ingestion events."""
    return {
        "events": get_event_log(limit),
        "queue": get_queue_status(),
    }


@router.get("/search")
async def semantic_search(query: str, collection: str | None = None, limit: int = 10):
    """Perform semantic search across the vector store."""
    store = get_vector_store()
    results = store.search(query, collection_name=collection, n_results=limit)
    return {"query": query, "results": results}
