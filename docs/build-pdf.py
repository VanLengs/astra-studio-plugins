#!/usr/bin/env python3
"""Convert whitepaper markdown (with mermaid) to PDF via Chrome headless.

Usage: python build-pdf.py
"""

import markdown
import subprocess
import sys
from pathlib import Path


def extract_and_wrap_mermaid(md_text: str) -> str:
    """Convert ```mermaid blocks to <div class="mermaid"> for client-side rendering."""
    lines = md_text.split("\n")
    result = []
    in_mermaid = False

    for line in lines:
        if line.strip() == "```mermaid":
            in_mermaid = True
            result.append('<div class="mermaid">')
            continue
        if in_mermaid and line.strip() == "```":
            in_mermaid = False
            result.append("</div>")
            continue
        if in_mermaid:
            result.append(line)
        else:
            result.append(line)

    return "\n".join(result)


def md_to_html(md_path: Path) -> str:
    """Convert markdown to full HTML with mermaid support."""
    md_text = md_path.read_text(encoding="utf-8")

    # Pre-process mermaid blocks
    md_text = extract_and_wrap_mermaid(md_text)

    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
        extension_configs={"codehilite": {"css_class": "highlight"}},
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Astra Studio 白皮书</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({{
        startOnLoad: true,
        theme: 'neutral',
        flowchart: {{ useMaxWidth: true, htmlLabels: true }},
        sequence: {{ useMaxWidth: true }},
        mindmap: {{ useMaxWidth: true }}
    }});
</script>
<style>
    @page {{
        size: A4;
        margin: 2cm 2.5cm;
        margin-top: 1.5cm;
        margin-bottom: 1.5cm;
    }}
    @page :first {{
        margin-top: 0;
    }}
    body {{
        font-family: -apple-system, "PingFang SC", "Noto Sans SC", "Microsoft YaHei",
                     "Helvetica Neue", Arial, sans-serif;
        font-size: 11pt;
        line-height: 1.7;
        color: #1a1a1a;
        max-width: 210mm;
        margin: 0 auto;
        padding: 2cm 0;
    }}
    h1 {{
        font-size: 24pt;
        color: #1a1a2e;
        border-bottom: 3px solid #4a90d9;
        padding-bottom: 12px;
        margin-top: 40px;
        page-break-before: always;
    }}
    h1:first-of-type {{
        page-break-before: avoid;
        font-size: 28pt;
        text-align: center;
        border-bottom: none;
        margin-top: 60px;
    }}
    h2 {{
        font-size: 16pt;
        color: #2c3e6b;
        border-bottom: 1px solid #ddd;
        padding-bottom: 6px;
        margin-top: 30px;
    }}
    h3 {{
        font-size: 13pt;
        color: #34495e;
        margin-top: 20px;
    }}
    h4 {{
        font-size: 11pt;
        color: #555;
        margin-top: 16px;
    }}
    p {{
        text-align: justify;
        margin: 8px 0;
    }}
    blockquote {{
        border-left: 4px solid #4a90d9;
        margin: 16px 0;
        padding: 8px 16px;
        background: #f8f9fa;
        color: #555;
        font-style: italic;
    }}
    blockquote p {{
        margin: 4px 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 10pt;
    }}
    th {{
        background: #4a90d9;
        color: white;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
    }}
    td {{
        padding: 8px 12px;
        border-bottom: 1px solid #e0e0e0;
    }}
    tr:nth-child(even) td {{
        background: #f8f9fa;
    }}
    code {{
        font-family: "SF Mono", "Fira Code", "Cascadia Code", Menlo, monospace;
        font-size: 9.5pt;
        background: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        color: #d63384;
    }}
    pre {{
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.5;
        margin: 12px 0;
    }}
    pre code {{
        background: none;
        color: inherit;
        padding: 0;
    }}
    .highlight pre {{
        background: #1e1e2e;
    }}
    .mermaid {{
        text-align: center;
        margin: 20px 0;
        padding: 16px;
        background: #fafbfc;
        border: 1px solid #e8e8e8;
        border-radius: 6px;
    }}
    .mermaid svg {{
        max-width: 100%;
    }}
    hr {{
        border: none;
        border-top: 2px solid #e0e0e0;
        margin: 30px 0;
    }}
    ul, ol {{
        padding-left: 24px;
    }}
    li {{
        margin: 4px 0;
    }}
    a {{
        color: #4a90d9;
        text-decoration: none;
    }}
    /* Cover page subtitle */
    h1:first-of-type + p {{
        text-align: center;
        font-size: 14pt;
        color: #555;
    }}
    h1:first-of-type + p + blockquote {{
        text-align: center;
        border: none;
        background: none;
        font-size: 10pt;
    }}
    /* Table of contents */
    #table-of-contents + ol,
    #目录 + ol {{
        column-count: 2;
        font-size: 10pt;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    return html


def html_to_pdf_chrome(html_path: Path, pdf_path: Path):
    """Use Chrome headless to render HTML (with mermaid JS) to PDF."""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "google-chrome",
        "chromium",
    ]

    chrome = None
    for p in chrome_paths:
        try:
            subprocess.run([p, "--version"], capture_output=True, check=True)
            chrome = p
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    if not chrome:
        print("Error: No Chrome/Chromium found", file=sys.stderr)
        sys.exit(1)

    print(f"Using: {chrome}")
    print(f"Rendering: {html_path} → {pdf_path}")

    result = subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=15000",
            f"--print-to-pdf={pdf_path}",
            "--no-pdf-header-footer",
            str(html_path.resolve().as_uri()),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        print(f"PDF generated: {pdf_path} ({pdf_path.stat().st_size / 1024:.0f} KB)")
    else:
        print(f"Error: PDF generation failed", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(1)


def main():
    docs_dir = Path(__file__).parent
    md_path = docs_dir / "astra-studio-whitepaper.md"
    html_path = docs_dir / "astra-studio-whitepaper.html"
    pdf_path = docs_dir / "astra-studio-whitepaper.pdf"

    if not md_path.exists():
        print(f"Error: {md_path} not found", file=sys.stderr)
        sys.exit(1)

    print("Step 1: Converting Markdown → HTML...")
    html = md_to_html(md_path)
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML written: {html_path}")

    print("Step 2: Rendering HTML → PDF (with mermaid)...")
    html_to_pdf_chrome(html_path, pdf_path)

    # Clean up HTML
    html_path.unlink()
    print("Done.")


if __name__ == "__main__":
    main()
