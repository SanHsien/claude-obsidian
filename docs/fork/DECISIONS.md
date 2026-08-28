# 維護決策

## 2026-08-28：建立 Windows-first 維護型 fork

**決定**：fork `AgriciDaniel/claude-obsidian`，保留 MIT 與完整歷史，預設分支維持 `main` 以降低與上游同步摩擦。本線聚焦 Windows 開發 gate、fork CI，以及逐筆審查的上游追蹤。根目錄 `README.md` 保持上游英文產品說明。

**理由**：上游已是可安裝的 Claude Code 外掛（15 個 Agent Skills + 標準庫 Python 核心），符合維護者用本機 Markdown 當第二大腦的需求。產品 CI 會驗證 README 的 `--apply` 範例與套件契約，把落地頁改成繁中會炸掉產品驗證——這是 everything-claude-code 已經踩過的坑。授權是 MIT，fork 修改同樣走 MIT。

**限制**：

- 不把 fork 包裝成原創專案，不移除原作者與 MIT 標示。
- `skills/*/SKILL.md`、`claude_obsidian/` 保持產品規格，不用維護索引覆寫。
- 不把產品 skill 翻譯成繁體；產品語言跟隨上游。
- 上游更新必須逐筆審查。
- 不回貢，除非維護者在當次對話明確同意。

## 2026-08-28：維護線直接推 main

**決定**：fork 維護不再開功能分支。改完在本機跑 gate，通過後直接推 `origin/main`。遠端只留 `main`；`upstream/main` 只追蹤。

**理由**：這是單人維護 fork，分支與 PR 沒有第二審查者，只增加同步成本。

**限制**：

- Dependabot 與外部 fork 仍可能開 PR，讀 diff 後再合併，不自動合併。
- 不推 `upstream`，不 force-push `main`。
- 不刪 `upstream` remote。

## 2026-08-28：不改寫產品 README／不另做 README.en.md

**決定**：根目錄 `README.md` 只加頂部 overlay，正文保持上游英文。不新增 `README.en.md`。繁中維護寫在 `FORK.md`、`docs/fork/`、`REVIEW.md`。

**理由**：`claude_obsidian/package_validation.py` 會掃 `README.md`、`docs/*.md`、`skills/**/*.md` 的 `--apply` 範例。產品 `test.yml` 是 hermetic 回歸。everything-claude-code 把落地頁改繁中曾讓產品 CI 失敗。

**限制**：`docs/fork/` 不放進 `docs/*.md` 的產品驗證 glob（該 glob 非遞迴），但 `docs` 仍在 release allowlist 的 `include_roots`，公開 zip 會帶上 fork 文件。這可接受：zip 仍由 allowlist 選檔，`tools/` 不在 `include_roots`。

## 2026-08-28：保留產品 test.yml，不加官方-repo-only guard

**決定**：`.github/workflows/test.yml` 在本 fork 繼續跑 Linux／macOS 全測與 Windows portable smoke。

**理由**：這是產品回歸，不是會發佈或覆寫 README 的 workflow。閘住它等於本線不再驗證產品。

**限制**：上游若新增會自動 tag／publish／開 issue 的 workflow，merge 時要加官方 repo 閘門。

## 2026-08-28：不改 plugin.json 與 FUNDING.yml

**決定**：`.claude-plugin/plugin.json` 的 homepage／repository 仍指向上游。`.github/FUNDING.yml` 仍是上游 Skool 連結。

**理由**：改掛 `SanHsien/claude-obsidian` 會把 fork 包裝成第二個官方 marketplace。不把贊助改掛到維護者。

**限制**：本線 README overlay 與 `FORK.md` 不轉載 Skool CTA。

## 2026-08-28：不改產品 .gitattributes

**決定**：維持上游 `* -text`。不套其他 fork 的 `* text=auto eol=lf`。

**理由**：frontmatter 解析要求精確 `---\n`，templates、release manifests、approval plans 必須跨平台 byte-identical。Windows CI 在 checkout 前關掉 `core.autocrlf`。

## 2026-08-28：不新增根目錄 CLAUDE.md

**決定**：本 fork 不新增 `CLAUDE.md`。Claude Code 入口走開頭已加 overlay 的 `AGENTS.md`。

**理由**：產品 `tests/test_knowledge_contracts.py::test_release_excludes_host_only_root_claude_context` 規定：有 `.claude-plugin/marketplace.json` 的樹不能有根目錄 `CLAUDE.md`。本 checkout 帶著 marketplace 模板產物。加 `CLAUDE.md` 會讓 windows-smoke 同等測試失敗。

**限制**：同步上游時若上游拿掉 marketplace.json 並加入 `CLAUDE.md`，再考慮 overlay，而不是自己先加。

## 2026-08-28：根目錄 vault 路徑加入 gitignore

**決定**：產品根 `.gitignore` 加上 `/wiki/`、`/inbox/`、`/.raw/`（只限 repo 根目錄）。

**理由**：產品契約說 checkout 不是用戶 vault，但 gitignore 先前只忽略 `.vault-meta/` 執行期檔。有人把筆記開在 checkout 裡時，`wiki/` 可以直接被 `git add`。根前綴不影響 `templates/vault/wiki` 與 `examples/sample-vault`。

**限制**：不忽略 `templates/` 或 `examples/` 底下的示範 vault。

## 2026-08-28：公開產物排除 docs/fork

**決定**：`config/release-allowlist.json` 的 `exclude_globs` 加上 `docs/fork/**`。

**理由**：`docs` 在 `include_roots`，否則 `release build` 會把本 fork 的繁中維護文件打進公開 zip。這不是產品文件。

**限制**：這是對產品 allowlist 的已記錄 fork 修正。merge 上游時若該檔被重寫，要把這條 exclude 加回去。

**決定**：Dependabot 只開 PR；CI 與人工讀 diff 通過後才合併。

**理由**：開發依賴只有 pytest / ruff，體積小，但自動合併仍會跳過「讀 diff」這一步。
