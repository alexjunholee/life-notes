#!/usr/bin/env python3
"""Build ``guide.html`` from the 24 canonical Markdown chapters.

The existing guide shell (styles, navigation, and the About block) lives in
``guide.template.html``.  Run once with ``--bootstrap-template`` when adopting
an older guide that still contains embedded chapter Markdown; normal builds
then depend only on that template and the chapter sources.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "guide.template.html"
OUTPUT = ROOT / "guide.html"
PLACEHOLDER = "{{MD_KO}}"
TEXTAREA_RE = re.compile(
    r'(<textarea id="md-source-ko"[^>]*>\n?)(.*?)(\n?</textarea>)', re.DOTALL
)


def chapter_files() -> list[Path]:
    files = sorted(ROOT.glob("chapter_*.md"))
    if len(files) != 24:
        raise RuntimeError(f"expected 24 chapters, found {len(files)}")
    return files


def escape_textarea(text: str) -> str:
    return text.replace("</textarea>", "&lt;/textarea&gt;")


def bootstrap_template() -> None:
    if TEMPLATE.exists():
        raise RuntimeError(f"template already exists: {TEMPLATE}")
    shell = OUTPUT.read_text(encoding="utf-8")
    match = TEXTAREA_RE.search(shell)
    if not match:
        raise RuntimeError("Korean Markdown textarea not found in guide.html")
    first_chapter = re.search(r"(?m)^#\s+Ch\.?\s*1\b", match.group(2))
    if not first_chapter:
        raise RuntimeError("first chapter heading not found in embedded Markdown")
    about = match.group(2)[: first_chapter.start()]
    replacement = match.group(1) + about + PLACEHOLDER + match.group(3)
    template = shell[: match.start()] + replacement + shell[match.end() :]
    TEMPLATE.write_text(template, encoding="utf-8")
    print(f"Bootstrapped {TEMPLATE}")


def build() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count(PLACEHOLDER) != 1:
        raise RuntimeError(f"template must contain exactly one {PLACEHOLDER}")
    chapters = [path.read_text(encoding="utf-8").rstrip() for path in chapter_files()]
    markdown = "\n\n".join(chapters) + "\n"
    html = template.replace(PLACEHOLDER, escape_textarea(markdown))
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built {OUTPUT}")
    print(f"  chapters: {len(chapters)}")
    print(f"  Markdown: {len(markdown):,} chars")
    print(f"  HTML: {len(html):,} chars")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap-template", action="store_true")
    args = parser.parse_args()
    if args.bootstrap_template:
        bootstrap_template()
    build()


if __name__ == "__main__":
    main()
