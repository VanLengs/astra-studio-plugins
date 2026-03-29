---
name: plugin-validator
description: Validate a completed plugin for structural correctness, manifest compliance, skill quality, and dependency integrity. Use when a plugin is ready for review, before packaging or promotion, after editing a plugin, or when you want a detailed diagnostic report with remediation steps. Works on any Claude Code plugin directory.
allowed-tools: Bash, Read, Write, Glob, Grep
user-invocable: true
---

# Plugin Validator

Run comprehensive validation on a plugin and produce an actionable report. Checks manifest schema, skill quality, cross-references, and dependency integrity.

## Workflow

1. **Identify plugin** — get the plugin directory path from the user
2. **Structural validation** — manifest and directory checks
3. **Skill validation** — SKILL.md quality checks
4. **Dependency checks** — MCP and inter-skill dependencies
5. **Present findings** — summarize pass/fail with remediation steps
6. **Update studio status** — if the plugin has a matching change workspace, update that workspace's status.json

## Step 1: Identify Plugin

Accept the plugin directory path via `$ARGUMENTS`. The path can be:
- A `{target_dir}/` directory (during development — the single source of truth for implementation)
- A root-level plugin directory such as `{name}/` (production)
- Any directory with `.claude-plugin/plugin.json`

If the user gives a skill directory, navigate up to find the plugin root.

## Step 2: Structural Validation

Run the structural validation script:

```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/validate_plugin.py <plugin-dir>
```

This checks: manifest exists and is valid JSON, required fields (name, version, description), kebab-case naming, semver version, and all declared paths (skills, commands, hooks, mcpServers) resolve.

## Step 3: Skill Validation

Run the skill validation script:

```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/validate_skills.py <plugin-dir>
```

This checks per skill: SKILL.md exists with valid YAML frontmatter, required fields (name, description), name matches directory, description under 1024 chars, warns on unknown frontmatter keys and files over 500 lines, and verifies referenced scripts/ and references/ files exist.

## Step 4: Dependency Checks

Run the dependency check script:

```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/check_dependencies.py <plugin-dir>
```

This checks: .mcp.json validity and server entries, hooks.json validity and recognized event names, and declared plugin dependencies.

## Step 5: Present Findings

Generate the combined report by running:

```bash
python ${CLAUDE_SKILL_DIR}/../../scripts/generate_report.py <plugin-dir>
```

The script also saves a JSON report to `.validation-report.json` in the plugin directory.

Summarize the report:

```
Plugin Validation: {plugin-name}
══════════════════════════════════

Structure:  ✅ 8/8 passed
Skills:     ⚠️ 3/4 passed (1 warning)
Dependencies: ✅ 2/2 passed

Warnings:
  - skills/data-loader/SKILL.md: 520 lines (recommend < 500)

Overall: PASS (with warnings)
```

Categories:
- **Error**: Must fix before shipping
- **Warning**: Advisory, worth addressing
- **Pass**: All good

## Step 6: Update Studio Status (optional)

If the plugin has a corresponding workspace in `studio/changes/` (look up by plugin name, regardless of where the implementation lives) and all checks pass:
- Ask the user if they want to update the workspace's `status.json`
- If yes:
  - update all in-scope built skills to `tested`
  - set the plugin `phase` to `approved`
  - update `updated_at`

When updating the workspace:
- Match by plugin name from the validated manifest or directory name
- Do not require the implementation directory itself to be under `studio/changes/`
- Preserve `target_dir`, `action`, `iteration`, and unrelated skill statuses
- Only promote skill statuses forward (`built` → `tested`); do not downgrade already tested skills

If checks fail, suggest specific remediation steps for each failure:

| Common failure | Remediation |
|---------------|-------------|
| Missing plugin.json | Create `.claude-plugin/plugin.json` with name, version, description |
| Name mismatch | Rename the directory or update the `name` field in plugin.json |
| Invalid semver | Use `X.Y.Z` format (e.g., `0.1.0`) |
| Missing SKILL.md | Create a SKILL.md with at least `name` and `description` in frontmatter |
| Broken script ref | Create the missing script file or remove the reference |
| Invalid .mcp.json | Run `/studio-quality:wire-mcp` to regenerate it |
