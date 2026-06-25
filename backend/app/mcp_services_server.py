from mcp.server.fastmcp import FastMCP

from app.services.github_service import GitHubService
from app.services.jira_service import JiraService
from app.services.notes_service import NotesService
from app.services.teams_service import TeamsService

mcp = FastMCP("jira-sick-park-services")


@mcp.tool()
async def jira_get_sprint_issues(project_key: str, sprint_id: str | None = None) -> dict:
    """Get Jira issues for a project and optional sprint."""
    jira = JiraService()
    return await jira.get_sprint_issues(project_key=project_key, sprint_id=sprint_id)


@mcp.tool()
async def jira_get_issue_details(issue_key: str) -> dict:
    """Get details for a Jira issue key."""
    jira = JiraService()
    return await jira.get_issue_details(issue_key=issue_key)


@mcp.tool()
async def github_get_open_prs(repo: str) -> list:
    """Get open pull requests for a GitHub repo (owner/repo)."""
    github = GitHubService()
    return await github.get_open_prs(repo=repo)


@mcp.tool()
async def github_get_repo_issues(repo: str) -> list:
    """Get open issues for a GitHub repo (owner/repo)."""
    github = GitHubService()
    return await github.get_repo_issues(repo=repo)


@mcp.tool()
async def teams_get_channel_messages(channel: str, limit: int = 30, team_id: str | None = None) -> list:
    """Get recent messages from a Microsoft Teams channel."""
    teams = TeamsService()
    return await teams.get_channel_messages(channel=channel, limit=limit, team_id=team_id)


@mcp.tool()
async def teams_get_meeting_notes(channel: str, limit: int = 10, team_id: str | None = None) -> list[dict]:
    """Get meeting notes/minutes/recaps from a Microsoft Teams channel."""
    teams = TeamsService()
    return await teams.get_meeting_notes(channel=channel, limit=limit, team_id=team_id)


@mcp.tool()
async def teams_get_meeting_transcripts(channel: str, limit: int = 5, team_id: str | None = None) -> list[dict]:
    """Get meeting transcriptions (VTT content) from Teams channel meetings."""
    teams = TeamsService()
    return await teams.get_meeting_transcripts(channel=channel, limit=limit, team_id=team_id)


@mcp.tool()
async def teams_post_message(channel: str, text: str, team_id: str | None = None) -> dict:
    """Post a text message to a Microsoft Teams channel."""
    teams = TeamsService()
    return await teams.post_message(channel=channel, text=text, team_id=team_id)


@mcp.tool()
async def notes_get_recent(limit: int = 5) -> list[dict]:
    """Get recent meeting notes from local storage."""
    notes = NotesService()
    return await notes.get_recent_notes(limit=limit)


@mcp.tool()
async def notes_save(filename: str, content: str) -> str:
    """Save a meeting note to local storage as a markdown file."""
    safe_name = filename if filename.endswith(".md") else f"{filename}.md"
    notes = NotesService()
    return await notes.save_note(filename=safe_name, content=content)


@mcp.tool()
def project_search(query: str, collection: str | None = None, limit: int = 10) -> list[dict]:
    """Semantic search across all project knowledge (commits, PRs, tickets, messages, reports)."""
    from app.services.vector_store import get_vector_store
    store = get_vector_store()
    return store.search(query, collection_name=collection, n_results=limit)


@mcp.tool()
async def project_ask(question: str, project_key: str | None = None) -> str:
    """Ask a natural language question about a project. Uses RAG over the vector database."""
    from app.services.vector_store import get_vector_store
    from app.services.llm_service import get_chat_model

    store = get_vector_store()
    query = f"{project_key}: {question}" if project_key else question
    results = store.search(query, n_results=15)

    if not results:
        return "No project data available. Ingest data via webhooks or manual sync first."

    context = "\n---\n".join(r["document"] for r in results)
    llm = get_chat_model()
    prompt = f"Answer based on this project data:\n\n{context}\n\nQuestion: {question}"
    response = await llm.ainvoke(prompt)
    return response.content


if __name__ == "__main__":
    mcp.run()
