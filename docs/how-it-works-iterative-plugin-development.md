# How It Works: Iterative Plugin Development

This document walks through a detailed, end-to-end simulation of iterative plugin development with Astra Studio.

It uses a realistic domain inspired by `course-workshop-plugins` and shows how the workspace evolves from `init` through planning, building, validation, promotion, and a second iteration of change.

## Scope

This document focuses on:

- How `studio/changes/` evolves across phases
- How domain workspaces and plugin workspaces differ
- How `target_dir` acts as the single source of truth for implementation
- How shipped design history moves into `studio/archive/`
- How iterative `create` and `modify` flows differ

This document also uses the clarified interaction model:

- Users confirm at major workflow boundaries
- The system executes the internal steps automatically
- Built-in capabilities such as `skill-creator` are treated as internal execution steps, not user-run commands

## Core Model

### Design vs implementation

`studio/changes/` is the active design workspace.

It contains:

- domain artifacts such as `event-storm.md`, `domain-map.md`, `changelog.md`
- plugin design artifacts such as `skill-map.md`, `brief.md`, `plugin.json.draft`, `status.json`

It does not contain runnable implementation files.

Implementation lives directly in each plugin's `target_dir` and is the single source of truth:

- `skills/*/SKILL.md`
- `commands/*.md`
- `scripts/`
- `hooks/`
- `.mcp.json`

### Confirmation vs execution

The workflow has confirmation gates, but the system executes the steps.

Examples:

- The user confirms event storm results before moving to domain modeling
- The user confirms plugin boundaries before skill design
- The user confirms the skill breakdown before build starts

After confirmation, the system continues automatically:

- generate specs
- run `build-skills`
- invoke `skill-creator`
- validate the plugin
- promote approved changes

The user should not need to manually run internal skills as a normal part of the pipeline.

## Example Domain

We simulate a course workshop domain with these plugins:

- `workshop-core`
- `workshop-designer`
- `workshop-insight`
- `workshop-quality`
- `workshop-resource`

In iteration 2, a new plugin is added:

- `workshop-feedback`

For this simulation, plugin implementation lives directly at the project root, so example `target_dir` values look like:

- `workshop-core`
- `workshop-designer`
- `workshop-insight`
- `workshop-quality`
- `workshop-resource`
- `workshop-feedback`

## Scenario 0: `/studio-core:init`

The user initializes studio in the project.

### Workspace snapshot

```text
studio/
├── config.yaml
├── changes/
│   └── .gitkeep
├── agents/
│   └── .gitkeep
└── archive/
    └── .gitkeep
```

### Notes

- `changes/` is empty
- `archive/` is empty
- no plugin workspaces exist yet

## Scenario 1: `/studio-planner:plan "course-workshop"` - event-storm phase

The system creates a domain workspace and produces domain discovery artifacts.

### Workspace snapshot

```text
studio/
├── config.yaml
├── agents/
│   ├── .gitkeep
│   ├── child-development-psychologist.md
│   ├── early-childhood-curriculum-expert.md
│   └── instructional-designer.md
├── changes/
│   ├── .gitkeep
│   └── course-workshop/
│       ├── event-storm.md
│       ├── changelog.md
│       ├── status.json
│       ├── personas/
│       │   ├── curriculum-director.md
│       │   ├── classroom-teacher.md
│       │   └── principal.md
│       ├── journeys/
│       │   └── curriculum-director-monthly-proposal.md
│       └── processes/
│           ├── activity-design.md
│           └── monthly-proposal-creation.md
└── archive/
    └── .gitkeep
```

### `status.json`

```json
{
  "type": "domain",
  "domain": "course-workshop",
  "iteration": 1,
  "phase": "planning",
  "created_at": "2026-03-28T21:00:00+08:00",
  "updated_at": "2026-03-28T21:00:00+08:00",
  "plugins": []
}
```

### What happened

- The system discovered events, personas, journeys, and processes
- The system wrote `event-storm.md`
- The system created `changelog.md`
- The domain workspace was initialized as iteration 1

### Confirmation gate

The user confirms:

- the domain framing
- the roles involved
- the hotspot ranking

After confirmation, the system proceeds to domain modeling.

## Scenario 2: domain-model phase

The system clusters the domain into plugin candidates and creates plugin change workspaces.

