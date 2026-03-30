---
name: promote
description: Create a versioned milestone for an approved plugin — convert the manifest draft to production, snapshot design documents, and prepare for the next iteration. Supports iterative promotion (v0.1 → v0.2). Use when a plugin has passed validation, all skills are tested, and you want to ship a version.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# Studio Promote

Create a versioned milestone for a plugin and prepare for continued iteration. Implementation files already live in the target plugin directory (written there by `spec-generate` and developed in place) — promote only needs to finalize the manifest and snapshot the design docs.

## Design Principle

`studio/changes/` holds **design documents** (brief.md, skill-map.md, plugin.json.draft, status.json). Implementation files (SKILL.md, commands, scripts, hooks) live directly in the **target plugin directory** as the single source of truth. Promote does NOT copy implementation files — they are already where they belong.

**Promotion is a milestone, not a terminal state.** Design documents are **copied** to the archive (not moved), so the active workspace remains available for the next iteration. This supports the natural lifecycle where plugins evolve continuously after initial shipping.

Promote works identically for `action: "create"` and `action: "modify"` — in both cases it finalizes the manifest and snapshots the change workspace.

## Pre-conditions

1. If `$ARGUMENTS` is empty, scan `studio/changes/` for plugins with phase `approved` and list them. If exactly one, use it. If multiple, ask the user to choose. If none, explain what's needed and exit.
2. Read `studio/changes/$ARGUMENTS/status.json`
3. Verify `phase` is `approved` — if not, show the current phase and explain:
   - `planning` → "Run `/studio-planner:plan` to complete the design"
   - `building` → "Continue the build stage so Astra Studio can finish skill implementation"
   - `testing` → "Run `/studio-quality:validate` to approve it"
   - `shipped` → "This plugin has already been shipped"
4. Read `target_dir` from status.json (fallback: derive from `target_collection` + plugin name)
5. Verify `{target_dir}/` exists and contains at least a `skills/` directory with SKILL.md files
6. Verify all in-scope skills in status.json have status `tested`

If pre-conditions fail, print a clear message about what needs to happen first and exit.

## Promote Steps

### Step 1: Verify target plugin directory

Check that `{target_dir}/` already has the expected structure:

```
{target_dir}/
├── skills/
│   └── {skill-name}/
│       └── SKILL.md         # should already exist (written by spec-generate, developed by the build stage via skill-creator)
├── commands/                # should already exist if skills are user-invocable
└── ...                      # scripts/, hooks/, .mcp.json may also exist
```

If the target directory is missing or empty, abort: "Target directory `{target_dir}/` does not contain implementation files. Did you run `/studio-planner:spec-generate` first?"

### Step 2: Finalize plugin manifest

Read `studio/changes/{name}/plugin.json.draft` and write the production manifest to `{target_dir}/.claude-plugin/plugin.json`:

- Remove the `.draft` suffix
- **Version handling**:
  - If `{target_dir}/.claude-plugin/plugin.json` already exists, read the existing `version` field
  - Bump the patch version (e.g., `0.1.0` → `0.1.1`, `0.2.3` → `0.2.4`)
  - If the user provides an explicit version in `$ARGUMENTS` (e.g., `promote my-plugin v0.2.0`), use that instead
  - If no existing manifest, use the version from `plugin.json.draft`
- Ensure `name`, `version`, `description` are present
- Set `skills` to `"./skills/"`
- Add `"commands": "./commands/"` if a commands/ directory exists in the target
- Add `"hooks": "./hooks/hooks.json"` if a hooks/ directory exists in the target
- Add `"mcpServers": "./.mcp.json"` if a .mcp.json file exists in the target

### Step 3: Snapshot design workspace to archive

Archive by plugin name so a plugin's design history stays grouped:

```
studio/archive/{name}/{YYYY-MM-DD}-iteration-{N}/
```

Where `{N}` is the `iteration` field from `status.json`.

If that directory already exists, append a numeric suffix:

```
studio/archive/{name}/{YYYY-MM-DD}-iteration-{N}-1/
studio/archive/{name}/{YYYY-MM-DD}-iteration-{N}-2/
```

This avoids collisions when a plugin is promoted multiple times on the same day or when a previous archive already exists for that iteration label.

**Copy** (not move) `studio/changes/{name}/` into the resolved archive path. The active workspace remains in place for continued iteration.

**Update the archived copy's `status.json`:**
- Set `phase` to `shipped`
- Add `shipped_at` timestamp
- Add `shipped_version` with the version from Step 2
- Add `shipped_to` path (the `target_dir` value)
- Add `archive_path` with the final archive directory path

**Update the active workspace's `studio/changes/{name}/status.json`:**
- Increment `iteration` by 1
- Reset `phase` to `planning`
- Add `last_shipped_at` timestamp
- Add `last_shipped_version` with the version from Step 2
- Keep all other fields intact (domain, target_dir, skills, etc.)

### Step 4: Report

Print:
- What was promoted: "Plugin `{name}` v{version} finalized at `{target_dir}/`"
- Manifest location: `{target_dir}/.claude-plugin/plugin.json`
- Archive snapshot: `studio/archive/{name}/{date}-iteration-{N}/`
- Active workspace: "Design docs remain active at `studio/changes/{name}/` for continued iteration (iteration {N+1})"
- Remind user to review and commit: "Review the finalized plugin, then commit when ready"

## Does NOT

- Copy implementation files — they already live in `{target_dir}/`
- Run `git add` or `git commit` — the user decides when to commit
- Delete implementation files — only design docs are snapshotted
- Run validation — that should have happened before approval
- Remove the active workspace — design docs stay in `studio/changes/` for the next iteration
- Treat promotion as a terminal state — plugins evolve continuously
