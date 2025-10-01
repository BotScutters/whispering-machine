# Agents Workflow (Cursor)

## Read these first
- `docs/ARCHITECTURE.md`
- `docs/TASKS.md` and `docs/TICKETS.md`
- `docs/AGENTS_GUIDE.md`, `docs/CODING_STANDARDS.md`
- Existing code under `services/`, `firmware/`, `infra/`

## Rules of Engagement
1) Pick a **single ticket**; restate acceptance criteria.
2) Propose a **minimal plan** (bulleted) and file delta (files to touch).
3) Implement incrementally; keep PR small.
4) Update `docs/AGENT_MEMORY.md` with any new rule/gotcha.
5) Update `docs/TICKETS.md` to mark ticket as done (with commit hash).
6) Run locally (`docker compose ...`) and attach a screenshot/GIF if UI-related.

## Don’ts
- Don’t change MQTT shapes without updating `schemas/` and `ARCHITECTURE.md`.
- Don’t add heavy deps unless justified in the PR description.
