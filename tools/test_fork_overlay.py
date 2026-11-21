from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_links  # noqa: E402
import check_upstream_updates as checker  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_REPO = "AgriciDaniel/claude-obsidian"
FORK_OWNED_WORKFLOWS = {
    "fork-maintenance.yml",
    "upstream-check.yml",
    "codeql.yml",
    "dependency-freshness.yml",
}
PRODUCT_WORKFLOWS = ("test.yml",)


def test_baseline_file_is_valid_and_complete() -> None:
    baseline = checker.load_baseline()

    assert baseline["repo"].endswith("claude-obsidian.git")
    assert baseline["branch"] == "main"
    assert len(baseline["reviewed_through"]) == 40
    # Pinned as a shape, not as a literal. A hardcoded date turns every
    # legitimate upstream review into a test failure, and the pressure is then
    # to edit the test rather than to record the review.
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", baseline["reviewed_date"])
    # Same reasoning: the property is that all four upstream axes carry a
    # number, not what last week's number happened to be. Zero is legitimate --
    # it means the axis was queried and was empty -- so presence and type are
    # what get pinned.
    assert isinstance(baseline["reviewed_pr_through"], int)
    assert isinstance(baseline["reviewed_issue_through"], int)


def test_workflow_is_scheduled_and_fails_on_unreviewed_commits() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "upstream-check.yml"
    ).read_text(encoding="utf-8")

    assert "schedule:" in workflow
    assert "cron:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "tools/check_upstream_updates.py" in workflow
    assert "fetch-depth: 0" in workflow
    assert "exit 1" in workflow


def test_render_markdown_reports_no_new_commits() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-28",
    }

    report = checker.render_markdown(baseline, [])

    assert "No new upstream commits" in report


def test_load_baseline_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(checker.UpstreamCheckError):
        checker.load_baseline(tmp_path / "nope.json")


def test_baseline_matches_decisions_record() -> None:
    decisions = (ROOT / "docs" / "fork" / "DECISIONS.md").read_text(encoding="utf-8")
    upstream = (ROOT / "docs" / "fork" / "UPSTREAM.md").read_text(encoding="utf-8")
    baseline = json.loads(
        (ROOT / "tools" / "upstream_baseline.json").read_text(encoding="utf-8")
    )

    assert baseline["reviewed_date"] in decisions
    assert baseline["reviewed_through"][:7] in upstream
    assert "ad67087" in upstream


def test_overlay_markdown_links_resolve() -> None:
    failures = 0
    for path in check_links.iter_documents():
        problems = check_links.check_document(path)
        failures += len(problems)
        for problem in problems:
            print(f"{path}: {problem}")
    assert failures == 0


def test_readme_keeps_upstream_english_product_contract() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert not (ROOT / "README.en.md").exists()
    assert "SanHsien 維護型 fork" in readme
    assert "SanHsien/claude-obsidian" in readme
    assert UPSTREAM_REPO in readme
    assert "FORK.md" in readme
    assert "REVIEW.md" in readme
    assert "docs/windows-wsl.md" in readme
    assert "Your AI second brain for" in readme
    assert "## Install" in readme
    assert "## FAQ" in readme


def test_link_checker_skips_product_readme_and_scans_review() -> None:
    rels = {path.relative_to(ROOT).as_posix() for path in check_links.iter_documents()}

    assert "README.md" not in rels
    assert "REVIEW.md" in rels
    assert "FORK.md" in rels
    assert "NOTICE.md" in rels
    assert "SECURITY.md" in rels
    assert "CONTRIBUTING.md" in rels
    assert "docs/fork/DECISIONS.md" in rels
    assert "docs/fork/DEVELOPMENT.md" in rels
    assert ".github/ISSUE_TEMPLATE/bug_report.md" in rels


