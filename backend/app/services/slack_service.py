import httpx
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

SLACK_API = "https://slack.com/api"


class SlackService:
    def __init__(self):
        settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        }

    async def get_channel_messages(self, channel: str, limit: int = 50) -> list:
        logger.info(f"Fetching Slack messages from #{channel}")
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(
                f"{SLACK_API}/conversations.history",
                params={"channel": channel, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("messages", [])

    async def post_message(self, channel: str, text: str) -> dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.post(
                f"{SLACK_API}/chat.postMessage",
                json={"channel": channel, "text": text},
            )
            response.raise_for_status()
            return response.json()

    async def post_report(self, channel: str, blocks: list[dict]) -> dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.post(
                f"{SLACK_API}/chat.postMessage",
                json={"channel": channel, "blocks": blocks},
            )
            response.raise_for_status()
            return response.json()
