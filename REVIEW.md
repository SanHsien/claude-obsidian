# Repository review（Windows-first）

- Review date: 2026-08-28；增量審查 2026-11-20（`cacbcc8..ab3dd42`，見下方「2026-11-20 增量審查」）
- Review baseline: overlay `8d945a7900231c94c38065f412de41fcea91091e`；本輪修復另記於後續 commit
- Upstream reviewed through: `ad67087cad22ad84cc3288f915588ae42c0c2b44`
- Upstream watermarks: PR `reviewed_pr_through` = **180**；issue `reviewed_issue_through` = **181**
- Primary environment: Windows 11、PowerShell、Python 3.14.7（本機）、產品 CI Ubuntu／macOS 3.11–3.14、Windows portable smoke 3.12
- Status: 維護骨架可用。R-01～R-04、R-09～R-16 已在本線修。R-05～R-08 刻意不修。不回貢。

## 結論

這個 fork 適合作為 Windows 本機維護線。產品是 **Claude Code 終端機外掛**（不是 Obsidian 社群插件商店套件）：標準庫 Python 核心 + 15 個 Agent Skills。原生 Windows 只保證唯讀／dry-run；vault 寫入需 WSL。這是上游 POSIX 目錄描述子契約，不是本線漏做。

根目錄 `README.md` 必須維持上游英文產品說明。產品套件驗證會掃 README 的 `--apply` 範例；everything-claude-code 曾因把落地頁改繁中而炸掉產品 CI。

**沒有**改寫產品 skill、**沒有**改 `.claude-plugin/plugin.json` 的 homepage／repository、**沒有**把 `FUNDING.yml` 改掛到維護者、**沒有**回貢。安裝與發佈仍以上游 [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian) 為準。不要把這個 checkout 當作用戶 vault。

## 本輪實證

### 本機（Windows 11，Python 3.14.7）

```text
git rev-parse HEAD（審查起點 overlay）
→ 8d945a7900231c94c38065f412de41fcea91091e

pwsh -NoProfile -File tools\dev_check.ps1（本輪 overlay 修復後）
→ compileall / ruff E9+F / pytest tools 35 passed
→ 15 份 overlay 文件，0 斷連結
→ 產品 portable：package_validation 11 OK、knowledge_contracts 13 OK、
  contracts 25 OK（skipped=1，wiki-lint 在原生 Windows 依設計拒絕寫入）、
  benchmark_tools skipped=5（source-only helpers excluded）、
  windows_compat 通過
→ package validate：ok true、15 skills、findings []
→ contracts --check-only：valid true
→ WINDOWS DEV CHECK GREEN

tests/test_release.py CanonicalReleasePolicyTests.test_public_policy_never_selects_root_contributor_vault_state
→ ok
tests/test_release.py CanonicalPolicyTests.test_repository_allowlist_is_canonical_and_valid
→ ok（完整 hermetic release 套件不在原生 Windows 跑）
```

實查（不是只讀 README）：

- `git ls-files -s` 無 `120000` symlink。
- `git ls-files '*.env' '.env*'` 為空。
- overlay `tools/` 無 `os.system`、`shell=True`、`eval(`、`exec(`、`pickle`。`check_upstream_updates.py` 以 argv 列表呼叫 `git`。
- 產品 `claude_obsidian/` 的 `subprocess.run` 皆 argv 列表，無 `shell=True`。
- `.github/workflows/` 沒有發佈／tag／GitHub Release job。`test.yml` 權限 `contents: read`。
- SessionStart hook 預設靜默；`CLAUDE_OBSIDIAN_SESSION_CONTEXT` 必須精確等於 `1` 才會把 `wiki/hot.md` 放進模型上下文（`hook_adapter.py`）。
- `gh repo set-default --view` → `SanHsien/claude-obsidian`。
- 產品 CI `test.yml` **沒有** `github.repository ==` 官方閘門（刻意保留）。

**沒有**在真實 Obsidian vault 跑 `/wiki-ingest`。**沒有**在 WSL 跑完整 `make test`（交給 GitHub `test.yml`）。

### GitHub Actions（overlay `8d945a7`）

