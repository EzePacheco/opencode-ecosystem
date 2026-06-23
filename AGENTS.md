# opencode-ecosystem Guidance

- This repo contains two maintained surfaces: the native OpenCode setup at the
  repo root and the Codex-native adaptation under `codex/`.
- For Codex harness changes, edit `codex/` and keep the installed copies in
  `~/.codex` and `$HOME/.agents/skills` in sync, or run `./install-codex.sh`.
- Use `./doctor-codex.sh` after Codex harness changes.
- Root `standards/`, `skills/`, and legacy installers are OpenCode material;
  touch them when the task explicitly targets the native OpenCode setup.
- Keep repo guidance focused on layout, commands, and ownership boundaries.
  OpenCode runtime workflow lives in `GLOBAL.md`; Codex global workflow lives in
  `codex/AGENTS.md`.
