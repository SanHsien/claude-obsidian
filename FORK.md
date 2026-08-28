# Fork 維護說明

本 repo fork 自 [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian)，
沿用 MIT License 與完整 Git 歷史。

## 為什麼維護 fork

- 保留原作者把 Obsidian 筆記做成可累積知識圖的 Claude Code 外掛（不是 Obsidian 社群插件商店套件）。
- 採 Windows-first 維護：Windows 11 + PowerShell 是主要開發、除錯與完整驗收環境。
- 繁中維護規則放 `FORK.md`；根目錄 `README.md` 必須保持上游英文產品說明（產品套件驗證會掃 README 的 `--apply` 範例）。
- 建立可重現的 Windows 開發 gate、fork CI，以及逐筆審查的上游追蹤。
- 原生 Windows 僅支援唯讀檢查與 dry-run；vault 寫入需 WSL，見 [`docs/windows-wsl.md`](docs/windows-wsl.md)。

**回貢判準：修的是上游的 bug 就送回去；這裡獨創的文件／Windows 維護骨架留在這裡。**
回貢前必須在當次對話取得維護者明確同意；「fork」「建開發環境」「開 PR」都不是同意。

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `README.md` | 上游英文產品說明 + 頂部 fork overlay。繁中維護在 `FORK.md`／`REVIEW.md` |
| `AGENTS.md` | 開頭加上本 fork overlay；下文仍是上游產品規則。不新增根目錄 `CLAUDE.md`：本 checkout 有 `.claude-plugin/marketplace.json`，產品契約禁止同時存在 host-only `CLAUDE.md` |
| `CONTRIBUTING.md` / `SECURITY.md` / `CODE_OF_CONDUCT.md` | 開頭 overlay：本線 overlay 問題走 SanHsien；產品貢獻與產品漏洞仍指向上游 |
| `NOTICE.md` / `FORK.md` | 來源、授權與同步說明 |
| `tools/dev_check.ps1` | Windows 本機一鍵 gate（overlay + 上游 windows-smoke 同等的 portable surface） |
| `.github/workflows/fork-maintenance.yml` | fork 文件與連結檢查 |
| `.github/workflows/upstream-check.yml` | 每週對 `upstream/main` 做未審查 commit 檢查 |
| `.github/workflows/test.yml` | **保留並在本 fork 跑**，這是產品回歸 |
| `docs/fork/` | Windows 開發、上游審查、決策、本 fork 變更紀錄 |
| `REVIEW.md` | 風險快照，不是每個一般 bug 的流水帳 |

產品 `skills/`、`claude_obsidian/`、`hooks/`、`scripts/`、`bin/` 以上游為準，除非有已記錄的 fork 修正。目前已記錄的產品檔修正只有 `config/release-allowlist.json` 排除 `docs/fork/**`，以及根目錄 `.gitignore` 的 vault 路徑。

## 分支與 remote

- `origin/main`：SanHsien 維護線，也是唯一長期分支。
- 日常修改在本機跑 gate 後直接推 `origin/main`。只有需要他人審查或高風險改動時才開 branch → PR。
- `upstream/main`：AgriciDaniel 原始專案，只追蹤、不推送。
- Dependabot 或外部 fork 的變更同樣走 PR，讀 diff 並通過 CI 後再合併。

不要 `git push upstream`。同步方式見 [`docs/fork/UPSTREAM.md`](docs/fork/UPSTREAM.md)。

上游更新英文 `README.md` 時，保留頂部 overlay，不要把產品說明改寫成維護索引。繁中維護差異寫在 `FORK.md`。來源 credit 留在 README 與 [`NOTICE.md`](NOTICE.md)。

## 換一台電腦怎麼開發

```powershell
git clone https://github.com/SanHsien/claude-obsidian.git
cd claude-obsidian
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements-dev.txt
pwsh -NoProfile -File tools\dev_check.ps1
```

`dev_check.ps1` 含 overlay 閘門，以及上游 `windows-smoke` 同等的 portable surface。完整 hermetic 套件（含 bash／dirfd）仍走 `make test`，只在 WSL／Linux／macOS 上跑。

只想使用產品、不開發時，請走上游官方來源與 [`docs/install-guide.md`](docs/install-guide.md)。不要把這個 checkout 當作用戶 vault，也不要把 `tools/`、`docs/fork/` 當成產品裝包。

## 審查紀錄

本輪倉庫審查見 [`REVIEW.md`](REVIEW.md)。