def test_link_checker_scans_every_file_that_carries_overlay_links() -> None:
    """AGENTS.md is the only host file left with overlay links once GEMINI.md
    was folded into it, and ROADMAP.md is fork-owned; neither was scanned, so a
    renamed FORK.md or docs/fork file would break them silently. Host adapter
    files are discovered, so a new upstream adapter is covered automatically."""
    rels = {path.relative_to(ROOT).as_posix() for path in check_links.iter_documents()}
    host_files = {
        path.relative_to(ROOT).as_posix() for path in _host_instruction_files()
    }

    missing = ({"AGENTS.md", "ROADMAP.md"} | host_files) - rels
    assert not missing, missing


def test_code_is_not_a_link(tmp_path: Path, monkeypatch) -> None:
    """Link syntax quoted in a code span or fence is an example, not a link.
    ROADMAP.md quotes `<img src="a b.png">` and was reported as missing `a`."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(
        'Quote `<img src="a b.png">` and `[x](gone.md)` inline.\n'
        "\n"
        "```markdown\n"
        "[y](also-gone.md)\n"
        "```\n",
        encoding="utf-8",
    )

    assert check_links.check_document(doc) == []


def test_html_src_with_a_space_is_one_target(tmp_path: Path, monkeypatch) -> None:
    """A quoted `src` attribute has no title part; splitting it on whitespace
    reported `a` missing when the real file `a b.png` exists."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    (tmp_path / "a b.png").write_bytes(b"")
    doc = tmp_path / "doc.md"
    doc.write_text('<img src="a b.png">\n<img src="gone b.png">\n', encoding="utf-8")

    problems = check_links.check_document(doc)

    assert len(problems) == 1
    assert "gone b.png" in problems[0]


def test_missing_relative_rejects_path_escape() -> None:
    problem = check_links._missing_relative(ROOT / "FORK.md", "../outside-the-repo")

    assert problem is not None
    assert "逃出 repo 根目錄" in problem
    assert check_links._missing_relative(ROOT / "FORK.md", "NOTICE.md") is None


def test_host_only_claude_md_is_absent_in_this_checkout() -> None:
    assert not (ROOT / "CLAUDE.md").exists()
    marketplace = ROOT / ".claude-plugin" / "marketplace.json"
    assert marketplace.is_file()


def test_product_ci_is_not_gated_to_upstream_only() -> None:
    workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")

    assert "windows-smoke" in workflow
    assert "make test" in workflow
    assert f"github.repository == '{UPSTREAM_REPO}'" not in workflow


