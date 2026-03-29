# Astra Studio Plugins

This is a marketplace of Claude Code plugins for plugin development workflows. Each subdirectory is a standalone plugin.

## Repository Structure

```
├── studio-core/         # Workspace management (init, promote, status, create-expert) — 4 skills
├── studio-insight/      # Business analysis toolkit (personas, journeys, processes, domains) — 6 skills
├── studio-planner/      # Planning pipeline (event-storm, domain-model, skill-design, spec-generate, build-skills) — 5 skills
├── studio-quality/      # Quality assurance (plugin validation, MCP wiring) — 2 skills
```

## Plugin Dependencies

```
studio-core      (zero deps)
studio-insight   (zero deps)
studio-planner   (depends on studio-core + studio-insight)
studio-quality   (zero deps)
```

## Plugin Structure

Each plugin follows this layout:
```
plugin-name/
├── .claude-plugin/plugin.json   # Plugin manifest (name, description, version)
├── commands/                    # Slash commands (.md files)
├── skills/                      # SKILL.md files for specific tasks
│   └── skill-name/SKILL.md
├── agents/                      # Subagent role definitions (.md files)
├── hooks/                       # Event-driven automation (hooks.json)
├── scripts/                     # Python helper scripts
├── references/                  # Reference docs loaded on demand
└── templates/                   # File templates for scaffolding
```

## Key Files

- `.claude-plugin/marketplace.json`: Marketplace manifest — registers all 4 plugins with source paths
- `.claude-plugin/plugin.json`: Root-level marketplace metadata
- `*/plugin.json`: Per-plugin metadata — name, description, version, dependencies
- `commands/*.md`: Slash commands invoked as `/plugin:command-name`
- `skills/*/SKILL.md`: Detailed knowledge and workflows with YAML frontmatter (name, description, allowed-tools)
- `agents/*.md`: Subagent role definitions — personas adopted by Claude during multi-role brainstorming
- `templates/`: Scaffolding templates used by init skill to create `studio/` in user projects

## Agent System

studio-insight ships 11 built-in agent roles + 1 template:
- **General roles**: product-manager, architect, ux-researcher, data-analyst, compliance-officer, operations-manager
- **Health domain**: child-nutrition-expert, child-exercise-expert, elderly-nutrition-expert, elderly-rehab-exercise-expert
- **Beauty domain**: skincare-expert
- **Template**: `_domain-expert-template.md` for creating new experts

Agent lookup order: `studio/agents/` (project-level) > built-in `agents/` (plugin-level). Same-name overrides.

All 6 insight skills use **dynamic expert discovery** — they scan for relevant domain experts at runtime and invoke them for review via the Agent tool.

## Design Principles

1. **Spec-implementation separation**: `studio/changes/` holds only design documents (brief, skill-map, status, plugin.json.draft). Implementation files (SKILL.md, commands, scripts) live directly in the target plugin directory — single source of truth, no duplication.
2. **Plugin-first**: The workspace (`studio/changes/`) is organized by plugin, not by skill
3. **Outer loop orchestration**: Astra Studio orchestrates planning, build, validation, and shipping, while individual skill authoring is executed through the built-in `anthropic-skills:skill-creator`
4. **Git-tracked workspace**: `studio/` directory in user projects is version-controlled (briefs, status, design decisions)
5. **Standard Claude Code plugin spec**: No proprietary extensions — works with any Claude Code installation
6. **Platform-neutral outputs**: SKILL.md skeletons produced by spec-generate contain no Claude-specific references — they run on any compatible runtime
7. **Customizable experts**: Users create domain experts via `/studio-core:create-expert`, saved to `studio/agents/` (git-tracked, team-shared)

## Workspace Lifecycle

When a user runs `/studio-core:init` in their project, it creates:
```
studio/
├── config.yaml          # Studio configuration
├── agents/              # Custom domain expert definitions (override built-ins)
├── changes/             # Design documents only — NO executable implementation
│   ├── {domain}/              # Domain-level workspace (type: "domain")
│   │   ├── event-storm.md     # Brainstorming output (updated in-place on iterations)
│   │   ├── changelog.md       # Append-only iteration log
│   │   ├── domain-map.md      # Domain analysis
│   │   ├── domain-canvas.md   # Domain boundaries
│   │   ├── behavior-matrix.md # Actor/action/event matrix
│   │   ├── opportunity-brief.md # Priority assessment
│   │   ├── personas/          # Persona cards
│   │   ├── journeys/          # Journey maps
│   │   ├── processes/         # Process flows
│   │   └── status.json        # { type: "domain", iteration: N, plugins: [...] }
│   └── {plugin-name}/        # Plugin-level workspace (type: "plugin")
│       ├── brief.md           # Business context
│       ├── plugin.json.draft  # Manifest draft
│       ├── skill-map.md       # Skill design rationale
│       └── status.json        # { type: "plugin", domain, target_dir, action, phase }
└── archive/             # Shipped plugin design records

{target_dir}/                  # Implementation — single source of truth
├── skills/{skill}/SKILL.md    # Skeletons generated here by spec-generate
├── commands/{skill}.md        # Command files generated here
├── scripts/                   # Helper scripts created here
├── hooks/                     # Hooks created here
└── .mcp.json                  # MCP config created here
```

## Two-level Workspace Model

- **Domain workspace** (`type: "domain"`): Holds event-storm.md, domain-map.md, and artifact outputs (personas/, journeys/, processes/). Shared across multiple plugins.
- **Plugin workspace** (`type: "plugin"`): Holds design docs only (skill-map.md, brief.md, plugin.json.draft). References parent domain via `domain` field and implementation location via `target_dir` field in status.json. Does NOT contain SKILL.md or commands — those live in `{target_dir}/`.

## Iteration Model

Domains evolve incrementally. Each re-run of the pipeline on an existing domain is an **iteration** that builds on previous work:

- **Artifacts are updated in-place** — event-storm.md, personas, journeys, processes are revised directly. Git diff is the revision history.
- **changelog.md** tracks each iteration — what was added, revised, and which plugins are impacted.
- **Plugin actions**: Only `create` and `modify`. Unchanged plugins don't appear in `studio/changes/`.
- **Small changes bypass the pipeline** — users can directly edit SKILL.md files or other implementation without re-running event-storm/domain-model.

## Planning Pipeline

`/studio-planner:plan` chains 5 pipeline skills, each invoking insight artifact skills:

```
event-storm → persona-insight + journey-map + process-flow
     ↓
domain-model → domain-canvas + behavior-matrix + opportunity-brief
     ↓
skill-design
     ↓
spec-generate → SKILL.md skeletons (platform-neutral output)
     ↓
build-skills → auto-build via skill-creator
```

## Development Workflow

1. Edit SKILL.md files directly — changes take effect immediately when loaded via `--plugin-dir`
2. Test commands with `/plugin:command-name` syntax (e.g., `/studio-core:init`)
3. Skills trigger automatically when their description matches user intent
4. Test locally: `claude --plugin-dir ./studio-core --plugin-dir ./studio-insight --plugin-dir ./studio-planner --plugin-dir ./studio-quality`
