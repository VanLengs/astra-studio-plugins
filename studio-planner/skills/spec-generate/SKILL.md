---
name: spec-generate
description: Generate all plugin specification files from planning artifacts — SKILL.md skeletons, plugin.json.draft, brief.md, and commands. Use after skill-design when the skill map is ready and you want to produce the complete workspace that the build stage can consume. Pure automation, no interactive input needed.
allowed-tools: Read, Write, Glob, Grep
user-invocable: true
---

# Spec Generate

Automatically produce all specification files for a plugin based on the planning artifacts (event-storm.md, domain-map.md, skill-map.md). This is pure output — no brainstorming or analysis, just structured file generation.

## Design Principle: Spec vs Implementation Separation

`studio/changes/` is a **design workspace** — it holds proposals, specs, and rationale. It does NOT hold executable implementation files. All runnable artifacts (SKILL.md, commands, scripts, hooks) are written **directly to the target plugin directory** so there is always a single source of truth.

```
studio/changes/{plugin}/     ← design docs only
  status.json, brief.md, skill-map.md, plugin.json.draft

{target_dir}/                ← single source of truth for implementation
  skills/{skill}/SKILL.md, commands/, scripts/, hooks/
```

## Pre-check

1. Verify `studio/` exists.
2. Read `studio/changes/$ARGUMENTS/skill-map.md` — required. If missing, tell the user to run `/studio-planner:skill-design` first.
3. Read `studio/changes/$ARGUMENTS/status.json` to get the `domain`, `target_dir`, and `action` fields.
   - `target_dir` is the path where implementation files are written (e.g., `nutrition-planner`).
   - If `target_dir` is missing, derive it as `{plugin-name}` when `target_collection` is `.` or empty; otherwise derive it as `{target_collection}/{plugin-name}`.
   - `action` is `"create"` (default) or `"modify"`.
   - Read `studio/changes/{domain}/domain-map.md` — optional, used for brief and manifest context.
   - Read `studio/changes/{domain}/event-storm.md` — optional, used for brief context.
   - If no `domain` field or domain-level files don't exist, proceed without them.
4. Read `${CLAUDE_SKILL_DIR}/../../templates/brief.md.tmpl` — template for brief.md.
5. Read `${CLAUDE_SKILL_DIR}/../../templates/status.json.tmpl` — template for status.json.

## Workflow

1. **Ensure target directory** — create `{target_dir}/` if it doesn't exist
2. **Generate brief.md** — synthesize business context (→ `studio/changes/`)
3. **Generate plugin.json.draft** — create the plugin manifest (→ `studio/changes/`)
4. **Generate SKILL.md skeletons** — one per skill from the skill map (→ `{target_dir}/`)
5. **Generate commands** — create command files that invoke skills (→ `{target_dir}/`)
6. **Update status.json** — add all skills with status `draft`
7. **Report** — summarize what was generated

## Step 1: Ensure Target Directory

Create `{target_dir}/` and its subdirectories if they don't exist:

```
{target_dir}/
├── skills/
└── commands/
```

If the target directory already has files (e.g., from a previous run or manual work), **do not delete anything**. This step only creates missing directories.

## Step 2: Generate brief.md

Write to `studio/changes/{plugin-name}/brief.md` — this is a design document.

If `brief.md` doesn't exist yet, create it using the template. Fill in:

- **Business Context**: from event-storm.md's domain context and personas
- **Plugin Candidates**: from domain-map.md's plugin candidates section
- **Success Criteria**: derived from event-storm.md's hotspots — the plugin succeeds if it addresses the top hotspots
- **Notes**: any constraints, regulations, or special considerations from domain expert input

If `brief.md` already exists:
- For `action: "create"`: leave it unchanged
- For `action: "modify"`: preserve the existing content and append a short `## Iteration Update` section summarizing what changed in this iteration. Do not rewrite the whole file.

## Step 3: Generate plugin.json.draft

Write to `studio/changes/{plugin-name}/plugin.json.draft` — this is a manifest proposal, not the final manifest.

```json
{
  "name": "{plugin-name}",
  "version": "0.1.0",
  "description": "{from domain-map.md plugin candidate description}",
  "author": { "name": "{from studio/config.yaml or prompt}" },
  "license": "Apache-2.0",
  "keywords": ["{derived from domain and skill names}"],
  "dependencies": ["{from domain-map.md dependencies}"],
  "skills": "./skills/",
  "commands": "./commands/"
}
```

Rules:
- `name` must match the workspace directory name
- `description` must be one clear sentence
- `keywords` should be 3-5 searchable terms
- `dependencies` only list other plugins in the same collection

