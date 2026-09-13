# claude-obsidian: Windsurf rules

> **SanHsien 維護型 fork overlay。** 維護規則以 [`FORK.md`](../../FORK.md) 為準。產品行為遵守 [`AGENTS.md`](../../AGENTS.md)。不要把本 checkout 當作用戶 vault。

Read `AGENTS.md` as the canonical host-neutral contract. Preview and then
install Cascade skill links with
`bash bin/setup-multi-agent.sh --host windsurf --workspace "$PWD"` followed by
the same command with `--apply`, and load the matching
`skills/<name>/SKILL.md` when a request triggers it.

The product clone and user vault are separate. Resolve the user vault before
reading hot context or mutating knowledge. Raw payloads are create-only;
parallel workers return drafts; one orchestrator inspects and applies one
recoverable transaction. Queries and lint remain read-only. Network egress,
destructive repair, and Git checkpoints require explicit user consent.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