Detected plugin candidates:

- `workshop-core`
- `workshop-designer`
- `workshop-insight`
- `workshop-quality`
- `workshop-resource`

### Workspace snapshot

```text
studio/
├── config.yaml
├── agents/
│   └── ...
├── changes/
│   ├── .gitkeep
│   ├── course-workshop/
│   │   ├── event-storm.md
│   │   ├── changelog.md
│   │   ├── status.json
│   │   ├── domain-map.md
│   │   ├── domain-canvas.md
│   │   ├── behavior-matrix.md
│   │   ├── opportunity-brief.md
│   │   ├── personas/
│   │   │   └── ...
│   │   ├── journeys/
│   │   │   └── ...
│   │   └── processes/
│   │       └── ...
│   ├── workshop-core/
│   │   └── status.json
│   ├── workshop-designer/
│   │   └── status.json
│   ├── workshop-insight/
│   │   └── status.json
│   ├── workshop-quality/
│   │   └── status.json
│   └── workshop-resource/
│       └── status.json
└── archive/
    └── .gitkeep

workshop-core/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep

workshop-designer/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep

workshop-insight/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep

workshop-quality/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep

workshop-resource/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep
```

### Example plugin workspace status

`studio/changes/workshop-designer/status.json`

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "planning",
  "created_at": "2026-03-28T21:30:00+08:00",
  "skills": {}
}
```

### Example domain status

```json
{
  "type": "domain",
  "domain": "course-workshop",
  "iteration": 1,
  "phase": "planning",
  "created_at": "2026-03-28T21:00:00+08:00",
  "updated_at": "2026-03-28T21:30:00+08:00",
  "plugins": [
    "workshop-core",
    "workshop-designer",
    "workshop-insight",
    "workshop-quality",
    "workshop-resource"
  ]
}
```

### What happened

- The system wrote domain analysis artifacts
- The system created one plugin workspace per plugin candidate
- Each plugin workspace started with `action: "create"`
- Each plugin got an empty implementation scaffold in its `target_dir`

### Confirmation gate

The user confirms:

- plugin boundaries
- plugin responsibilities
- collection structure

After confirmation, the system proceeds to skill design.

## Scenario 3: skill-design phase

The system designs skills for each plugin and records them in `skill-map.md`.

### Workspace snapshot

```text
studio/
├── ...
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-core/
│   │   ├── status.json
│   │   └── skill-map.md
│   ├── workshop-designer/
│   │   ├── status.json
│   │   └── skill-map.md
│   ├── workshop-insight/
│   │   ├── status.json
│   │   └── skill-map.md
│   ├── workshop-quality/
│   │   ├── status.json
│   │   └── skill-map.md
│   └── workshop-resource/
│       ├── status.json
│       └── skill-map.md
└── ...
```

### Example plugin status after skill design

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "planning",
  "created_at": "2026-03-28T21:30:00+08:00",
  "skills": {
    "driving-question": "draft",
    "network-map": "draft",
    "inquiry-scaffold": "draft",
    "activity-design": "draft",
    "proposal-generate": "draft"
  }
}
```

### What happened

- The system derived a skill breakdown for each plugin
- The system recorded the design in `skill-map.md`
- The status file now tracks which skills belong to this iteration

### Confirmation gate

The user confirms:

- skill boundaries
- data flow
- complexity assumptions

After confirmation, the system proceeds to build generation.

## Scenario 4: spec-generate phase

This is where the design and implementation tracks separate.

`spec-generate` writes design outputs into `studio/changes/`, and writes implementation skeletons into `target_dir`.

### Workspace snapshot after spec generation

```text
studio/
├── ...
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-core/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   ├── workshop-designer/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   ├── workshop-insight/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   ├── workshop-quality/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   └── workshop-resource/
│       ├── status.json
│       ├── skill-map.md
│       ├── brief.md
│       └── plugin.json.draft
└── archive/
    └── .gitkeep
```

### Example implementation snapshot

```text
workshop-designer/
├── skills/
│   ├── driving-question/
│   │   └── SKILL.md
│   ├── network-map/
│   │   └── SKILL.md
│   ├── inquiry-scaffold/
│   │   └── SKILL.md
│   ├── activity-design/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── .gitkeep
│   └── proposal-generate/
│       ├── SKILL.md
│       └── scripts/
│           └── .gitkeep
└── commands/
    ├── driving-question.md
    ├── network-map.md
    ├── inquiry-scaffold.md
    ├── activity-design.md
    └── proposal-generate.md
```

