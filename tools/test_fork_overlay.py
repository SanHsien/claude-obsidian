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
    assert baseline["reviewed_date"] == "2026-08-28"
    assert baseline["reviewed_pr_through"] == 180
    assert baseline["reviewed_issue_through"] == 181


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


def test_render_markdown_surfaces_check_failure() -> None:
    baseline = {
        "repo": "https://example.invalid/upstream.git",
        "branch": "main",
        "reviewed_through": "a" * 40,
        "reviewed_date": "2026-08-28",
    }

    report = checker.render_markdown(baseline, [], error="git fetch failed")

    assert "Check failed" in report
    assert "git fetch failed" in report
    assert "docs/fork/DECISIONS.md" in checker.render_markdown(baseline, [{"sha": "b" * 40, "short": "bbbbbbb", "date": "2026-08-28", "subject": "x", "files": ["a.py"]}])


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
    assert "Build an Obsidian knowledge base" in readme
    assert "python3 scripts/claude-obsidian.py init" in readme
    assert "--approved-plan-sha256" in readme


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
