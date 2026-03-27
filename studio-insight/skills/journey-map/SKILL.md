---
name: journey-map
description: Create a user journey map that traces a persona's experience step by step — actions, touchpoints, emotions, pain points, and opportunities. Use when you need to understand user workflows, identify friction points, design service improvements, or when someone asks "what does the user experience look like". Produces a structured journey document.
allowed-tools: Read, Write, Glob, Agent
user-invocable: true
---

# Journey Map

Produce a professional user journey map that traces a specific persona through a real workflow — from trigger to outcome. Captures what the user does, how they feel, where they struggle, and where plugin opportunities exist.

Read `${CLAUDE_SKILL_DIR}/../../agents/product-manager.md` for the PM perspective that guides journey analysis.

## Inputs

Accept one of:
- A persona + scenario via `$ARGUMENTS` (e.g., "李妈妈的日常营养管理流程")
- A workspace path — read persona cards from `studio/changes/{name}/personas/` and `event-storm.md`

If a persona card exists at `studio/changes/{name}/personas/{persona}.md`, read it for context.

## Workflow

1. **Define scope** — which persona, which journey, start/end points
2. **Map stages** — break the journey into phases
3. **Detail each stage** — actions, touchpoints, thoughts, emotions
4. **Identify pain points and opportunities** — where to intervene
5. **Validate** — present to user
6. **Write output** — save journey map document

## Step 1: Define Scope

Clarify with the user:
- **Persona**: Who is going through this journey?
- **Scenario**: What are they trying to accomplish?
- **Trigger**: What starts this journey? (e.g., "早上起床准备早餐")
- **End state**: What does success look like? (e.g., "确认孩子今天营养达标")
- **Time span**: How long does this journey take? (minutes, hours, days, weeks)

## Step 2: Map Stages

Break the journey into 4-7 phases. Each phase represents a distinct mindset or context shift:

```
[触发] → [信息收集] → [决策] → [执行] → [验证] → [反思]
```

Name each phase with the user's language, not technical terms.

## Step 3: Detail Each Stage

For each stage, fill in the journey row:

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Stage    │ 准备早餐  │ 记录饮食  │ 查看报告  │ 获取建议  │ 调整计划  │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Actions  │ 翻食谱   │ 打开App  │ 看图表    │ 问营养师  │ 修改菜单  │
│          │ 查冰箱   │ 输入食物  │ 对比标准  │ 搜小红书  │          │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Touch-   │ 食谱书   │ Excel/   │ 无工具    │ 微信群   │ 手写笔记  │
│ points   │ 小红书   │ 微信备忘  │          │ 小红书   │          │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Thoughts │ 今天吃啥 │ 好麻烦   │ 看不懂   │ 等太久了  │ 希望简单  │
│          │ 有变化吗 │ 又忘了   │ 怎么调整  │ 不够针对  │ 点      │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Emotion  │ 😐 纠结  │ 😩 烦躁  │ 😕 困惑  │ 😤 焦虑  │ 😌 还行  │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Pain     │ 缺乏膳食 │ 记录成本 │ 数据不直 │ 专业建议 │          │
│ points   │ 计划     │ 太高     │ 观       │ 获取难   │          │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘
```

### Emotional Curve

Draw the emotional arc across stages:

```
高  ·                                          ·
    ·                                    ·····
    ·  ···                         ·····
中  ·······                  ······
    ·      ·····       ······
    ·           ·······
低  ·
    ├────────┼────────┼────────┼────────┼────────┤
    准备早餐   记录饮食   查看报告   获取建议   调整计划
```

## Step 4: Identify Pain Points and Opportunities

For each pain point found in the journey:

| # | Stage | Pain Point | Severity | Opportunity |
|---|-------|-----------|----------|-------------|
| 1 | 准备早餐 | 每天纠结吃什么 | 高 | 自动膳食计划推荐 |
| 2 | 记录饮食 | 记录太麻烦 | 高 | 语音/拍照快速记录 |
| 3 | 查看报告 | 看不懂营养数据 | 中 | 可视化 + 简单语言解读 |
| 4 | 获取建议 | 等回复太久 | 高 | AI 即时营养建议 |

Mark which opportunities could become **plugin skills**.

## Step 5: Validate

Present the complete journey map to the user:
- "Does this journey reflect real user behavior?"
- "Are there stages I missed?"
- "Is the emotional curve accurate?"
- "Which opportunities feel most impactful?"

## Step 6: Write Output

If working within a studio workspace:
```
studio/changes/{domain-or-plugin}/journeys/{persona-slug}-{scenario-slug}.md
```

If standalone, write to the current directory or let the user choose.

The file contains:
- Journey metadata (persona, scenario, trigger, end state)
- Stage-by-stage detail table
- Emotional curve (text diagram)
- Pain point × opportunity table
- Key insights summary
