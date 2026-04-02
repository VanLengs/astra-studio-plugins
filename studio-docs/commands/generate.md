---
description: Generate a complete project document from planning artifacts — plan chapters, write in parallel, assemble, and optionally export
argument-hint: [document-type domain-name]
---

Generate a complete project document for `$ARGUMENTS` by chaining the full document pipeline:

1. **plan-document** — Analyze planning artifacts (event storms, domain models, skill designs, etc.), map them to blueprint chapters, and create a detailed writing plan with section assignments and data references.

2. **write-section** (×N parallel) — Write each chapter/section in parallel via the Agent tool, using the assigned writing expert's style. Each section receives its writing plan, relevant artifacts, and style guide.

3. **assemble-document** — Merge all written sections into a single coherent document. Harmonize cross-references, ensure terminology consistency, run compliance checks against the blueprint, and generate table of contents.

4. (Optional) **export-document** — If the user adds "export", "docx", or "pdf" to the command, convert the final markdown to DOCX and/or PDF with proper formatting, Mermaid diagram rendering, and Chinese government document styling.

Before starting:
- Verify `studio/` exists — if not, suggest running the init skill first
- Verify planning artifacts exist for the specified domain — if not, suggest running `/studio-planner:plan` first
- If no blueprint exists for the document type, suggest `/studio-docs:blueprint` first
- If no writing expert exists, ask if the user wants to create one via `/studio-docs:writer` or proceed with default style

After each major step, pause and present results to the user for validation before proceeding to the next stage. The user may skip or re-run any stage.

Examples:
- `/studio-docs:generate 建设方案 linxi-edutech`
- `/studio-docs:generate feasibility-study my-project export`
- `/studio-docs:generate 投标文件 smart-campus docx+pdf`

Use skill: "plan-document" (then chains to write-section → assemble-document → export-document)
