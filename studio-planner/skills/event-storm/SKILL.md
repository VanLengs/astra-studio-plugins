---
name: event-storm
description: Run a multi-role brainstorming session to discover business events, user journeys, pain points, and processes. Use when starting a new plugin project, exploring a business domain, or when someone says "let's brainstorm" or "help me figure out what to build". Produces a structured event storm with personas, journeys, and process flows.
allowed-tools: Read, Write, Glob, Agent
user-invocable: true
---

# Event Storm

Run a structured brainstorming session with multiple perspectives — product manager, architect, and domain experts — to discover what's really going on in a business domain and where plugins can help.

## Pre-check

1. Verify `studio/` exists. If not, run the init skill first.
2. **Detect mode**: Check if `studio/changes/$ARGUMENTS/event-storm.md` already exists.
   - If yes → **Incremental mode**. Read existing artifacts to establish baseline.
   - If no → **Initial mode**. Fresh brainstorming session.
3. Load agent definitions using the **lookup order**:
   - First check `studio/agents/{name}.md` (project-level customizations)
   - Then fall back to built-in agents (in studio-insight and studio-planner)
   - Project-level agents override built-ins with the same filename
4. Always load: `product-manager.md` (PM) and `architect.md` (architect).
5. Read `_domain-expert-template.md` — used to create new domain experts on the fly.
6. Scan `studio/agents/` for any custom domain experts the team has created (via `/studio-insight:create-expert`).

## Execution Mode

At the start, ask the user which mode they prefer:

> **选择执行模式：**
> - **🔍 精细模式**（默认）— 每个步骤暂停确认，适合第一次使用或需要仔细校验的场景
> - **⚡ 快速模式** — 仅在 3 个关键节点暂停确认，适合探索性尝试或已有领域经验的用户
>   - 确认点 1: 专家角色 + 事件清单（合并 Step 1-2）
>   - 确认点 2: Persona + Journey + Process 一起展示（合并 Step 3-5）
>   - 确认点 3: Hotspot 排名（Step 6）

In **fast mode**, still generate all artifacts with the same quality — just batch the validation points. If the user spots issues in a batch, pause to fix before continuing.

## Incremental Mode

When running on a domain that already has `event-storm.md`, the session is **incremental** — it builds on previous work rather than starting from scratch.

### Entering incremental mode

Present the current state to the user:

> **检测到已有领域分析：`{domain-slug}`**
>
> | 已有产物 | 数量/状态 |
> |---------|----------|
> | 事件 | {N} 个已发现 |
> | Persona | {list} |
> | Journey | {list} |
> | 流程 | {list} |
> | 已关联插件 | {list from status.json plugins[]} |
>
> 请描述本次变更的背景：新增了什么？哪里需要修正？

### Incremental workflow

Each step focuses on **delta** — what's new or corrected:

- **Set the stage**: Review existing context, describe what changed
- **Discover events**: Focus on new/corrected events, update `event-storm.md` in-place
- **Build personas**: Only create new or revise existing ones (update file in-place)
- **Map journeys**: Only map new or revise impacted ones
- **Model processes**: Only model new or revise corrected ones
- **Identify hotspots**: Re-rank with full updated set

Revised artifacts are **updated in-place** — git diff is the revision history. New artifacts are appended to the existing directories normally.

## Workflow

1. **Set the stage** — understand the domain and assemble roles
2. **Discover events** — what happens in the business?
3. **Build personas** — invoke `studio-insight:persona-insight` for each user type
4. **Map user journeys** — invoke `studio-insight:journey-map` for each persona
5. **Model processes** — invoke `studio-insight:process-flow` for each major process
6. **Identify hotspots** — synthesize all artifacts to find opportunities
7. **Write output** — save event storm results to studio/changes/

## Step 1: Set the Stage

Ask the user to describe their business domain. Use the following **guided prompt** to help them structure their input:

