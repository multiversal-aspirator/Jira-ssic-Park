import asyncio
import httpx
from app.core.config import get_settings


async def main():
    settings = get_settings()

    base_url = settings.JIRA_URL.rstrip("/")
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

    print("JIRA_URL =", base_url)
    print("JIRA_EMAIL =", settings.JIRA_EMAIL)
    print("TOKEN_SET =", bool(settings.JIRA_API_TOKEN))

    tests = [
        ("myself", f"{base_url}/rest/api/3/myself", {}),
        ("serverInfo", f"{base_url}/rest/api/3/serverInfo", {}),
        ("search-old", f"{base_url}/rest/api/3/search", {
            "jql": "project = SCRUM",
            "maxResults": 5,
            "fields": "summary,status",
        }),
        ("search-new", f"{base_url}/rest/api/3/search/jql", {
            "jql": "project = SCRUM",
            "maxResults": 5,
            "fields": "summary,status",
        }),
        ("search-open-sprint", f"{base_url}/rest/api/3/search/jql", {
            "jql": "project = SCRUM AND sprint in openSprints()",
            "maxResults": 5,
            "fields": "summary,status",
        }),
    ]

    async with httpx.AsyncClient(auth=auth, timeout=30, follow_redirects=False) as client:
        for name, url, params in tests:
            print("\n" + "=" * 80)
            print("TEST:", name)
            print("URL:", url)
            print("PARAMS:", params)

            try:
                response = await client.get(url, params=params)
                print("STATUS:", response.status_code)
                print("FINAL URL:", response.url)
                print("HEADERS location:", response.headers.get("location"))
                print("BODY FIRST 1000 CHARS:")
                print(response.text[:1000])
            except Exception as e:
                print("ERROR TYPE:", type(e).__name__)
                print("ERROR:", e)


asyncio.run(main())