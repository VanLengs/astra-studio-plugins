---
name: openspec-to-code
description: Implement an OpenSpec change proposal as working React/Next.js code. Use when you have an approved OpenSpec proposal with requirements, scenarios, and tasks, and need to generate the actual UI components, pages, and routes. Reads tasks.md and spec deltas to produce production-ready code.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task
user-invocable: true
---

# OpenSpec to Code

Read an OpenSpec change proposal and implement it as working React/Next.js code using the project's existing component library (shadcn/ui, Radix, Tailwind CSS).

## Pre-conditions

1. **Locate the change proposal**:
   - If `$ARGUMENTS` specifies a change-id, look for `openspec/changes/{change-id}/`
   - Otherwise, list active changes via `ls openspec/changes/` (excluding `archive/`) and ask the user to choose
   - If no changes found, explain and suggest running `pencil-to-openspec` first

2. **Read the proposal**:
   - Read `proposal.md` — understand why and what
   - Read `tasks.md` — get the implementation checklist
   - Read `design.md` (if exists) — understand technical decisions
   - Read all files in `specs/` — get the requirements and scenarios

3. **Understand the project**:
   - Scan `app/` directory structure for existing routes and layouts
   - Scan `components/` for existing shared components
   - Check `components/ui/` for available shadcn components
   - Read `tailwind.config.ts` or `tailwind.config.js` for theme configuration
   - Read `package.json` for dependencies (especially UI libraries)

4. **Load references**: 
   - Read `references/component-mapping.md` for .pen-to-code mappings
   - Read `references/tech-stack.md` for technology choices, coding conventions, and project structure

5. **Load .pen file** (if referenced in proposal): If the proposal mentions a .pen file or if one exists at the standard location, read it for exact measurements, colors, and layout details.

## Implementation Steps

### Step 1: Plan Implementation Order

From tasks.md, determine the implementation order:

1. **Layouts first** — page layouts and shared containers
2. **Shared components** — reusable components used across features
3. **Feature components** — specific feature implementations
4. **Pages** — page components that compose feature components
5. **Routes** — Next.js routing setup
6. **Integration** — data connections, state management, navigation

### Step 2: Implement Each Task

For each task in tasks.md, follow this pattern:

#### Creating a Page Component

```typescript
// app/{route}/page.tsx
"use client";

import { /* components */ } from "@/components/...";

export default function PageName() {
  return (
    // Implement layout from spec requirements
  );
}
```

#### Creating a Feature Component

```typescript
// components/{feature}/{component-name}.tsx
"use client";

import { /* shadcn components */ } from "@/components/ui/...";
import { /* icons */ } from "lucide-react";

interface ComponentNameProps {
  // Props derived from spec requirements
}

export function ComponentName({ ...props }: ComponentNameProps) {
  return (
    // Implement UI from requirements and scenarios
  );
}
```

### Step 3: Map Requirements to Code

For each requirement in the spec deltas:

1. **Layout requirements** → Create container components with the specified arrangement
   - Use Tailwind flex/grid classes matching the .pen layout properties
   - Apply exact dimensions from the .pen file when available
   - Use design tokens mapped to Tailwind CSS variables

2. **Component requirements** → Create or compose shadcn/ui components
   - Match .pen node types to shadcn components (see component-mapping.md)
   - Apply correct variants (default, outline, ghost) based on .pen styling
   - Set correct sizes based on .pen dimensions

3. **State requirements** → Implement with React state hooks
   - Dropdown open/close → `useState<boolean>`
   - Form input → `useState<string>` or form library
   - Selection → `useState<string | null>`
   - Loading states → `useState<boolean>` + skeleton components

4. **Navigation requirements** → Use Next.js routing
   - Link navigation → `<Link href="...">` from `next/link`
   - Programmatic → `useRouter()` from `next/navigation`
   - Active state → compare `usePathname()` with route

5. **Visual requirements** → Apply Tailwind classes
   - Map .pen `$variables` to Tailwind CSS variables (see component-mapping.md)
   - Apply spacing: gap, padding, margin
   - Apply typography: font-size, font-weight, color

### Step 4: Verify Against Scenarios

For each `#### Scenario:` in the specs, mentally verify:

1. **WHEN** condition — is there a code path that handles this trigger?
2. **THEN** result — does the code produce the expected output?
3. **AND** additional conditions — are all conditions met?

If a scenario cannot be satisfied by the current implementation, add the missing logic.

### Step 5: Update Tasks

After implementing each task:
1. Mark completed in the mental checklist
2. If tasks.md has checkboxes, update them: `- [ ]` → `- [x]`

### Step 6: Integration Check

1. Verify imports are correct (no missing dependencies)
2. Verify route structure matches Next.js conventions
3. Verify shared components are properly exported
4. Verify Tailwind classes are valid
5. Check for TypeScript type errors if `tsconfig.json` is strict

### Step 7: Report

Print summary:
- Files created/modified (with paths)
- Requirements implemented (count)
- Scenarios covered (count)
- Any requirements that need manual attention (e.g., API integration, data sources)
- Remind: "Run `pnpm dev` to test the implementation"

## Code Style Guidelines

1. **"use client"** — add to all components (Next.js App Router with client-side rendering)
2. **Named exports** — use `export function ComponentName` (not default exports for components)
3. **shadcn/ui imports** — from `@/components/ui/{component}`
4. **Lucide imports** — from `lucide-react`
5. **Tailwind-first** — use Tailwind utility classes, avoid inline styles
6. **TypeScript** — add proper interfaces for props
7. **Responsive** — implement responsive behavior if the .pen has both desktop and mobile frames
8. **Accessibility** — add `aria-label`, `role`, keyboard navigation where appropriate

## Handling Missing Information

If the spec doesn't cover something needed for implementation:

1. **Missing API endpoints** — create mock data with `TODO: connect to API` comments
2. **Missing state management** — use local `useState` with `TODO: lift state` comments
3. **Missing auth/permissions** — skip auth checks with `TODO: add auth guard` comments
4. **Missing error states** — add basic error boundaries with `TODO: improve error handling`

## Does NOT

- Create or modify OpenSpec proposals — that's `pencil-to-openspec`
- Generate .pen files — that's `screenshot-to-pencil`
- Run the development server — that's the user's responsibility
- Deploy the code — only generates/modifies source files
- Add new npm dependencies without asking — prompt the user first
