import os
import re
from datetime import datetime
from pathlib import Path

import httpx
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GRAPH_API = "https://graph.microsoft.com/v1.0"
GRAPH_BETA = "https://graph.microsoft.com/beta"

# Path to local Messages folder for testing
MESSAGES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "Messages"


class TeamsService:
    def __init__(self):
        settings = get_settings()
        self.default_team_id = settings.TEAMS_TEAM_ID
        self.access_token = settings.TEAMS_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        # Use local files when no valid token is configured
        self.use_local = (
            not self.access_token
            or self.access_token.startswith("your")
            or len(self.access_token) < 20
        )

    def _parse_message_file(self, filepath: Path) -> list[dict]:
        """Parse a Messages/*.txt file into structured message records."""
        messages = []
        current_day = ""
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                # Detect day headers like "DAY 1:-"
                if re.match(r"^DAY\s+\d+", line, re.IGNORECASE):
                    current_day = line.strip().rstrip(":-").strip()
                    continue
                # Parse message lines: [HH:MM AM/PM] Speaker: Message
                match = re.match(
                    r"\[(\d{1,2}:\d{2}\s*[AP]M)\]\s+(.+?):\s+(.*)", line
                )
                if match:
                    timestamp, speaker, content = match.groups()
                    messages.append({
                        "day": current_day,
                        "timestamp": timestamp.strip(),
                        "speaker": speaker.strip(),
                        "content": content.strip(),
                        "created": f"{current_day} {timestamp.strip()}",
                    })
        return messages

    def _get_local_messages(self, pattern: str = "Grp_chat") -> list[dict]:
        """Load messages from local Messages folder matching pattern."""
        all_messages = []
        if not MESSAGES_DIR.exists():
            logger.warning(f"Messages directory not found: {MESSAGES_DIR}")
            return []
        for filepath in sorted(MESSAGES_DIR.glob("*.txt")):
            if pattern.lower() in filepath.name.lower():
                all_messages.extend(self._parse_message_file(filepath))
        return all_messages

    def _get_local_transcripts(self, pattern: str = "Transcript") -> list[dict]:
        """Load transcripts from local Messages folder matching pattern."""
        transcripts = []
        if not MESSAGES_DIR.exists():
            logger.warning(f"Messages directory not found: {MESSAGES_DIR}")
            return []
        for filepath in sorted(MESSAGES_DIR.glob("*.txt")):
            if pattern.lower() in filepath.name.lower():
                content = filepath.read_text(encoding="utf-8")
                transcripts.append({
                    "meeting_id": filepath.stem,
                    "transcript_id": filepath.stem,
                    "created": datetime.now().isoformat(),
                    "content": content,
                    "source_file": filepath.name,
                })
        return transcripts

    def _resolve_team_id(self, team_id: str | None = None) -> str:
        resolved_team_id = team_id or self.default_team_id
        if not resolved_team_id:
            raise ValueError("TEAMS_TEAM_ID is not configured and no team_id was provided")
        return resolved_team_id

    async def get_channel_messages(
        self,
        channel: str,
        limit: int = 50,
        team_id: str | None = None,
    ) -> list:
        if self.use_local:
            logger.info("Using local Messages folder for channel messages")
            messages = self._get_local_messages("Grp_chat")
            return messages[:limit]

        resolved_team_id = self._resolve_team_id(team_id)
        logger.info(f"Fetching Teams messages from channel {channel}")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(
                f"{GRAPH_API}/teams/{resolved_team_id}/channels/{channel}/messages",
                params={"$top": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("value", [])

    async def post_message(
        self,
        channel: str,
        text: str,
        team_id: str | None = None,
    ) -> dict:
        if self.use_local:
            logger.info(f"[LOCAL MODE] Would post to Teams channel {channel}: {text[:100]}...")
            return {"id": "local-mock", "status": "simulated", "content": text}

        resolved_team_id = self._resolve_team_id(team_id)

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.post(
                f"{GRAPH_API}/teams/{resolved_team_id}/channels/{channel}/messages",
                json={
                    "body": {
                        "contentType": "text",
                        "content": text,
                    }
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_meeting_notes(
        self,
        channel: str,
        limit: int = 10,
        team_id: str | None = None,
    ) -> list[dict]:
        """Fetch meeting-related messages (event summaries, notes, recordings) from a channel."""
        if self.use_local:
            logger.info("Using local Messages folder for meeting notes")
            messages = self._get_local_messages("Grp_chat")
            # Return all messages as meeting notes context
            notes = []
            for msg in messages[:limit]:
                notes.append({
                    "subject": f"{msg['day']} - Team Discussion",
                    "content": msg["content"],
                    "from": msg["speaker"],
                    "created": msg["created"],
                })
            return notes

        resolved_team_id = self._resolve_team_id(team_id)
        logger.info(f"Fetching meeting notes from Teams channel {channel}")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            # Get messages filtered to those containing meeting content
            response = await client.get(
                f"{GRAPH_API}/teams/{resolved_team_id}/channels/{channel}/messages",
                params={"$top": 50},
            )
            response.raise_for_status()
            messages = response.json().get("value", [])

        # Filter messages that are meeting-related (event type or contain meeting keywords)
        meeting_keywords = {"meeting", "notes", "agenda", "action items", "minutes", "recap", "standup", "retro"}
        notes = []
        for msg in messages:
            body = msg.get("body", {}).get("content", "")
            msg_type = msg.get("messageType", "")
            subject = msg.get("subject", "") or ""

            is_meeting = (
                msg_type == "systemEventMessage"
                or any(kw in body.lower() for kw in meeting_keywords)
                or any(kw in subject.lower() for kw in meeting_keywords)
            )

            if is_meeting:
                notes.append({
                    "subject": subject,
                    "content": body,
                    "from": msg.get("from", {}).get("user", {}).get("displayName", "Unknown"),
                    "created": msg.get("createdDateTime", ""),
                })

            if len(notes) >= limit:
                break

        return notes

    async def get_meeting_transcripts(
        self,
        channel: str,
        limit: int = 5,
        team_id: str | None = None,
    ) -> list[dict]:
        """Fetch meeting transcriptions from Teams channel meetings."""
        if self.use_local:
            logger.info("Using local Messages folder for meeting transcripts")
            transcripts = self._get_local_transcripts("Transcript")
            return transcripts[:limit]

        resolved_team_id = self._resolve_team_id(team_id)
        logger.info(f"Fetching meeting transcripts from Teams channel {channel}")

        async with httpx.AsyncClient(headers=self.headers, timeout=60) as client:
            # Step 1: Get channel messages to find meeting event messages with join URLs
            response = await client.get(
                f"{GRAPH_API}/teams/{resolved_team_id}/channels/{channel}/messages",
                params={"$top": 50},
            )
            response.raise_for_status()
            messages = response.json().get("value", [])

            # Step 2: Extract online meeting IDs from event messages
            meeting_ids = []
            for msg in messages:
                event_detail = msg.get("eventDetail")
                if event_detail and event_detail.get("@odata.type", "").endswith("callEndedEventMessageDetail"):
                    call_id = event_detail.get("callId")
                    if call_id:
                        meeting_ids.append(call_id)

                # Also check for meeting join URLs in message body to extract meeting IDs
                body = msg.get("body", {}).get("content", "")
                join_urls = re.findall(
                    r"https://teams\.microsoft\.com/l/meetup-join/([^\s\"<]+)",
                    body,
                )
                for url_id in join_urls:
                    meeting_ids.append(url_id)

                if len(meeting_ids) >= limit:
                    break

            # Step 3: Fetch transcripts for each meeting
            transcripts = []
            for meeting_id in meeting_ids[:limit]:
                try:
                    # List transcripts for this meeting
                    tr_response = await client.get(
                        f"{GRAPH_BETA}/communications/onlineMeetings/{meeting_id}/transcripts",
                    )
                    if tr_response.status_code != 200:
                        continue

                    tr_list = tr_response.json().get("value", [])
                    for tr in tr_list:
                        transcript_id = tr.get("id")
                        created = tr.get("createdDateTime", "")

                        # Fetch transcript content as plain text
                        content_response = await client.get(
                            f"{GRAPH_BETA}/communications/onlineMeetings/{meeting_id}/transcripts/{transcript_id}/content",
                            params={"$format": "text/vtt"},
                        )
                        if content_response.status_code == 200:
                            transcripts.append({
                                "meeting_id": meeting_id,
                                "transcript_id": transcript_id,
                                "created": created,
                                "content": content_response.text,
                            })
                except Exception as e:
                    logger.warning(f"Failed to fetch transcript for meeting {meeting_id}: {e}")
                    continue

        logger.info(f"Retrieved {len(transcripts)} meeting transcripts")
        return transcripts

    async def post_report(
        self,
        channel: str,
        blocks: list[dict],
        team_id: str | None = None,
    ) -> dict:
        # Convert structured blocks to a readable plain-text report for Teams.
        rendered_text = "\n".join(str(block) for block in blocks)
        return await self.post_message(channel, rendered_text, team_id=team_id)
