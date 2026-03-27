---
name: spec-generate
description: Generate all plugin specification files from planning artifacts — SKILL.md skeletons, plugin.json.draft, brief.md, and commands. Use after skill-design when the skill map is ready and you want to produce the complete workspace that skill-creator can consume. Pure automation, no interactive input needed.
allowed-tools: Read, Write, Glob, Grep
user-invocable: true
---

# Spec Generate

Automatically produce all specification files for a plugin based on the planning artifacts (event-storm.md, domain-map.md, skill-map.md). This is pure output — no brainstorming or analysis, just structured file generation.

## Pre-check

1. Verify `studio/` exists.
2. Read `studio/changes/$ARGUMENTS/skill-map.md` — required. If missing, tell the user to run `/studio-planner:skill-design` first.
3. Read `studio/changes/$ARGUMENTS/status.json` to get the `domain` field. Use it to locate domain-level artifacts:
   - Read `studio/changes/{domain}/domain-map.md` — optional, used for brief and manifest context.
   - Read `studio/changes/{domain}/event-storm.md` — optional, used for brief context.
   - If no `domain` field or domain-level files don't exist, proceed without them.
4. Read `${CLAUDE_SKILL_DIR}/../../templates/brief.md.tmpl` — template for brief.md.
5. Read `${CLAUDE_SKILL_DIR}/../../templates/status.json.tmpl` — template for status.json.

## Workflow

1. **Generate brief.md** — synthesize business context from planning artifacts
2. **Generate plugin.json.draft** — create the plugin manifest
3. **Generate SKILL.md skeletons** — one per skill from the skill map
4. **Generate commands** — create command files that invoke skills
5. **Update status.json** — add all skills with status `draft`
6. **Report** — summarize what was generated

## Step 1: Generate brief.md

If `brief.md` doesn't exist yet, create it using the template. Fill in:

- **Business Context**: from event-storm.md's domain context and personas
- **Plugin Candidates**: from domain-map.md's plugin candidates section
- **Success Criteria**: derived from event-storm.md's hotspots — the plugin succeeds if it addresses the top hotspots
- **Notes**: any constraints, regulations, or special considerations from domain expert input

If `brief.md` already exists (e.g., from a manual process), leave it unchanged.

## Step 2: Generate plugin.json.draft

Create `studio/changes/{plugin-name}/plugin.json.draft`:

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

## Step 3: Generate SKILL.md Skeletons

For each skill in `skill-map.md`, create:

```
studio/changes/{plugin-name}/skills/{skill-name}/SKILL.md
```

Skeleton content — designed for the official `/skill-creator` to flesh out:

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

If a SKILL.md already exists at that path, **do not overwrite** — the user or skill-creator may have already started working on it. Print a warning instead.

If the skill is classified as **Moderate** or above, also create the `scripts/` directory:

```
studio/changes/{plugin-name}/skills/{skill-name}/scripts/.gitkeep
```

If the skill is classified as **MCP-dependent**, note it for later — `/studio-quality:wire-mcp` will handle the MCP config.

## Step 4: Generate Commands

For each user-invocable skill, create a command file:

```
studio/changes/{plugin-name}/commands/{skill-name}.md
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

## Step 5: Update status.json

Update `studio/changes/{plugin-name}/status.json`:

```json
{
  "plugin": "{plugin-name}",
  "target_collection": "{from domain-map.md or config.yaml default}",
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

Note: phase advances from `planning` to `building` because the specs are now ready for implementation.

## Step 6: Report

Print a summary:

```
Spec generation complete for {plugin-name}

Generated:
  brief.md              — business context and success criteria
  plugin.json.draft     — plugin manifest
  skills/
    {skill-a}/SKILL.md  — skeleton (Simple)
    {skill-b}/SKILL.md  — skeleton (Moderate, scripts/ created)
    {skill-c}/SKILL.md  — skeleton (MCP-dependent, needs wire-mcp)
  commands/
    {skill-a}.md
    {skill-b}.md

Status: planning → building

Next steps:
  Use /skill-creator to flesh out each skill skeleton
  Run /studio-quality:wire-mcp {plugin-name} if MCP servers are needed
  Run /studio-quality:validate {plugin-name} when all skills are ready
```

If this is part of a multi-plugin collection, remind the user to run spec-generate for each plugin.
