# Plugin Architecture Guide

Reference for designing Claude Code plugin collections. Used by `domain-model` to make architecture decisions.

## Core Concepts

### Plugin

A plugin is the **unit of installation** in Claude Code. It contains:
- A manifest (`.claude-plugin/plugin.json`)
- One or more skills (`skills/`)
- Optional: commands, hooks, MCP config, scripts, references

### Collection

A collection is a **marketplace repository** that groups related plugins. Users install individual plugins from a collection:
```bash
claude plugin marketplace add github:org/collection-name
claude plugin install plugin-name@collection-name
```

### Marketplace

A marketplace repo declares its plugins in `.claude-plugin/marketplace.json`.

---

## Architecture Patterns

### Pattern 1: Single Plugin

Use when the scope is narrow and self-contained.

```
my-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── skill-a/SKILL.md
│   └── skill-b/SKILL.md
└── commands/
```

**When to use:**
- 1-4 skills that share a single domain
- No optional features that users might want to exclude
- Simple install story

### Pattern 2: Core + Add-ons

Use when there's shared foundation logic plus optional extensions.

```
collection/
├── .claude-plugin/marketplace.json
├── core-plugin/              # required, others depend on it
│   ├── .claude-plugin/plugin.json
│   ├── skills/
│   └── templates/
├── addon-alpha/              # optional, imports from core
│   └── ...
└── addon-beta/               # optional, independent
    └── ...
```

**When to use:**
- 2-5 plugins with a clear shared base
- Some features are optional or domain-specific
- Users should be able to install only what they need

**Rules:**
- At most **one core** plugin per collection
- Core should be minimal — only what add-ons depend on
- Add-ons declare `"dependencies": ["core-plugin"]` in their manifest

### Pattern 3: Independent Plugins

Use when plugins are related by theme but not by dependency.

```
collection/
├── .claude-plugin/marketplace.json
├── plugin-alpha/
├── plugin-beta/
└── plugin-gamma/
```

**When to use:**
- Plugins share a domain but no code or data
- Each plugin is fully functional on its own
- Grouping is for discoverability, not dependency

---

## Decision Framework

### How Many Plugins?

| Signal | Recommendation |
|--------|---------------|
| All skills share data/context | 1 plugin |
| Some skills are optional or domain-specific | Core + add-ons |
| Skills serve different user personas | Separate plugins |
| 6+ skills in one plugin | Consider splitting |
| Users would install/uninstall parts independently | Separate plugins |

### Core vs Add-on Checklist

A plugin is **core** if:
- [ ] Removing it breaks other plugins in the collection
- [ ] It provides shared templates, schemas, or config
- [ ] It manages shared state (workspace, data directory)
- [ ] Other plugins import or reference its artifacts

A plugin is **add-on** if:
- [ ] It can be installed and uninstalled independently
- [ ] It adds optional capability to the collection
- [ ] It serves a subset of users

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Collection | `kebab-case`, short, domain-descriptive | `trading-ops` |
| Plugin | `kebab-case`, function-descriptive | `deal-screener` |
| Skill | `kebab-case`, verb-noun preferred | `analyze-portfolio` |
| Command | `kebab-case`, matches skill name | `analyze-portfolio` |

---

## Manifest Schema

```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "What this plugin does — one sentence",
  "author": {
    "name": "Author Name",
    "url": "https://github.com/author"
  },
  "license": "Apache-2.0",
  "keywords": ["relevant", "searchable", "terms"],
  "dependencies": ["other-plugin"],
  "skills": "./skills/",
  "commands": "./commands/",
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**Required fields:** `name`, `version`, `description`
**Optional fields:** everything else

---

## Boundaries and Scope

### What Goes in a Plugin

- Skills that users invoke (SKILL.md)
- Commands that alias skill invocations (commands/*.md)
- Hooks for lifecycle events (hooks/hooks.json)
- MCP server configuration (.mcp.json)
- Helper scripts used by skills (scripts/)
- Reference documents used by skills (references/)
- Templates used by skills (templates/)

### What Does NOT Go in a Plugin

- Application code (belongs in the project, not the plugin)
- User data or credentials (use environment variables)
- Large binary assets (reference external URLs)
- Duplicate functionality already in Claude Code built-ins
- Functionality that belongs in the official `skill-creator`

### Interaction with skill-creator

The official `skill-creator` handles the **inner loop**: writing a single skill, creating evals, benchmarking, iterating. Studio plugins handle the **outer loop**: deciding what plugins and skills to build, structuring them, validating, and shipping.

Do not duplicate skill-creator's capabilities. Instead, produce artifacts (SKILL.md skeletons) that skill-creator can consume.

---

## Plugin Traits

Traits are cross-cutting characteristics detected during `skill-design` that shape the plugin's architecture. They drive conditional scaffolding in `spec-generate`.

| Trait | What it means | What gets generated |
|-------|--------------|-------------------|
| `stateful` | Plugin manages project data across sessions | `init-workspace` skill, runtime config/status templates |
| `hil-gated` | Workflow has human approval checkpoints | `## Approval Gate` sections in relevant SKILL.md |
| `kb-dependent` | Skills need domain knowledge beyond LLM | KB integration notes; possibly companion KB plugin |
| `multi-pipeline` | 2+ independent business workflows | Per-pipeline orchestration commands |
| `expert-scoped` | Runtime needs different experts than planning | Runtime agent definitions in `agents/` |