### Example plugin status

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "building",
  "created_at": "2026-03-28T21:30:00+08:00",
  "updated_at": "2026-03-28T22:00:00+08:00",
  "skills": {
    "driving-question": "draft",
    "network-map": "draft",
    "inquiry-scaffold": "draft",
    "activity-design": "draft",
    "proposal-generate": "draft"
  }
}
```

### What happened

- `brief.md` and `plugin.json.draft` were written to the plugin change workspace
- skill skeletons were written directly into `target_dir`
- command files were written directly into `target_dir`

### Important rule

The user confirms entry into the build stage, but does not manually run `skill-creator`.

That is a system step handled by the next pipeline stage.

## Scenario 5: build-skills phase

After the user confirms the build stage, Astra Studio runs `build-skills`.

`build-skills` reads the plugin workspace in `studio/changes/{plugin}/`, determines which skills are in scope for this iteration, and automatically invokes `skill-creator` against the implementation in `target_dir`.

### Workspace snapshot

```text
studio/
├── ...
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-designer/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   └── ...
└── archive/
    └── .gitkeep

workshop-designer/
├── skills/
│   ├── driving-question/
│   │   └── SKILL.md
│   ├── network-map/
│   │   └── SKILL.md
│   ├── inquiry-scaffold/
│   │   └── SKILL.md
│   ├── activity-design/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── .gitkeep
│   └── proposal-generate/
│       ├── SKILL.md
│       └── scripts/
│           └── .gitkeep
└── commands/
    └── ...
```

### Example status during build

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "building",
  "created_at": "2026-03-28T21:30:00+08:00",
  "updated_at": "2026-03-28T22:20:00+08:00",
  "skills": {
    "driving-question": "built",
    "network-map": "built",
    "inquiry-scaffold": "built",
    "activity-design": "built",
    "proposal-generate": "built"
  }
}
```

### What happened

- Astra Studio ran `build-skills`
- `build-skills` invoked `skill-creator` internally
- the implementation in `target_dir` was fleshed out in place
- the plugin remained in `phase: "building"`
- per-skill states advanced from `draft` to `built`

## Scenario 6: validate passed

The system has already completed `build-skills` and used `skill-creator` to fill in implementation detail in `target_dir`.

Then the system validates the plugin by running validation against `target_dir`, and updates the matching change workspace.

### Workspace snapshot

```text
studio/
├── ...
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-designer/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   └── ...
└── archive/
    └── .gitkeep

workshop-designer/
├── skills/
│   ├── driving-question/
│   │   └── SKILL.md
│   ├── network-map/
│   │   └── SKILL.md
│   ├── inquiry-scaffold/
│   │   └── SKILL.md
│   ├── activity-design/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── .gitkeep
│   └── proposal-generate/
│       ├── SKILL.md
│       └── scripts/
│           └── .gitkeep
└── commands/
    └── ...
```

### Example status after validation

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "approved",
  "created_at": "2026-03-28T21:30:00+08:00",
  "updated_at": "2026-03-28T23:00:00+08:00",
  "skills": {
    "driving-question": "tested",
    "network-map": "tested",
    "inquiry-scaffold": "tested",
    "activity-design": "tested",
    "proposal-generate": "tested"
  }
}
```

### What happened

- Validation ran against `target_dir`
- The system looked up the matching change workspace by plugin name
- The system updated the workspace phase to `approved`

### Confirmation gate

The user confirms:

- ship now
- or hold for more edits

If confirmed, the system promotes the plugin.

## Scenario 7: promote

Promotion finalizes the manifest and archives only the design workspace.

Implementation remains where it already lives.

### Workspace snapshot after promoting `workshop-designer`

```text
studio/
├── ...
├── changes/
│   ├── .gitkeep
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-core/
│   │   └── ...
│   ├── workshop-insight/
│   │   └── ...
│   ├── workshop-quality/
│   │   └── ...
│   └── workshop-resource/
│       └── ...
└── archive/
    ├── .gitkeep
    └── workshop-designer/
        └── 2026-03-28-iteration-1/
            ├── skill-map.md
            ├── brief.md
            ├── plugin.json.draft
            └── status.json

