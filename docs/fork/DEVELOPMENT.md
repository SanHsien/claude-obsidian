# 開發環境

維護者與 AI 接手用的開發文件。產品用法看 [`README.md`](../../README.md)；上游同步在 [`UPSTREAM.md`](UPSTREAM.md)；決策在 [`DECISIONS.md`](DECISIONS.md)。

## 架構

```text
Claude Code / Cursor / Codex / Gemini / 其他 Agent Skills 宿主
        │
        ▼
 skills/  agents/  hooks/  claude_obsidian/  scripts/  bin/
        │
        ├─ python scripts/claude-obsidian.py   可攜核心（標準庫）
        ├─ make test                             完整 hermetic 套件（POSIX）
        └─ 上游 .github/workflows/test.yml       Linux / macOS 全測 + Windows smoke
```

根目錄 `FORK.md`、`tools/`、`docs/fork/` 是本 fork 的開發與治理骨架。`skills/`、`claude_obsidian/`、`hooks/`、`scripts/`、`bin/` 以上游為準。

產品 checkout **不是**用戶 vault。vault 必須是含 `.claude-obsidian.json` 的獨立目錄。

## 本機開發（Windows）

需要 Python 3.11+（產品核心）與 PowerShell 7。fork gate 以 Python 3.14 為主。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PYTHONUTF8 = "1"
pwsh -NoProfile -File tools\dev_check.ps1
```

## Canonical gate

`tools\dev_check.ps1` 會依序：

1. `python -m compileall`（`tools`）
2. `ruff check`（E9 + F，僅 `tools`，`--target-version py311`）
3. `pytest tools -q`
4. `python tools/check_links.py`
5. 上游 windows-smoke 同等的 portable surface：
   `tests/test_package_validation.py`、`tests/test_knowledge_contracts.py`、
   `tests/test_contracts.py`、`tests/test_benchmark_tools.py`、`tests/test_windows_compat.py`
6. `python scripts/claude-obsidian.py package validate`
7. `python scripts/claude-obsidian.py contracts --check-only`

完整 hermetic 套件（含 bash、dirfd confinement、shell 測試）只在 WSL／Linux／macOS：

```bash
make test
```

上游 `test.yml` 仍會在本 fork 的 `main` 上跑。不要把那條 workflow 加上官方-repo-only guard。

`.gitattributes` 是產品契約：`* -text`。不要改成 `text=auto eol=lf`，否則 frontmatter 與 content hash 會漂。

`pyproject.toml` **只放工具設定**，沒有 `[project]` 與 `[build-system]`：產品核心是標準庫 Python，不是要發佈的套件。Ruff 只掃 `tools/`。

## 依賴新鮮度

`tools/check_dependency_freshness.py` 把 `requirements-dev.txt` 宣告的每一筆直接依賴拿去對 PyPI 現行版本，`.github/workflows/dependency-freshness.yml` 每月跑一次。紅燈只有兩條誠實出口：`# freshness-hold:`（常態政策）或 `.github/dependency-deferrals.json` 的 `deferredLatest`（會過期）。調高宣告下限來讓報告變綠不是出口。

## 不要做的事

- 不要把產品 `README.md` 改寫成繁中維護索引。
- 不要把產品 `AGENTS.md` 整份改寫；只保留開頭 overlay。
- 不要新增根目錄 `CLAUDE.md`（本 checkout 有 marketplace.json，產品契約禁止）。
- 不要翻譯 `skills/`。
- 不要改 `.claude-plugin/plugin.json` 的 homepage／repository，不要把 `FUNDING.yml` 改掛到維護者。
- 不要把這個 checkout 當作用戶 vault，不要提交 `wiki/`、`.raw/`、`.vault-meta/`。
- 不要提交 `.env`、API key 或筆記內容。
- 原生 Windows 上不要對 vault 跑 `--apply`；寫入會以 `UNSUPPORTED_PLATFORM` 拒絕。
