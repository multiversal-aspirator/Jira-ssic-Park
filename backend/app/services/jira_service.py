import httpx
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

STORY_POINT_FIELDS = [
    "customfield_10016",
    "customfield_10026",
    "customfield_10024",
]


class JiraService:
    def __init__(self):
        settings = get_settings()
        self.base_url = settings.JIRA_URL.rstrip("/")
        self.auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        if not self.base_url:
            raise ValueError("JIRA_URL is not configured")

        url = f"{self.base_url}/rest/api/3/{endpoint}"
        async with httpx.AsyncClient(auth=self.auth, timeout=30) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    def _extract_story_points(self, fields: dict) -> float:
        for field in STORY_POINT_FIELDS:
            value = fields.get(field)
            if isinstance(value, (int, float)):
                return float(value)
        return 0.0

    def _is_blocked(self, fields: dict) -> bool:
        status_name = (fields.get("status") or {}).get("name", "").lower()
        priority_name = (fields.get("priority") or {}).get("name", "").lower()

        if "block" in status_name:
            return True

        if priority_name in {"blocker", "highest"}:
            return True

        for link in fields.get("issuelinks", []) or []:
            link_type = (link.get("type") or {}).get("name", "").lower()
            inward = (link.get("type") or {}).get("inward", "").lower()
            outward = (link.get("type") or {}).get("outward", "").lower()

            link_text = f"{link_type} {inward} {outward}"
            if "block" in link_text:
                return True

        return False

    def _normalize_issue(self, issue: dict) -> dict:
        fields = issue.get("fields", {}) or {}

        assignee = fields.get("assignee") or {}
        priority = fields.get("priority") or {}
        issue_type = fields.get("issuetype") or {}
        status = fields.get("status") or {}

        return {
            "key": issue.get("key", ""),
            "summary": fields.get("summary", ""),
            "status": status.get("name", "Unknown"),
            "assignee": assignee.get("displayName", "Unassigned"),
            "priority": priority.get("name", "None"),
            "issue_type": issue_type.get("name", "Unknown"),
            "story_points": self._extract_story_points(fields),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "duedate": fields.get("duedate"),
            "is_blocked": self._is_blocked(fields),
        }

    def _normalize_search_response(
        self,
        response: dict,
        project_key: str,
        sprint_id: str | None,
        jql: str,
    ) -> dict:
        raw_issues = response.get("issues", []) or []
        normalized_issues = [self._normalize_issue(issue) for issue in raw_issues]

        return {
            "source": "jira",
            "project_key": project_key,
            "sprint_id": sprint_id,
            "jql": jql,
            "total": response.get("total", len(normalized_issues)),
            "max_results": response.get("maxResults"),
            "start_at": response.get("startAt"),
            "issues": normalized_issues,
        }

    async def get_sprint_issues(
        self,
        project_key: str,
        sprint_id: str | None = None,
    ) -> dict:
        jql = f"project = {project_key}"
        if sprint_id:
            jql += f" AND sprint = {sprint_id}"
        else:
            jql += " AND sprint in openSprints()"

        logger.info(f"Fetching Jira issues: {jql}")

        fields = [
            "summary",
            "status",
            "assignee",
            "priority",
            "issuetype",
            "created",
            "updated",
            "duedate",
            "issuelinks",
            *STORY_POINT_FIELDS,
        ]

        response = await self._request(
            "GET",
            "search/jql",
            params={
                "jql": jql,
                "maxResults": 100,
                "fields": ",".join(fields),
            },
        )

        normalized = self._normalize_search_response(
            response,
            project_key,
            sprint_id,
            jql,
        )

        logger.info(
            f"Fetched and normalized {len(normalized['issues'])} Jira issues"
        )

        return normalized

    async def get_board_sprints(self, board_id: str) -> dict:
        if not self.base_url:
            raise ValueError("JIRA_URL is not configured")

        url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/sprint"

        async with httpx.AsyncClient(auth=self.auth, timeout=30) as client:
            response = await client.request(
                "GET",
                url,
                params={"state": "active,closed"},
            )
            response.raise_for_status()
            return response.json()

    async def get_issue_details(self, issue_key: str) -> dict:
        return await self._request("GET", f"issue/{issue_key}")