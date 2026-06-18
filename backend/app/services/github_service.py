import httpx
from app.core.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubService:
    def __init__(self):
        settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

    async def _request(self, endpoint: str, params: dict | None = None) -> dict | list:
        url = f"{GITHUB_API}/{endpoint}"
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(url, params=params or {})
            response.raise_for_status()
            return response.json()

    async def get_open_prs(self, repo: str) -> list:
        logger.info(f"Fetching open PRs for {repo}")
        return await self._request(f"repos/{repo}/pulls", {"state": "open", "per_page": 50})

    async def get_recent_commits(self, repo: str, since: str | None = None) -> list:
        params = {"per_page": 50}
        if since:
            params["since"] = since
        return await self._request(f"repos/{repo}/commits", params)

    async def get_repo_issues(self, repo: str) -> list:
        return await self._request(f"repos/{repo}/issues", {"state": "open", "per_page": 50})

    async def get_pr_reviews(self, repo: str, pr_number: int) -> list:
        return await self._request(f"repos/{repo}/pulls/{pr_number}/reviews")
