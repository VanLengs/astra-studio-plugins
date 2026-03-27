# Plugin Architecture Guide

Reference for designing plugin collections. Used by `domain-model` to make architecture decisions.

## Core Concepts

### Plugin

A plugin is the **unit of installation**. It contains:
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
- Duplicate functionality already available as built-in platform tools

### Interaction with Skill Authoring Tools

Skill authoring tools handle the **inner loop**: writing a single skill, creating evals, benchmarking, iterating. Studio plugins handle the **outer loop**: deciding what plugins and skills to build, structuring them, validating, and shipping.

Do not duplicate skill authoring capabilities. Instead, produce artifacts (SKILL.md skeletons) that authoring tools can consume.