workshop-designer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── ...
└── commands/
    └── ...
```

### Example archived status

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "create",
  "iteration": 1,
  "phase": "shipped",
  "created_at": "2026-03-28T21:30:00+08:00",
  "updated_at": "2026-03-28T23:10:00+08:00",
  "shipped_at": "2026-03-28T23:10:00+08:00",
  "shipped_to": "workshop-designer",
  "archive_path": "studio/archive/workshop-designer/2026-03-28-iteration-1",
  "skills": {
    "driving-question": "tested",
    "network-map": "tested",
    "inquiry-scaffold": "tested",
    "activity-design": "tested",
    "proposal-generate": "tested"
  }
}
```

### What happened

- The production manifest was finalized in `target_dir`
- The design workspace was moved from `studio/changes/` to `studio/archive/`
- Implementation files were not copied
- `changes/` became clean again for active work

The same process happens for the other plugins in iteration 1.

At the end of iteration 1, `changes/` contains only the domain workspace.

## Scenario 8: iteration 2 starts

A new request arrives:

- add a home-school feedback scenario
- revise proposal generation to include a principal approval summary

The user runs `/studio-planner:plan course-workshop`.

### 8a. event-storm incremental mode

The domain workspace already exists, so the system enters incremental mode and updates the domain artifacts in place.

### Workspace snapshot

```text
studio/
├── changes/
│   ├── .gitkeep
│   └── course-workshop/
│       ├── event-storm.md
│       ├── changelog.md
│       ├── status.json
│       ├── domain-map.md
│       ├── domain-canvas.md
│       ├── behavior-matrix.md
│       ├── opportunity-brief.md
│       ├── personas/
│       │   ├── curriculum-director.md
│       │   ├── classroom-teacher.md
│       │   ├── principal.md
│       │   └── parent.md
│       ├── journeys/
│       │   ├── curriculum-director-monthly-proposal.md
│       │   └── parent-feedback-cycle.md
│       └── processes/
│           ├── activity-design.md
│           ├── monthly-proposal-creation.md
│           └── home-school-feedback.md
└── archive/
    └── ...
```

### Example domain status

```json
{
  "type": "domain",
  "domain": "course-workshop",
  "iteration": 2,
  "phase": "planning",
  "created_at": "2026-03-28T21:00:00+08:00",
  "updated_at": "2026-04-10T09:30:00+08:00",
  "plugins": [
    "workshop-core",
    "workshop-designer",
    "workshop-insight",
    "workshop-quality",
    "workshop-resource"
  ]
}
```

### Example changelog entry

```markdown
## 2026-04-10

**Summary**: Added a home-school feedback scenario and revised proposal generation to include a principal approval summary.

### Added
- Persona: parent
- Journey: parent-feedback-cycle
- Process: home-school-feedback

### Revised
- Process: monthly-proposal-creation — added principal approval summary output

### Impact on Plugins
- `workshop-designer`: needs modification — proposal output changed
- `workshop-quality`: needs modification — review checklist changed
- `workshop-feedback`: new plugin needed — home-school feedback scenario
- `workshop-core`: no change
- `workshop-insight`: no change
- `workshop-resource`: no change
```

### Confirmation gate

The user confirms the delta:

- what changed
- which personas/journeys/processes were added
- which plugins are impacted

After confirmation, the system proceeds to incremental domain modeling.

## Scenario 8b: domain-model incremental mode

The system creates change workspaces only for impacted plugins:

- `workshop-designer` → `modify`
- `workshop-quality` → `modify`
- `workshop-feedback` → `create`

Unchanged shipped plugins do not reappear in `changes/`.

### Workspace snapshot

