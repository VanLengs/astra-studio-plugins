---
name: skill-design
description: Design the skill breakdown for a plugin — enumerate skills, map data flow, assess complexity, and plan implementation. Use after domain-model when you have plugin candidates and need to decide what individual skills each plugin should contain. Produces a skill map with dependencies and complexity tiers.
allowed-tools: Read, Write, Glob, Grep, Agent
user-invocable: true
---

# Skill Design

Break a plugin down into individual skills with clear responsibilities, data flow, and complexity assessment.

Consult `${CLAUDE_SKILL_DIR}/../../references/skill-decomposition-guide.md` for split/merge rules, naming conventions, and complexity tiers.

## Pre-check

1. Verify `studio/` exists.
2. If `$ARGUMENTS` is a plugin name, read `studio/changes/$ARGUMENTS/status.json` to get the `action` field and `domain`.
3. Read the parent domain's `domain-map.md` that references this plugin.
4. If no domain-map.md exists, this skill can work from a user description — but recommend running event-storm and domain-model first for better results.
5. Read `${CLAUDE_SKILL_DIR}/../../agents/architect.md` — the architect perspective leads skill design.
6. **For `action: "modify"`**: Also read the existing SKILL.md files in `{target_dir}/skills/` to understand the current implementation.

## Workflow

1. **Identify capabilities** — what should this plugin be able to do?
2. **Group into skills** — apply single-responsibility principle
3. **Define interfaces** — inputs, outputs, and boundaries for each skill
4. **Map data flow** — how do skills connect?
5. **Assess complexity** — what does each skill need to work?
6. **Write output** — save skill map to the workspace

## Step 1: Identify Capabilities

List everything the plugin should be able to do. Sources:
- `domain-map.md`: the events and responsibilities assigned to this plugin's domain
- `event-storm.md`: the process flows and decision points within this domain
- User input: additional capabilities they want

Express each capability as a **user action**: "As [persona], I want to [action] so that [outcome]".

**For `action: "modify"`**: Start by listing the **existing** capabilities from `{target_dir}/skills/*/SKILL.md`, then overlay the changes from the domain's `changelog.md` and updated `event-storm.md`:
- New capabilities not covered by existing skills
- Modified capabilities where existing skill behavior needs to change
- Existing capabilities that remain unchanged

Present the analysis:

> **现有 Skill 与变更的匹配分析：**
>
> | 现有 Skill | 现有能力 | 受变更影响？ | 影响说明 |
> |-----------|---------|------------|---------|
> | {skill-a} | {desc} | ✅ 不变 | — |
> | {skill-b} | {desc} | ✏️ 需修改 | {what changed} |
> | — | {new capability} | 🆕 新增 | {why needed} |

## Step 1.5: Detect Plugin Traits

Before grouping capabilities into skills, analyze the domain artifacts to detect **plugin traits** — cross-cutting characteristics that shape the plugin's architecture. Traits are inferred from planning artifacts, not configured manually.

Scan `domain-map.md`, `event-storm.md`, and the capabilities list from Step 1 for these signals:

| Trait | Detection Signal | Downstream Impact |
|-------|-----------------|-------------------|
| `stateful` | Plugin manages project data across sessions (e.g., user profiles, plans, records); capabilities reference "create project", "track progress", "manage workspace" | spec-generate creates `init-workspace` skill skeleton + runtime config/status templates |
| `hil-gated` | Process flows contain human approval/review gates; capabilities reference "review", "approve", "confirm before publishing" | Skills split at approval boundaries; SKILL.md skeletons get `## Approval Gate` sections |
| `kb-dependent` | Skills need domain knowledge beyond general LLM capability (regulatory tables, professional standards, historical data) | Notes KB integration needs; may recommend companion KB plugin |
| `multi-pipeline` | Domain has 2+ independent business workflows with different entry points, steps, and outputs (e.g., "design pipeline" vs "lesson pipeline" vs "planning pipeline") | spec-generate creates per-pipeline orchestration commands |
| `expert-scoped` | Runtime skills need domain experts different from planning-phase experts (e.g., planning uses architect; runtime uses curriculum-expert) | Distinguishes planning vs runtime experts; runtime experts ship with the plugin in `agents/` |

