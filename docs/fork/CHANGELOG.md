# 本 fork 變更紀錄

格式參考 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，新的在上面。
本檔只記錄**本 fork 的維護歷史**（2026-08-28 起）；上游
[`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian)
的產品演進見其自身 [`CHANGELOG.md`](../../CHANGELOG.md) 與 [`UPSTREAM.md`](UPSTREAM.md) 的審查清冊。
逐筆採用／略過的理由記在 [`DECISIONS.md`](DECISIONS.md)。

---

## 2026-08-28

### 新增

- **Windows-first 維護骨架。** `FORK.md`、`NOTICE.md`、`REVIEW.md`、
  `docs/fork/`、`tools/` 維護腳本、fork CI（fork-maintenance／upstream-check／
  CodeQL／dependency-freshness）、Dependabot。
- 根目錄 `README.md`、`AGENTS.md`、`CONTRIBUTING.md`、`SECURITY.md`、
  `CODE_OF_CONDUCT.md` 加上 fork overlay；產品正文不改寫。不新增 `CLAUDE.md`（產品契約）。
- `ISSUE_TEMPLATE/config.yml` 導流：本線 overlay 問題走 SanHsien，產品行為走上游。
