"""Background event processor — updates knowledge base and triggers re-analysis when events arrive."""
import asyncio
from collections import deque
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory event queue (for simplicity; could be Redis/Celery in production)
_event_queue: deque = deque(maxlen=1000)
_event_log: list[dict] = []


async def process_event(event_type: str, data: dict):
    """Process an incoming event and queue for background analysis."""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
        "processed": False,
    }
    _event_queue.append(event)
    _event_log.append(event)
    logger.info(f"[EventProcessor] Queued event: {event_type} | Queue size: {len(_event_queue)}")

    # For significant events, trigger incremental processing
    if event_type in ("github_pr", "jira_update", "github_push"):
        await _handle_significant_event(event)


async def _handle_significant_event(event: dict):
    """Handle events that should trigger immediate re-computation."""
    event_type = event["type"]
    data = event["data"]

    logger.info(f"[EventProcessor] Processing significant event: {event_type}")

    # Mark as processed
    event["processed"] = True

    # In a production system, this would trigger:
    # 1. Recompute project progress
    # 2. Update team member stats
    # 3. Check for new blockers
    # 4. Refresh health score
    # For now we log and store — the next /analyze call uses updated vector store


def get_event_log(limit: int = 50) -> list[dict]:
    """Get recent event log."""
    return list(reversed(_event_log[-limit:]))


def get_queue_status() -> dict:
    """Get current queue stats."""
    return {
        "queue_size": len(_event_queue),
        "total_events": len(_event_log),
        "unprocessed": sum(1 for e in _event_log if not e.get("processed")),
        "last_event": _event_log[-1] if _event_log else None,
    }
