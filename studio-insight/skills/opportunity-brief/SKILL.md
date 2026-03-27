---
name: opportunity-brief
description: Create an opportunity assessment brief with hotspot ranking, impact/feasibility scoring, and ROI estimation for plugin candidates. Use when you need to prioritize what to build, justify investment, present options to stakeholders, or when someone asks "what should we build first". Produces a structured opportunity document.
allowed-tools: Read, Write, Glob, Agent
user-invocable: true
---

# Opportunity Brief

Produce a structured opportunity assessment that ranks plugin opportunities by impact and feasibility, with clear reasoning for what to build first. Designed for decision-makers — concise, evidence-based, actionable.

Read `${CLAUDE_SKILL_DIR}/../../agents/product-manager.md` for the PM perspective on prioritization.

## Inputs

Accept one of:
- A domain or project description via `$ARGUMENTS`
- A workspace path — read from `event-storm.md` (hotspots), `personas/` (user impact), `journeys/` (pain severity), `domain-canvas.md` (build strategy), `behavior-matrix.md` (automation potential)

The more prior artifacts exist, the more evidence-based the assessment.

## Workflow

1. **Collect evidence** — gather pain points, hotspots, and opportunities from artifacts
2. **Define candidates** — list plugin opportunities with scope
3. **Score** — rate impact and feasibility
4. **Estimate effort** — rough complexity and timeline indicators
5. **Rank and recommend** — prioritized list with rationale
6. **Validate** — present to user
7. **Write output** — save opportunity brief

## Step 1: Collect Evidence

Gather from available sources:

| Source | What to extract |
|--------|----------------|
| `event-storm.md` | Hotspots with severity ratings |
| `personas/*.md` | Who is affected, how severely |
| `journeys/*.md` | Pain points per stage, emotional lows |
| `processes/*.md` | Decision points, manual steps, bottlenecks |
| `domain-canvas.md` | Core vs supporting classification |
| `behavior-matrix.md` | Automation opportunities, data gaps |

If none of these exist, interview the user to gather equivalent information.

## Step 2: Define Candidates

Each opportunity candidate is a potential plugin or feature:

| ID | Candidate | Scope | Addresses |
|----|-----------|-------|-----------|
| OP-1 | 智能膳食计划 | 根据目标和偏好自动生成周计划 | HS-1 早餐纠结, PP-准备早餐 |
| OP-2 | 快速饮食记录 | 语音/文字快速记录一餐 | HS-2 记录成本高 |
| OP-3 | AI 营养顾问 | 即时个性化营养建议 | HS-3 咨询慢 |
| OP-4 | 运动方案适配 | 年龄段运动推荐 | HS-4 运动不知选什么 |

Keep candidates **focused** — each should be one plugin or one major feature, not a whole platform.

## Step 3: Score

Rate each candidate on two axes (1-5):

**Impact** — How much value does this deliver?
- 5: Daily use, eliminates a major pain point, affects all users
- 4: Frequent use, significantly reduces friction
- 3: Regular use, noticeable improvement
- 2: Occasional use, minor convenience
- 1: Rare use, minimal impact

**Feasibility** — How achievable is this?
- 5: Prompt-only skill, no external dependencies, proven pattern
- 4: Script-assisted, standard data processing
- 3: Needs domain knowledge base or moderate scripting
- 2: Needs MCP servers or external APIs
- 1: Needs complex orchestration, uncertain feasibility

```
        Feasibility →
    5   4   3   2   1
  ┌───┬───┬───┬───┬───┐
5 │★★★│★★★│★★ │★★ │★  │  ↑
  ├───┼───┼───┼───┼───┤  Impact
4 │★★★│★★ │★★ │★  │★  │
  ├───┼───┼───┼───┼───┤
3 │★★ │★★ │★  │★  │   │
  ├───┼───┼───┼───┼───┤
2 │★★ │★  │★  │   │   │
  ├───┼───┼───┼───┼───┤
1 │★  │★  │   │   │   │
  └───┴───┴───┴───┴───┘

★★★ = Build first   ★★ = Build next   ★ = Consider   (blank) = Defer
```

## Step 4: Estimate Effort

For each candidate, provide rough indicators:

| Candidate | Skills needed | Complexity tier | Dependencies | Effort hint |
|-----------|-------------|-----------------|-------------|-------------|
| 智能膳食计划 | 2 | Moderate | 营养数据库 | 中 |
| 快速饮食记录 | 1 | Simple | — | 小 |
| AI 营养顾问 | 1-2 | Simple | 累计数据 | 小 |
| 运动方案适配 | 2 | Moderate | 运动知识库 | 中 |

Effort hints: **小** (1-2 skills, simple tier), **中** (2-4 skills, moderate tier), **大** (4+ skills, script-heavy or MCP).

Do NOT give time estimates — they're unreliable at this stage.

## Step 5: Rank and Recommend

Produce the final priority ranking:

```
Priority Ranking
════════════════

 #  Candidate          Impact  Feasibility  Score  Effort
 1  快速饮食记录         5       5            25     小
    → 数据基础，其他一切都依赖它先存在

 2  AI 营养顾问         5       4            20     小
    → 高频痛点，替代人工咨询，prompt-only 可实现

 3  智能膳食计划         5       3            15     中
    → 核心价值，但需要营养数据库支撑

 4  运动方案适配         3       3             9     中
    → 有价值但非核心，可以后做

Recommendation:
  先建 #1 和 #2 — 两个小型 skill，快速验证价值
  然后建 #3 — 核心差异化功能
  #4 作为后续 add-on
```

Include a **dependency note** if candidates depend on each other (e.g., "AI 营养顾问 needs meal-log data from 快速饮食记录").

## Step 6: Validate

Present the ranking to the user:
- "Do you agree with the impact and feasibility scores?"
- "Are there business constraints that change the priority?" (budget, timeline, team capacity)
- "Any candidates I missed?"

The user may override scores based on factors not visible in the data (e.g., "investors want to see the meal planning feature first").

## Step 7: Write Output

If working within a studio workspace:
```
studio/changes/{domain}/opportunity-brief.md
```

If standalone, write to the current directory.

The file contains:
- Evidence summary (sources used)
- Candidate list with scope
- Impact × Feasibility scoring matrix
- Effort estimates
- Priority ranking with rationale
- Recommendation paragraph
- Dependencies between candidates
