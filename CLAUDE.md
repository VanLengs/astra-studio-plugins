# Astra Studio Plugins

This is a marketplace of Claude Code plugins for plugin development workflows. Each subdirectory is a standalone plugin.

## Repository Structure

```
├── studio-core/         # Workspace management (init, promote, status)
├── studio-planner/      # Plugin planning (business insight, architecture, skill decomposition)
├── studio-quality/      # Quality assurance (plugin validation, MCP wiring)
```

## Plugin Structure

Each plugin follows this layout:
```
plugin-name/
├── .claude-plugin/plugin.json   # Plugin manifest (name, description, version)
├── commands/                    # Slash commands (.md files)
├── skills/                      # SKILL.md files for specific tasks
│   └── skill-name/SKILL.md
├── hooks/                       # Event-driven automation (hooks.json)
├── scripts/                     # Python helper scripts
├── references/                  # Reference docs loaded on demand
└── templates/                   # File templates for scaffolding
```

## Key Files

- `.claude-plugin/marketplace.json`: Marketplace manifest — registers all plugins with source paths
- `.claude-plugin/plugin.json`: Root-level marketplace metadata
- `*/plugin.json`: Per-plugin metadata — name, description, version, dependencies
- `commands/*.md`: Slash commands invoked as `/plugin:command-name`
- `skills/*/SKILL.md`: Detailed knowledge and workflows with YAML frontmatter (name, description, allowed-tools)
- `templates/`: Scaffolding templates used by init skill to create `studio/` in user projects

## Design Principles

1. **Plugin-first**: The workspace (`studio/changes/`) is organized by plugin, not by skill
2. **Outer loop only**: Individual skill authoring delegates to the built-in `anthropic-skills:skill-creator`
3. **Git-tracked workspace**: `studio/` directory in user projects is version-controlled (briefs, status, design decisions)
4. **Promote target unified**: `studio/changes/{plugin}/ → plugins/{collection}/{plugin}/` regardless of collection type
5. **Standard Claude Code plugin spec**: No proprietary extensions — works with any Claude Code installation

## Workspace Lifecycle

When a user runs `/studio-core:init` in their project, it creates:
```
studio/
├── config.yaml          # Studio configuration
├── changes/             # Active plugin development (one dir per plugin)
│   └── {plugin-name}/
│       ├── brief.md           # Business context
│       ├── plugin.json.draft  # Manifest draft
│       ├── status.json        # Phase tracking (planning→building→testing→approved→shipped)
│       └── skills/            # Skill specs and evals
└── archive/             # Shipped plugin dev records
```

## Development Workflow

1. Edit SKILL.md files directly — changes take effect immediately when loaded via `--plugin-dir`
2. Test commands with `/plugin:command-name` syntax (e.g., `/studio-core:init`)
3. Skills trigger automatically when their description matches user intent
4. Test locally: `claude --plugin-dir ./studio-core --plugin-dir ./studio-planner --plugin-dir ./studio-quality`