Present the trait analysis to the user:

> **插件特征分析：**
>
> | 特征 | 是否检测到 | 检测依据 | 下游影响 |
> |------|-----------|---------|---------|
> | 有状态 (stateful) | ✅ / — | {evidence} | {impact} |
> | 人在回路 (hil-gated) | ✅ / — | {evidence} | {impact} |
> | 知识库依赖 (kb-dependent) | ✅ / — | {evidence} | {impact} |
> | 多流水线 (multi-pipeline) | ✅ / — | {evidence} | {impact} |
> | 专家分域 (expert-scoped) | ✅ / — | {evidence} | {impact} |
>
> 特征会影响后续骨架生成的内容。你可以增加或移除特征，确认后继续。

The user confirms or adjusts before proceeding. Traits flow into the skill-map.md output (Step 6) and are consumed by spec-generate.

**Trait-driven architectural implications:**

- **stateful** → add `init-workspace` and optionally `manage-config` as standard skills in Step 2
- **hil-gated** → ensure skills split at every approval boundary (one HIL checkpoint per skill maximum)
- **kb-dependent** → if knowledge needs are complex (3+ distinct sources, frequent updates), recommend a companion `{plugin-name}-kb` plugin; otherwise inline as `references/`
- **multi-pipeline** → each pipeline gets its own orchestration command; skills may be pipeline-specific or shared across pipelines
- **expert-scoped** → runtime experts become agent definitions in `{target_dir}/agents/`, separate from studio-insight planning agents

## Step 2: Group into Skills

Apply the single-responsibility principle to group capabilities into skills.

**Split when:**
- The capability serves a different persona
- There's a user decision point between two sub-tasks
- The description needs "and" to join unrelated actions
- Different capabilities need different tool access (e.g., one needs Bash, another only needs Read)
- There is an HIL checkpoint (approval gate) between two sub-tasks — each gate must be in its own skill
- The capability spans two independent pipelines — split into pipeline-specific skills
- The plugin is `stateful` but has no workspace initialization — add a dedicated `init-workspace` skill

**Merge when:**
- Two capabilities always run in sequence with no user review between them
- One capability's only purpose is to feed the next
- A capability is too small to stand alone (1-2 trivial steps)

**Naming**: kebab-case, verb-noun pattern preferred. Be specific enough for Claude's trigger matching:
- Good: `generate-meal-plan`, `analyze-nutrition`, `track-progress`
- Bad: `process-data`, `do-stuff`, `helper`

## Step 3: Define Interfaces

For each skill, specify:

| Field | Description |
|-------|-------------|
| **Inputs** | What data the skill receives (files, arguments, context) |
| **Outputs** | What the skill produces (files, terminal output, side effects) |
| **Out of scope** | What this skill explicitly does NOT do |
| **Preconditions** | What must be true before this skill runs |

This prevents scope creep and makes dependencies explicit.

## Step 4: Map Data Flow

Show how skills connect:

```
[generate-meal-plan]
    │ produces: meal-plan.json
    ▼
[analyze-nutrition]
    │ produces: nutrition-report.md
    ▼
[track-progress] ←── [import-measurements] (parallel, independent)
    │ produces: progress-dashboard.md
    ▼
[generate-weekly-summary]
```

Rules:
- No circular dependencies
- Data flows in one direction (pipeline or fan-out)
- Independent skills can run in parallel
- Orchestration is handled by commands, not hard-wired into skills

Mark which connections are **required** (skill B cannot run without A's output) vs **optional** (skill B can use A's output if available, but also works standalone).

## Step 5: Assess Complexity

For each skill, classify into an implementation tier:

