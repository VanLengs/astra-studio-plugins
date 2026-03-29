---
name: status
description: Show the current state of all plugin development in studio/changes/. Use to check what's in progress, what's ready for review, or what needs attention. Also shows recently archived plugins.
allowed-tools: Read, Glob, Grep
user-invocable: true
---

# Studio Status

Display a dashboard of all active plugin development and recent archives.

## Steps

### Step 1: Check studio/ exists

If `studio/` doesn't exist, suggest running `/studio-core:init`.

### Step 2: Scan active changes

For each directory in `studio/changes/` (excluding `.gitkeep`):
1. Read `status.json` — if missing, show the entry with phase "unknown"
2. Check `type` field to distinguish workspace types:
   - `"type": "domain"` → domain-level workspace (event-storm, domain-map). Show domain name, `iteration`, and its `plugins` list.
   - `"type": "plugin"` (or no `type` field for legacy) → plugin-level workspace. Read `target_dir`, `action` (create/modify). Show plugin name, action, phase, target_dir, skill statuses.
3. For plugin workspaces:
   - Extract plugin name, phase, target_dir, skill statuses from status.json
   - Verify implementation exists: check that `{target_dir}/skills/` directory exists and contains SKILL.md files
   - Calculate completion: count skills with status `tested` vs total
   - If skills are in `draft`, `building`, or `built`, show the most advanced status reached so far
   - If `{target_dir}/` doesn't exist yet, note "target not scaffolded"

If `studio/changes/` is empty (only `.gitkeep`), note "No active work" and skip to Step 3.

### Step 3: Scan recent archives

List the 5 most recent archived iterations in `studio/archive/` across all plugin subdirectories.
For each archive entry, read `status.json` to get `shipped_to` and `archive_path` if available.

If `studio/archive/` is empty, note "No shipped plugins yet".

### Step 4: Display dashboard

Format as a table:

```
Studio Status
═════════════

Domains (studio/changes/)
  children-health    iteration 2    plugins: nutrition-planner, exercise-addon, health-reports

Plugins (studio/changes/ → target)
┌──────────────────┬─────────┬────────────┬────────────────┬───────────────────────────────┐
│ Plugin           │ Action  │ Phase      │ Skills         │ Target Dir                    │
├──────────────────┼─────────┼────────────┼────────────────┼───────────────────────────────┤
│ nutrition-planner│ create  │ building   │ 1/4 built      │ nutrition-planner             │
│ exercise-addon   │ modify  │ planning   │ 0/3 draft      │ exercise-addon                │
│ health-reports   │ create  │ approved   │ 2/2 tested     │ health-reports                │
└──────────────────┴─────────┴────────────┴────────────────┴───────────────────────────────┘

Recently Shipped (studio/archive/)
  auth-plugin/2026-03-25-iteration-1 → auth-plugin
  data-tools/2026-03-20-iteration-3  → data-tools
```

### Step 5: Suggest next actions

Based on current state, suggest what to do next:
- If a plugin is `approved`: "Run `/studio-core:promote {name}` to ship it"
- If a plugin is `building` and any skill is `draft` or `building`: "Continue the build stage to complete skill implementation"
- If a plugin is `building` and all in-scope skills are `built`: "Run `/studio-quality:validate {target_dir}` to approve it"
- If a plugin is `planning`: "Continue with `/studio-planner:plan`"
- If no active changes: "Run `/studio-planner:plan <domain>` to start"
