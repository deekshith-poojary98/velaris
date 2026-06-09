# Design Partner Outreach Plan

| Field | Value |
|-------|-------|
| Status | Draft |
| Created | 2026-06-02 |
| Goal | Identify 2–3 platform teams for RFC review and Phase 1 design partnership |

## Objective

Before writing Phase 1 code, Velaris needs **external validation** from platform engineering teams who:

- Build test infrastructure for other developers
- Maintain integration/E2E suites (500+ tests ideally)
- Experience pain from fixture sprawl, driver lock-in, or inconsistent reporting
- Can critique RFC-001 (Capability Model) with real-world context

This document identifies target partner profiles, outreach channels, interview script, and selection criteria.

## Target partner profiles

### Profile A: Enterprise platform team (primary)

**Characteristics:**
- 50–500+ engineers in the organization
- Dedicated platform/DevOps/Test Infrastructure team (3+ people)
- Mixed pytest + Robot/Cypress/Playwright in different repos
- CI on GitHub Actions, GitLab CI, or Buildkite
- Pain: standardizing browser/API fixtures across business units

**Example organizations (archetypes, not confirmed partners):**

| Archetype | Why they fit |
|-----------|--------------|
| Fintech with compliance-driven E2E | Need swappable environments, audit trails, unified reporting |
| E-commerce platform team | Multi-team repos, Selenium legacy + Playwright migration |
| SaaS B2B with staging/production parity | Config-driven capability binding across envs |

### Profile B: Open-source project with integration test burden

**Characteristics:**
- OSS project with 100+ integration tests
- Maintainer acts as "platform team of one"
- Public CI visible on GitHub
- Willing to provide public feedback via GitHub issues/discussions

**Value:** Public credibility, real CI constraints, lower NDA friction.

**Example archetypes:**
- Database or API server projects (HTTP client testing pain)
- Developer tools with cross-platform E2E (editor plugins, CLI tools)

### Profile C: QA platform / test automation consultancy

**Characteristics:**
- Builds test frameworks for clients
- Sees repeated fixture sprawl patterns across clients
- Neutral on pytest vs new runner if capability contracts deliver value

**Value:** Broad pattern exposure, honest "build vs buy" feedback.

**Risk:** May prefer extending pytest for client deliverables.

## Recommended design partners (3 targets)

These are **identified targets for outreach**, not confirmed engagements. Update status as conversations progress.

### Partner 1: Enterprise fintech platform team

| Field | Value |
|-------|-------|
| Target | Platform engineering team at a mid-size fintech (500–2000 employees) |
| Entry point | Engineering blog authors on "test infrastructure", conference talks (PlatformCon, TestGuild) |
| LinkedIn search | "Test Platform Engineer", "SDET Lead", "Developer Experience" + fintech |
| Hypothesis | Compliance requires environment swapping; capability model resonates |
| Ask | 45-min RFC-001 review + async comments |
| Status | **Not contacted** |

### Partner 2: OSS infrastructure project maintainers

| Field | Value |
|-------|-------|
| Target | Maintainers of projects with heavy HTTP integration tests (e.g., API gateways, workflow engines, data platforms) |
| Entry point | GitHub issue or discussion: "RFC review request: test framework capability model" |
| Candidates to research | Projects using pytest + httpx with 200+ integration tests in `tests/integration/` |
| Hypothesis | Maintainer-as-platform-team validates Mode A side-by-side adoption |
| Ask | Public RFC comment + optional 30-min call |
| Status | **Not contacted** |

### Partner 3: Large-tech alumni platform network

| Field | Value |
|-------|-------|
| Target | Ex-FAANG/unicorn platform engineers now at growth-stage startups building test infra greenfield |
| Entry point | Personal network, LinkedIn, local platform engineering meetups |
| Hypothesis | Greenfield infra decisions happen now; no pytest lock-in yet |
| Ask | Design partner for Phase 1 prototype feedback |
| Status | **Not contacted** |

## Outreach channels

| Channel | Use for | Template |
|---------|---------|----------|
| LinkedIn direct message | Profile A, C | Short intro + link to RFC-001 |
| GitHub Discussion/Issue | Profile B | Public RFC review request |
| Platform engineering Slack/Discord communities | All profiles | "Seeking RFC reviewers" post |
| Conference CFP networking | Profile A | In-person follow-up after talks |
| Personal network warm intro | Partner 3 | Highest conversion |

## Outreach message template

**Subject:** RFC review request — capability-based test framework (30 min)

**Body:**