Traits are observations, not configuration. They're detected from planning artifacts and confirmed by the user. A plugin with no detected traits follows the standard generation path.

---

## Runtime Patterns

### Runtime Workspace Pattern

Use when a plugin manages project data across sessions (trait: `stateful`).

```
.{plugin-name}/
├── config.yaml          # runtime configuration
├── projects/            # active project workspaces
│   └── {project-name}/
│       └── status.json  # project phase, skill completion
├── agents/
│   └── custom/          # project-specific expert overrides
└── archive/             # completed project deliverables
```

**When to use:**
- Plugin tracks project state (creation → in-progress → review → done)
- Users work on multiple projects simultaneously
- Project data should persist between sessions

**When NOT to use:**
- Plugin is stateless (single invocation, no project concept)
- Plugin only produces output files without tracking state

**Standard skills for stateful plugins:**
- `init-workspace` — creates `.{plugin-name}/` directory structure
- `manage-config` (optional) — view/update runtime settings
- `status` (optional) — show project dashboard

**Runtime workspace vs studio workspace:**
- `studio/` = plugin **development** workspace (design docs, planning artifacts)
- `.{plugin-name}/` = plugin **runtime** workspace (end-user project data)
- These serve different purposes and should never be conflated

### HIL Checkpoint Pattern

Use when a workflow requires human review/approval before proceeding (trait: `hil-gated`).

```markdown
## Approval Gate

1. Present draft result with clear summary
2. Ask for explicit confirmation:
   - ✅ Confirm — proceed
   - ✏️ Modify — apply changes and re-present
   - ❌ Reject — discard and explain what's needed
3. Record the decision in project status.json (if stateful)
```

**Rules:**
- Maximum one HIL checkpoint per skill. If a skill needs multiple gates, split it.
- The checkpoint always comes **after** the skill produces its draft, **before** it writes the final output.
- In pipeline orchestration commands, the pause between skills is implicit (user confirms before next step starts). HIL checkpoints are for **within-skill** approval gates that have different reviewers or higher stakes.
- Record decisions for audit trail: who approved, when, any notes.

### Knowledge Base Integration Pattern

Three levels of domain knowledge integration:

| Level | Mechanism | When to use |
|-------|-----------|-------------|
| **Inline** | `references/` in skill directory | 1-2 static documents, rarely updated |
| **Plugin-level** | `references/` at plugin root | Shared across skills, moderate volume |
| **Companion KB plugin** | Separate `{name}-kb` plugin with import/index/query skills | 3+ knowledge sources, frequently updated, needs search |

**Companion KB plugin structure:**
```
{name}-kb/
├── skills/
│   ├── kb-import/SKILL.md    # Import documents into KB
│   ├── kb-index/SKILL.md     # Index and categorize
│   └── kb-query/SKILL.md     # Search and retrieve
└── commands/
```

The main plugin declares a dependency on the KB plugin. Skills that need domain knowledge invoke `kb-query` or read from the KB directory.

### Multi-Pipeline Orchestration Pattern

Use when a plugin serves 2+ independent business workflows (trait: `multi-pipeline`).

```
{plugin-name}/
├── skills/
│   ├── shared-skill-a/       # used by multiple pipelines
│   ├── pipeline1-step1/      # pipeline 1 only
│   ├── pipeline1-step2/
│   ├── pipeline2-step1/      # pipeline 2 only
│   └── pipeline2-step2/
└── commands/
    ├── pipeline1.md           # orchestrates pipeline 1
    ├── pipeline2.md           # orchestrates pipeline 2
    └── shared-skill-a.md      # standalone invocation
```

**Rules:**
- Each pipeline gets its own orchestration command
- Shared skills are invocable standalone AND as part of pipelines
- Pipeline commands chain skills with user review pauses between steps
- Skill naming: prefix pipeline-specific skills with the pipeline name only if there's ambiguity; prefer descriptive verb-noun names
- Users can run any pipeline independently; no pipeline depends on another completing first
