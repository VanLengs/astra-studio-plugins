# Skill Decomposition Guide

Reference for breaking plugins into well-scoped skills. Used by `skill-design` to design skill boundaries.

## Principles

### 1. Single Responsibility

Each skill does **one thing well**. If you need "and" to describe it, it's probably two skills.

- Good: "Analyze portfolio risk exposure"
- Bad: "Analyze portfolio risk and generate compliance report"

### 2. Clear Input/Output Contract

Every skill should have:
- **Defined inputs**: What it reads (files, arguments, context)
- **Defined outputs**: What it produces (files, terminal output, side effects)
- **Explicit boundaries**: What it does NOT do

### 3. User Decision Points

Skills should break at points where the user needs to make a decision. If two operations always run in sequence with no user review between them, they're probably one skill.

### 4. Composability

Skills should be usable independently and in combination. Avoid tight coupling where Skill B can only run immediately after Skill A.

---

## Decomposition Process

### Step 1: List All Capabilities

Write down everything the plugin should be able to do, as user stories:

```
- As a trader, I want to screen deals against criteria
- As a trader, I want to run due diligence on a specific deal
- As a manager, I want a summary report of the pipeline
```

### Step 2: Group by Cohesion

Cluster capabilities that:
- Share the same data context
- Are invoked by the same persona
- Naturally occur in the same workflow step

### Step 3: Apply Split/Merge Rules

**Split when:**
| Signal | Action |
|--------|--------|
| Description uses "and" joining unrelated tasks | Split into separate skills |
| More than 3 distinct input types | Split by input type |
| Different users invoke different parts | Split by persona |
| Skill would exceed ~300 lines of SKILL.md | Split by phase |
| Output serves as input to a user decision | Split at the decision point |
| HIL checkpoint (approval gate) exists between steps | Split at the approval boundary |
| Skill spans two independent pipelines | Split into pipeline-specific skills |
| Plugin is stateful but has no workspace init | Add dedicated `init-workspace` skill |
| Skill needs domain KB but others don't | Separate KB-dependent skills for clarity |

**Merge when:**
| Signal | Action |
|--------|--------|
| One skill only feeds data to another | Merge into one |
| Always run in sequence, no decision between them | Merge into pipeline |
| Skill has only 1-2 trivial steps | Merge into parent |

### Step 4: Name and Describe

| Convention | Rule | Example |
|-----------|------|---------|
| Format | `kebab-case` | `analyze-risk` |
| Pattern | `verb-noun` preferred | `generate-report` |
| Length | 2-4 words | `screen-deals` |
| Description | Slightly "pushy" for trigger matching | "Analyze and score risk..." |

The `description` field in SKILL.md frontmatter is what Claude uses to decide whether to invoke the skill. Make it specific and action-oriented — err on the side of being slightly pushy so it triggers when relevant.

---

## Dependency Mapping

### Pipeline Pattern

Skills form a directed chain:
```
analyze-data → enrich-results → generate-report
```

Rules:
- No circular dependencies
- Each skill can run independently with manual input
- Pipeline is orchestrated by a command, not hard-wired

### Fan-out Pattern

One skill produces data consumed by multiple independent skills:
```
               ┌→ check-compliance
scan-portfolio ├→ analyze-risk
               └→ generate-summary
```

### Independent Pattern

Skills share a domain but no data flow:
```
configure-settings
import-data
export-report
```

---

## Trait-Driven Standard Skills

When `skill-design` detects plugin traits, certain standard skills and patterns should be included:

### Stateful plugins

| Standard Skill | Purpose | Complexity |
|---------------|---------|-----------|
| `init-workspace` | Create `.{plugin-name}/` runtime directory | Moderate (scripts for directory creation + config) |
| `manage-config` (optional) | View/update runtime settings | Simple |
| `status` (optional) | Show project dashboard | Moderate (scripts for status aggregation) |

The `init-workspace` skill is always generated for stateful plugins. `manage-config` and `status` are recommended when the plugin manages multiple projects.

### HIL-gated plugins