If `plugin.json.draft` already exists:
- For `action: "create"`: replace it with the newly generated draft
- For `action: "modify"`: refresh only the generated fields (`description`, `keywords`, `dependencies`, `updated_at` if present) and preserve user-maintained fields such as custom metadata or manually added keys

In `action: "modify"` mode, treat the draft as a proposal refresh for the next release, not as the source of truth for existing implementation files.

## Step 4: Generate SKILL.md Skeletons

For each skill in `skill-map.md`, create the skeleton **in the target plugin directory**:

```
{target_dir}/skills/{skill-name}/SKILL.md
```

This is the single source of truth — the build stage works directly on these files via `skill-creator`.

Skeleton content — designed for the build stage to flesh out via `skill-creator`:

```markdown
---
name: {skill-name}
description: {from skill-map.md — one line, specific, action-oriented}
allowed-tools: {from skill-map.md complexity assessment}
user-invocable: true
---

# {Skill Title}

{2-3 sentence summary: what it does, when to use it, what it produces.}

## Intent
- {What this skill enables the agent to do}
- {When this skill should trigger}

## Expected Inputs
- {Input 1: from skill-map.md interface definition}
- {Input 2}

## Expected Outputs
- {Output 1: from skill-map.md interface definition}
- {Output 2}

## Preconditions
- {From skill-map.md preconditions}

## Workflow
1. {High-level step 1}
2. {High-level step 2}
3. {High-level step 3}

## Out of Scope
- {From skill-map.md out-of-scope list}
```

If a SKILL.md already exists at that path, **do not overwrite** — the build stage may have already updated it in a previous run. Print a warning instead. This is especially important for `action: "modify"` where existing skills should be preserved.

In `action: "modify"` mode:
- Only generate skeletons for skills explicitly listed in `skill-map.md` as **new**
- For skills listed as **modified**, do not replace the existing `SKILL.md`; the subsequent build stage should update it in place via `skill-creator`
- Skills not listed in this iteration's `skill-map.md` are out of scope and must not be created, deleted, or rewritten

If the skill is classified as **Moderate** or above, also create the `scripts/` directory:

```
{target_dir}/skills/{skill-name}/scripts/.gitkeep
```

If the skill is classified as **MCP-dependent**, note it for later — `/studio-quality:wire-mcp` will handle the MCP config.

## Step 5: Generate Commands

For each user-invocable skill, create a command file **in the target plugin directory**:

```
{target_dir}/commands/{skill-name}.md
```

Command content:

```markdown
---
description: {same as skill description}
argument-hint: [{relevant hint}]
---

{One sentence about what this command does with `$ARGUMENTS`.}

Use skill: "{skill-name}"
```

Only create commands for skills marked `user-invocable: true`. Internal/helper skills don't need commands.

If a command file already exists at that path:
- For `action: "create"`: replace it with the generated command if it still appears to be a scaffold
- For `action: "modify"`: do not overwrite it; print a warning instead

In `action: "modify"` mode, only create commands for newly added user-invocable skills.

## Step 6: Update status.json

Update `studio/changes/{plugin-name}/status.json`:

```json
{
  "plugin": "{plugin-name}",
  "domain": "{domain-slug}",
  "target_collection": "{from domain-map.md or config.yaml default}",
  "target_dir": "{plugin-name}",
  "phase": "building",
  "created_at": "{original timestamp}",
  "updated_at": "{now ISO-8601}",
  "skills": {
    "skill-a": "draft",
    "skill-b": "draft",
    "skill-c": "draft"
  }
}
```

For `action: "modify"`, only add or reset statuses for the skills that need work in this iteration. Leave unrelated skill statuses untouched.

Note: phase advances from `planning` to `building` because the specs are now ready for implementation.

## Step 7: Report

Print a summary showing the separation clearly:

```
Spec generation complete for {plugin-name}

Design docs (studio/changes/{plugin-name}/):
  brief.md              — business context and success criteria
  plugin.json.draft     — plugin manifest proposal
  status.json           — updated: planning → building

Implementation ({target_dir}/):
  skills/
    {skill-a}/SKILL.md  — skeleton (Simple)
    {skill-b}/SKILL.md  — skeleton (Moderate, scripts/ created)
    {skill-c}/SKILL.md  — skeleton (MCP-dependent, needs wire-mcp)
  commands/
    {skill-a}.md
    {skill-b}.md

Warnings:
  - Existing SKILL.md files were preserved and not overwritten
  - Existing commands were preserved in modify mode

Next steps:
  Confirm the build stage so Astra Studio can invoke skill-creator in {target_dir}/
  Run /studio-quality:wire-mcp {target_dir} if MCP servers are needed
  Run /studio-quality:validate {target_dir} when all skills are ready
```

If this is part of a multi-plugin collection, remind the user to run spec-generate for each plugin.
