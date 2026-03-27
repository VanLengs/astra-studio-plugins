---
name: domain-canvas
description: Create a domain canvas that maps business domains, their classifications (core/supporting/generic), boundaries, and relationships. Use when you need to understand system architecture, draw service boundaries, decide what to build vs buy, or when someone asks "how should we structure this". Produces a structured domain model document.
allowed-tools: Read, Write, Glob, Grep, Agent
user-invocable: true
---

# Domain Canvas

Produce a domain canvas — a visual map of business domains, their roles, boundaries, and interactions. Helps decide what deserves a custom plugin (core), what's supporting, and what can use off-the-shelf tools.

Read `${CLAUDE_SKILL_DIR}/../../agents/architect.md` for the architect perspective on boundaries and dependencies.

## Inputs

Accept one of:
- A domain description via `$ARGUMENTS` (e.g., "儿童健康管理平台")
- A workspace path — read `event-storm.md` for events and `personas/` for actors

## Workflow

1. **Discover domains** — identify distinct business areas
2. **Define boundaries** — what each domain owns and doesn't own
3. **Classify** — core vs supporting vs generic
4. **Map relationships** — how domains interact
5. **Draw canvas** — produce the visual domain map
6. **Validate** — present to user
7. **Write output** — save domain canvas document

## Step 1: Discover Domains

Identify distinct business areas by clustering:
- **By data ownership**: entities that are always accessed together
- **By actor**: who interacts with this area
- **By business rule**: rules that apply to the same concepts
- **By change frequency**: things that change together

Use the **language test**: if practitioners use different vocabulary, it's probably a different domain.

Name each domain in **plain business language** (2-3 words):
- Good: "营养管理", "运动追踪", "健康报告"
- Bad: "NutritionService", "Module3", "后端逻辑"

## Step 2: Define Boundaries

For each domain, specify:

```
┌─────────────────────────────────────┐
│  {Domain Name}                      │
├─────────────────────────────────────┤
│  Owns:                              │
│  - {data entities}                  │
│  - {business rules}                 │
│  - {user-facing capabilities}       │
│                                     │
│  Does NOT own:                      │
│  - {explicit exclusions}            │
│  - {things that belong elsewhere}   │
│                                     │
│  Key actors:                        │
│  - {who interacts with this domain} │
│                                     │
│  Key events:                        │
│  - {events this domain produces}    │
│  - {events this domain consumes}    │
└─────────────────────────────────────┘
```

The boundary test: "If I removed this domain entirely, would the others still make sense?"

## Step 3: Classify

Assess each domain:

```
┌───────────────────────────────────────────────────────────┐
│                    Domain Classification                   │
├──────────────┬──────────┬─────────────────────────────────┤
│ Domain       │ Type     │ Rationale                       │
├──────────────┼──────────┼─────────────────────────────────┤
│ 营养管理      │ Core     │ 核心差异化，用户选择产品的原因      │
│ 运动追踪      │ Support  │ 重要辅助，但不是主打              │
│ 用户档案      │ Generic  │ 标准 CRUD，内置工具可满足          │
│ 健康报告      │ Support  │ 有价值但依赖其他域数据             │
└──────────────┴──────────┴─────────────────────────────────┘
```

| Type | Meaning | Build strategy |
|------|---------|---------------|
| **Core** | Unique value, competitive advantage | Custom plugin, invest in quality |
| **Supporting** | Necessary but not differentiating | Add-on plugin, adequate quality |
| **Generic** | Standard capability | Use existing tools (MCP, built-in) |

## Step 4: Map Relationships

Define how domains interact:

| Relationship | Symbol | Meaning |
|-------------|--------|---------|
| Feeds into | `──▶` | A produces data that B consumes |
| Shares data | `◀──▶` | Both read/write same entities |
| Independent | `· · ·` | No interaction |
| Orchestrates | `══▶` | A coordinates B's behavior |

## Step 5: Draw Canvas

Produce the domain canvas as a visual map:

```
┌──────────────────────────────────────────────────┐
│                Domain Canvas                      │
│                {Project Name}                     │
├──────────────────────────────────────────────────┤
│                                                  │
│   ┌──────────────┐         ┌──────────────┐     │
│   │  营养管理 ★    │──▶──▶──│  健康报告     │     │
│   │  [Core]       │         │  [Supporting] │     │
│   └──────┬───────┘         └──────▲───────┘     │
│          │                        │              │
│          │ shares                  │ feeds        │
│          ▼                        │              │
│   ┌──────────────┐               │              │
│   │  用户档案     │               │              │
│   │  [Generic]   │               │              │
│   └──────┬───────┘               │              │
│          │                        │              │
│          │ feeds                   │              │
│          ▼                        │              │
│   ┌──────────────┐               │              │
│   │  运动追踪     │──▶──▶────────┘              │
│   │  [Supporting] │                              │
│   └──────────────┘                              │
│                                                  │
│  ★ = Core domain                                │
│  [Generic] domains → use existing tools          │
└──────────────────────────────────────────────────┘
```

## Step 6: Validate

Present the canvas to the user:
- "Does this domain structure match your mental model?"
- "Do you agree with the core/supporting/generic classifications?"
- "Are the relationships correct?"
- "Is anything missing?"

## Step 7: Write Output

If working within a studio workspace:
```
studio/changes/{domain}/domain-canvas.md
```

If standalone, write to the current directory.

The file contains:
- Domain inventory with boundary definitions
- Classification table with rationale
- Relationship map (text diagram)
- Full domain canvas visualization
- Build strategy recommendations (which domains → plugins, which → existing tools)
