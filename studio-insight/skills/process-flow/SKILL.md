---
name: process-flow
description: Create a business process flow diagram showing events in sequence, decision points, parallel branches, actors, and data flow. Use when you need to model a workflow, document a business process, identify automation opportunities, or when someone asks "how does this process work". Produces a structured process document.
allowed-tools: Read, Write, Glob, Agent
user-invocable: true
---

# Process Flow

Produce a business process flow that shows how work actually happens — who does what, in what order, where decisions are made, and where things can happen in parallel. Designed for clarity, not technical notation.

## Expert Discovery

This skill uses **dynamic expert loading**. On every run:

1. **Primary role**: Always load `architect.md` (leads process design)
2. **Scan project experts**: Glob `studio/agents/*.md` — load all custom experts the team has created
3. **Scan built-in experts**: Glob `${CLAUDE_SKILL_DIR}/../../agents/*.md` — load shipped experts (skip any already loaded from project)
4. **Match by relevance**: From the loaded experts, select those relevant to the current domain context. Match by comparing the expert's `## Your Domain` section and title against the user's input topic. Include 1-3 most relevant domain experts.
5. **Skip template**: Do not load `_domain-expert-template.md` — it's for creating new experts, not for consultation.

The primary role produces the initial artifact. Domain experts review and correct it in the Expert Review step.

## Inputs

Accept one of:
- A process description via `$ARGUMENTS` (e.g., "从饮食记录到生成营养周报的流程")
- A workspace path — read `event-storm.md` for events and actors to model

## Workflow

1. **Define scope** — which process, boundaries, actors
2. **List events** — everything that happens in this process
3. **Order events** — arrange in time sequence
4. **Mark decision points** — where does the flow branch?
5. **Identify parallelism** — what can happen simultaneously?
6. **Assign actors** — who or what performs each step?
7. **Expert review** — domain experts verify process accuracy
8. **Validate** — present to user
9. **Write output** — save process flow document

## Step 1: Define Scope

If the user is unfamiliar with process modeling, provide a quick orientation:

> **流程图怎么看？**
> 把一件事从"开始"到"结束"画成路线图。只有 3 种元素：
> - **方框 `[xxx]`** = 一个动作发生了
> - **菱形 `◇ xxx？`** = 一个判断点，走不同的路
> - **箭头 `→`** = 顺序，从上到下、从左到右
>
> 你不需要自己画，我会生成后请你看看"是不是你们实际的做法"。

Clarify:
- **Process name**: What is this process called?
- **Trigger**: What starts it? (user action, schedule, external event)
- **End states**: What are the possible outcomes? (success, failure, exception)
- **Boundary**: What's included vs out of scope?
- **Frequency**: How often does this run? (per meal, daily, weekly)

## Step 2: List Events

Enumerate every event (thing that happens) in the process. Express in past tense:
- "早餐食物被记录"
- "单餐营养被评估"
- "不达标提醒被发送"

If reading from `event-storm.md`, filter to events relevant to this process scope.

## Step 3: Order Events

Arrange events into a time-ordered sequence. Use a text flow diagram:

```
[Trigger: 家长打开App]
    │
    ▼
[记录本餐食物]
    │
    ▼
[系统计算营养成分]
    │
    ▼
◇ 是否达标？
    ├─ 是 → [显示达标确认] → [累计到日统计]
    │
    └─ 否 → [生成调整建议] → [推送提醒] → [累计到日统计]
                                                │
                                                ▼
                                        ◇ 今天三餐都记录了？
                                            ├─ 否 → [等待]
                                            └─ 是 → [生成日营养总结]
```

### Notation

| Symbol | Meaning |
|--------|---------|
| `[事件]` | A step/event that happens |
| `◇ 问题？` | A decision point (flow branches) |
| `→` | Flow direction |
| `│ ▼` | Vertical flow |
| `├─` | Branch |
| `(Actor)` | Who performs this step |

## Step 4: Mark Decision Points

For each `◇` decision point:

| ID | Decision | Condition | True path | False path |
|----|----------|-----------|-----------|------------|
| D1 | 是否达标？ | 营养值 >= 目标80% | 显示确认 | 生成建议 |
| D2 | 三餐都记录了？ | 早+午+晚都有记录 | 生成日总结 | 等待 |

Decision points are **natural boundaries for skill splitting** — note this for skill design.

## Step 5: Identify Parallelism

Mark steps that can happen simultaneously:

```
[记录饮食] ──→ [计算营养]
                              ── 可并行 ──
[记录运动] ──→ [计算运动量]
```

Parallel branches mean:
- Independent data flows → can be separate skills
- No ordering dependency → can run concurrently
- Merge point → where parallel branches converge

## Step 6: Assign Actors

Map each step to its actor using swim lanes or annotations:

```
家长:     [记录食物] ─────────────────── [查看建议] ── [确认/调整]
系统:                → [计算营养] → ◇ → [生成建议] ──┘
AI:                                     [分析模式] → [个性化推荐]
```

Actor types:
- **User**: Human performing an action
- **System**: Automated computation or data processing
- **AI**: Claude-powered analysis or generation
- **External**: Third-party service or API

## Step 7: Expert Review

If domain experts were discovered in Expert Discovery, use the Agent tool to have each relevant expert review the process flow.

Give each expert subagent:
- Their agent definition (.md file content)
- The draft process flow (events, decisions, actors, parallel branches)
- The instruction: "Review this business process from your domain expertise. Flag: steps that are out of order or missing, decision conditions that are wrong, actors assigned to the wrong steps, exception paths not accounted for, and regulatory or safety checkpoints that must be included."

Incorporate corrections. Common improvements from domain experts:
- Missing steps that are invisible to outsiders but critical in practice
- Decision conditions that are more nuanced than the architect assumed
- Regulatory checkpoints that must happen at specific points
- Exception paths that happen frequently but weren't modeled

If no relevant domain experts were found, skip this step.

## Step 8: Validate

Present the complete process flow to the user:
- "Does this match how it actually works (or should work)?"
- "Are there exception paths I missed?" (errors, timeouts, edge cases)
- "Are the decision conditions correct?"
- "Are the actor assignments right?"

## Step 9: Write Output

If working within a studio workspace:
```
studio/changes/{domain-or-plugin}/processes/{process-slug}.md
```

If standalone, write to the current directory.

The file contains:
- Process metadata (name, trigger, end states, frequency)
- Full flow diagram (text notation)
- Decision point table
- Parallelism notes
- Actor swim lanes
- Key observations (bottlenecks, automation candidates, exception paths)