- Every skill with an approval gate gets an `## Approval Gate` section
- Maximum one gate per skill — if a workflow has multiple gates, split into separate skills
- The gate goes after draft production, before final output write
- If the plugin is also stateful, record decisions in `status.json`

### KB-dependent plugins

| KB complexity | Approach |
|--------------|---------|
| 1-2 static docs | Inline `references/` in skill directory |
| 3+ docs, shared across skills | Plugin-level `references/` |
| Complex, frequently updated, needs search | Companion `{name}-kb` plugin |

### Multi-pipeline plugins

- Each pipeline gets an orchestration command (`commands/{pipeline-name}.md`)
- Skills can be pipeline-specific or shared
- Shared skills are listed in the `## Pipelines → Shared skills` section of skill-map.md
- Pipeline commands chain skills with user review pauses between steps

### Expert-scoped plugins

- Planning-phase experts stay in `studio-insight/agents/` or `studio/agents/`
- Runtime experts are shipped with the plugin in `{target_dir}/agents/`
- If an expert serves both phases, the runtime version is a copy (may be simplified for end-user context)

---

## Complexity Tiers

Classify each skill to set expectations for implementation effort:

### Tier 1: Simple (Prompt-only)

- SKILL.md with clear instructions
- May use `references/` for domain knowledge
- No scripts needed
- `allowed-tools`: Read, Write, Glob

```
skills/
└── my-skill/
    ├── SKILL.md
    └── references/
        └── domain-guide.md
```

### Tier 2: Moderate (Scripts needed)

- SKILL.md orchestrates helper scripts
- Python/Bash scripts for data processing or validation
- `allowed-tools`: Read, Write, Bash, Glob, Grep

```
skills/
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    │   ├── process_data.py
    │   └── validate.py
    └── references/
```

### Tier 3: Complex (Multi-stage orchestration)

- Multiple phases with user checkpoints
- May invoke other skills or agents
- Significant script infrastructure
- `allowed-tools`: Read, Write, Bash, Glob, Grep, Edit, Agent

```
skills/
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    │   ├── stage1_analyze.py
    │   ├── stage2_transform.py
    │   └── stage3_validate.py
    └── references/
```

---

## SKILL.md Skeleton Format

When producing skeletons for `skill-creator` to flesh out:

```markdown
---
name: {skill-name}
description: {One line — specific, action-oriented, slightly pushy for trigger matching}
allowed-tools: {comma-separated list based on complexity tier}
user-invocable: true
---

# {Skill Title}

{2-3 sentence summary: what it does, when to use it, what it produces.}

## Intent
- {What should this skill enable the agent to do?}
- {When should this skill trigger?}

## Expected Inputs
- {Input 1: description and format}
- {Input 2: description and format}

## Expected Outputs
- {Output 1: description and format}
- {Output 2: description and format}

## Workflow
1. {High-level step 1}
2. {High-level step 2}
3. {High-level step 3}

## Out of Scope
- {What this skill explicitly does NOT do}
```

This skeleton gives `skill-creator` enough context to:
1. Write full instructions
2. Design evals
3. Create helper scripts if needed

### Extended Skeleton (trait-driven)

When plugin traits are detected, the skeleton may include additional sections:

```markdown
## Approval Gate
{Only for skills with HIL checkpoint — standardized approval prompt}

## Knowledge Base
{Only for KB-dependent skills — what domain knowledge is needed and where to find it}

## Pipeline Context
{Only for multi-pipeline skills — which pipeline(s) this skill belongs to}
```

These sections are injected by `spec-generate` based on the `## Plugin Traits` section in skill-map.md.

---

## Anti-patterns

| Anti-pattern | Problem | Fix |
|-------------|---------|-----|
| God skill | One skill does everything | Split by responsibility |
| Trivial skill | Skill has 1-2 lines of instruction | Merge into parent |
| Hidden dependency | Skill assumes another ran first but doesn't declare it | Make input explicit or add dependency |
| Leaky abstraction | Skill exposes implementation details in its interface | Define clean input/output contract |
| Premature generalization | Skill tries to handle all possible cases | Start specific, generalize when needed |
| Duplicate capability | Two skills do the same thing slightly differently | Merge and parameterize |
