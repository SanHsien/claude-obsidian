#!/usr/bin/env python3
"""檢查本 fork overlay 文件之間的相對連結。

只驗 overlay 文件：AGENTS.md、FORK.md、NOTICE.md、REVIEW.md、ROADMAP.md、
SECURITY.md、CONTRIBUTING.md、CODE_OF_CONDUCT.md、docs/fork/、
以及已加 overlay 的 GitHub 模板與宿主指示（copilot／cursor／windsurf／ZCODE.md）。
以 markdown-it-py（CommonMark + GFM 表格）解析；
程式碼區塊與 inline code 裡的連結語法是範例，不檢查。
不掃根目錄 README.md：那是上游英文產品契約，由產品 CI 負責。
不掃 CLAUDE.md：本產品 checkout 依契約不得有該檔。

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.token import Token

ROOT = Path(__file__).resolve().parent.parent
HTML_SRC_PATTERN = re.compile(r"""(?is)<img[^>]+src=["']([^"']+)["']""")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
SKIP_NAMES = {
    "upstream-review-report.md",
    "dependency-freshness-report.md",
}

FORK_DOCUMENTS = [
    ROOT / "AGENTS.md",
    ROOT / "FORK.md",
    ROOT / "NOTICE.md",
    ROOT / "REVIEW.md",
    ROOT / "ROADMAP.md",
    ROOT / "SECURITY.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "ZCODE.md",
    ROOT / ".cursor" / "rules" / "claude-obsidian.mdc",
    ROOT / ".windsurf" / "rules" / "claude-obsidian.md",
]


# Read Markdown with a real CommonMark + GFM table parser, the way GitHub
# renders it. Hand-written regexes for code spans and fences kept hiding real
# links (HTML blocks, tables, list items opening with a heading, tabs after ">"),
# so the parser decides what is code; links quoted in code are never tokens.
MARKDOWN = MarkdownIt("commonmark", {"html": True}).enable("table")
FENCE_CLOSE = re.compile(r"[ \t>]*(?P<fence>`{3,}|~{3,})[ \t]*$")


def _walk(tokens: list[Token]) -> Iterator[Token]:
    for token in tokens:
        yield token
        if token.children:
            yield from _walk(token.children)


def _fence_is_closed(token: Token, lines: list[str]) -> bool:
    """A closed fence's source range ends on its closing line."""
    start, end = token.map or (0, 0)
    if end - start < 2 or end > len(lines):
        return False
    closer = FENCE_CLOSE.match(lines[end - 1])
    return bool(
        closer
        and closer.group("fence")[0] == token.markup[0]
        and len(closer.group("fence")) >= len(token.markup)
    )


def extract_targets(text: str) -> tuple[list[tuple[str, bool]], int | None]:
    """Return the link targets of a document and the line of an unclosed fence.

    Each target is (destination, is_markdown): Markdown links and images carry a
    parsed destination (titles already removed), an HTML <img src> is the raw
    attribute. CommonMark runs an unclosed fence to the end of its container and
    hides every link after it; that is almost always a typo, so the caller
    reports it instead of passing silently.
    """
    lines = text.splitlines()
    targets: list[tuple[str, bool]] = []
    unclosed: int | None = None
    for token in _walk(MARKDOWN.parse(text)):
        if token.type == "link_open":
            targets.append((str(token.attrGet("href") or ""), True))
        elif token.type == "image":
            targets.append((str(token.attrGet("src") or ""), True))
        elif token.type in ("html_block", "html_inline"):
            targets.extend(
                (match.group(1), False)
                for match in HTML_SRC_PATTERN.finditer(token.content)
            )
        elif (
            token.type == "fence"
            and unclosed is None
            and not _fence_is_closed(token, lines)
        ):
            unclosed = (token.map or (0, 0))[0] + 1
    return targets, unclosed


def iter_documents() -> list[Path]:
    documents = [path for path in FORK_DOCUMENTS if path.is_file()]
    fork_docs = ROOT / "docs" / "fork"
    if fork_docs.is_dir():
        documents.extend(sorted(fork_docs.glob("*.md")))
    github = ROOT / ".github"
    documents.extend(
        [
            github / "copilot-instructions.md",
            github / "pull_request_template.md",
            github / "ISSUE_TEMPLATE" / "bug_report.md",
            github / "ISSUE_TEMPLATE" / "feature_request.md",
        ]
    )
    return [
        path
        for path in documents
        if path.is_file() and path.name not in SKIP_NAMES
    ]


def _missing_relative(path: Path, target: str, *, has_title: bool = True) -> str | None:
    # A quoted HTML `src` (has_title=False) is the whole destination: a space in
    # it is part of the filename, not the start of a title.
    target = target.strip()
    if has_title and target.startswith("<"):
        # `<a path with spaces.md> "optional title"`
        target = target[1:].split(">", 1)[0].strip()
    elif has_title and target:
        # `path.md "optional title"`: the title is not part of the destination.
        target = target.split(None, 1)[0]
    if not target or target.startswith(SKIP_PREFIXES):
        return None
    file_part = unquote(target.split("#", 1)[0])
    if not file_part:
        return None
    # GitHub resolves a leading "/" from the repo root, not from the file.
    base = ROOT if file_part.startswith("/") else path.parent
    resolved = (base / file_part.lstrip("/")).resolve()
    if not resolved.is_relative_to(ROOT):
        return f"{target} → 逃出 repo 根目錄"
    if resolved.exists():
        return None
    try:
        shown = resolved.relative_to(ROOT)
    except ValueError:
        shown = resolved
    return f"{target} → 找不到 {shown}"


def check_document(path: Path) -> list[str]:
    problems: list[str] = []
    found, unclosed = extract_targets(path.read_text(encoding="utf-8"))
    if unclosed is not None:
        problems.append(f"第 {unclosed} 行的 code fence 沒有收尾，之後的連結都不會被檢查")
    # The same target linked twice is one problem.
    targets = dict.fromkeys(found)
    for target, has_title in targets:
        missing = _missing_relative(path, target, has_title=has_title)
        if missing:
            problems.append(missing)
    return problems


def main() -> int:
    documents = iter_documents()
    if not documents:
        print("找不到任何 fork overlay Markdown 檔")
        return 1

    failures = 0
    for path in documents:
        problems = check_document(path)
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            for problem in problems:
                print(f"FAIL {rel}: {problem}")
        else:
            print(f"OK   {rel}")

    print(f"\n共 {len(documents)} 份 overlay 文件，{failures} 份有缺檔。")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
