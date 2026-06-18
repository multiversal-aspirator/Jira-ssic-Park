from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger(__name__)

NOTES_DIR = Path(__file__).parent.parent.parent / "meeting_notes"


class NotesService:
    def __init__(self, notes_dir: Path | None = None):
        self.notes_dir = notes_dir or NOTES_DIR
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    async def get_recent_notes(self, limit: int = 5) -> list[dict]:
        logger.info(f"Loading up to {limit} recent meeting notes")
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
