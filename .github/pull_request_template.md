# Pull request

> **SanHsien 維護型 fork。** 本線 PR 必須打到 [`SanHsien/claude-obsidian`](https://github.com/SanHsien/claude-obsidian)。對上游 [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian) 開 PR 需要維護者在當次對話明確同意回貢。產品行為變更請優先考慮上游。見 [`FORK.md`](../FORK.md)。

## Summary
One-paragraph description of what this PR changes and why.

## Type
- [ ] Bug fix (`fix:`)
- [ ] New feature (`feat:`)
- [ ] Documentation (`docs:`)
- [ ] Refactor (`refactor:`)
- [ ] Test coverage (`test:`)
- [ ] Chore / build / maintenance (`chore:`)

## Related issue
Closes #<issue-number> (if applicable)

## Changes
List the files and surfaces touched:
- `skills/<name>/SKILL.md` — what changed
- `scripts/<name>.py` — what changed
- ...

## Safety self-review
- [ ] Read every file before changing it
- [ ] New identifiers named for the next reader
- [ ] Smallest unit that works (no speculative abstraction)
- [ ] Deletions kept up with additions where applicable
- [ ] New behavior has hermetic test coverage
- [ ] New failure modes have explicit handling + undo plan
- [ ] Product code and mutable user-vault state remain separate
- [ ] Knowledge writes use one recoverable transaction; workers only draft
- [ ] Network/destructive/external actions have explicit consent
- [ ] Claims and capability maturity are evidence-backed

## Testing
```
make test
```
Paste the tail of the output here (or a summary if too long):

```
All tests passed.
```

## Verifier
For non-trivial changes, dispatch `agents/verifier.md` on the declared worktree or path scope and paste its verdict:

- Verdict: SHIP / HOLD-FIX-FIRST / NEEDS-REWORK
- BLOCKER: N / HIGH: N / MEDIUM: N / LOW: N

## CHANGELOG
- [ ] Added an entry under `## [Unreleased]` in `CHANGELOG.md`

## Screenshots / output
If the change affects user-visible output, paste a before/after example.

## Notes for reviewer
Anything specific the reviewer should focus on, or context that's not obvious from the diff.
