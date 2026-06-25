"""Webhook endpoints for GitHub, Jira, and Teams event ingestion."""
import hashlib
import hmac
from fastapi import APIRouter, Request, HTTPException
from app.services.vector_store import get_vector_store
from app.services.event_processor import process_event
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/github")
async def github_webhook(request: Request):
    """Ingest GitHub events (push, pull_request, issues, etc.)."""
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    repo = payload.get("repository", {}).get("full_name", "unknown")

    logger.info(f"[Webhook] GitHub event: {event_type} from {repo}")

    store = get_vector_store()

    if event_type == "push":
        commits = payload.get("commits", [])
        for commit in commits:
            store.ingest_commit(repo, {
                "sha": commit.get("id", ""),
                "commit": {
                    "message": commit.get("message", ""),
                    "author": {"name": commit.get("author", {}).get("name", ""), "date": commit.get("timestamp", "")},
                },
            })
        await process_event("github_push", {"repo": repo, "commits": len(commits)})

    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        action = payload.get("action", "")
        store.ingest_pr(repo, pr)
        await process_event("github_pr", {"repo": repo, "action": action, "number": pr.get("number")})

    elif event_type == "issues":
        issue = payload.get("issue", {})
        action = payload.get("action", "")
        store.ingest_pr(repo, issue)  # Same schema shape
        await process_event("github_issue", {"repo": repo, "action": action, "number": issue.get("number")})

    return {"status": "accepted", "event": event_type}


@router.post("/jira")
async def jira_webhook(request: Request):
    """Ingest Jira events (issue created, updated, sprint changes, etc.)."""
    payload = await request.json()
    event_type = payload.get("webhookEvent", "unknown")
    issue = payload.get("issue", {})
    project_key = issue.get("fields", {}).get("project", {}).get("key", "unknown")

    logger.info(f"[Webhook] Jira event: {event_type} for {project_key}")

    store = get_vector_store()
    store.ingest_jira_issue(project_key, issue)

    await process_event("jira_update", {
        "project_key": project_key,
        "event_type": event_type,
        "issue_key": issue.get("key", ""),
    })

    return {"status": "accepted", "event": event_type}


@router.post("/teams")
async def teams_webhook(request: Request):
    """Ingest Microsoft Teams events (messages, meetings, etc.)."""
    payload = await request.json()

    # Teams sends a validation request on setup
    if payload.get("type") == "validationEvent":
        return {"validationResponse": payload.get("value", "")}

    event_type = payload.get("changeType", "unknown")
    resource = payload.get("resource", "")

    logger.info(f"[Webhook] Teams event: {event_type} on {resource}")

    # Extract message data from the change notification
    resource_data = payload.get("resourceData", {})
    channel_id = resource_data.get("channelIdentity", {}).get("channelId", "unknown")

    store = get_vector_store()
    store.ingest_teams_message(channel_id, resource_data)

    await process_event("teams_message", {
        "channel": channel_id,
        "event_type": event_type,
    })

    return {"status": "accepted", "event": event_type}


@router.get("/status")
async def webhook_status():
    """Check webhook ingestion status and vector store stats."""
    store = get_vector_store()
    return {
        "status": "active",
        "collections": {
            "commits": store.commits.count(),
            "pull_requests": store.pull_requests.count(),
            "jira_tickets": store.jira_tickets.count(),
            "teams_messages": store.teams_messages.count(),
            "meeting_notes": store.meeting_notes.count(),
            "reports": store.reports.count(),
        },
    }
