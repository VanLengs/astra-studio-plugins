---
name: behavior-matrix
description: Create a behavior matrix that cross-references actors, actions, events, and data flows across a business domain. Use when you need a comprehensive view of who does what with what data, for gap analysis, permission modeling, test planning, or when someone asks "what are all the interactions in this system". Produces a structured matrix document.
allowed-tools: Read, Write, Glob, Grep, Agent
user-invocable: true
---

# Behavior Matrix

Produce a behavior matrix — a comprehensive cross-reference table showing every actor, the actions they perform, the events those actions trigger, and the data that flows between them. Reveals gaps, redundancies, and automation opportunities.

Read `${CLAUDE_SKILL_DIR}/../../agents/architect.md` for the system perspective.

## Inputs

Accept one of:
- A domain description via `$ARGUMENTS` (e.g., "儿童健康管理")
- A workspace path — read `event-storm.md` for events, `personas/` for actors, `processes/` for flows

## Workflow

1. **Enumerate actors** — who participates in this system
2. **Enumerate actions** — what can each actor do
3. **Map events** — what events does each action trigger
4. **Trace data** — what data flows in and out
5. **Build matrix** — cross-reference everything
6. **Analyze** — identify patterns, gaps, and opportunities
7. **Validate** — present to user
8. **Write output** — save matrix document

## Step 1: Enumerate Actors

List every actor in the system:

| Actor | Type | Description |
|-------|------|-------------|
| 家长 | User | 记录数据、查看报告、调整计划 |
| 营养AI | AI Agent | 评估营养、生成建议、创建膳食计划 |
| 系统 | System | 数据聚合、定时任务、推送通知 |
| 外部数据源 | External | 食物营养数据库 |

Actor types: **User** (human), **AI Agent** (Claude-powered), **System** (automated), **External** (third-party).

## Step 2: Enumerate Actions

For each actor, list all actions they can perform:

| Actor | Action | Frequency | Trigger |
|-------|--------|-----------|---------|
| 家长 | 记录一餐 | 每餐 | 主动 |
| 家长 | 查看周报 | 每周 | 主动 |
| 家长 | 设置目标 | 偶尔 | 主动 |
| 营养AI | 评估单餐 | 每次记录后 | 自动 |
| 营养AI | 生成膳食计划 | 每周 | 手动/自动 |
| 系统 | 聚合日数据 | 每天 | 定时 |
| 系统 | 推送提醒 | 条件触发 | 自动 |

## Step 3: Map Events

For each action, identify what events it triggers:

| Action | Triggers Event | Consumed By |
|--------|---------------|-------------|
| 记录一餐 | meal_recorded | 营养AI (评估) |
| 评估单餐 | nutrition_assessed | 系统 (聚合), 家长 (查看) |
| 生成膳食计划 | plan_generated | 家长 (查看/调整) |
| 聚合日数据 | daily_summary_ready | 系统 (检查阈值) |
| 检查阈值 | alert_triggered | 家长 (收到提醒) |

## Step 4: Trace Data

For each action, identify data inputs and outputs:

| Action | Reads (input) | Writes (output) |
|--------|--------------|-----------------|
| 记录一餐 | — | meal-log entry |
| 评估单餐 | meal-log entry, nutrition-profile | assessment result |
| 生成膳食计划 | nutrition-profile, meal history | weekly-plan |
| 聚合日数据 | all meal-logs of the day | daily-summary |
| 推送提醒 | daily-summary, thresholds | notification |

## Step 5: Build Matrix

Cross-reference into the full behavior matrix:

```
┌────────────┬───────────────┬─────────────────┬──────────────┬──────────────┐
│ Actor      │ Action        │ Event           │ Data In      │ Data Out     │
├────────────┼───────────────┼─────────────────┼──────────────┼──────────────┤
│ 家长       │ 记录一餐       │ meal_recorded   │ —            │ meal-log     │
│ 家长       │ 设置目标       │ goal_set        │ —            │ nutrition-   │
│            │               │                 │              │ profile      │
│ 家长       │ 查看周报       │ report_viewed   │ weekly-      │ —            │
│            │               │                 │ summary      │              │
├────────────┼───────────────┼─────────────────┼──────────────┼──────────────┤
│ 营养AI     │ 评估单餐       │ nutrition_      │ meal-log,    │ assessment   │
│            │               │ assessed        │ profile      │              │
│ 营养AI     │ 生成膳食计划   │ plan_generated  │ profile,     │ weekly-plan  │
│            │               │                 │ meal-history │              │
│ 营养AI     │ 个性化建议     │ advice_given    │ assessments, │ advice       │
│            │               │                 │ profile      │              │
├────────────┼───────────────┼─────────────────┼──────────────┼──────────────┤
│ 系统       │ 聚合日数据     │ daily_summary_  │ meal-logs    │ daily-       │
│            │               │ ready           │              │ summary      │
│ 系统       │ 推送提醒       │ alert_triggered │ summary,     │ notification │
│            │               │                 │ thresholds   │              │
└────────────┴───────────────┴─────────────────┴──────────────┴──────────────┘
```

## Step 6: Analyze

From the matrix, identify:

### Data Entity Map
List all unique data entities and who reads/writes them:

| Entity | Written by | Read by |
|--------|-----------|---------|
| meal-log | 家长 | 营养AI, 系统 |
| nutrition-profile | 家长 | 营养AI |
| weekly-plan | 营养AI | 家长 |
| daily-summary | 系统 | 系统, 家长 |

### Gaps
- Actions with no data output → side-effect only, might be missing persistence
- Data entities read but never written → external dependency or missing action
- Actors with only read actions → passive role, confirm if intentional

### Automation Opportunities
- High-frequency actions by users → automation candidates (plugin skills)
- System actions that need intelligence → AI skill candidates
- Manual handoffs between actors → orchestration candidates

### Skill Mapping Hints
Each row in the matrix can potentially map to a plugin skill:
- User actions → user-invocable skills
- AI actions → auto-triggered or invocable skills
- System actions → hook-triggered or scheduled tasks

## Step 7: Validate

Present the matrix and analysis to the user:
- "Is this complete? Any missing actors or actions?"
- "Are the data flows correct?"
- "Do the automation opportunities make sense?"

## Step 8: Write Output

If working within a studio workspace:
```
studio/changes/{domain}/behavior-matrix.md
```

If standalone, write to the current directory.

The file contains:
- Actor inventory
- Full behavior matrix table
- Data entity map
- Gap analysis
- Automation opportunities
- Skill mapping hints
