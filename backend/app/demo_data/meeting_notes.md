# Sprint 21 Meeting Notes

## Sprint Planning (2026-06-04)

**Sprint Goal:** Complete auth module and payment integration

**Capacity:** 5 engineers, 40 story points planned

**Key decisions:**
- OAuth2 implementation takes priority as it unblocks payment flow
- Payment integration is the highest risk item due to third-party SDK dependency
- CI/CD pipeline setup moved to first week to unblock deployments

**Risks discussed:**
- Payment provider SDK has known stability issues (documented in their status page)
- Tight timeline for payment + email notifications in same sprint

---

## Standup Summary (2026-06-11)

**Completed:**
- DEMO-101: OAuth2 login flow (Alice) — merged and deployed to staging
- DEMO-103: CI/CD pipeline (Charlie) — fully operational
- DEMO-107: API documentation (Charlie)

**In Progress:**
- DEMO-102: Payment gateway (Bob) — SDK issues causing delays
- DEMO-105: Webhook processor (Dana) — on track for today

**Blockers:**
- DEMO-108: Payment SDK returning 503 errors intermittently
- Bob waiting on provider support response

**Action Items:**
- Bob to implement retry logic as workaround
- Alice to start on race condition fix (DEMO-104)

---

## Mid-Sprint Review (2026-06-14)

**Status: AT RISK**

**Progress:** 15/40 story points completed (37.5%)

**Key concerns:**
1. Payment integration (8 SP) still blocked by SDK issues
2. Session race condition fix taking longer than estimated
3. Email notification and load testing depend on payment — cascading delay risk

**Decisions:**
- Carry over email notifications (DEMO-106) to Sprint 22 if payment not resolved by EOD Monday
- Prioritize DEMO-108 fix (SDK retry logic) to unblock payment flow
- Dana's rate limiter is independent — keep on track

**Risk mitigation:**
- Bob to pair with Alice on SDK workaround
- Charlie to prepare rollback plan for staging

---

## Daily Standup (2026-06-16)

**Completed since last standup:**
- DEMO-109: Rate limiter in review (Dana)

**Still blocked:**
- DEMO-108: Payment SDK 503 — support ticket open, no response
- DEMO-102: Payment integration — blocked by DEMO-108
- DEMO-110: Load testing — blocked by DEMO-102

**Sprint burndown:**
- 5 of 10 issues completed
- 3 in progress
- 2 blocked
- Sprint ends today — likely to miss 15 story points
