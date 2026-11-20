#!/usr/bin/env python3
"""檢查本 fork overlay 文件之間的相對連結。

只驗 overlay 文件：AGENTS.md、FORK.md、NOTICE.md、REVIEW.md、ROADMAP.md、
SECURITY.md、CONTRIBUTING.md、CODE_OF_CONDUCT.md、docs/fork/、
以及已加 overlay 的 GitHub 模板與宿主指示（copilot／cursor／windsurf／ZCODE.md）。
程式碼區塊與 inline code 裡的連結語法是範例，不檢查。
不掃根目錄 README.md：那是上游英文產品契約，由產品 CI 負責。
不掃 CLAUDE.md：本產品 checkout 依契約不得有該檔。

    python tools/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_PATTERN = re.compile(r"""(?is)<img[^>]+src=["']([^"']+)["']""")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")
SKIP_NAMES = {
    "upstream-review-report.md",
    "dependency-freshness-report.md",
}

# CommonMark: a fence is 3+ backticks or tildes; a backtick fence's info string
# cannot contain a backtick (so "```x``` text" is inline code, not a fence), and
# the closing run uses the same character and is at least as long.
FENCE_PATTERN = re.compile(
    r"(?ms)^[ ]{0,3}(?P<fence>`{3,}(?=[^`\n]*$)|~{3,})[^\n]*\n"
    r".*?"
    r"^[ ]{0,3}(?P=fence)[`~]*[ \t]*$"
)
# A code span opens and closes with backtick runs of equal length and never
# crosses a blank line, so a stray backtick cannot swallow a later paragraph.
INLINE_CODE_PATTERN = re.compile(
    r"(?<!`)(?P<run>`+)(?!`)(?:(?!\n[ \t]*\n)[\s\S])*?(?<!`)(?P=run)(?!`)"
)

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


def _strip_code(text: str) -> str:
    """Link syntax quoted in a fence or code span is an example, not a link."""
    return INLINE_CODE_PATTERN.sub("", FENCE_PATTERN.sub("", text))


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
    text = _strip_code(path.read_text(encoding="utf-8"))
    # `![a](b)` also contains the link `[a](b)`; report each target once.
    targets = dict.fromkeys(
        (match.group(1), pattern is not HTML_SRC_PATTERN)
        for pattern in (LINK_PATTERN, IMAGE_PATTERN, HTML_SRC_PATTERN)
        for match in pattern.finditer(text)
    )
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
