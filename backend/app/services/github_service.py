import httpx
from urllib.parse import urlparse
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

    @staticmethod
    def _normalize_repo(repo: str) -> str:
        """Normalize repo input to owner/repo.

        Accepts:
        - owner/repo
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - https://github.com/owner/repo/... (tree, pull, etc.)
        - git@github.com:owner/repo(.git)
        """
        if not repo or not repo.strip():
            raise ValueError("GitHub repo cannot be empty")

        raw = repo.strip()

        if raw.startswith("git@github.com:"):
            path = raw.split(":", 1)[1]
        elif raw.startswith("http://") or raw.startswith("https://"):
            parsed = urlparse(raw)
            if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
                raise ValueError("Only github.com repository URLs are supported")
            path = parsed.path
        else:
            path = raw

        path = path.strip().lstrip("/").rstrip("/")

        if path.endswith(".git"):
            path = path[:-4]

        parts = [p for p in path.split("/") if p]
        if len(parts) < 2:
            raise ValueError("GitHub repo must be in owner/repo format")

        owner, name = parts[0], parts[1]
        if not owner or not name:
            raise ValueError("GitHub repo must be in owner/repo format")

        return f"{owner}/{name}"

    @staticmethod
    def normalize_repo_input(repo: str) -> str:
        """Public helper for callers that also store repo identifiers."""
        return GitHubService._normalize_repo(repo)

    async def get_open_prs(self, repo: str) -> list:
        normalized_repo = self._normalize_repo(repo)
        logger.info(f"Fetching open PRs for {normalized_repo}")
        return await self._request(f"repos/{normalized_repo}/pulls", {"state": "open", "per_page": 50})

    async def get_recent_commits(self, repo: str, since: str | None = None) -> list:
        normalized_repo = self._normalize_repo(repo)
        params = {"per_page": 50}
        if since:
            params["since"] = since
        return await self._request(f"repos/{normalized_repo}/commits", params)

    async def get_repo_issues(self, repo: str) -> list:
        normalized_repo = self._normalize_repo(repo)
        return await self._request(f"repos/{normalized_repo}/issues", {"state": "open", "per_page": 50})

    async def get_pr_reviews(self, repo: str, pr_number: int) -> list:
        normalized_repo = self._normalize_repo(repo)
        return await self._request(f"repos/{normalized_repo}/pulls/{pr_number}/reviews")