def test_plugin_manifest_still_points_upstream() -> None:
    plugin = json.loads(
        (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )

    assert plugin["homepage"] == f"https://github.com/{UPSTREAM_REPO}"
    assert plugin["repository"] == f"https://github.com/{UPSTREAM_REPO}"
    assert plugin["name"] == "claude-obsidian"


def test_funding_is_not_rewired_to_the_fork() -> None:
    funding = (ROOT / ".github" / "FUNDING.yml").read_text(encoding="utf-8")

    assert "skool.com/ai-marketing-hub-pro" in funding
    assert "SanHsien" not in funding


def test_gitattributes_remain_byte_exact() -> None:
    attrs = (ROOT / ".gitattributes").read_text(encoding="utf-8")

    assert "* -text" in attrs
    assert "text=auto eol=lf" not in attrs


def test_issue_contact_links_point_at_this_fork() -> None:
    text = (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(
        encoding="utf-8"
    )
    assert "SanHsien/claude-obsidian/blob/main/CONTRIBUTING.md" in text
    assert "AgriciDaniel/claude-obsidian/blob/main/CONTRIBUTING.md" in text


def test_fork_owned_workflows_exist() -> None:
    workflows = ROOT / ".github" / "workflows"
    for name in FORK_OWNED_WORKFLOWS | set(PRODUCT_WORKFLOWS):
        assert (workflows / name).is_file(), name


def test_tool_config_matches_ci_flags() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "fork-maintenance.yml").read_text(
        encoding="utf-8"
    )
    assert 'target-version = "py311"' in pyproject
    assert "--target-version py311" in ci
    assert 'select = ["E9", "F"]' in pyproject
    assert "--select E9,F" in ci
    assert 'testpaths = ["tools"]' in pyproject
    assert not re.search(r"^\[project\]", pyproject, re.M)
    assert not re.search(r"^\[build-system\]", pyproject, re.M)


def test_gitignore_covers_overlay_reports() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert ".venv/" in text
    assert "upstream-review-report.md" in text
    assert "dependency-freshness-report.md" in text
    assert "/wiki/" in text.splitlines()
    assert "/inbox/" in text.splitlines()
    assert "/.raw/" in text.splitlines()


def test_codeowners_points_at_this_fork() -> None:
    text = (ROOT / "CODEOWNERS").read_text(encoding="utf-8")
    assert "* @SanHsien" in text
    assert "@AgriciDaniel" not in text


def test_issue_templates_redirect_product_work_upstream() -> None:
    bug = (ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").read_text(
        encoding="utf-8"
    )
    feature = (
        ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.md"
    ).read_text(encoding="utf-8")
    for text in (bug, feature):
        assert "AgriciDaniel/claude-obsidian" in text
        assert "FORK.md" in text
        assert "overlay" in text


def test_release_allowlist_excludes_fork_docs() -> None:
    allowlist = json.loads(
        (ROOT / "config" / "release-allowlist.json").read_text(encoding="utf-8")
    )
    excluded = set(allowlist["exclude_globs"])
    assert allowlist["exclude_globs"] == sorted(allowlist["exclude_globs"])
    assert "docs/fork/**" in excluded
    for name in (
        ".github/dependabot.yml",
        ".github/workflows/codeql.yml",
        ".github/workflows/dependency-freshness.yml",
        ".github/workflows/fork-maintenance.yml",
        ".github/workflows/upstream-check.yml",
        ".cursor/rules/no-upstream-pr.mdc",
    ):
        assert name in excluded


# Tracked files that mention AGENTS.md without being a host entry point. This
# list fails closed: a new file that mentions AGENTS.md is treated as a host
# file (and must carry the overlay) until someone decides it is not one here.
NOT_HOST_FILES = {
    ".github/workflows/fork-maintenance.yml",  # runs the gate, not read by a host
    "CHANGELOG.md",
    "FORK.md",  # the overlay itself
    "README.md",  # product landing page; overlay checked by its own test
    "RELEASE_MANIFEST.json",
    "REVIEW.md",
    "SHA256SUMS",
    "config/product-contract.json",
    "config/release-allowlist.json",
}


def _host_instruction_files(root: Path = ROOT) -> list[Path]:
    """Every tracked file that points a host at `AGENTS.md` is a host entry point.

    Discovered from content, not listed by hand: upstream adds and renames host
    adapters (GEMINI.md went away, ZCODE.md arrived) and a hand-kept list
    silently stopped covering the new one. Any mention counts, not one wording
    ("Read `AGENTS.md`", "Follow AGENTS.md", ...); known non-hosts are exempted.
    """
    result = subprocess.run(
        [
            "git", "grep", "-l", "-I", "--fixed-strings", "AGENTS.md",
            # Overlay tooling and fork docs quote the name; they are not hosts.
            "--", ".", ":!tools", ":!docs/fork",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    # git grep exits 1 for "no match"; anything else means the search failed.
    assert result.returncode in (0, 1), result.stderr
    return [
        root / line
        for line in result.stdout.splitlines()
        if line and line not in NOT_HOST_FILES
    ]


def test_host_instruction_files_have_fork_overlay() -> None:
    files = _host_instruction_files()
    found = {path.relative_to(ROOT).as_posix() for path in files}
    # Guard the discovery itself: if it finds nothing, the loop below proves nothing.
    assert {
        ".github/copilot-instructions.md",
        ".cursor/rules/claude-obsidian.mdc",
        ".windsurf/rules/claude-obsidian.md",
        "ZCODE.md",
    } <= found, found
    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "SanHsien" in text, path
        assert "FORK.md" in text, path
        assert "AgriciDaniel/claude-obsidian" in text, path


def test_review_is_windows_first_record() -> None:
    review = (ROOT / "REVIEW.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Windows-first" in review
    assert "R-01" in review
    assert "FORK.md" in agents
    assert "`REVIEW.md`" in (ROOT / "FORK.md").read_text(encoding="utf-8")


def test_tracked_files_are_not_git_symlinks() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    symlinks = [
        line.split("\t", 1)[-1]
        for line in result.stdout.splitlines()
        if line.startswith("120000 ")
    ]
    assert symlinks == [], f"git symlink 會讓 Windows checkout 失敗: {symlinks}"


def test_overlay_python_is_not_in_release_roots() -> None:
    allowlist = json.loads(
        (ROOT / "config" / "release-allowlist.json").read_text(encoding="utf-8")
    )

    assert "tools" not in allowlist["include_roots"]
    assert "FORK.md" not in allowlist["include_files"]
    assert "NOTICE.md" not in allowlist["include_files"]
    assert "REVIEW.md" not in allowlist["include_files"]


def test_link_title_is_not_part_of_the_target() -> None:
    """`[x](NOTICE.md "title")` is a valid link; the title is not a filename."""
    assert check_links._missing_relative(ROOT / "FORK.md", 'NOTICE.md "the notice"') is None
    assert check_links._missing_relative(ROOT / "FORK.md", "NOTICE.md 'the notice'") is None
    assert check_links._missing_relative(ROOT / "FORK.md", "<NOTICE.md> \"t\"") is None


def test_repo_root_relative_link_resolves_against_the_repo_root() -> None:
    """GitHub renders `/docs/fork/DECISIONS.md` from the repo root; joining it
    onto the document directory sends it to the drive root instead."""
    assert check_links._missing_relative(
        ROOT / "docs" / "fork" / "UPSTREAM.md", "/docs/fork/DECISIONS.md"
    ) is None
    problem = check_links._missing_relative(ROOT / "FORK.md", "/no-such-file.md")
    assert problem is not None
    assert "找不到" in problem


def test_an_image_link_is_reported_once(tmp_path: Path, monkeypatch) -> None:
    """IMAGE_PATTERN also matches inside LINK_PATTERN, so `![a](gone.png)` was
    reported twice and inflated the problem count."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text("![a](gone.png) [b](gone.md)\n", encoding="utf-8")

    problems = check_links.check_document(doc)

    assert len(problems) == 2
    assert len(set(problems)) == 2


def test_inline_code_does_not_cross_a_blank_line(tmp_path: Path, monkeypatch) -> None:
    """A lone backtick must not pair with one in a later paragraph: CommonMark
    code spans never span a blank line, and the link between them is real."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(
        "A stray ` backtick.\n\n[real](gone.md)\n\nAnother ` backtick.\n",
        encoding="utf-8",
    )

    problems = check_links.check_document(doc)

    assert len(problems) == 1
    assert "gone.md" in problems[0]


def test_inline_code_needs_equal_backtick_runs(tmp_path: Path, monkeypatch) -> None:
    """`` opens a span that only `` closes; a single ` inside does not end it,
    and a run of a different length does not close it."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(
        "``a ` [x](quoted.md) b`` then [y](gone.md) and ``` lone\n",
        encoding="utf-8",
    )

    problems = check_links.check_document(doc)

    assert len(problems) == 1
    assert "gone.md" in problems[0]


def test_backtick_line_with_backticks_in_info_is_not_a_fence(
    tmp_path: Path, monkeypatch
) -> None:
    """A backtick fence's info string cannot contain backticks, so a line like
    "```x``` inline" is inline code, not a fence that hides the rest of the file."""
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(
        "```x``` inline code\n\n[real](gone.md)\n\n```\n[y](fenced.md)\n```\n",
        encoding="utf-8",
    )

    problems = check_links.check_document(doc)

    assert len(problems) == 1
    assert "gone.md" in problems[0]


def _link_problems(tmp_path: Path, monkeypatch, text: str) -> list[str]:
    monkeypatch.setattr(check_links, "ROOT", tmp_path)
    doc = tmp_path / "doc.md"
    doc.write_text(text, encoding="utf-8")
    return check_links.check_document(doc)


# Each text renders [real](gone.md) as a real link in CommonMark (checked with
# markdown-it-py 4.2.0); a stray backtick or fence-like line must not hide it.
HIDDEN_LINK_CASES = {
    "code span crosses a blockquote paragraph break": (
        "> A stray ` backtick.\n>\n> [real](gone.md)\n>\n> Another ` backtick.\n"
    ),
    "escaped backtick opens a code span": (
        "An escaped \\` backtick, [real](gone.md), then `code`.\n"
    ),
    "code span crosses an ATX heading": "# A ` heading\n[real](gone.md) and ` here.\n",
    "indented backticks open a fence": "Para.\n\n    ```\n[real](gone.md)\n    ```\n",
    "fence outlives its list item": (
        "- Step:\n\n  ```sh\n  run\n\n[real](gone.md)\n\n  ```\n"
    ),
    "html block interrupts a paragraph": (
        "A stray ` tick.\n<pre>x</pre>\n[real](gone.md) and ` another.\n"
    ),
    "html comment interrupts a paragraph": (
        "A stray ` tick.\n<!-- note -->\n[real](gone.md) and ` another.\n"
    ),
    "list item opens with an ATX heading": (
        "- # A ` heading\n  [real](gone.md) and ` here.\n"
    ),
    "table cells split code spans": (
        "| a ` b | [real](gone.md) | c ` d |\n|---|---|---|\n"
    ),
    "five spaces after a list marker is indented code": (
        "-     ```\n  [real](gone.md)\n-     code ` x\n"
    ),
    "tab after a blockquote marker counts from line start": (
        ">\t```\n> ` x\n[real](gone.md)\n>\t` x\n"
    ),
}


@pytest.mark.parametrize("text", HIDDEN_LINK_CASES.values(), ids=HIDDEN_LINK_CASES.keys())
def test_code_detection_does_not_hide_a_real_link(
    tmp_path: Path, monkeypatch, text: str
) -> None:
    problems = _link_problems(tmp_path, monkeypatch, text)

    assert any("gone.md" in problem for problem in problems)


def test_unclosed_fence_fails_instead_of_hiding_the_rest(
    tmp_path: Path, monkeypatch
) -> None:
    """CommonMark runs an unclosed fence to the end of the file, hiding every
    later link; the gate reports the fence rather than passing silently."""
    problems = _link_problems(tmp_path, monkeypatch, "Intro.\n\n```\n[real](gone.md)\n")

    assert any("第 3 行" in problem and "fence" in problem for problem in problems)


def test_code_in_blockquotes_and_spans_is_still_not_a_link(
    tmp_path: Path, monkeypatch
) -> None:
    text = (
        "> ```\n> [x](fenced.md)\n>\n> ```\n\n"
        "Use `[y](span.md)` and ``a ` [z](z.md)``.\n"
    )

    assert _link_problems(tmp_path, monkeypatch, text) == []


def test_host_discovery_does_not_depend_on_one_wording(tmp_path: Path) -> None:
    """A new adapter worded "Follow AGENTS.md" is still a host entry point; the
    discovery must not hinge on the exact phrase upstream happened to use."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "NEWHOST.md").write_text("Follow AGENTS.md first.\n", encoding="utf-8")
    subprocess.run(["git", "add", "NEWHOST.md"], cwd=tmp_path, check=True)

    found = {path.name for path in _host_instruction_files(tmp_path)}

    assert "NEWHOST.md" in found