```text
studio/
├── changes/
│   ├── .gitkeep
│   ├── course-workshop/
│   │   ├── event-storm.md
│   │   ├── changelog.md
│   │   ├── status.json
│   │   ├── domain-map.md
│   │   ├── domain-canvas.md
│   │   ├── behavior-matrix.md
│   │   ├── opportunity-brief.md
│   │   ├── personas/
│   │   │   └── ...
│   │   ├── journeys/
│   │   │   └── ...
│   │   └── processes/
│   │       └── ...
│   ├── workshop-designer/
│   │   └── status.json
│   ├── workshop-quality/
│   │   └── status.json
│   └── workshop-feedback/
│       └── status.json
└── archive/
    ├── workshop-core/
    │   └── 2026-03-28-iteration-1/
    ├── workshop-designer/
    │   └── 2026-03-28-iteration-1/
    ├── workshop-insight/
    │   └── 2026-03-28-iteration-1/
    ├── workshop-quality/
    │   └── 2026-03-28-iteration-1/
    └── workshop-resource/
        └── 2026-03-28-iteration-1/

workshop-feedback/
├── skills/
│   └── .gitkeep
└── commands/
    └── .gitkeep
```

### Example modify workspace status

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "modify",
  "iteration": 2,
  "phase": "planning",
  "created_at": "2026-04-10T10:00:00+08:00",
  "skills": {}
}
```

### What happened

- The system created new change workspaces only for impacted plugins
- `modify` workspaces reference existing `target_dir`
- only the new plugin got a fresh scaffold

### Confirmation gate

The user confirms:

- impact classification
- which plugins are `modify`
- which plugin is `create`

After confirmation, the system proceeds to incremental skill design.

## Scenario 8c: skill-design incremental mode

In `modify` mode, the system reads existing implementation and produces a delta-oriented `skill-map.md`.

### Workspace snapshot

```text
studio/
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-designer/
│   │   ├── status.json
│   │   └── skill-map.md
│   ├── workshop-quality/
│   │   ├── status.json
│   │   └── skill-map.md
│   └── workshop-feedback/
│       ├── status.json
│       └── skill-map.md
└── ...
```

### Example modify status after skill design

```json
{
  "type": "plugin",
  "plugin": "workshop-designer",
  "domain": "course-workshop",
  "target_collection": ".",
  "target_dir": "workshop-designer",
  "action": "modify",
  "iteration": 2,
  "phase": "planning",
  "created_at": "2026-04-10T10:00:00+08:00",
  "skills": {
    "proposal-generate": "draft"
  }
}
```

### What happened

- For `modify`, only impacted skills are listed
- unchanged skills are not fully redescribed
- `skill-map.md` represents the design delta for this iteration

### Confirmation gate

The user confirms:

- affected skills
- new vs modified behavior
- whether to proceed into build

After confirmation, the system proceeds to incremental spec generation and `build-skills`.

## Scenario 8d: spec-generate + build-skills in modify mode

This is the key difference in iteration 2.

Rules for `modify`:

- `brief.md` is preserved and appended with an iteration update
- `plugin.json.draft` is refreshed only in generated fields
- existing `SKILL.md` files are not overwritten during spec generation
- existing command files are not overwritten
- new skills get skeletons
- modified existing skills are passed to `build-skills`, which uses `skill-creator` for targeted updates

### Workspace snapshot

```text
studio/
├── changes/
│   ├── course-workshop/
│   │   └── ...
│   ├── workshop-designer/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   ├── workshop-quality/
│   │   ├── status.json
│   │   ├── skill-map.md
│   │   ├── brief.md
│   │   └── plugin.json.draft
│   └── workshop-feedback/
│       ├── status.json
│       ├── skill-map.md
│       ├── brief.md
│       └── plugin.json.draft
└── archive/
    └── ...
```

### Existing plugin implementation snapshot

```text
workshop-designer/
├── skills/
│   ├── driving-question/
│   │   └── SKILL.md
│   ├── network-map/
│   │   └── SKILL.md
│   ├── inquiry-scaffold/
│   │   └── SKILL.md
│   ├── activity-design/
│   │   └── SKILL.md
│   └── proposal-generate/
│       └── SKILL.md
└── commands/
    └── proposal-generate.md
```

### New plugin implementation snapshot

```text
workshop-feedback/
├── skills/
│   ├── feedback-summary/
│   │   └── SKILL.md
│   └── parent-report/
│       └── SKILL.md
└── commands/
    ├── feedback-summary.md
    └── parent-report.md
