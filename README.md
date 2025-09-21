# Whispering Machine

Interactive AI party tracker dashboard with ESP32 sensor nodes (Wi-Fi/MQTT),
a Raspberry Pi touchscreen UI, and optional UnRAID workers for heavier jobs.

## Quickstart (on unRAID)
1) `cp .env.example .env`
2) `docker compose -f infra/docker-compose.yml up --build -d`
3) Open http://<unraid-ip>:8000

See docs/AGENTS_GUIDE.md and docs/CODING_STANDARDS.md.
