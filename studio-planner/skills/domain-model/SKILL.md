---
name: domain-model
description: Analyze event storm results to identify business domains, draw plugin boundaries, and map relationships between them. Use after event-storm, when you have a set of events and processes and need to decide how many plugins to build and what each one owns. Produces a domain map with plugin candidates.
allowed-tools: Read, Write, Glob, Grep, Agent
user-invocable: true
---

# Domain Model

Take the raw output from event-storm and organize it into clear business domains, each mapping to a potential plugin. Determine what's core vs supporting vs off-the-shelf.

Consult `${CLAUDE_SKILL_DIR}/../../references/plugin-architecture-guide.md` for collection architecture patterns and core/add-on decision framework.

## Pre-check

1. Verify `studio/` exists.
2. If `$ARGUMENTS` is provided, read `studio/changes/$ARGUMENTS/event-storm.md`. If it doesn't exist, ask the user to run `/studio-planner:event-storm` first.
3. If no argument, scan `studio/changes/` for workspaces that have `event-storm.md` but no `domain-map.md`, or whose `domain-map.md` is outdated (check `updated_at` in status.json vs event-storm.md modification). If exactly one, use it. If multiple, ask the user to choose.
4. Read `${CLAUDE_SKILL_DIR}/../../agents/architect.md` — the architect perspective leads this step.
5. **Detect mode**: Read `studio/changes/{domain}/status.json`. If `plugins` list is non-empty → **Incremental mode**: compare updated event clusters against existing plugins. Otherwise → **Initial mode**: all candidates are `create`.

## Workflow

1. **Cluster events** — group related events into business domains
2. **Build domain canvas** — invoke `studio-insight:domain-canvas` to define boundaries, classify, and map relationships
3. **Build behavior matrix** — invoke `studio-insight:behavior-matrix` to cross-reference actors, actions, events, and data
4. **Propose plugins** — translate domains into plugin candidates
5. **Assess opportunities** — invoke `studio-insight:opportunity-brief` to prioritize
6. **Write output** — save domain map to the workspace

## Step 1: Cluster Events

Read the events and process flows from `event-storm.md`. Group them by **business affinity** — events that share the same data, actors, or business rules belong together.

Guidelines for clustering:
- Events that must happen **atomically** (all-or-nothing) belong in the same domain
- Events that different **user personas** own may indicate separate domains
- Events connected by **data flow** often cluster together
- When in doubt, use the **language test**: do practitioners use the same vocabulary for these events? If yes, same domain.

Present the clusters to the user: "I see these natural groupings — does this match how you think about your business?"

## Step 2: Build Domain Canvas

Invoke the **studio-insight:domain-canvas** skill with the domain workspace path. Pass:
- The event clusters from Step 1
- The workspace path for output

