# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `345e4974ce50` 查的快照，開工前先重查 GitHub。

## 現況

這是 AgriciDaniel/claude-obsidian（Obsidian＋Claude Code 本機知識庫外掛）的 Windows-first 維護 fork，產品樹已整批併入上游 v3.0.1。維護面健康：`main` 上 CodeQL、Hermetic verification、Fork maintenance、Upstream check 最近一次皆 success，open PR 0 筆、Dependabot 與 Code scanning 告警 0 筆；issue 功能已停用，issue 數「未查到」不是 0（2026-10-29 `gh` 查詢）。上游 PR 水位已審至 #215、issue 水位審至 #212（`tools/upstream_baseline.json`），上游暫無待審項目；目前 `Dependency freshness` 只由每月排程與手動觸發，最近一次是 2026-10-01，早於 10-25 的整批併入。

## 近期：可以直接動手

| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 手動觸發 `Dependency freshness` 驗證 10-25 整批併入之後的依賴狀態 | 該 workflow 只有 cron（每月 1 日）與 `workflow_dispatch`，最近一次成功早於整批併入；紅燈只能靠它發現 | `gh workflow run "Dependency freshness" -R SanHsien/claude-obsidian` 後該 run 結論為 success，或每個紅項都有 `# freshness-hold:` 或 deferrals 條目與理由 | Claude Haiku | `gh run list -R SanHsien/claude-obsidian --workflow "Dependency freshness"`；`.github/workflows/dependency-freshness.yml:3-6` |

## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 審上游 PR #210（NFC／NFD）與 #202（內容管線工具） | 上游合併，或本線 vault 出現 NFD 檔名／有內容管線需求 | 讀 diff 後採用或略過，結論記入 `docs/fork/DECISIONS.md`；`tools\dev_check.ps1` 綠 | Claude Sonnet | `docs/fork/DECISIONS.md:242-249` |
| 評估讓 CodeQL 也掃 `actions` 語言（workflow 本身） | 維護者想檢查 workflow 注入面，或 新增會讀外部輸入（issue／PR 內容、`workflow_run` 事件等）的 workflow | CodeQL 矩陣新增 `actions`；該 workflow 在 `main` 綠；新增的告警筆數用 `gh api repos/SanHsien/claude-obsidian/code-scanning/alerts?state=open` 查並逐筆處理 | Claude Sonnet | `docs/fork/DECISIONS.md` 2026-10-25「`dependabot.yml`、`codeql.yml` 上游版」列 |
| 補 `check_links.py` 對 `<img src="a b.png">` 的處理（跳過標題切分） | 文件出現含空白的 HTML `src` 寫法 | 新增測試：該寫法不再被誤報缺檔，修前紅修後綠；`pytest tools` 綠 | Codex | 深掃報告（2026-10-26）「刻意不修」 |
| 在 Linux 上跑完整產品測試與 release build | 取得 Linux／CI runner 並決定要發布本 fork 自己的 release | 一次完整 Linux 測試與 build 的 workflow 紀錄為 success | 維護者 | 接續開發報告（2026-10-25）：本機 Windows 無法跑 Linux 完整測試與 release build |

## 刻意不做

| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 採用上游 `dependabot.yml` 的 `cooldown: 14 天` | 本線靠新鮮度檢查與人工審查把關（`docs/fork/DECISIONS.md` 2026-10-25 表格） | 出現因新版剛發布就合併而踩雷的事故 |
| 改寫產品樹（`skills/`、`claude_obsidian/`、`scripts/`） | 產品以上游為準，fork 只加 overlay（`docs/fork/DECISIONS.md:3-15`） | 上游停止維護 |
| 發布本 fork 自己的 release | 本 fork 沒有自己的 release，產品版本跟上游走 | 維護者決定要發布 Windows 版產物 |
| 對上游開 PR／回貢 | 預設只打 `SanHsien/` 名下 repo | 維護者在新的對話中明確要求回貢 |

## 維護方式

fork：以 `Upstream check` workflow 為訊號（failure＝上游有未審項目），審完在 `docs/fork/DECISIONS.md` 記採用與否並推進水位；上游釋出新 release 時整批審。直接推 `main`；Dependabot 只開 PR，CI 綠且讀完 diff 才合併；`Dependency freshness` 每月 1 日排程，產品整批併入後要手動跑一次。
