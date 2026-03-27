---
name: persona-insight
description: Create detailed user persona cards with goals, pain points, context, and empathy mapping. Use when you need to understand who the users are, when designing features, when starting user research, or when someone asks "who is our user". Produces structured persona documents.
allowed-tools: Read, Write, Glob, Agent
user-invocable: true
---

# Persona Insight

Produce professional user persona cards that capture who the real users are — their roles, goals, daily context, pain points, and emotional landscape. Each persona is a standalone reference document that can inform design, planning, and prioritization decisions.

Read `${CLAUDE_SKILL_DIR}/../../agents/product-manager.md` for the PM perspective that guides persona development.

## Inputs

Accept one of:
- A description of the user or user type via `$ARGUMENTS` (e.g., "全职妈妈，两个孩子，关注营养")
- A domain workspace path — read `studio/changes/{name}/event-storm.md` to extract personas mentioned there
- A conversation context — infer from what the user has been discussing

## Workflow

1. **Gather context** — understand the domain and user segment
2. **Build persona** — construct a structured persona card
3. **Map empathy** — understand what the user thinks, feels, sees, does
4. **Validate** — present to user for feedback
5. **Write output** — save persona document

## Step 1: Gather Context

Extract or ask for:
- **Domain**: What industry/product/service?
- **User segment**: Which type of user? (may be multiple)
- **Data sources**: Any existing user research, support tickets, interview notes?

If working within a studio workspace, scan `event-storm.md` for personas already mentioned.

## Step 2: Build Persona Card

For each persona, produce:

```
┌─────────────────────────────────────────────────┐
│  {Persona Name}                                 │
│  "{One-sentence quote that captures their voice}"│
├─────────────────────────────────────────────────┤
│                                                 │
│  Role:        {job title or life role}          │
│  Age range:   {typical age}                     │
│  Tech level:  {高/中/低}                         │
│  Context:     {daily situation, constraints}     │
│                                                 │
│  Goals:                                         │
│  1. {Primary goal — what they're trying to do}  │
│  2. {Secondary goal}                            │
│  3. {Underlying motivation — why they care}     │
│                                                 │
│  Pain points:                                   │
│  1. {Biggest frustration} — severity: 高         │
│  2. {Second frustration} — severity: 中          │
│  3. {Third frustration} — severity: 低           │
│                                                 │
│  Current tools:                                 │
│  - {What they use today and why}                │
│  - {Where current tools fail}                   │
│                                                 │
│  Success looks like:                            │
│  "{What 'mission accomplished' means to them}"  │
│                                                 │
└─────────────────────────────────────────────────┘
```

Use the **product manager** agent perspective to challenge and refine: "Is this persona based on real behavior patterns, or is it an idealized version?"

## Step 3: Map Empathy

For each persona, produce an empathy map:

```
            ┌─────────────┐
            │   Thinks     │
            │ {beliefs,    │
            │  concerns,   │
            │  priorities} │
┌───────────┼─────────────┼───────────┐
│   Sees    │             │   Hears   │
│ {what they│   PERSONA   │ {advice,  │
│  observe  │             │  feedback,│
│  in their │             │  noise}   │
│  world}   │             │           │
└───────────┼─────────────┼───────────┘
            │   Does      │
            │ {actions,   │
            │  behaviors, │
            │  workarounds│
            └─────────────┘

Pain: {core frustration that cuts across all quadrants}
Gain: {core desire that would resolve the pain}
```

## Step 4: Validate

Present the persona card and empathy map to the user:
- "Does this match real users you know?"
- "What's missing or inaccurate?"
- "Are there distinct sub-segments within this persona?"

If the user identifies sub-segments, create separate persona cards for each.

## Step 5: Write Output

If working within a studio workspace, write to:
```
studio/changes/{domain-or-plugin}/personas/{persona-slug}.md
```

If standalone (no workspace), write to the current directory or let the user choose.

Each persona file contains the full persona card + empathy map in markdown format.

If multiple personas were created, also write an index:
```
studio/changes/{name}/personas/README.md
```

Listing all personas with one-line summaries.