| Tier | Characteristics | allowed-tools | Structure |
|------|-----------------|---------------|-----------|
| **Simple** | Prompt instructions only, no computation | Read, Write, Glob | SKILL.md + references/ |
| **Moderate** | Needs helper scripts for data processing or validation | Read, Write, Bash, Glob, Grep | SKILL.md + scripts/ |
| **Script-heavy** | Significant automation, data transformation | Read, Write, Bash, Glob, Grep, Edit | SKILL.md + scripts/ + references/ |
| **MCP-dependent** | Requires external service access | + MCP tools | SKILL.md + scripts/ + .mcp.json |

Also note:
- Does this skill need to invoke subagents? (multi-perspective analysis)
- Does this skill need web access? (research, API calls)
- Does this skill need file system access beyond the project? (MCP filesystem)

**Trait-driven fields** — for each skill, also record:
- **Pipeline**: which business pipeline this skill belongs to (or "shared" if used by multiple pipelines). Only relevant when `multi-pipeline` trait is detected.
- **HIL checkpoint**: `yes` if this skill contains an approval gate, `no` otherwise. Only relevant when `hil-gated` trait is detected.
- **KB needs**: what domain knowledge this skill requires beyond general LLM capability (e.g., "nutrition standards table", "regulatory compliance rules"). Only relevant when `kb-dependent` trait is detected.

## Step 6: Write Output

Write `studio/changes/{plugin-name}/skill-map.md`:

```markdown
# Skill Map: {plugin-name}

> Date: {YYYY-MM-DD}
> Action: {create | modify}

## Skills

### {skill-name}
- **Description**: {one sentence — specific, action-oriented}
- **Inputs**: {what it receives}
- **Outputs**: {what it produces}
- **Out of scope**: {what it does NOT do}
- **Complexity**: {Simple / Moderate / Script-heavy / MCP-dependent}
- **allowed-tools**: {comma-separated list}
- **Preconditions**: {what must be true}

### {skill-name-2}
...

## Data Flow
{Flow diagram from Step 4}

## Complexity Summary

| Skill | Tier | Scripts needed | MCP needed |
|-------|------|---------------|------------|
| {name} | Simple | — | — |
| {name} | Moderate | data_processor.py | — |
| {name} | MCP-dependent | — | web-search |

## Plugin Traits

| Trait | Detected | Evidence |
|-------|----------|----------|
| stateful | ✅ / — | {evidence from Step 1.5} |
| hil-gated | ✅ / — | {evidence} |
| kb-dependent | ✅ / — | {evidence} |
| multi-pipeline | ✅ / — | {evidence} |
| expert-scoped | ✅ / — | {evidence} |

## Pipelines

_(Only include this section when `multi-pipeline` trait is detected)_

### {pipeline-name-1}
- **Entry point**: {trigger or command}
- **Skills**: {skill-a} → {skill-b} → {skill-c}
- **Output**: {what this pipeline produces}

### {pipeline-name-2}
- **Entry point**: {trigger or command}
- **Skills**: {skill-d} → {skill-e}
- **Output**: {what this pipeline produces}

### Shared skills
- {skill-f} — used by both pipelines

## Implementation Order
{Recommended order to build skills, based on dependencies}
1. {skill-a} — no dependencies, can start immediately
2. {skill-b} — depends on skill-a's output format
3. {skill-c} — depends on skill-b
```

For `action: "modify"`, only list skills that need work (new or modified). Unchanged skills can be noted briefly at the bottom but don't need full specs.

Update `studio/changes/{plugin-name}/status.json`:
- Add each skill that needs work with status `draft`
- Keep phase as `planning`

```json
{
  "skills": {
    "existing-skill-b": "draft",
    "new-skill-c": "draft"
  }
}
```

Tell the user: "Skill design complete. Run `/studio-planner:spec-generate {plugin-name}` to generate all specification files, then confirm the build stage to let Astra Studio invoke skill-creator automatically."
