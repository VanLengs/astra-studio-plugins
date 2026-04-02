---
name: assemble-document
description: Assemble written chapter parts into a complete document — merge sections, harmonize numbering, verify terminology consistency, check cross-references, and validate against blueprint compliance rules. Produces the final markdown document and a quality report.
allowed-tools: Read, Write, Glob, Grep
user-invocable: true
---

# Assemble Document

Merge individually written chapter parts into a single, coherent document. This skill is the **post-production** phase — it takes the raw parts produced by `write-section` instances and performs merging, numbering harmonization, terminology consistency, cross-reference validation, and blueprint compliance checking. The output is a publication-ready markdown document plus a quality report.

## Inputs

Accept one of:
- A doc plan path via `$ARGUMENTS` (e.g., `studio/changes/linxi-edutech/doc-plan-construction-plan.yaml`)
- A domain name — the skill will auto-discover the doc plan in `studio/changes/{domain}/`

## Workflow

1. **Read doc plan** — identify all chapters and their status
2. **Collect parts** — gather written chapter files from parts directory
3. **Pre-assembly checks** — verify critical chapters are present
4. **Merge** — concatenate parts in order with document header
5. **Harmonize numbering** — fix heading numbers and hierarchy
6. **Terminology consistency** — enforce preferred terms
7. **Cross-reference validation** — verify internal references
8. **Figure and table numbering** — assign sequential IDs
9. **Compliance check** — validate against blueprint rules
10. **Write output** — produce final document and quality report
11. **Report** — print assembly summary

## Step 1: Read Doc Plan

Read the doc plan YAML:
```
studio/changes/{domain}/doc-plan-{type}.yaml
```

Extract:
- **Chapter list**: All chapters with their IDs, titles, order, and status
- **Parts directory**: Where `write-section` wrote its output files (e.g., `docs/{domain}/.parts/`)
- **Blueprint reference**: Which blueprint governs this document
- **Writer reference**: Which writer agent was used (for terminology preferences)
- **Document metadata**: Title, domain, document type, display name

Build a chapter manifest:

| ID | Title | Status | Required | Part File |
|----|-------|--------|----------|-----------|
| ch1 | 项目概述 | written | yes | `.parts/ch1.md` |
| ch2 | 建设背景 | written | yes | `.parts/ch2.md` |
| ch3 | 需求分析 | written | yes | `.parts/ch3.md` |
| ch7 | 项目管理 | failed | yes | — |
| ch8 | 附录 | pending | no | — |

## Step 2: Collect Parts

Glob the parts directory for all markdown files:
```
{parts_dir}/*.md
```

Sort files by chapter order (using the chapter list from the doc plan, not alphabetical order).

For chapters with sub-tasks, also collect sub-task files:
```
{parts_dir}/{chapter_id}-*.md
```

Sub-task files are merged within their parent chapter in sub-task order.

Build a collection report:
- **Present**: Parts found on disk with matching chapter IDs
- **Missing**: Chapters with status `failed` or `pending` — no part file exists
- **Orphaned**: Part files that don't match any chapter ID (warn but ignore)

## Step 3: Pre-Assembly Checks

### Critical chapter check

Read the blueprint to determine which chapters are `required: true`.

If any **required** chapter is missing (status is `failed` or `pending` with no part file):
- **STOP assembly**
- Report which critical chapters are missing
- Suggest: re-run `generate` for the failed chapters, or write them manually

### Optional chapter check

If **optional** chapters are missing:
- Note in the quality report
- Continue assembly — the document is valid without optional chapters

### Minimum content check

For each present part file:
- Verify file is not empty (>10 lines of content)
- Verify file starts with a heading (`#`)
- If a part file is effectively empty, treat it as missing

## Step 4: Merge

Assemble the document in this order:

### Document header

```markdown
# {display_name}

<!-- TOC -->

```

The `display_name` comes from the blueprint (e.g., "XX大学智慧校园建设方案").

The `<!-- TOC -->` marker is a placeholder for table of contents generation — downstream tools (pandoc, export-document) can use it.

### Chapter concatenation

For each chapter in order:
1. Read the part file content
2. Append to the document with a blank line separator
3. If the chapter has sub-task parts, merge them in order within the chapter

### Section breaks

Insert a horizontal rule (`---`) between major chapters (top-level `#` headings) for visual separation, but not between sub-sections within a chapter.

## Step 5: Harmonize Numbering

After merging, scan the entire document for heading consistency.

### Chapter-level numbering

Verify the top-level chapter numbering follows the blueprint convention:

| Convention | Pattern | Example |
|------------|---------|---------|
| Chinese ordinal | 一、二、三、四... | `# 一、项目概述` |
| Chinese chapter | 第一章、第二章... | `# 第一章 项目概述` |
| Arabic | 1、2、3... | `# 1 项目概述` |

Fix any gaps (e.g., if chapter 三 is missing, renumber 四→三, 五→四, etc.) or duplicates.

### Section-level numbering

Within each chapter, verify sub-section numbering:

| Level | Convention | Example |
|-------|------------|---------|
| `##` | （一）（二）（三） | `## （一）建设目标` |
| `###` | 1. 2. 3. | `### 1. 数据采集体系` |
| `####` | (1) (2) (3) | `#### (1) 采集范围` |

Fix numbering within each chapter independently — renumber sequentially.

### Heading level integrity

Verify no heading levels are skipped:
- `#` → `##` → `###` ✅
- `#` → `###` (skipped `##`) ❌ — insert or fix

## Step 6: Terminology Consistency

### Load terminology preferences

If a writer agent was used, read its terminology section:
```
studio/agents/writers/{writer}.md → ## Terminology
```