This produces `studio/changes/{domain}/domain-canvas.md` with:
- Domain boundary definitions (what each domain owns and doesn't)
- Classifications (core / supporting / generic)
- Relationship map between domains
- Build strategy recommendations

Present the domain canvas to the user for validation before proceeding.

## Step 3: Build Behavior Matrix

Invoke the **studio-insight:behavior-matrix** skill with the domain workspace path. Pass:
- The events, personas, and processes from event-storm artifacts
- The workspace path for output

This produces `studio/changes/{domain}/behavior-matrix.md` with:
- Actor × Action × Event × Data cross-reference
- Data entity ownership map
- Gap analysis
- Automation opportunities and skill mapping hints

## Step 4: Propose Plugins

Translate each non-generic domain into a plugin candidate. In **incremental mode**, also assess existing plugins for changes.

### Initial mode (iteration 1)

For each candidate:
- **Plugin name**: kebab-case, derived from domain name (e.g., `meal-planner`)
- **Domain**: Which domain it represents
- **Role**: `core` or `add-on` (from classification)
- **Action**: `create`
- **Responsibility**: 1-2 sentence description of what it does
- **Expected skills**: Rough list of capabilities (will be refined in skill-design)
- **Dependencies**: Which other plugins it depends on
- **MCP needs**: External services it might need (from generic domain analysis)

### Incremental mode

For each domain cluster, determine whether it maps to an **existing** or **new** plugin:

1. Read the `plugins` list from the domain's `status.json`
2. Cross-reference the updated event clusters and `changelog.md` impact section
3. Classify each candidate: `create` (new) or `modify` (existing plugin with changed events/processes)

Plugins that are **not affected** by this iteration do NOT appear in `studio/changes/` — skip them.

Present the **impact assessment** to the user:

> **插件影响分析：**
>
> | 插件 | 动作 | 原因 |
> |------|------|------|
> | {name} | 🆕 新建 | {reason} |
> | {name} | ✏️ 修改 | {reason} |
>
> 不受影响的插件不会出现在变更列表中。确认后我会创建对应的变更工作区。

The user must explicitly confirm before proceeding. This is a key decision point.

### Collection structure decision

Same rules as initial mode:
- 1 plugin → single plugin, no collection
- 2-5 related plugins → one collection with clear core
- Independent plugins in different domains → separate collections

## Step 5: Assess Opportunities

Invoke the **studio-insight:opportunity-brief** skill with the domain workspace path. Pass:
- All prior artifacts (event-storm, personas, journeys, domain-canvas, behavior-matrix)
- The plugin candidates from Step 4

This produces `studio/changes/{domain}/opportunity-brief.md` with:
- Impact × Feasibility scoring for each plugin candidate
- Priority ranking with rationale
- Effort estimates and dependency notes

Present the opportunity assessment to the user. They may reorder priorities based on business constraints.

## Step 6: Write Output

Write `studio/changes/{name}/domain-map.md`:

```markdown
# Domain Map: {Domain}

> Date: {YYYY-MM-DD}
> Iteration: {N}

## Artifacts
- Domain Canvas: see `domain-canvas.md`
- Behavior Matrix: see `behavior-matrix.md`
- Opportunity Brief: see `opportunity-brief.md`

## Plugin Candidates

| Plugin | Domain | Role | Action | Description | Dependencies | Priority |
|--------|--------|------|--------|-------------|-------------|----------|
| {name} | {domain} | core | create | {desc} | — | 1 |
| {name} | {domain} | add-on | modify | {desc} | {core-name} | 2 |

## Generic Capabilities (no custom plugin needed)
- {capability} → {existing solution}

## Collection Structure
- **Pattern**: {single / core+add-on / independent}
- **Rationale**: {why this structure}
```

### Create workspace per plugin

**For `action: "create"` plugins**:

```
studio/changes/{plugin-name}/
└── status.json
```

```json
{
  "type": "plugin",
  "plugin": "{plugin-name}",
  "domain": "{domain-slug}",
  "target_collection": ".",
  "target_dir": "{plugin-name}",
  "action": "create",
  "iteration": {N},
  "phase": "planning",
  "created_at": "{ISO-8601}",
  "skills": {}
}
```

Also create the target plugin directory as an empty scaffold:

```
{target_dir}/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep
```

**For `action: "modify"` plugins** — create a change workspace referencing the existing target:

```
studio/changes/{plugin-name}/
└── status.json
```

```json
{
  "type": "plugin",
  "plugin": "{plugin-name}",
  "domain": "{domain-slug}",
  "target_collection": ".",
  "target_dir": "{plugin-name}",
  "action": "modify",
  "iteration": {N},
  "phase": "planning",
  "created_at": "{ISO-8601}",
  "skills": {}
}
```

Do NOT create a new target directory scaffold — the target already exists.

The `domain` field points to `studio/changes/{domain-slug}/` where `event-storm.md` and `domain-map.md` live. This avoids duplicating domain-level artifacts into each plugin workspace.

The `target_dir` field is where implementation files (SKILL.md, commands, scripts) will be written by `spec-generate` and edited by `skill-creator`. This is the **single source of truth** for runnable code — `studio/changes/` only holds design documents.

Also update the domain workspace's `status.json` — add new plugins to the `plugins` list and bump `iteration`:

```json
{
  "type": "domain",
  "domain": "{domain-slug}",
  "iteration": {N},
  "phase": "planning",
  "created_at": "...",
  "updated_at": "{now ISO-8601}",
  "plugins": ["{plugin-name-1}", "{plugin-name-2}", "{new-plugin}"]
}
```

The `plugins` list is cumulative — it contains all plugins ever associated with this domain.

Tell the user: "Domain model complete. Run `/studio-planner:skill-design {plugin-name}` to design skills for each plugin."
