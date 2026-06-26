"""Webhook endpoints for GitHub, Jira, and Teams event ingestion."""
# TODO (production hardening): add HMAC-SHA256 signature verification for GitHub webhooks
#   using the X-Hub-Signature-256 header and a shared secret in settings.
from fastapi import APIRouter, Request
from app.services.vector_store import get_vector_store
from app.services.event_processor import process_event
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/github")
async def github_webhook(request: Request):
    """Ingest GitHub events (push, pull_request, issues, etc.).

    Always returns 200 Accepted \u2014 processing errors are logged, not re-raised,
    so GitHub doesn't retry delivery unnecessarily.
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"[Webhook] GitHub: failed to parse JSON body: {e}")
        return {"status": "accepted", "error": "invalid_json"}

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    repo = payload.get("repository", {}).get("full_name", "unknown")

    logger.info(f"[Webhook] GitHub event: {event_type} from {repo}")

    try:
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
            # GitHub issues go into the commits collection as a plain document
            # (they don't have the same schema as PRs — avoid writing to the wrong collection)
            store.ingest_commit(repo, {
                "sha": f"issue-{issue.get('number', 0)}",
                "commit": {
                    "message": f"Issue #{issue.get('number')}: {issue.get('title', '')}",
                    "author": {"name": issue.get("user", {}).get("login", ""), "date": issue.get("created_at", "")},
                },
            })
            await process_event("github_issue", {"repo": repo, "action": action, "number": issue.get("number")})

    except Exception as e:
        logger.error(f"[Webhook] GitHub processing error: {e}", exc_info=True)
        return {"status": "accepted", "error": str(e)}

    return {"status": "accepted", "event": event_type}


@router.post("/jira")
async def jira_webhook(request: Request):
    """Ingest Jira events (issue created, updated, sprint changes, etc.).

    Always returns 200 Accepted — processing errors are logged but not re-raised.
    Handles delete events by skipping ingestion (no stale data written).
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"[Webhook] Jira: failed to parse JSON body: {e}")
        return {"status": "accepted", "error": "invalid_json"}

    event_type = payload.get("webhookEvent", "unknown")
    issue = payload.get("issue", {})
    project_key = issue.get("fields", {}).get("project", {}).get("key", "unknown")

    logger.info(f"[Webhook] Jira event: {event_type} for {project_key}")

    try:
        store = get_vector_store()

        # Skip ingestion for delete events \u2014 don't store deleted issues in the vector DB
        if event_type == "jira:issue_deleted":
            logger.info(f"[Webhook] Jira delete event \u2014 skipping ingestion for {issue.get('key', '?')}")
        else:
            store.ingest_jira_issue(project_key, issue)

        await process_event("jira_update", {
            "project_key": project_key,
            "event_type": event_type,
            "issue_key": issue.get("key", ""),
        })

    except Exception as e:
        logger.error(f"[Webhook] Jira processing error: {e}", exc_info=True)
        return {"status": "accepted", "error": str(e)}

    return {"status": "accepted", "event": event_type}


@router.post("/teams")
async def teams_webhook(request: Request):
    """Ingest Microsoft Teams events (messages, meetings, etc.).

    Always returns 200 Accepted \u2014 processing errors are logged but not re-raised.
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"[Webhook] Teams: failed to parse JSON body: {e}")
        return {"status": "accepted", "error": "invalid_json"}

    # Teams sends a validation request on setup
    if payload.get("type") == "validationEvent":
        return {"validationResponse": payload.get("value", "")}

    event_type = payload.get("changeType", "unknown")
    resource = payload.get("resource", "")

    logger.info(f"[Webhook] Teams event: {event_type} on {resource}")

    try:
        resource_data = payload.get("resourceData", {})
        channel_id = resource_data.get("channelIdentity", {}).get("channelId", "unknown")

        store = get_vector_store()
        store.ingest_teams_message(channel_id, resource_data)

        await process_event("teams_message", {
            "channel": channel_id,
            "event_type": event_type,
        })

    except Exception as e:
        logger.error(f"[Webhook] Teams processing error: {e}", exc_info=True)
        return {"status": "accepted", "error": str(e)}

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
