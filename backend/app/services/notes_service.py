from pathlib import Path
from app.core.config import get_settings
from app.services.teams_service import TeamsService
from app.utils.logger import get_logger

logger = get_logger(__name__)

NOTES_DIR = Path(__file__).parent.parent.parent / "meeting_notes"


class NotesService:
    def __init__(self, notes_dir: Path | None = None):
        self.notes_dir = notes_dir or NOTES_DIR
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    async def get_recent_notes(self, limit: int = 5, teams_channel: str | None = None) -> list[dict]:
        """Get meeting notes — from Teams channel if provided, else from local files."""
        if teams_channel:
            return await self._get_from_teams(teams_channel, limit)
        return await self._get_from_local(limit)

    async def _get_from_teams(self, channel: str, limit: int) -> list[dict]:
        logger.info(f"Loading meeting notes and transcripts from Teams channel {channel}")
        teams = TeamsService()

        # Fetch both meeting notes and transcriptions in parallel
        notes = await teams.get_meeting_notes(channel=channel, limit=limit)
        transcripts = await teams.get_meeting_transcripts(channel=channel, limit=limit)

        # Merge transcripts into notes list
        for tr in transcripts:
            notes.append({
                "subject": f"Meeting Transcript ({tr['created']})",
                "content": tr["content"],
                "from": "Teams Transcription",
                "created": tr["created"],
                "type": "transcript",
            })

        return notes

    async def _get_from_local(self, limit: int) -> list[dict]:
        logger.info(f"Loading up to {limit} recent meeting notes from local files")
        notes = []
        files = sorted(self.notes_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

        for f in files[:limit]:
            notes.append({
                "filename": f.name,
                "content": f.read_text(encoding="utf-8"),
            })
        return notes

    async def save_note(self, filename: str, content: str) -> str:
        filepath = self.notes_dir / filename
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Saved meeting note: {filename}")
        return str(filepath)
