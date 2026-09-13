# 上游維護

## Remote

- Fork：`origin` → `https://github.com/SanHsien/claude-obsidian.git`
- 原作者：`upstream` → `https://github.com/AgriciDaniel/claude-obsidian.git`
- 追蹤分支：`main`

## 檢查新提交

```powershell
git fetch upstream main
python tools\check_upstream_updates.py --strict
```

工具以 `tools/upstream_baseline.json` 的 `reviewed_through` 為起點，列出所有未審查提交。
有新提交或檢查失敗時，`--strict` 回傳非零；排程 workflow 也會因此明確失敗。

## 審查清冊

每次只做一次批次審查：

1. 讀 commit 主旨與變更檔案（open PR 必須讀 diff，禁止只憑標題結案）。
2. 判斷是否與 README overlay、Windows gate、`test.yml` 或測試衝突。
3. 可直接同步的提交用 merge；只需要部分修正時 cherry-pick 或最小重做。
4. 跑 `pwsh -NoProfile -File tools\dev_check.ps1`。
5. 在 `docs/fork/DECISIONS.md` 記錄採用／略過理由（須引用具體檔案與衝突點）。
6. 驗證完成後才把 baseline 推進到已審查的完整 40 字元 SHA。

Baseline 代表「已審查」，不代表「全部已合併」。

README 衝突的解法：保留頂部 fork overlay，把上游新產品說明留在英文 `README.md`。不要改寫成維護索引。作者宣傳、Skool CTA 不轉載進 `FORK.md`。來源與授權 credit 留在 README 與 `NOTICE.md`。

`test.yml` 是產品回歸，本 fork **不**加官方-repo-only guard。merge 上游時若 overlay workflow 被覆蓋，必須把 `fork-maintenance.yml`／`upstream-check.yml` 加回去。

## 2026-08-28：fork 起點

本 fork 自上游 `main` `ad67087cad22ad84cc3288f915588ae42c0c2b44`
（`fix: harden recovery and response boundaries`）建立。此 SHA 設為第一個 `reviewed_through`。
之後的上游 commit 才需要進入審查清冊。

水位：

- PR：已看到 **#180**（`reviewed_pr_through`）
- issue：已看到 **#181**（`reviewed_issue_through`）
- commit baseline：`ad67087`（完整 SHA 見 `tools/upstream_baseline.json`）
- 下次只看編號更大的，或已評估項目是否出現新 commit／新 head

Open issue 值得記但不提前移植：

| Issue | 為什麼值得記 | 觸發條件 |
| --- | --- | --- |
| [#151](https://github.com/AgriciDaniel/claude-obsidian/issues/151) 降級原生 Windows 寫入模式 | 本線 Windows-first，原生寫入目前 fail-closed | 上游合併該設計，或本線實際被 WSL 卡住需要降級寫入 |
