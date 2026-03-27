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

When producing skeletons for a skill authoring tool to flesh out:

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
- {What should this skill enable Claude to do?}
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

This skeleton gives a skill authoring tool enough context to:
1. Write full instructions
2. Design evals
3. Create helper scripts if needed

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