> 请用 2-3 句话描述你的业务领域，包含以下三个要素：
> 1. **做什么** — 哪个行业/领域，为谁服务？
> 2. **现状** — 现在用什么工具/流程？最大的痛点是什么？
> 3. **期望** — 希望通过插件实现什么改变？

**Good vs Bad examples** — use these to coach the user if their initial description is too vague or too detailed:

| ❌ Too vague | ✅ Good | ❌ Too detailed |
|-------------|---------|----------------|
| "做一个健康管理产品" | "儿童健康 SaaS — 帮助家长管理 3-12 岁孩子的饮食和运动。目前用 Excel + 微信群，记录麻烦且缺乏专业指导" | "我需要一个可以拍照识别食物、自动计算卡路里、生成周报PDF、对接微信小程序的系统，用 React + Node.js 开发" |
| "帮我做个工具" | "跨境电商选品 — 帮助中小卖家在亚马逊上选品。目前人工刷榜单和看评价，效率低且容易错过趋势" | (features/tech stack = too early, this is about the domain) |
| "教育相关" | "K12 课后辅导机构 — 帮助老师管理 30+ 学生的作业和进度。目前用纸质登记，家长沟通全靠微信群发" | (technical architecture belongs in later phases) |

If the user's description is good, proceed. If too vague, ask them to add the missing element(s). If too detailed, say: "先聚焦业务场景，具体功能会在后续阶段自然浮现。"

Extract:
- **Industry/function**: What field is this? (e.g., pediatric health, fintech, content marketing)
- **Target users**: Who will use the plugins being designed?
- **Current situation**: What tools/processes exist today?

Based on the domain, **propose 2-4 domain expert roles**. Check for matching built-in experts first, then use the template for new ones.

Built-in domain experts available in studio-insight:
- `child-nutrition-expert.md` — pediatric dietary planning
- `child-exercise-expert.md` — pediatric movement and motor development
- `elderly-nutrition-expert.md` — geriatric diet and chronic disease
- `elderly-rehab-exercise-expert.md` — fall prevention and rehabilitation
- `skincare-expert.md` — women's skincare and dermatology

Also check `studio/agents/` for any custom experts the team has created.

If no built-in expert matches, use `_domain-expert-template.md` to create one on the fly — or suggest the user runs `/studio-insight:create-expert` to save it for reuse.

Present the proposed roles to the user with a brief explanation of **why each role is needed** and **what unique perspective it brings**. Format:

> **本次头脑风暴的参与角色：**
>
> | 角色 | 为什么需要 | 带来的独特视角 |
> |------|-----------|---------------|
> | 产品经理 | 确保从用户需求出发 | 用户行为模式、优先级排序 |
> | 架构师 | 评估技术可行性 | 系统边界、数据流、集成约束 |
> | {领域专家} | 提供专业领域知识 | {具体贡献，如"儿童营养的年龄差异标准"} |
>
> 你可以增加、删除或调整角色。确认后开始头脑风暴。

The user can adjust, add, or remove roles. Once confirmed, the brainstorming begins.

## Step 2: Discover Events

Before diving in, briefly explain the concept of "business events" to the user:

> **什么是业务事件？**
> 事件是"已经发生的事实"，用过去式描述。它不是功能需求，而是业务中真实发生的事情。
>
> | ❌ 不是事件（功能/需求） | ✅ 是事件（已发生的事实） |
> |------------------------|------------------------|
> | 记录餐食 | 早餐食物已记录 |
> | 需要一个营养计算器 | 单餐营养已评估 |
> | 支持多孩管理 | 第二个孩子档案已创建 |
> | 推送通知功能 | 营养不达标提醒已发送 |
>
> 我会以不同角色的视角分别列出事件，然后合并去重。你只需要看合并后的清单是否完整。

Adopt each role in turn and contribute **business events** — things that happen in the domain. For each event:

- **What happened**: past tense, one sentence (e.g., "Child's weekly meal plan was generated")
- **Who triggered it**: which actor or system
- **What it affects**: downstream consequences

