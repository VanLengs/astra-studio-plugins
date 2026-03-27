---
name: promote
description: Promote an approved plugin from studio/changes/ to the target plugins directory. Use when a plugin has passed validation, all skills are tested, and you want to ship it. Handles file copy, manifest finalization, and archiving the development record.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# Studio Promote

Move a completed plugin from the development workspace (`studio/changes/`) to its production location, then archive the development record.

## Pre-conditions

1. If `$ARGUMENTS` is empty, scan `studio/changes/` for plugins with phase `approved` and list them. If exactly one, use it. If multiple, ask the user to choose. If none, explain what's needed and exit.
2. Read `studio/changes/$ARGUMENTS/status.json`
3. Verify `phase` is `approved` — if not, show the current phase and explain:
   - `planning` → "Run `/studio-planner:plan` to complete the design"
   - `building` → "Finish building skills using your preferred skill authoring tool"
   - `testing` → "Run `/studio-quality:validate` to approve it"
   - `shipped` → "This plugin has already been shipped"
4. Read `target_collection` from status.json (fallback to `studio/config.yaml` `defaults.target_collection`)
5. Verify all skills in status.json have status `tested` or `approved`

If pre-conditions fail, print a clear message about what needs to happen first and exit.

## Promote Steps

### Step 1: Determine target

```
{target_collection}/{plugin-name}/
```

Where `target_collection` is the path from status.json (e.g., `plugins/my-collection` or just `plugins`).

If the target directory already exists, ask the user whether to overwrite.

### Step 2: Build production plugin structure

Create the target directory with standard plugin layout:

```
{target}/{plugin-name}/
├── .claude-plugin/
│   └── plugin.json         # finalized from plugin.json.draft
├── skills/
│   └── {skill-name}/
│       ├── SKILL.md         # from studio/changes/{name}/skills/{skill}/SKILL.md
│       ├── evals/           # copy if present
│       ├── scripts/         # copy if present
│       └── references/      # copy if present
├── commands/                # copy if present
├── hooks/                   # copy if present
└── .mcp.json                # copy if present
```

When copying `plugin.json.draft` → `plugin.json`:
- Remove the `.draft` suffix
- Ensure `name`, `version`, `description` are present
- Set `skills` to `"./skills/"`
- Add `"commands": "./commands/"` if a commands/ directory exists
- Add `"hooks": "./hooks/hooks.json"` if a hooks/ directory exists
- Add `"mcpServers": "./.mcp.json"` if a .mcp.json file exists

### Step 3: Archive development record

Move `studio/changes/{name}/` to `studio/archive/{YYYY-MM-DD}-{name}/`

Update the archived `status.json`:
- Set `phase` to `shipped`
- Add `shipped_at` timestamp
- Add `shipped_to` path

### Step 4: Report

Print:
- What was promoted and where
- Archive location
- Remind user to review and commit: "Review the promoted plugin, then commit when ready"

## Does NOT

- Run `git add` or `git commit` — the user decides when to commit
- Delete source files — they're archived, not deleted
- Run validation — that should have happened before approval
