---
description: Plan a new plugin — brainstorm, model domains, design skills, generate specs
argument-hint: [business domain or plugin idea]
---

Plan a complete plugin from scratch by chaining four pipeline skills, which in turn invoke six artifact skills to produce standalone deliverables:

1. **event-storm** — Multi-role brainstorming for `$ARGUMENTS`.
   - Invokes: `studio-insight:persona-insight` → persona cards
   - Invokes: `studio-insight:journey-map` → user journey maps
   - Invokes: `studio-insight:process-flow` → business process diagrams
   - Also produces: event list, hotspot ranking

2. **domain-model** — Analyze event storm output to identify plugin boundaries.
   - Invokes: `studio-insight:domain-canvas` → domain boundary map
   - Invokes: `studio-insight:behavior-matrix` → actor/action/event cross-reference
   - Invokes: `studio-insight:opportunity-brief` → prioritized opportunity assessment
   - Also produces: plugin candidates, collection structure

3. **skill-design** — Break each plugin into individual skills with data flow and complexity assessment.

4. **spec-generate** — Generate all specification files: brief.md, plugin.json.draft, SKILL.md skeletons, commands.

Before starting, verify `studio/` exists. If not, run the init skill first.

After each pipeline step, pause and present results to the user for validation before proceeding. The user may also invoke any artifact skill independently at any time (e.g., `/studio-insight:journey-map` for a standalone journey map).

After planning is complete, suggest: "Use `/skill-creator` to flesh out each skill skeleton with full instructions, scripts, and evals."
