# claude-obsidian Copilot instructions

> **SanHsien 維護型 fork。** 維護規則見 [`FORK.md`](../FORK.md)。PR 打 [`SanHsien/claude-obsidian`](https://github.com/SanHsien/claude-obsidian)。產品行為貢獻請去上游 [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian)。不要把本 checkout 當作用戶 vault。

Read `AGENTS.md` before proposing changes. The repository is an Agent Skills
package, Claude Code adapter, standard-library Python core, and deterministic
vault template—not the default live user vault.

When editing:

- Keep skill frontmatter to exactly `name` and single-line `description`.
- Use Obsidian Flavored Markdown, flat YAML properties, and `YYYY-MM-DD` dates.
- Never modify existing raw source payloads.
- Route all logical knowledge mutations through one inspected operation bundle.
- Keep workers draft-only and lint/query read-only.
- Preserve vault path containment and product/vault separation.
- Add hermetic regression tests for behavior changes and run `make test`.
- Do not add secrets, private paths, unsupported capability claims, or duplicate
  command wrappers.

Public canonical: https://github.com/AgriciDaniel/claude-obsidian
