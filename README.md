# Whispering Machine

Interactive AI party tracker dashboard with ESP32 sensor nodes (Wi-Fi/MQTT),
a Raspberry Pi touchscreen UI, and optional UnRAID workers for heavier jobs.

## Quickstart (on unRAID)
1) `cp .env.example .env`
2) `docker compose -f infra/docker-compose.yml up --build -d`
3) Open http://<unraid-ip>:8000

## Documentation

**For agents and developers:** Start with [`docs/README.md`](docs/README.md) for a comprehensive guide to the project documentation.

**Key files:**
- [`docs/AGENTS_GUIDE.md`](docs/AGENTS_GUIDE.md) - Project overview and quick start
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System design and data flow  
- [`docs/TICKETS.md`](docs/TICKETS.md) - Available work items
- [`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md) - Code style and patterns

## Development

This project is designed for agent-led development. All agents should follow the workflow documented in `docs/AGENTS_WORKFLOW.md` and read `docs/AGENT_MEMORY.md` for project-specific learnings.
