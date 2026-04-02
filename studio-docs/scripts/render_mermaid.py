#!/usr/bin/env python3
"""
Render Mermaid code blocks in a Markdown file to PNG images.

Extracts all ```mermaid code blocks, renders each to PNG using mmdc (mermaid-cli),
and returns a modified markdown with mermaid blocks replaced by image references.

Requirements:
  - Node.js and @mermaid-js/mermaid-cli (`npm install -g @mermaid-js/mermaid-cli`)
  - Chrome or Chromium (auto-detected on macOS/Linux)

Usage:
  python3 render_mermaid.py input.md [--output modified.md] [--img-dir ./images] [--base64]
"""

import argparse
import base64
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MERMAID_BLOCK_RE = re.compile(
    r"(<!-- figure:\s*(.+?)\s*-->\s*\n)?"  # optional figure caption comment
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL,
)

CHROME_PATHS_MACOS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

CHROME_PATHS_LINUX = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]


def find_chrome() -> str | None:
    """Auto-detect Chrome/Chromium executable path."""
    system = platform.system()
    if system == "Darwin":
        candidates = CHROME_PATHS_MACOS
    elif system == "Linux":
        candidates = CHROME_PATHS_LINUX
    else:
        candidates = []

    for path in candidates:
        if os.path.isfile(path):
            return path

    # Fallback: try common command names in PATH
    for cmd in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(cmd)
        if found:
            return found

    return None


def find_mmdc() -> str:
    """Find the mmdc (mermaid-cli) executable."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        return mmdc

    # Check common npx/node_modules locations
    for candidate in ("./node_modules/.bin/mmdc", "../node_modules/.bin/mmdc"):
        if os.path.isfile(candidate):
            return os.path.abspath(candidate)

    print(
        "Error: mmdc (mermaid-cli) not found.\n"
        "Install it with: npm install -g @mermaid-js/mermaid-cli",
        file=sys.stderr,
    )
    sys.exit(1)


def render_mermaid_block(
    mermaid_code: str,
    output_path: Path,
    mmdc_path: str,
    chrome_path: str | None,
) -> bool:
    """Render a single mermaid code block to PNG."""
    # Write mermaid code to a temporary .mmd file
    mmd_file = output_path.with_suffix(".mmd")
    try:
        mmd_file.write_text(mermaid_code, encoding="utf-8")

        cmd = [
            mmdc_path,
            "-i", str(mmd_file),
            "-o", str(output_path),
            "-b", "white",
            "-s", "2",  # scale factor for higher DPI
        ]
        if chrome_path:
            cmd.extend(["-p", _puppeteer_config(chrome_path)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"Warning: mmdc failed for {output_path.name}:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False
        return output_path.exists()
    except subprocess.TimeoutExpired:
        print(f"Warning: mmdc timed out for {output_path.name}", file=sys.stderr)
        return False
    finally:
        if mmd_file.exists():
            mmd_file.unlink()


def _puppeteer_config(chrome_path: str) -> str:
    """Create a temporary puppeteer config file with the Chrome path."""
    config_path = os.path.join(os.path.dirname(__file__), ".puppeteer-config.json")
    import json
    config = {"executablePath": chrome_path}
    with open(config_path, "w") as f:
        json.dump(config, f)
    return config_path


def image_to_base64(image_path: Path) -> str:
    """Convert an image file to a base64 data URI."""
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def process_markdown(
    input_path: Path,
    output_path: Path,
    img_dir: Path,
    use_base64: bool,
    mmdc_path: str,
    chrome_path: str | None,
) -> int:
    """Process a markdown file, rendering all mermaid blocks."""
    content = input_path.read_text(encoding="utf-8")

    img_dir.mkdir(parents=True, exist_ok=True)

    rendered_count = 0
    figure_index = 0

    def replace_block(match: re.Match) -> str:
        nonlocal rendered_count, figure_index
        figure_index += 1

        caption_block = match.group(1) or ""
        caption_text = match.group(2) or f"figure-{figure_index}"
        mermaid_code = match.group(3)

        # Generate a safe filename from caption
        safe_name = re.sub(r"[^\w\u4e00-\u9fff-]", "_", caption_text).strip("_")
        if not safe_name:
            safe_name = f"mermaid_{figure_index}"
        img_filename = f"{safe_name}.png"
        img_path = img_dir / img_filename

        success = render_mermaid_block(mermaid_code, img_path, mmdc_path, chrome_path)

        if not success:
            # Keep original block if rendering fails
            return match.group(0)

        rendered_count += 1

        if use_base64:
            img_ref = image_to_base64(img_path)
        else:
            img_ref = os.path.relpath(img_path, output_path.parent)

        replacement = f"![{caption_text}]({img_ref})"
        if caption_block:
            replacement += f"\n\n<p align=\"center\"><em>{caption_text}</em></p>"

        return replacement

    new_content = MERMAID_BLOCK_RE.sub(replace_block, content)

    output_path.write_text(new_content, encoding="utf-8")
    return rendered_count


def main():
    parser = argparse.ArgumentParser(
        description="Render Mermaid code blocks in Markdown to PNG images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 render_mermaid.py input.md\n"
            "  python3 render_mermaid.py input.md --output modified.md --img-dir ./images\n"
            "  python3 render_mermaid.py input.md --base64\n"
        ),
    )
    parser.add_argument("input", type=Path, help="Input markdown file path")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output markdown file path (default: overwrite input)",
    )
    parser.add_argument(
        "--img-dir",
        type=Path,
        default=None,
        help="Directory for rendered images (default: ./images next to input)",
    )
    parser.add_argument(
        "--base64",
        action="store_true",
        help="Embed images as base64 data URIs instead of file references",
    )

    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or args.input
    img_dir = args.img_dir or (args.input.parent / "images")

    # Locate dependencies
    mmdc_path = find_mmdc()
    chrome_path = find_chrome()
    if not chrome_path:
        print(
            "Warning: Chrome/Chromium not found. mmdc may fail or use its own bundled browser.",
            file=sys.stderr,
        )

    print(f"Processing: {args.input}")
    print(f"Output:     {output_path}")
    print(f"Images:     {img_dir}")
    if chrome_path:
        print(f"Chrome:     {chrome_path}")
    print()

    count = process_markdown(
        args.input, output_path, img_dir, args.base64, mmdc_path, chrome_path
    )

    print(f"Done. Rendered {count} Mermaid diagram(s).")

    # Clean up puppeteer config if created
    config_path = os.path.join(os.path.dirname(__file__), ".puppeteer-config.json")
    if os.path.exists(config_path):
        os.unlink(config_path)


if __name__ == "__main__":
    main()
