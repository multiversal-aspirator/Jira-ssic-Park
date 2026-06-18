import httpx
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class JiraService:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.JIRA_URL.rstrip("/")
        self.auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        async with httpx.AsyncClient(auth=self.auth, timeout=30) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    async def get_sprint_issues(self, project_key: str, sprint_id: str | None = None) -> dict:
        jql = f"project = {project_key}"
        if sprint_id:
            jql += f" AND sprint = {sprint_id}"
        else:
            jql += " AND sprint in openSprints()"

        logger.info(f"Fetching Jira issues: {jql}")
        return await self._request("GET", "search", params={
            "jql": jql,
            "maxResults": 100,
            "fields": "summary,status,assignee,priority,issuetype,created,updated,duedate,issuelinks",
        })

    async def get_board_sprints(self, board_id: str) -> dict:
        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"
        async with httpx.AsyncClient(auth=self.auth, timeout=30) as client:
            response = await client.request("GET", url, params={"state": "active,closed"})
            response.raise_for_status()
            return response.json()

    async def get_issue_details(self, issue_key: str) -> dict:
        return await self._request("GET", f"issue/{issue_key}")
