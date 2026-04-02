---
description: Export a markdown document to DOCX and/or PDF with Mermaid rendering and formatting
argument-hint: [markdown-file-path format]
---

Export a markdown document to production-ready DOCX and/or PDF for `$ARGUMENTS`. Handles the full export pipeline:

1. **Mermaid rendering** — Detect all ```mermaid code blocks, render each to PNG via mermaid-cli (mmdc), and replace blocks with image references
2. **Markdown → DOCX conversion** — Convert via pandoc with Chinese government document formatting (方正小标宋简体 headings, 仿宋 body, proper margins and spacing)
3. **DOCX formatting** — Apply blueprint-defined styles: heading hierarchy, table formatting, page headers/footers, and page numbering
4. **PDF generation** (optional) — Convert DOCX to PDF via LibreOffice or wkhtmltopdf

Supported formats:
- `docx` — Microsoft Word format with full styling
- `pdf` — PDF with embedded fonts
- `docx+pdf` — Both formats

Output files are placed alongside the source markdown file unless an output directory is specified.

Examples:
- `/studio-docs:export docs/solutions/方案.md docx+pdf`
- `/studio-docs:export docs/solutions/方案.md pdf`
- `/studio-docs:export docs/solutions/方案.md docx`

Use skill: "export-document"
