---
description: Create or customize a document blueprint for project documents
argument-hint: [document type name or "list"]
---

Create or customize a document blueprint for `$ARGUMENTS`. A blueprint defines the chapter structure, required sections, compliance checkpoints, and quality criteria for a specific document type (e.g., 建设方案, 可行性研究报告, 投标文件).

Blueprints are stored in `studio/docs/blueprints/` as YAML files and are consumed by the `plan-document` and `assemble-document` skills during document generation.

Modes:
- **Create**: Generate a new blueprint from a document type name, including standard chapter structures and section requirements
- **List**: Show all available blueprints in the current project
- **Customize**: Modify an existing blueprint to fit project-specific requirements

Examples:
- `/studio-docs:blueprint 可行性研究报告`
- `/studio-docs:blueprint list`
- `/studio-docs:blueprint customize construction-plan`

Use skill: "define-blueprint"