Expected format:
```
Preferred Term → Variants to Replace
产教融合 → 产教结合, 产教合作
信息化 → 信息技术化, IT化
```

### Scan and replace

For each terminology rule:
1. Grep the merged document for variant terms
2. Replace with the preferred term
3. Log each replacement in the quality report:
   ```
   ⚠️ Terminology: "产教结合" → "产教融合" (3 occurrences, lines 45, 128, 302)
   ```

### Context-aware replacement

Do NOT replace terms inside:
- Code blocks (fenced with ``` )
- Mermaid diagram blocks
- Direct policy quotations (text within「」or 《》)
- Table headers that match a specific schema

## Step 7: Cross-Reference Validation

Find all internal cross-references in the document:

### Reference patterns to detect

| Pattern | Example | Validation |
|---------|---------|------------|
| Chapter reference | "详见第四章" "见第三部分" | Verify chapter exists |
| Section reference | "如（二）所述" | Verify section exists in context |
| Table reference | "如表3-1所示" "见表4-2" | Verify table exists |
| Figure reference | "如图2-1所示" "见图5-3" | Verify figure exists |
| Appendix reference | "详见附录A" | Verify appendix exists |

### Validation process

For each cross-reference found:
1. Parse the target (chapter number, table number, figure number)
2. Search the document for the referenced element
3. If found: mark as ✅ in quality report
4. If not found: mark as ❌ and flag for manual review

Do NOT auto-fix broken cross-references — just report them. The references may point to content that needs to be written.

## Step 8: Figure and Table Numbering

### Figure numbering

Scan all mermaid diagram blocks and image references:
1. Assign sequential figure numbers by chapter: 图X-Y (X = chapter number, Y = sequence within chapter)
2. Add or update caption lines below each figure:
   ```markdown
   ```mermaid
   graph TD
       A --> B
   ```
   
   **图3-1 数据治理架构**
   ```
3. If a figure already has a caption, preserve the text but update the number

### Table numbering

Scan all markdown tables:
1. Assign sequential table numbers by chapter: 表X-Y
2. Add or update caption lines above each table:
   ```markdown
   **表2-1 建设经费预算**
   
   | 项目 | 金额（万元） | 说明 |
   |------|-------------|------|
   | ... | ... | ... |
   ```
3. Skip tables that are clearly inline formatting (e.g., single-row tables used for layout)

## Step 9: Compliance Check

Read the blueprint's compliance rules section and check each rule against the assembled document.

### Standard compliance checks

| Rule | How to check | Pass criteria |
|------|-------------|---------------|
| Policy citation count | Grep for `《.*》` pattern | Count ≥ blueprint minimum |
| Required sections present | Match heading text against blueprint chapter list | All required chapters exist |
| Investment/budget table | Grep for budget-related table captions | At least 1 table with financial data |
| Mermaid diagram count | Count ``` mermaid blocks | Count ≥ blueprint minimum |
| Word count | Estimate total words (Chinese characters + words) | Within blueprint range |
| Timeline/gantt present | Grep for gantt or timeline mermaid blocks | At least 1 if blueprint requires |

### Produce compliance checklist

```
Compliance: X/Y checks passed
  ✅ Policy citations ≥ 5 (found: 12)
  ✅ Investment table present
  ✅ Required sections: 7/7 present
  ❌ Social stability risk analysis missing
  ✅ Mermaid diagrams ≥ 10 (found: 15)
  ✅ Word count in range [30000, 50000] (actual: ~42000)
```

## Step 10: Write Output

### Main document

Write the assembled document to:
```
docs/{domain}/{display_name}.md
```

Example: `docs/linxi-edutech/临溪教育科技智慧校园建设方案.md`

If the file already exists, overwrite it (this skill is idempotent).

### Quality report

Write the quality report to:
```
docs/{domain}/.quality-report-{type}.md
```

The quality report contains:
- Assembly timestamp
- Chapter manifest (present/missing status)
- Terminology changes log
- Cross-reference validation results
- Figure and table numbering assignments
- Compliance checklist
- Missing chapters list with recommendations

## Step 11: Report

Print a summary to the user:

```
Document assembled: docs/{domain}/{display_name}.md

Statistics:
  Chapters: X/Y present
  Total words: ~NNNNN
  Mermaid diagrams: N
  Tables: N
  Policy citations: N

Compliance: X/Y checks passed
  ✅ Policy citations ≥ 5
  ✅ Investment table present
  ❌ Social stability risk analysis missing

Quality issues: N items
  ⚠️ Terminology: "产教结合" changed to "产教融合" (3 occurrences)
  ⚠️ Cross-reference: "详见第六章" — chapter 六 exists ✓

Missing chapters (manual required):
  - 七、项目管理 (write-section failed)

Next: /studio-docs:export-document docs/{domain}/{display_name}.md docx+pdf
```

## Edge Cases

### Empty parts directory

If the parts directory doesn't exist or contains no files:
- STOP with error: "No parts found. Run /studio-docs:generate first."

### All chapters failed

If every chapter has status `failed`:
- STOP with error: "All chapters failed during generation. Check artifacts and retry."

### Partial assembly

If some chapters are present and some failed:
- Assemble what's available
- Insert placeholder markers for missing chapters:
  ```markdown
  # 七、项目管理
  
  > ⚠️ **本章内容待补充** — write-section 生成失败，需手动编写。
  > 失败原因：{error from doc plan}
  ```
- Clearly note in the quality report and summary

### Re-assembly

Running `assemble-document` again on the same doc plan is safe:
- Overwrites the previous assembled document
- Regenerates the quality report
- Picks up any newly written parts since the last assembly