| Workflow | 結果 | 說明 |
|---|---|---|
| [Hermetic verification](https://github.com/SanHsien/claude-obsidian/actions/runs/33143140819) | success | Linux／macOS 3.11–3.14 `make test`、Windows portable smoke、release-safety |
| [Fork maintenance](https://github.com/SanHsien/claude-obsidian/actions/runs/33143140926) | success | Ubuntu／Windows fork gate |
| [CodeQL](https://github.com/SanHsien/claude-obsidian/actions/runs/33143140874) | success | Python `security-extended` |
| [Upstream check](https://github.com/SanHsien/claude-obsidian/actions/runs/33143140643) | success | 仍在 `ad67087` |

本輪 gitignore／allowlist 修復後的產品 CI 以新 push 為準，不沿用上表當「修復後綠燈」。

## 已修 findings

| ID | 嚴重度 | Finding | 修復 |
|---|---|---|---|
| R-01 | P2 | 裸 fork 沒有 Windows 可重現 gate；上游 `make test` 依賴 bash／dirfd。 | `tools/dev_check.ps1`：overlay 閘門 + windows-smoke 同等 portable surface。 |
| R-02 | P2 | 沒有上游追蹤水位。 | `tools/upstream_baseline.json` + 每週 `upstream-check.yml`；PR／issue 水位 180／181。 |
| R-03 | P3 | GitHub 訪客會把 fork Issues 當成產品入口。 | `ISSUE_TEMPLATE/config.yml` 導流本線與上游 `CONTRIBUTING.md`。 |
| R-04 | P3 | `gh` 在 fork clone 預設 repo 是上游。 | `.cursor/rules/no-upstream-pr.mdc`；本 clone 已 `gh repo set-default SanHsien/claude-obsidian`。 |
| R-09 | P1 | 一度新增根目錄 `CLAUDE.md`。本 checkout 有 `.claude-plugin/marketplace.json`，`test_knowledge_contracts.py` 禁止兩者並存。 | 刪除 `CLAUDE.md`。測試鎖「此樹不得有 CLAUDE.md」。 |
| R-10 | P2 | 產品根 `.gitignore` 不忽略 `/wiki/`、`/inbox/`、`/.raw/`。有人把 checkout 當 vault 時，筆記可被 `git add`。 | 加上根前綴規則；不影響 `templates/vault` 與 `examples/sample-vault`。 |
| R-11 | P3 | `docs` 在 release `include_roots`，`docs/fork/` 會進公開 zip。 | `config/release-allowlist.json` 排除 `docs/fork/**`。這是已記錄的產品 allowlist fork 修正。 |
| R-12 | P3 | `CODEOWNERS` 仍是 `@AgriciDaniel`。本線不回貢，對方不是 collaborator，Dependabot／外部 PR 會卡死。 | 改為 `* @SanHsien`。該檔仍在 release `include_files`；本線不代發產品 zip。 |
| R-13 | P3 | `bug_report.md`／`feature_request.md` 沒標明產品請走上游。 | 開頭加上 overlay，指向上游產品 repo 與本線 `FORK.md`。 |
| R-14 | P3 | overlay workflow／Dependabot 會經 `.github/workflows/*.yml` 與 `.github/*.yml` 進公開 zip。 | `exclude_globs` 排除五個 overlay 檔；產品 `test.yml` 與 `FUNDING.yml` 仍進去。 |
| R-15 | P3 | `GEMINI.md`、copilot、cursor、windsurf 指示沒有 fork overlay。 | 開頭加上 overlay；產品正文與 Public canonical 上游 URL 保留。`GEMINI.md` 已刪；上游 `ZCODE.md` 於 `d72e2d7`（2026-11-20）補上，見 F-1。 |
| R-16 | P3 | `.cursor` 在 `include_roots`，fork-only `no-upstream-pr.mdc` 會進公開 zip。 | `exclude_globs` 排除該檔。 |

## 2026-11-20 增量審查

範圍 `cacbcc8..ab3dd42`。產品樹與上游 v3.0.1 tip `2e54556` 逐位元組相同，findings 都在 fork overlay。

| ID | 分類 | Finding | 狀態 |
|---|---|---|---|
| F-1 | P3 | `ZCODE.md`（上游 ZCode adapter，進公開 zip）沒有 fork overlay；R-15 測試刪 `GEMINI.md` 時沒補上它；DECISIONS 仍記 ZCode not-applicable。 | 已修 `d72e2d7`（2026-11-20）：加 overlay，`test_host_instruction_files_have_fork_overlay` 改為從內容探索宿主檔。DECISIONS 更正於 `68c7bb4`。 |
| F-2 | needs_validation | `check_upstream_updates.py` 把任何含 "not found" 的 `gh` 錯誤當成「已漂移」，該是「無法檢查」。 | 不在本 repo 修：該檔是 repo-fleet-ops canonical 的逐字副本，於 canonical 端修後再同步。 |
| F-3 | hardening | `load_baseline` 不容忍 UTF-8 BOM。 | 同 F-2，於 canonical 端修。 |
| F-4 | hardening | baseline `decision_log` 路徑沒有測試鎖住。 | 同 F-2，於 canonical 端修。 |
| F-5 | hardening | 根目錄 `RELEASE_MANIFEST.json`／`SHA256SUMS` 是上游快照，列著已刪的 `GEMINI.md`，overlay 檔雜湊對不上。 | 依慣例不重產（本線不發 release，`release build` 會重產）；於 `68c7bb4`（2026-11-20）在 `FORK.md` 與 DECISIONS 註明為上游快照。 |
| F-6 | hardening | `check_links.py` 沒掃 `AGENTS.md`、`ROADMAP.md`。 | 已修 `ae5bb10`（2026-11-20）：本檔是 fork 自有版本（與 repo-fleet-ops 的不同），補掃兩檔與宿主規則檔；順手修掉 code span 誤報與 HTML `src` 被切分（ROADMAP 原列項），測試 `test_link_checker_scans_every_file_that_carries_overlay_links`、`test_code_is_not_a_link`、`test_html_src_with_a_space_is_one_target`。獨立驗收再找到兩個缺口（inline code 跨段落吞掉真斷連結、"```x```" 開頭的行被當 fence 藏住後文），已修 `82adc01`（2026-11-20），測試 `test_inline_code_does_not_cross_a_blank_line`、`test_backtick_line_with_backticks_in_info_is_not_a_fence`；宿主檔探索改為不限措辭（`test_host_discovery_does_not_depend_on_one_wording`）。 |

## 刻意不修

| ID | 嚴重度 | Finding | 理由 |
|---|---|---|---|
| R-05 | P2 | 原生 Windows 不能 vault 寫入（`UNSUPPORTED_PLATFORM`）。 | 上游產品契約，見 `docs/windows-wsl.md` 與 [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151)。本線不提前做降級寫入。 |
| R-06 | P3 | `.claude-plugin/plugin.json` 與 `config/public-marketplace.json` 仍指向上游。 | 產品 marketplace。改掛本 fork 會包裝成第二個官方來源。 |
| R-07 | P3 | `.github/FUNDING.yml` 仍是上游 Skool 連結。 | 不把贊助改掛到 fork 維護者。 |
| R-08 | P3 | 根目錄 `README.md` 保持英文。 | 產品套件驗證契約。繁中維護在 `FORK.md`。 |

## 已檢查、不列為 finding

- 產品現況：15 個 `skills/*/SKILL.md`；plugin version `2.1.1`。
- `.gitattributes` 維持 `* -text`（frontmatter 與 content hash 契約）。不要改成其他 fork 的 `text=auto eol=lf`。
- `release-allowlist.json` 的 `include_roots` 不含 `tools/`；`FORK.md`／`NOTICE.md`／`REVIEW.md` 不在 `include_files`。
- overlay 測試放 `tools/`，不會被產品 `make test` 的 `tests/test_*.py` 掃進去。
- Dependabot 只開 PR，不自動合併。新鮮度只看 `requirements-dev.txt`。
- Fork 的 checkout／setup-python／codeql-action 已 pin SHA，且 `persist-credentials: false`。
- 無發佈 workflow 需要官方-repo-only guard。
- `PRIVACY.md`：無遙測；SessionStart 預設不注入 vault。
- 上游 open issue [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151) 列為觀察，不提前移植。

## 尚未宣稱範圍

- **沒有**在真實 Obsidian vault 跑 `/wiki`、`/wiki-ingest`、`/autoresearch` 或 `/save`。
- **沒有**在本機 WSL 跑完整 `make test`（Linux／macOS 以 GitHub `test.yml` 為準）。
- **沒有**把本線 `release build` zip 拿去跟上游 artifact 比對 byte（本線不代發產品 release）。
- `dev_check.ps1` **不含** Bandit、完整 `tests/test_release.py`；CodeQL 是獨立 workflow。
- **不宣稱** 本 fork 是官方 marketplace 或會發自己的 GitHub Release。
- **不宣稱** 已把 overlay 送回上游。

## 建議下一步

1. 日常使用：另開獨立 vault，不要用本 checkout。流程見 [`docs/install-guide.md`](docs/install-guide.md)。原生 Windows 只做 doctor／dry-run；寫入進 WSL。
2. 上游若合併 [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151) 降級 Windows 寫入，再評估是否跟。
3. 之後維護直接推 `origin/main`。回貢需當次對話明確同意。
