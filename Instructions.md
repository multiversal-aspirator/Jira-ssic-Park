# PROBLEM STATEMENT 5: AI Project Manager for Engineering Teams

## Background

Engineering managers spend substantial time coordinating sprint planning, tracking dependencies, managing risks, monitoring team progress, preparing status reports, and identifying blockers. Much of this work involves collecting information from multiple tools and stakeholders.

## Problem Statement

Build an AI Project Manager that acts as an autonomous coordination layer for software engineering teams. The system should analyze project artifacts, identify risks, track delivery progress, generate status reports, and proactively recommend actions to improve project execution.

## Required Capabilities

- Ingest data from Jira, GitHub, Linear, Slack, and meeting notes
- Track sprint progress and delivery status
- Identify blockers and project risks
- Detect dependency conflicts
- Generate stakeholder status reports
- Recommend corrective actions
- Forecast sprint completion likelihood
- Monitor engineering productivity trends

## Required Agents

- **Sprint Analysis Agent**
- **Risk Detection Agent**
- **Dependency Tracking Agent**
- **Stakeholder Reporting Agent**
- **Delivery Forecasting Agent**

## Fan-out Logic

A project update request must trigger parallel analysis across multiple project dimensions, with outputs merged into a unified project health report.

## Stretch Goals

- Autonomous sprint planning recommendations
- Resource allocation optimization
- Capacity planning
- Natural language project queries

## Constraints

- Recommendations must be supported by project data
- Historical trends must be considered during forecasting
- Every risk must include evidence and impact assessment

## Suggested Stack

| Component | Technology |
|---|---|
| Orchestration | LangGraph, CrewAI |
| Integrations | GitHub, Jira, Slack, Linear |
| Backend | FastAPI |
| Frontend | React |
| Observability | LangSmith |

## What a Strong Submission Looks Like

- Produces an accurate project health score
- Identifies hidden project risks and blockers
- Generates executive-ready status reports
- Demonstrates multi-agent collaboration across engineering data sources
- Explains why a project is on track or at risk with supporting evidence

---

# Judging Rubric

Each team is scored out of **30 points** (10 criteria × 3 points max). Scores are summed across all judges and averaged. In case of a tie, the team with the higher score on the **Technical Depth** criterion wins.

## Scoring Scale

| Score | Level | Description |
|---|---|---|
| 0 | Insufficient | Not attempted, broken, or does not meet the minimum requirement |
| 1 | Developing | Partially implemented; works in some cases but has significant gaps |
| 2 | Competent | Fully implemented; works reliably for the core use case |
| 3 | Excellent | Fully implemented with evidence of deeper thinking, edge case handling, or extensibility |

## Problem Rubric — Applies to All Five Statements

| Criterion | Weight | 0 – Insufficient | 1 – Developing | 2 – Competent | 3 – Excellent |
|---|---|---|---|---|---|
| Intent / request classification | 15% | Misclassifies most inputs; no routing logic | Correct on simple inputs; fails on ambiguous or mixed ones | Classifies the majority of inputs correctly and routes accordingly | High accuracy with confidence scoring and a clear fallback path |
| Multi-agent decomposition & fan-out | 15% | Single monolithic flow; no decomposition | Decomposes but runs sequentially or leaves sub-tasks unmerged | Splits work across agents in parallel and merges the results | Merged output is demonstrably better than any single agent's result |
| Agent specialisation | 10% | All agents are identical generic LLM calls | Agents differ but share the same tools and prompts | Each agent has distinct tools, prompts, and responsibilities | Agents are swappable; adding one requires no changes to existing code |
| Output quality & accuracy | 10% | Output is incoherent or unrelated to the input | Output is partially correct but misses key items | Output is accurate and complete for the core use case | Output is accurate, structured, and includes confidence or evidence |
| Observability & traceability | 10% | No logging or traceability | Logs exist but are unstructured | Structured logs show which agent handled each sub-task | Full trace or dashboard linking every output back to its source |
| Technical depth & code quality | 10% | Monolithic; no separation of concerns | Some structure; key logic is still entangled | Clear layer separation; readable without explanation | Clean abstractions; a new agent or capability can be added in < 30 lines |
| Demo clarity | 10% | Team cannot explain what the system does | Demo works but team struggles to explain choices | Demo is clear; team answers questions confidently | Demo shows a compelling real-world use case end-to-end |
| README | 5% | Missing or placeholder | Covers setup only | Covers setup, architecture, and design decisions | Includes a decision log and known limitations |
| Edge case handling | 10% | Crashes on unexpected input | Handles common errors; crashes on edge cases | Handles malformed input, API failures, and empty results | Graceful degradation with user-visible error context |
| Stretch goal bonus | 5% | None attempted | Partially attempted | One stretch goal working | Two or more stretch goals working |

## General Notes for Judges

- Score what you see working during the demo, not what the team says will work later
- A smaller system that is fully working scores higher than an ambitious system that is mostly broken
- Ask each team member at least one technical question; individual understanding is part of the assessment
- Bonus points are capped — a team cannot exceed 30 total points

## Submission Checklist

- [ ] GitHub repo link shared before demo slot
- [ ] README includes: setup steps, architecture diagram or description, known limitations
- [ ] Demo environment is ready before the slot — no live debugging during demo time
- [ ] Each team member can explain their individual contribution