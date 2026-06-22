import json
import os
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)

DEMO_DATA_DIR = Path(__file__).parent.parent / "demo_data"


def _load_json(filename: str) -> dict | list:
    filepath = DEMO_DATA_DIR / filename
    if not filepath.exists():
        logger.warning(f"[DemoData] File not found: {filepath}")
        return {} if filename.endswith(".json") else []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.info(f"[DemoData] Loaded {filename} ({len(data) if isinstance(data, list) else 'dict'})")
    return data


def _load_text(filename: str) -> str:
    filepath = DEMO_DATA_DIR / filename
    if not filepath.exists():
        logger.warning(f"[DemoData] File not found: {filepath}")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    logger.info(f"[DemoData] Loaded {filename} ({len(content)} chars)")
    return content


def load_demo_jira_issues() -> dict:
    """Load demo Jira sprint issues."""
    return _load_json("jira_issues.json")


def load_demo_github_prs() -> list:
    """Load demo GitHub PR data."""
    return _load_json("github_prs.json")


def load_demo_slack_messages() -> list:
    """Load demo Slack messages."""
    return _load_json("slack_messages.json")


def load_demo_meeting_notes() -> str:
    """Load demo meeting notes."""
    return _load_text("meeting_notes.md")
