"""Team member tracking — individual contributor progress and workload."""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.vector_store import get_vector_store
from app.services.llm_service import get_chat_model
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/team", tags=["team"])


class TeamMemberSummary(BaseModel):
    name: str
    assigned_tasks: int = 0
    completed_tasks: int = 0
    open_prs: int = 0
    blocked_items: int = 0
    workload: str = "normal"  # light, normal, heavy, overloaded
    summary: str = ""


class TeamOverview(BaseModel):
    members: list[TeamMemberSummary]
    total_members: int
    bottlenecks: list[str]
    recommendations: list[str]


@router.get("/overview", response_model=TeamOverview)
async def get_team_overview(project_key: str):
    """Get team workload overview with individual member summaries."""
    logger.info(f"[Team] Generating team overview for {project_key}")

    store = get_vector_store()

    # Search for all team-related data
    jira_results = store.search(f"{project_key} assignee task", collection_name="jira_tickets", n_results=50)
    pr_results = store.search(f"{project_key} pull request author", collection_name="github_prs", n_results=30)

    # Extract unique team members from data
    members_data: dict[str, dict] = {}

    for r in jira_results:
        meta = r.get("metadata", {})
        assignee = meta.get("assignee", "Unassigned")
        if assignee == "Unassigned":
            continue
        if assignee not in members_data:
            members_data[assignee] = {"assigned": 0, "completed": 0, "blocked": 0, "prs": 0}

        status = meta.get("status", "").lower()
        members_data[assignee]["assigned"] += 1
        if status in ("done", "closed", "resolved"):
            members_data[assignee]["completed"] += 1
        elif status in ("blocked",):
            members_data[assignee]["blocked"] += 1

    for r in pr_results:
        meta = r.get("metadata", {})
        author = meta.get("author", "")
        if author and author in members_data:
            members_data[author]["prs"] += 1
        elif author:
            members_data[author] = {"assigned": 0, "completed": 0, "blocked": 0, "prs": 1}

    # Build member summaries
    members = []
    for name, data in members_data.items():
        total = data["assigned"]
        workload = "light" if total <= 2 else "normal" if total <= 5 else "heavy" if total <= 8 else "overloaded"
        members.append(TeamMemberSummary(
            name=name,
            assigned_tasks=data["assigned"],
            completed_tasks=data["completed"],
            open_prs=data["prs"],
            blocked_items=data["blocked"],
            workload=workload,
            summary=f"{name}: {data['completed']}/{total} tasks done, {data['prs']} open PRs, {data['blocked']} blocked",
        ))

    # Detect bottlenecks
    bottlenecks = []
    for m in members:
        if m.workload == "overloaded":
            bottlenecks.append(f"{m.name} is overloaded ({m.assigned_tasks} tasks)")
        if m.blocked_items > 0:
            bottlenecks.append(f"{m.name} has {m.blocked_items} blocked items")

    recommendations = []
    overloaded = [m for m in members if m.workload == "overloaded"]
    light = [m for m in members if m.workload == "light"]
    if overloaded and light:
        recommendations.append(
            f"Rebalance: move tasks from {overloaded[0].name} to {light[0].name}"
        )
    if any(m.blocked_items > 0 for m in members):
        recommendations.append("Prioritize unblocking team members with blocked items")

    return TeamOverview(
        members=members,
        total_members=len(members),
        bottlenecks=bottlenecks,
        recommendations=recommendations,
    )


@router.get("/member/{member_name}")
async def get_member_detail(member_name: str, project_key: str):
    """Get detailed progress for a specific team member."""
    store = get_vector_store()

    # Search for this member's activity
    results = store.search(member_name, n_results=20)

    tasks = [r for r in results if r.get("metadata", {}).get("type") in ("jira_issue",)]
    prs = [r for r in results if r.get("metadata", {}).get("type") in ("pull_request",)]
    messages = [r for r in results if r.get("metadata", {}).get("type") in ("teams_message",)]

    # Generate AI summary
    try:
        llm = get_chat_model()
        context = "\n".join(r["document"] for r in results[:15])
        prompt = f"""Summarize what {member_name} has been working on based on this project data:

{context}

Provide:
1. What they completed recently
2. What they're currently working on
3. What's pending/blocked
4. Any potential delays"""

        response = await llm.ainvoke(prompt)
        ai_summary = response.content
    except Exception as e:
        logger.warning(f"[Team] AI summary failed: {e}")
        ai_summary = f"Found {len(tasks)} tasks, {len(prs)} PRs, {len(messages)} messages for {member_name}"

    return {
        "member": member_name,
        "project": project_key,
        "tasks": [r["document"] for r in tasks],
        "pull_requests": [r["document"] for r in prs],
        "recent_messages": [r["document"] for r in messages],
        "ai_summary": ai_summary,
    }
