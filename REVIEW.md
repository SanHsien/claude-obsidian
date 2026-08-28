# Repository review（Windows-first）

- Review date: 2026-08-28
- Review baseline: fork overlay 建立點 `ad67087cad22ad84cc3288f915588ae42c0c2b44`
- Upstream reviewed through: `ad67087cad22ad84cc3288f915588ae42c0c2b44`
- Upstream watermarks: PR `reviewed_pr_through` = **180**；issue `reviewed_issue_through` = **181**
- Primary environment: Windows 11、PowerShell、Python 3.14（本機）、產品 CI Ubuntu／macOS 3.11–3.14、Windows portable smoke 3.12
- Status: 維護骨架已落地；產品 `skills/`、`claude_obsidian/`、`hooks/`、`scripts/`、`.claude-plugin/` 未改寫

## 結論

這個 fork 適合作為 Windows 本機維護線：產品是 Claude Code 終端機外掛（不是 Obsidian 社群插件），核心是標準庫 Python + 15 個 Agent Skills。原生 Windows 只保證唯讀／dry-run；vault 寫入需 WSL，這是上游刻意的 POSIX 邊界，不是本線漏做。

根目錄 `README.md` 必須維持上游英文產品說明。產品套件驗證會掃 README 的 `--apply` 範例；everything-claude-code 曾因把落地頁改繁中而炸掉產品 CI。

**沒有**改寫產品 skill、**沒有**改 `.claude-plugin/plugin.json`、**沒有**把 `FUNDING.yml` 改掛到維護者、**沒有**回貢。

## 已修 findings

| ID | 嚴重度 | Finding | 修復 |
|---|---|---|---|
| R-01 | P2 | 裸 fork 沒有 Windows 可重現 gate；上游 `make test` 依賴 bash／dirfd，原生 Windows 不能當完整驗收。 | 新增 `tools/dev_check.ps1`：overlay 閘門 + 上游 windows-smoke 同等 portable surface。 |
| R-02 | P2 | 沒有上游追蹤水位；之後無法分辨「還沒看」與「看過決定略過」。 | `tools/upstream_baseline.json` + 每週 `upstream-check.yml`；PR／issue 水位 180／181。 |
| R-03 | P3 | GitHub 訪客會把 fork 的 Issues 當成產品入口。 | `ISSUE_TEMPLATE/config.yml` 導流本線 `CONTRIBUTING.md` 與上游產品貢獻。 |
| R-04 | P3 | `gh` 在 fork clone 預設 repo 是上游。 | `.cursor/rules/no-upstream-pr.mdc`；本 clone 已 `gh repo set-default SanHsien/claude-obsidian`。 |
| R-09 | P1 | 一度新增根目錄 `CLAUDE.md`。本 checkout 有 `.claude-plugin/marketplace.json`，`test_knowledge_contracts.py` 規定兩者不能並存。 | 刪除 `CLAUDE.md`；Claude Code 入口只 overlay `AGENTS.md`。 |

## 刻意不修

| ID | 嚴重度 | Finding | 理由 |
|---|---|---|---|
| R-05 | P2 | 原生 Windows 不能 vault 寫入（`UNSUPPORTED_PLATFORM`）。 | 上游產品契約，見 `docs/windows-wsl.md` 與 [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151)。本線不提前做降級寫入。 |
| R-06 | P3 | `.claude-plugin/plugin.json` 的 homepage／repository 仍是 `AgriciDaniel/claude-obsidian`。 | 產品 plugin 清單。改掛本 fork 會包裝成第二個官方來源。 |
| R-07 | P3 | `.github/FUNDING.yml` 仍是上游 Skool 連結。 | 不把贊助改掛到 fork 維護者。 |
| R-08 | P3 | 根目錄 `README.md` 保持英文。 | 產品套件驗證契約。繁中維護在 `FORK.md`。 |

## 本輪實證

### 本機（Windows 11）

```text
pwsh -NoProfile -File tools\dev_check.ps1
→ compileall / ruff E9+F / pytest tools 31 passed
→ 10 份 overlay 文件，0 斷連結
→ 產品 portable：package_validation 11 OK、knowledge_contracts 13 OK、
  contracts 25 OK（skipped=1，wiki-lint 在原生 Windows 依設計拒絕寫入）、
  benchmark_tools skipped=5（source-only helpers excluded）、
  windows_compat 通過
→ package validate：ok true、15 skills、findings []
→ contracts --check-only：valid true
→ WINDOWS DEV CHECK GREEN
```

產品 `test.yml` 的 Linux／macOS `make test` 與 GitHub Actions 結果以推送後的 workflow 為準。

## 已檢查、不列為 finding

- 產品現況：15 個 `skills/*/SKILL.md`；`.claude-plugin/plugin.json` version `2.1.1`。
- 沒有 git symlink（`git ls-files -s` 無 `120000`）。
- `.gitattributes` 維持 `* -text`（content hash 契約）。
- 上游 `test.yml` 不加官方-repo-only guard。
- `release-allowlist.json` 的 `include_roots` 不含 `tools/`；`FORK.md`／`NOTICE.md`／`REVIEW.md` 不在 `include_files`。
- `gh repo set-default --view` 為 `SanHsien/claude-obsidian`。不對上游開 PR、不 push `upstream`。

## 尚未宣稱範圍

- **沒有**在真實 Obsidian vault 跑 `/wiki-ingest` 或 `/autoresearch`。
- **沒有**在 WSL 跑完整 `make test`。
- **沒有**建 public release zip 並與上游 artifact 比對（本線不代發產品 release）。
- `dev_check.ps1` **不含** Bandit；CodeQL 是獨立 workflow。
