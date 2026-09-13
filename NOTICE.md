# NOTICE

claude-obsidian (SanHsien maintenance fork)
Copyright 2026 SanHsien

This project is derived from [`AgriciDaniel/claude-obsidian`](https://github.com/AgriciDaniel/claude-obsidian), originally licensed under the MIT License.

Original work:

- Project: `claude-obsidian`
- Author: AgriciDaniel (AI Marketing Hub)
- License: MIT
- Upstream: https://github.com/AgriciDaniel/claude-obsidian

This repository keeps the original MIT license text in [`LICENSE`](LICENSE). Modifications, documentation, and future project-specific changes in this fork are also licensed under MIT unless otherwise noted.

## License Notes

When redistributing this project or substantial parts of it:

- Keep [`LICENSE`](LICENSE) with the original MIT text.
- Keep attribution to `AgriciDaniel/claude-obsidian` and AgriciDaniel.
- License your modifications under MIT unless a third-party file says otherwise.

This fork does not grant additional permissions beyond MIT.

## Project Scope

This repository ships a local-first Agent Skills package and Claude Code plugin for source-cited Obsidian knowledge bases. The product checkout is not a user vault. User notes, inbox sources, `.raw/` payloads, and `.vault-meta/` runtime state belong to the user and must not be committed.

The design follows [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and uses [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) as the reference substrate for Obsidian Markdown, Bases, and JSON Canvas syntax. See [`ATTRIBUTION.md`](ATTRIBUTION.md).

## Credits

`claude-obsidian` is a fork of `AgriciDaniel/claude-obsidian` (MIT). The product skills, portable Python core, hooks, and setup scripts belong to the upstream project.

This project is not affiliated with, endorsed by, or sponsored by Anthropic, Obsidian, or Andrej Karpathy.

Do not commit secrets, vault content, or live `.raw/` source payloads.
