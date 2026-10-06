# opencode-ecosystem Guidance

- This repo contains two maintained surfaces: the native OpenCode setup at the
  repo root and the Codex-native adaptation under `codex/`.
- For the active personal Codex harness, edit `codex/personal/` and follow its
  `README.md` manual merge and verification instructions. Preserve host-specific
  configuration when updating `~/.codex` and `$HOME/.agents/skills`.
- `./install-codex.sh` and `./doctor-codex.sh` apply only to the historical Codex
  adaptation outside `codex/personal/`; do not use them for the personal baseline.
- Root `standards/`, `skills/`, and legacy installers are OpenCode material;
  touch them when the task explicitly targets the native OpenCode setup.
- Keep repo guidance focused on layout, commands, and ownership boundaries.
  OpenCode runtime workflow lives in `GLOBAL.md`; the historical Codex workflow
  lives in `codex/AGENTS.md` and the personal method in `codex/personal/AGENTS.md`.
