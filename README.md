# Astra Studio

A **Claude Code plugin marketplace** for planning, designing, validating, and shipping plugins.

Astra Studio handles the **outer loop** of plugin development — business analysis, domain modeling, plugin validation, and promotion. Individual skill authoring and testing is executed through the official [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) as an internal pipeline capability.

## Plugins

| Plugin | Skills | What it does | Install |
|--------|--------|-------------|---------|
| **studio-core** | 4 | Workspace management — init, promote, status, create-expert | `claude plugin install studio-core@astra-studio` |
| **studio-insight** | 6 | Business analysis toolkit — personas, journeys, processes, domains | `claude plugin install studio-insight@astra-studio` |
| **studio-planner** | 5 | Planning pipeline — event storming, domain modeling, skill design, build orchestration | `claude plugin install studio-planner@astra-studio` |
| **studio-quality** | 2 | Quality assurance — plugin validation, MCP wiring | `claude plugin install studio-quality@astra-studio` |

## Quick Start

```bash
# 1. Register the marketplace
claude plugin marketplace add github:VanLengs/astra-studio-plugins

# 2. Install what you need
claude plugin install studio-core@astra-studio
claude plugin install studio-insight@astra-studio
claude plugin install studio-planner@astra-studio
claude plugin install studio-quality@astra-studio

# 3. Initialize studio in your project
/studio-core:init

# 4. Plan a plugin
/studio-planner:plan "your business domain"

# 5. Confirm the build plan
# → Astra Studio generates specs, then automatically invokes skill-creator in {target_dir}/

# 6. Validate the plugin
/studio-quality:validate {target_dir}

# 7. Ship it
/studio-core:promote {plugin-name}
```

## studio-insight: Standalone Artifact Skills

These 6 skills produce professional deliverables independently — no pipeline required:

```bash
/studio-insight:persona-insight "全职妈妈，两个孩子"    # → persona card + empathy map
/studio-insight:journey-map "日常营养管理流程"           # → journey map + emotional curve
/studio-insight:process-flow "从记录饮食到生成周报"      # → process diagram + decision points
/studio-insight:domain-canvas "儿童健康管理"             # → domain boundary map + classification
/studio-insight:behavior-matrix "儿童健康管理"           # → actor × action × event × data table
/studio-insight:opportunity-brief "儿童健康管理"         # → prioritized opportunity assessment
```

## studio-planner: Planning Pipeline

`/studio-planner:plan` chains 5 pipeline skills, each invoking insight artifact skills:

```
Step 1: event-storm
  Multi-role brainstorming (PM, architect, domain experts)
  → Invokes: persona-insight, journey-map, process-flow
  → Writes: studio/changes/{domain}/event-storm.md

        ↓ user confirms

Step 2: domain-model
  Clusters events into business domains, draws plugin boundaries
  → Invokes: domain-canvas, behavior-matrix, opportunity-brief
  → Writes: studio/changes/{domain}/domain-map.md
  → Creates: {target_dir}/ scaffold for each plugin candidate

        ↓ user confirms

Step 3: skill-design
  Breaks each plugin into skills with interfaces and data flow
  → Assesses complexity: prompt-only / scripts / MCP
  → Writes: studio/changes/{plugin}/skill-map.md

        ↓ user confirms

Step 4: spec-generate
  Auto-generates all specification files
  → Design docs → studio/changes/ (brief.md, plugin.json.draft)
  → Implementation → {target_dir}/ (SKILL.md skeletons, commands)
  → Advances status: planning → building

Step 5+: build, validate, promote
  build-skills automatically invokes skill-creator to edit the implementation in {target_dir}/
  build-skills advances skill states from draft/building to built
  /studio-quality:validate validates {target_dir}/ and updates the matching workspace
  /studio-quality:validate advances built skills to tested and the plugin to approved
  /studio-core:promote finalizes the manifest and archives only the design workspace
```

### Subagent Roles

Both studio-insight and studio-planner use multiple perspectives via subagent roles:

| Role | Perspective | Used by |
|------|------------|---------|
| **Product Manager** | User personas, journey mapping, prioritization | persona-insight, journey-map, opportunity-brief, event-storm |
| **Architect** | System boundaries, dependencies, feasibility | process-flow, domain-canvas, behavior-matrix, domain-model |
| **Domain Expert** | Domain-specific knowledge, real-world constraints | All 6 insight skills (dynamically discovered) |

11 built-in domain experts ship with studio-insight — general roles (UX researcher, data analyst, compliance officer, operations manager) plus health and beauty domain experts.

### Customizing Experts

```bash
# Create a new domain expert
/studio-core:create-expert 宠物营养专家

# Customize a built-in expert with your company's terminology
/studio-core:create-expert customize product-manager
```

Custom experts are saved to `studio/agents/` (git-tracked, team-shared) and automatically discovered by all insight skills at runtime. Project-level experts override built-ins with the same filename.

## Full Workflow

```
/studio-core:init                       /studio-planner:plan
        ↓                                       ↓
    studio/                             event-storm
    ├── config.yaml                       ├── persona-insight  → personas/
    ├── changes/                          ├── journey-map      → journeys/
    └── archive/                          └── process-flow     → processes/
                                                ↓
                                        domain-model
                                          ├── domain-canvas    → domain-canvas.md
                                          ├── behavior-matrix  → behavior-matrix.md
                                          └── opportunity-brief→ opportunity-brief.md
                                                ↓
                                        skill-design → skill-map.md
                                                ↓
                                        spec-generate
                                                ↓
                                studio/changes/{plugin}/    {target_dir}/
                                ├── brief.md                skills/{skill}/SKILL.md
                                └── plugin.json.draft       commands/{skill}.md
                                                ↓
                              build-skills
                                                ↓
                              /studio-quality:validate
                                                ↓
                              /studio-core:promote
                                                ↓
          studio/archive/{plugin}/{date}-iteration-{N}/   {target_dir}/
```

## Architecture

Astra Studio is a **marketplace** (collection of plugins), not a monolithic plugin. Each plugin is independently installable:

- **studio-core**: Zero dependencies. Manages the `studio/` workspace.
- **studio-insight**: Zero dependencies. Standalone business analysis tools. Useful beyond plugin development.
- **studio-planner**: Depends on studio-core and studio-insight. Orchestrates the planning pipeline.
- **studio-quality**: Zero dependencies. Can validate any plugin, not just studio-managed ones.

The `studio/` directory is **git-tracked** — it holds development documentation (briefs, design decisions, status) with version control value. Inspired by [OpenSpec](https://github.com/Fission-AI/OpenSpec)'s spec-driven workspace pattern.

Domains evolve **incrementally** — re-running the pipeline updates artifacts in-place (git diff = revision history), `changelog.md` logs each iteration, and only affected plugins (`create`/`modify`) get change workspaces.

Shipped plugins keep their implementation in `{target_dir}/` and move only the design workspace to `studio/archive/{plugin}/{date}-iteration-{N}/` so active work stays clean while design history remains traceable.

## Development

```bash
# Test locally
claude --plugin-dir ./studio-core --plugin-dir ./studio-insight --plugin-dir ./studio-planner --plugin-dir ./studio-quality
```

## License

Apache-2.0
