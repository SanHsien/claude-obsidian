# claude-obsidian: Gemini instructions

> **SanHsien 維護型 fork overlay。** 維護規則以 [`FORK.md`](FORK.md) 為準。產品行為遵守 [`AGENTS.md`](AGENTS.md)。不要推 `upstream`、不要對上游開 PR（除非維護者在這次對話明確同意回貢）、不要把本 checkout 當作用戶 vault。

Read `AGENTS.md` as the canonical host-neutral contract. Skills live in
`skills/<name>/SKILL.md` and the portable core lives in `claude_obsidian/`.

Install skill discovery with:

```bash
bash bin/setup-multi-agent.sh --host gemini
bash bin/setup-multi-agent.sh --host gemini --apply
```

The first command previews the links; the second applies that reviewed scope.

This repository is product source, not the default user vault. Create a
separate vault with the dry-run-first `init` command or adopt an existing vault.
Resolve that vault before reading `wiki/hot.md` or running a skill.

All shared mutations use one inspected `claude-obsidian.transaction.v1` bundle.
Parallel workers draft only. Do not use direct shared writes, automatic commits,
or the deprecated per-file lock helper. Remote egress and destructive actions
need explicit user consent.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
