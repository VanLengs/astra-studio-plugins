---
description: Create a document writing expert with specific style and terminology
argument-hint: [expert name or reference document paths]
---

Create a document writing expert for `$ARGUMENTS`. A writing expert captures the style, tone, terminology preferences, and domain knowledge of a specific author or reference corpus. Experts are instantiated from the `_doc-expert-template.md` agent template.

Modes:
- **Create by name**: Generate a writing expert with a persona name and style description
- **Analyze references**: Extract style markers, four-character phrase patterns, policy citation habits, and paragraph structures from existing reference documents
- **List**: Show all available writing experts in the current project

Writing experts are stored in `studio/docs/experts/` and are loaded by `write-section` to maintain consistent voice across all chapters.

Examples:
- `/studio-docs:writer 解决方案专家-肖作仕`
- `/studio-docs:writer analyze /path/to/reference.docx`
- `/studio-docs:writer list`

Use skill: "create-doc-expert"
