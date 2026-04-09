---
name: screenshot-to-pencil
description: Convert a UI screenshot into a Pencil (.pen) prototype file. Use when you have a screenshot or mockup image and need to create a machine-readable design prototype. Analyzes layout, components, colors, typography, spacing, and icons to produce a structured .pen JSON file.
allowed-tools: Read, Write, Bash, Glob, Grep
user-invocable: true
---

# Screenshot to Pencil

Analyze a UI screenshot and generate a Pencil (.pen) prototype file that faithfully represents the visual design.

## Pre-conditions

1. **Identify the screenshot**: The user must provide a screenshot — either as a file path, clipboard image, or inline image in the conversation. If no image is provided, ask the user for one.

2. **Identify target .pen file**: Determine where to write the output:
   - If `$ARGUMENTS` specifies a path, use it
   - If a `.pen` file already exists in the project's `docs/design/` directory, ask whether to **append a new frame** to it or **create a new file**
   - Default: `docs/design/screens.pen`

3. **Load existing .pen** (if appending): Read the existing file to:
   - Reuse design tokens (`variables`)
   - Reuse reusable components (nodes with `"reusable": true`)
   - Determine the next frame index for naming (e.g., "7. New Screen")
   - Avoid duplicate IDs

4. **Load references**: 
   - Read `references/pencil-format-spec.md` for the .pen format specification
   - Read `references/tech-stack.md` for design token mappings and component conventions

## Analysis Steps

### Step 1: Visual Decomposition

Analyze the screenshot systematically:

1. **Overall layout**: Identify the page structure (sidebar + main content, header + body + footer, etc.)
2. **Major sections**: Break into top-level containers (frames)
3. **Components**: Identify UI components in each section:
   - Navigation bars, sidebars, headers
   - Buttons (primary, secondary, ghost, icon-only)
   - Input fields, text areas, search bars
   - Cards, lists, tables
   - Modals, dropdowns, tooltips
   - Icons and their approximate names (match to Lucide icon set)
4. **Typography**: Note font sizes, weights, and hierarchy
5. **Colors**: Extract the color palette — backgrounds, text, borders, accents
6. **Spacing**: Estimate gaps, padding, margins between elements
7. **Dimensions**: Estimate component sizes relative to the viewport

### Step 2: Design Token Extraction

Map observed colors to design tokens:

1. If appending to an existing .pen file, **reuse existing tokens**
2. If creating new, establish the standard token set:
   - Background tiers: `$bg`, `$bg-sidebar`, `$bg-card`, `$bg-input`, `$bg-muted`
   - Text tiers: `$text-primary`, `$text-secondary`, `$text-muted`
   - Accent colors: `$accent`, `$destructive`, `$green`, `$blue`, `$red`
   - Borders: `$border`, `$border-light`
3. Extract any additional colors not covered by standard tokens

### Step 3: Structure Generation

Build the .pen JSON:

1. **Generate unique IDs**: 5-character alphanumeric (e.g., `aE3Ug`). Use Python:
   ```python
   import random, string
   ''.join(random.choices(string.ascii_letters + string.digits, k=5))
   ```

2. **Build node tree** top-down:
   - Top-level: `frame` with screen name, 1440×900 (desktop) or 390×844 (mobile)
   - Second level: major layout sections (sidebar frame, header frame, content frame)
   - Third level: component groups
   - Leaf level: `text`, `icon_font`, `ellipse` nodes

3. **Apply layout rules**:
   - Use `layout: "vertical"` or `"horizontal"` for flexbox-like flows
   - Set `gap` based on observed spacing
   - Set `padding` based on observed internal spacing
   - Use `alignItems` for cross-axis alignment
   - Use `"fill_container"` for stretching elements, `"fit_content"` for auto-sized

4. **Map icons**: Match visual icons to Lucide names:
   - Hamburger/menu → `menu`
   - Left arrow → `arrow-left`
   - Search → `search`
   - Settings gear → `settings`
   - Plus/add → `plus`
   - Close/X → `x`
   - Chevron → `chevron-down`, `chevron-right`
   - User avatar → `user` or `ellipse` with initials

5. **Identify reusable components**: If a visual pattern repeats across screens (e.g., sidebar, header), mark it with `"reusable": true` and reference it with `"type": "ref"` in other frames.

### Step 4: Output

1. If creating new file: Write complete .pen JSON with `version`, `children`, `variables`
2. If appending: Add new frame(s) to existing `children` array, merge any new tokens into `variables`
3. Format JSON with 2-space indentation for readability
4. Report what was created: frame names, component count, token count

## Output Format

```json
{
  "version": "2.10",
  "children": [
    {
      "type": "frame",
      "id": "xxxxx",
      "name": "1. Screen Name",
      "width": 1440,
      "height": 900,
      "fill": "$bg",
      "layout": "horizontal",
      "children": [
        /* sidebar, content, etc. */
      ]
    }
  ],
  "variables": {
    "$bg": { "type": "color", "value": "#09090B" },
    /* ... */
  }
}
```

## Quality Checklist

- [ ] All colors use `$variable` references (no hardcoded hex except in `variables`)
- [ ] Layout uses `layout` + `gap` + `padding` (not absolute positioning, unless needed for overlays)
- [ ] Icons use valid Lucide names with `iconFontFamily: "lucide"`
- [ ] IDs are unique 5-char alphanumeric
- [ ] Frame names are descriptive and numbered
- [ ] Text elements have appropriate `fontSize`, `fontWeight`, `fill`
- [ ] Sizing uses `"fill_container"` / `"fit_content"` where appropriate

## Does NOT

- Generate actual code — that's the job of `openspec-to-code`
- Create OpenSpec proposals — that's `pencil-to-openspec`
- Require the Pencil desktop app — .pen is a standalone JSON format
- Handle animations or interactions — .pen is static layout only
