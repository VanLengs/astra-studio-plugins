---
name: build-skills
description: Build or update plugin skills in the target plugin directory after spec generation. Use when the user has confirmed the build stage and Astra Studio should automatically invoke skill-creator for new or modified skills. Works for both create and modify iterations.
allowed-tools: Read, Write, Glob, Grep, Agent
user-invocable: true
---

# Build Skills

Build the implementation for a plugin after `spec-generate` has produced the design artifacts and initial skeletons.

This stage is responsible for automatic skill construction. Users confirm entry into this stage, but they do not manually run `skill-creator` themselves.

## Purpose

Take a plugin workspace in `studio/changes/{plugin}/` plus the implementation files in `{target_dir}/`, determine which skills need work in this iteration, and use `skill-creator` as an internal build capability to update them in place.

## Pre-check

1. Verify `studio/` exists.
2. Read `studio/changes/$ARGUMENTS/status.json` — required.
3. Verify `phase` is `building`. If not:
   - `planning` → tell the user to complete `spec-generate` first
   - `approved` → tell the user the plugin is already built and validated
   - `shipped` → tell the user the active change workspace has already been promoted
4. Read `target_dir`, `action`, and `skills` from `status.json`.
5. Read `studio/changes/$ARGUMENTS/skill-map.md` — required.
6. Verify `{target_dir}/skills/` exists.

## Build Model

This stage follows these rules:

- Users confirm the build stage; the system executes it
- `target_dir` is the single source of truth for implementation
- Existing `SKILL.md` files are updated in place when needed
- Unchanged skills are not touched

## Execution Rules

### For `action: "create"`

- Every skill listed in `status.json.skills` is in scope
- Each skill in `{target_dir}/skills/{name}/SKILL.md` should be built
- Use `skill-creator` to flesh out each skeleton

### For `action: "modify"`

- Only skills listed in `status.json.skills` are in scope
- New skills should be built from the generated skeletons
- Existing skills should be updated in place
- Skills not listed in this iteration must not be rewritten

## Per-skill Workflow

For each in-scope skill:

1. Set the skill status to `building`
2. Read the current `SKILL.md`
3. Read the relevant section from `skill-map.md`
4. If this is a modified skill, also read the current implementation context from the existing `SKILL.md`
5. Invoke `skill-creator` as an internal build capability to:
   - flesh out new skeletons, or
   - revise existing skills in place for this iteration
6. If the build succeeds, set the skill status to `built`
7. If the build fails, leave the skill status as `draft` or set it to `building-failed` if the workspace schema supports it

## Status Updates

Update `studio/changes/{plugin}/status.json` as the build progresses.

Recommended progression:

- `draft` → spec exists but build not started
- `building` → currently being processed
- `built` → implementation updated successfully
- `tested` → validation passed later

Keep the plugin `phase` as `building` during this stage.

## Completion Rule

If all in-scope skills were built successfully:

- Keep plugin `phase` as `building`
- Tell the user the build stage is complete
- Suggest proceeding directly to `/studio-quality:validate {target_dir}`

If any in-scope skill fails:

- Keep plugin `phase` as `building`
- Report which skills succeeded and which failed
- Do not advance to validation automatically

## Report

Print a summary like:

```text
Build stage complete for {plugin-name}

Target: {target_dir}/
Action: {create|modify}

Built:
  - {skill-a}
  - {skill-b}

Updated in place:
  - {existing-skill-c}

Skipped:
  - {unchanged-skill-d}

Next step:
  Run /studio-quality:validate {target_dir}
```