> I'm designing Velaris, a test framework for platform teams building org-wide test infrastructure. The core idea: tests declare capabilities (`api`, `browser`) and config selects implementations (httpx vs requests, Playwright vs Selenium) without changing test code.
>
> Before writing code, I'm seeking 2–3 platform engineers to critique RFC-001 (Capability Model). Not a sales pitch — I need honest feedback on whether this differs meaningfully from "pytest fixtures + a conventions doc."
>
> Time commitment:
> - 30–45 min call, or async review via GitHub comments
> - Review doc: [link to RFC-001]
>
> Ideal background: you've built shared test infrastructure, felt fixture sprawl pain, or evaluated build-vs-buy for internal pytest plugins.
>
> Interested? Reply with availability or comments on the RFC.

## Interview / review script

### Pre-read (send 48h before)

- [RFC-001: Capability Model](../rfc/RFC-001-capability-model.md)
- [RFC-006: pytest Coexistence](../rfc/RFC-006-pytest-coexistence.md)
- [api@0.1 Contract](../contracts/api-0.1.md)

### Opening (5 min)

1. Context: Velaris targets platform teams, not pytest replacement for unit tests
2. Ask their role and team size
3. Ask current test stack (pytest, Robot, Playwright Test, internal framework)

### Pain discovery (10 min)

1. How do teams in your org share browser/API fixtures today?
2. Have you swapped automation tools (Selenium → Playwright)? What broke?
3. How do devs vs QA author tests? Same repo, same runner?
4. What does your CI reporting look like across domains?

### RFC reaction (15 min)

1. Read the "capabilities vs fixtures" table — does this match your experience?
2. Would config-driven provider binding solve a problem you have today?
3. Is side-by-side pytest + Velaris (RFC-006 Mode A) acceptable in your org?
4. What's missing from `api@0.1` as a first contract?
5. **Kill question:** "Would you adopt this over an internal pytest plugin?" Why or why not?

### Closing (5 min)

1. Would you commit to async RFC comments within 2 weeks?
2. Interest in Phase 1 prototype demo (3 months out)?
3. NDA needed? Public attribution OK?

### Capture template

```markdown
## Interview: [Org/Person] — [Date]

**Role:**
**Stack:**
**Test count (approx):**

### Pain points
-

### RFC-001 feedback
-

### pytest coexistence reaction
-

### Would adopt over internal pytest plugin?
- [ ] Yes  [ ] No  [ ] Maybe
- Reason:

### Follow-up actions
-
```

## Selection criteria

Accept as design partner if **3 of 5** met:

| Criterion | Weight |
|-----------|--------|
| Platform team builds infra for others (not just app devs) | Required |
| 100+ integration/E2E tests in scope | High |
| Expressed fixture sprawl or driver swap pain | High |
| Willing to review RFC-001 within 2 weeks | Required |
| pytest coexistence model acceptable | Medium |
| Can demo Phase 1 prototype to real test suite (Phase 1 exit) | High |

Decline if:

- Only interested in unit test runner replacement
- No bandwidth for feedback (ghost partner)
- Requires features out of Phase 0–2 scope as precondition (e.g., mobile Day 1)

## Success metrics (Phase 0)

| Metric | Target | Status |
|--------|--------|--------|
| Outreach messages sent | 10+ | 0 |
| RFC review calls completed | 3 | 0 |
| Written RFC-001 comments received | 2+ external | 0 |
| Design partners committed for Phase 1 | 2 | 0 |
| "Would adopt" yes/maybe | ≥1 | 0 |

## Timeline

| Week | Activity |
|------|----------|
| 1 | Send outreach to 10 targets; post GitHub discussion for OSS profile |
| 2 | Schedule 3 review calls; incorporate async comments into RFC-001 |
| 3 | Select 2 design partners; document feedback summary |
| 4 | RFC-001 status → "Reviewed"; proceed to Phase 1 gate |

## Feedback incorporation process

1. Collect comments in `docs/design-partners/feedback/` (one file per reviewer)
2. Triage: **accept**, **defer**, **reject** with rationale
3. Update RFCs (not the plan file) based on accepted items
4. Publish summary: `docs/design-partners/feedback-summary.md` after 3 reviews

## Risks

| Risk | Mitigation |
|------|------------|
| No responses | Broaden to QA communities; offer public attribution |
| NDA delays enterprise | Start with OSS Profile B |
| Feedback is "just use pytest" | Document as valid outcome; triggers kill criteria review |
| Partners want mobile/browser Day 1 | Redirect to api@0.1 pilot scope; browser RFC later |

## Next actions (immediate)

1. [ ] Create public GitHub repo or discussions area for RFC comments (when repo is public)
2. [ ] Send 5 LinkedIn messages to Profile A archetypes
3. [ ] Identify 3 OSS projects matching Profile B; open discussion threads
4. [ ] Schedule first review call within 14 days
5. [ ] After first 3 interviews, publish `feedback-summary.md`

## References

- [RFC-001: Capability Model](../rfc/RFC-001-capability-model.md)
- [RFC-006: pytest Coexistence](../rfc/RFC-006-pytest-coexistence.md)
- Phase 0 exit criteria: 2 external reviewers on RFC-001