Use the Agent tool to run each role as a subagent. Give each subagent:
- The role definition (from agents/*.md)
- The domain context from Step 1
- The instruction: "List 5-10 business events from your perspective"

Collect all events and **deduplicate** — different roles may describe the same event differently. Present the combined event list to the user for validation.

## Step 3: Build Personas

From the events discovered in Step 2, identify distinct user segments. **Propose the number and scope of personas** with reasoning:

> **建议创建的 Persona：**
>
> | Persona | 为什么单独建 | 与其他 Persona 的关键差异 |
> |---------|-------------|------------------------|
> | {name1} | {reason} | {difference} |
> | {name2} | {reason} | {difference} |
>
> **判断标准**：如果两类用户的 **目标、痛点、使用频率** 有显著差异，就值得拆分。
> 如果差异只在"偏好"层面（如界面语言），合并为一个即可。
> 建议 2-3 个 Persona，超过 4 个通常说明领域范围过大，可以考虑先聚焦。

Let the user confirm or adjust the persona list before proceeding.

Invoke the **studio-insight:persona-insight** skill for each confirmed user type. Pass:
- The domain context from Step 1
- The user segments discovered in Step 2
- The workspace path for output

This produces persona cards with empathy maps saved to `studio/changes/{domain-slug}/personas/`.

Present personas to the user for validation before proceeding.

## Step 4: Map User Journeys

For each persona, **propose which scenario to map** — typically the highest-frequency or highest-pain scenario:

> **每个 Persona 选择一个核心场景：**
>
> | Persona | 推荐场景 | 选择理由 | 频率 |
> |---------|---------|---------|------|
> | {name1} | {scenario} | {why — e.g., 最高频/最痛的场景} | {daily/weekly} |
> | {name2} | {scenario} | {why} | {frequency} |
>
> **选场景的原则**：选 **最能暴露痛点** 的场景，而不是最复杂的场景。
> 一个 Persona 画一条 Journey 就够了，后续需要可以追加。

Let the user confirm or adjust scenario selection.

Invoke the **studio-insight:journey-map** skill for each persona's selected scenario. Pass:
- The persona card from Step 3
- The events from Step 2
- The workspace path for output

This produces journey maps saved to `studio/changes/{domain-slug}/journeys/`.

Present journey maps to the user. Ask: "Does this match your experience? What's missing?"

## Step 5: Model Processes

From the events and journeys, identify **major business processes** (not every micro-step — focus on processes that span multiple actors or have decision points):

> **建议建模的业务流程：**
>
> | 流程 | 触发 → 结果 | 涉及几个参与者 | 为什么值得建模 |
> |------|------------|--------------|---------------|
> | {process1} | {trigger → outcome} | {N} | {reason — e.g., 有关键决策点} |
> | {process2} | {trigger → outcome} | {N} | {reason} |
>
> **判断标准**：一个流程值得建模，通常因为它 **跨多个角色** 或 **有分支判断**。
> 纯线性、单角色的操作不需要单独建模。

Let the user confirm process list.

Invoke the **studio-insight:process-flow** skill for each confirmed process. Pass:
- The events from Step 2
- The actors from persona cards
- The workspace path for output

This produces process flow diagrams saved to `studio/changes/{domain-slug}/processes/`.

Decision points and parallel branches are **natural boundaries for skill splitting** — note this for the next skill (domain-model).

## Step 6: Identify Hotspots

Synthesize all artifacts (events, personas, journeys, processes) to find **hotspots** — areas with concentrated pain, high frequency, or high stakes.

For each hotspot:
- **ID**: `HS-1`, `HS-2`, etc.
- **Description**: What's going wrong or could be better
- **Evidence**: Which events, journey pain points, and process bottlenecks point here
- **Severity**: High (daily impact, significant cost) / Medium (weekly friction) / Low (occasional annoyance)
- **Type**: Efficiency (too slow), Accuracy (error-prone), Knowledge (hard to find info), Integration (tools don't talk), Compliance (regulatory risk)

Rank hotspots by severity. Present with **transparent reasoning** so the user can adjust:

> **热点排名：**
>
> | 排名 | 热点 | 严重度 | 类型 | 判断依据 |
> |------|------|--------|------|---------|
> | 1 | {desc} | 高 | 效率 | Persona {X} 痛点 #1 + Journey {Y} 情绪最低点 + Process {Z} 瓶颈 |
> | 2 | {desc} | 高 | 知识 | Persona {X} 痛点 #3 + 专家指出缺乏{...} |
> | ... | | | | |
>
> **类型说明：**
> - **效率** — 做得到但太慢/太麻烦
> - **准确** — 容易出错，后果大
> - **知识** — 信息难获取或需要专业判断
> - **集成** — 工具之间不连通，需要手动搬数据
> - **合规** — 有法规/安全风险
>
> **如果你觉得排名不对**，告诉我哪个该上升/下降以及原因，我会调整。
> 常见调整理由：实际频率比我估计的高/低、有些痛点用户已经习惯了（虽然痛但不紧急）、某些痛点有监管压力必须优先。

### Knowledge Base Dependencies

For each hotspot, assess whether addressing it requires **domain knowledge beyond general LLM capability**:

> **知识库依赖分析：**
>
> | 热点 | 需要的领域知识 | 知识类型 | 更新频率 |
> |------|-------------|---------|---------|
> | {HS-1} | {e.g., 儿童营养标准表} | 结构化数据 | 年度更新 |
> | {HS-2} | {e.g., 教学大纲对照} | 参考文档 | 学期更新 |
> | {HS-3} | — (通用 LLM 能力足够) | — | — |
>
> **知识类型说明：**
> - **参考文档** — 静态指南、标准、规范（放在 `references/` 即可）
> - **结构化数据** — 表格、数据库、需要查询和匹配的知识（可能需要 KB 插件）
> - **历史案例** — 过往项目、案例库、需要检索的知识（建议 KB 插件）
> - **实时数据** — 需要 API 或外部数据源（需要 MCP 集成）
>
> 如果有 3+ 个知识源且更新频率较高，建议创建伴生 KB 插件来管理领域知识。

This analysis feeds the `kb-dependent` trait in skill-design.

### Expert Scope Analysis

Determine which domain experts are needed only during planning (this brainstorming session) vs also during runtime (when end users operate the plugin):

> **专家范围分析：**
>
> | 专家角色 | 规划阶段 | 运行阶段 | 说明 |
> |---------|---------|---------|------|
> | 产品经理 | ✅ | — | 仅用于规划（确定需求和优先级） |
> | 架构师 | ✅ | — | 仅用于规划（系统设计和边界） |
> | {领域专家 A} | ✅ | ✅ | 规划 + 运行（运行时用于质量审核） |
> | {领域专家 B} | — | ✅ | 仅运行时（用于实时建议和校验） |
>
> **规则：**
> - 规划阶段专家 → 保留在 `studio-insight/agents/` 或 `studio/agents/`，不随插件分发
> - 运行阶段专家 → 需要作为 agent 定义随插件分发到 `{target_dir}/agents/`
> - 两者兼有 → 规划阶段使用 studio 版本，运行阶段使用随插件分发的版本（可以是同一个定义的副本）

This analysis feeds the `expert-scoped` trait in skill-design.

## Step 7: Write Output

Create the workspace and save results. By this point the artifact skills have already created subdirectories:

```
studio/changes/{domain-slug}/
├── event-storm.md       # synthesized brainstorming output (updated in-place on iterations)
├── changelog.md         # append-only iteration log
├── status.json          # { type: "domain", iteration: N }
├── personas/            # created by persona-insight skill
│   ├── {persona-1}.md
│   └── {persona-2}.md
├── journeys/            # created by journey-map skill
│   └── {persona-scenario}.md
└── processes/           # created by process-flow skill
    └── {process-name}.md
```

**Derive `{domain-slug}`** from the domain description: lowercase, kebab-case, 2-3 words (e.g., "children-health", "trading-ops").

### event-storm.md

In **initial mode**, write all events, hotspots, and synthesis normally.

In **incremental mode**, update `event-storm.md` in-place — add new events, revise existing ones, re-rank hotspots. Git diff serves as the revision history.

### changelog.md

On every run, append an entry to `studio/changes/{domain-slug}/changelog.md`:

```markdown
## {YYYY-MM-DD}

**Summary**: {1-2 sentence description of what changed}

### Added
- {New persona: health-conscious-grandparent}
- {New journey: grandparent-weekly-checkup}

### Revised
- {Corrected process: meal-recording — fixed missing validation step}

### Impact on Plugins
- `{plugin-a}`: needs modification — {reason}
- `{plugin-b}`: new plugin needed — {reason}
- `{plugin-c}`: no change
```

For the first run, the "Added" section lists everything.

### status.json

Update `studio/changes/{domain-slug}/status.json`:

```json
{
  "type": "domain",
  "domain": "{domain-slug}",
  "iteration": 2,
  "phase": "planning",
  "created_at": "{original timestamp}",
  "updated_at": "{now ISO-8601}",
  "plugins": ["{existing-plugin-1}", "{new-plugin}"]
}
```

The `iteration` field is the current iteration number. The `plugins` list is cumulative.

Write `event-storm.md` with the following sections:

```markdown
# Event Storm: {Domain}

> Date: {YYYY-MM-DD}
> Roles: {list of roles used}

## Domain Context
{Summary from Step 1}

## Events
{Categorized event list from Step 2}

## Artifacts Produced
- Personas: see `personas/` directory
- User Journeys: see `journeys/` directory
- Process Flows: see `processes/` directory

## Hotspots
{Ranked hotspot list from Step 6}

## Knowledge Base Dependencies
{KB dependency table from Step 6 — which hotspots need domain knowledge, what type, update frequency}

## Expert Scope
{Expert scope table from Step 6 — which experts are planning-only vs runtime vs both}

## Decision Points
{List of all ◇ decision points — these inform skill boundaries}
```

Note: domain-level workspaces have `"type": "domain"` and a cumulative `plugins` list. Use the status schema shown above in the `### status.json` section. Plugin-level workspaces have `"type": "plugin"` and a `skills` map. The `domain-model` skill will create plugin-level workspaces and populate the `plugins` list here.

Present a **Phase 1 Summary** that ties all artifacts together before suggesting next steps:

> **📋 发现阶段完成 — 总览**
>
> **领域**：{domain description}
> **参与角色**：{roles used}
>
> **发现了什么：**
> - **{N} 个业务事件** — 覆盖 {event clusters summary, e.g., "档案管理、饮食记录、运动跟踪、报告生成 4 大类"}
> - **{N} 个用户画像** — {persona names and one-line summaries}
> - **{N} 条用户旅程** — {journey names}
> - **{N} 个业务流程** — {process names}
> - **{N} 个热点机会** — 其中 {M} 个为高严重度
>
> **Top 3 热点（下一阶段的重点）：**
> 1. {HS-1 description} — {severity} / {type}
> 2. {HS-2 description} — {severity} / {type}
> 3. {HS-3 description} — {severity} / {type}
>
> **所有产出文件：**
> ```
> studio/changes/{domain-slug}/
> ├── event-storm.md          ← 事件清单 + 热点排名
> ├── personas/{name1}.md     ← 用户画像
> ├── personas/{name2}.md
> ├── journeys/{name}.md      ← 用户旅程
> └── processes/{name}.md     ← 业务流程
> ```
>
> **下一步做什么：**
> 阶段二（领域建模）会基于以上产出，划分插件边界和技能拆分。
> 运行 `/studio-planner:domain-model {domain-slug}` 进入阶段二，
> 或运行 `/studio-planner:plan {domain-slug}` 继续完整流水线。
