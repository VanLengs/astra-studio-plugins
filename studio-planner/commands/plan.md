---
description: Plan a new plugin — brainstorm, model domains, design skills, generate specs, build initial drafts
argument-hint: [business domain or plugin idea]
---

Plan a complete plugin from scratch by chaining five pipeline skills, which in turn invoke artifact skills to produce standalone deliverables:

1. **event-storm** — Multi-role brainstorming for `$ARGUMENTS`.
   - Invokes: `studio-insight:persona-insight` → persona cards
   - Invokes: `studio-insight:journey-map` → user journey maps
   - Invokes: `studio-insight:process-flow` → business process diagrams
   - Also produces: event list, hotspot ranking, knowledge base dependencies, expert scope analysis

2. **domain-model** — Analyze event storm output to identify plugin boundaries.
   - Offers two modes: **full analysis** (default) or **fast mode** (skip insight tools)
   - Full analysis invokes: `studio-insight:domain-canvas`, `studio-insight:behavior-matrix`, `studio-insight:opportunity-brief`
   - Fast mode goes directly from event clustering to plugin proposals
   - Also produces: plugin candidates with pipeline identification, collection structure

3. **skill-design** — Break each plugin into individual skills with data flow and complexity assessment.
   - Detects **plugin traits**: stateful, hil-gated, kb-dependent, multi-pipeline, expert-scoped
   - Traits drive conditional scaffolding in the next step

4. **spec-generate** — Generate specification files based on skill map and detected traits.
   - Always: brief.md, plugin.json.draft, SKILL.md skeletons, commands
   - If stateful: runtime workspace init skill + config/status templates
   - If hil-gated: approval gate sections in relevant SKILL.md skeletons
   - If multi-pipeline: per-pipeline orchestration commands

5. **build-skills** — Generate initial skill implementations as working first drafts.
   - These are starting points, not finished products — test with real inputs and iterate with skill-creator

Before starting, verify `studio/` exists. If not, run the init skill first.

After each pipeline step, pause and present results to the user for validation before proceeding. The user may also invoke any artifact skill independently at any time (e.g., `/studio-insight:journey-map` for a standalone journey map).

After initial drafts are generated, suggest: "Test each skill with 2-3 real scenarios, iterate with skill-creator, then run `/studio-quality:validate {target_dir}` when ready."