```

### What happened

- The existing `proposal-generate/SKILL.md` in `workshop-designer/` was preserved
- The system did not overwrite it
- The system passed it to `build-skills`, which invoked `skill-creator` to modify it in place
- Existing commands in `workshop-designer/commands/` were preserved
- New plugin `workshop-feedback` received fresh skills and commands

### Important clarification

In `modify` mode, "do not overwrite" does not mean "the user must manually edit the file."

It means:

- `spec-generate` does not replace the file with a new skeleton
- the system still uses `build-skills` and `skill-creator` to update the existing file in place

## Scenario 9: validate and promote iteration 2

The system validates the changed plugins and promotes them.

Order:

- promote `workshop-feedback`
- promote `workshop-designer`
- promote `workshop-quality`

### Final workspace snapshot after iteration 2

```text
studio/
├── config.yaml
├── agents/
│   └── ...
├── changes/
│   ├── .gitkeep
│   └── course-workshop/
│       ├── event-storm.md
│       ├── changelog.md
│       ├── domain-map.md
│       ├── domain-canvas.md
│       ├── behavior-matrix.md
│       ├── opportunity-brief.md
│       ├── personas/
│       ├── journeys/
│       ├── processes/
│       └── status.json
└── archive/
    ├── workshop-core/
    │   └── 2026-03-28-iteration-1/
    ├── workshop-designer/
    │   ├── 2026-03-28-iteration-1/
    │   └── 2026-04-10-iteration-2/
    ├── workshop-insight/
    │   └── 2026-03-28-iteration-1/
    ├── workshop-quality/
    │   ├── 2026-03-28-iteration-1/
    │   └── 2026-04-10-iteration-2/
    ├── workshop-resource/
    │   └── 2026-03-28-iteration-1/
    └── workshop-feedback/
        └── 2026-04-10-iteration-2/
```

### Implementation snapshot

```text
workshop-designer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── ...
└── commands/
    └── ...

workshop-feedback/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── ...
└── commands/
    └── ...
```

### What happened

- active plugin change workspaces were archived
- the domain workspace remained active and cumulative
- implementation stayed in `target_dir`
- design history was preserved per plugin and per iteration

## Scenario 10: small direct implementation change

The user wants to change only the output format of an existing skill such as `proposal-generate`.

This does not require a full planning iteration.

The system or user can directly edit:

```text
workshop-designer/skills/proposal-generate/SKILL.md
```

### Workspace snapshot

```text
studio/
├── changes/
│   ├── .gitkeep
│   └── course-workshop/
│       └── ...
└── archive/
    └── ...
```

### What happened

- `studio/changes/` did not change
- `studio/archive/` did not change
- the implementation changed directly in `target_dir`
- git history captures the implementation-level change

## Summary Table

| Phase | What changes in `studio/changes/` | What changes in `target_dir` |
|------|------------------------------------|------------------------------|
| `init` | empty workspace created | — |
| `event-storm` | domain workspace appears with `event-storm.md`, `changelog.md`, personas, journeys, processes | — |
| `domain-model` | domain analysis docs appear; plugin change workspaces appear with `status.json` | `create` plugins get scaffold; `modify` plugins do not |
| `skill-design` | `skill-map.md` appears; skill statuses enter `draft` | — |
| `spec-generate` | `brief.md`, `plugin.json.draft`, status updates | skill skeletons and commands are generated |
| `build-skills` | no new design docs required beyond status updates | `skill-creator` fleshes out or modifies skills in place |
| `validate` | matching workspace moves to `approved` | validates implementation in `target_dir` |
| `promote` | plugin workspace moves from `changes/` to `archive/{plugin}/{date}-iteration-{N}` | finalized manifest is written; implementation stays in place |
| iteration N `event-storm` | domain artifacts updated in place; `changelog.md` appended | — |
| iteration N `domain-model` | only impacted plugin workspaces appear | `modify` does not scaffold |
| iteration N `spec-generate` | `brief.md`, `plugin.json.draft`, `status.json` updated | only new skills get skeletons; existing files preserved |
| iteration N `build-skills` | status updates only | new skills are built; modified skills are updated in place |
| small direct change | no change | implementation edited directly |

## Final Interpretation

The current intended Astra Studio model is:

- domain knowledge is cumulative and stays active in `studio/changes/{domain}`
- plugin design workspaces are temporary active change records
- implementation always lives in `target_dir`
- shipped design workspaces move into `studio/archive/`
- confirmation is a user decision point
- execution is a system responsibility

That distinction is what keeps the pipeline understandable:

- users confirm
- the system builds
- design stays traceable
- implementation stays singular
