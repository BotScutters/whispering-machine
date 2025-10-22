# Whispering Machine

Interactive party tracker with ESP32 sensor nodes and Raspberry Pi 5 hub featuring real-time audio transcription, occupancy tracking, and dynamic LED visualizations.

## Architecture

- **Raspberry Pi 5 Hub**: Central controller with 7" touchscreen, runs all services (MQTT, Aggregator, UI, Audio Bridge)
- **ESP32 Nodes (x2)**: Remote sensors with INMP441 mics, PIR sensors, rotary encoders, and WS2812 LED rings
- **unRAID Server**: External faster-whisper transcription service (via Tailscale)

## Quickstart

### Development (unRAID)
```bash
# Test services locally
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d
# Open http://localhost:8000/debug
```

### Production (Raspberry Pi)
```bash
# One-time setup (on Pi)
curl -sSL https://raw.githubusercontent.com/USER/whispering-machine/main/scripts/pi_bootstrap.sh | bash
sudo reboot

# Deploy from unRAID
./scripts/pi_deploy.sh

# Access party tracker
# http://<pi-ip>:8000/party
```

See [`docs/PI_HUB_DEPLOYMENT.md`](docs/PI_HUB_DEPLOYMENT.md) for complete setup guide.

## Documentation

**For agents and developers:** Start with [`docs/README.md`](docs/README.md) for a comprehensive guide to the project documentation.

**Key files:**
- [`docs/AGENTS_GUIDE.md`](docs/AGENTS_GUIDE.md) - Project overview and quick start
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System design and data flow  
- [`docs/TICKETS.md`](docs/TICKETS.md) - Available work items
- [`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md) - Code style and patterns

## Development

This project is designed for agent-led development. All agents should follow the workflow documented in `docs/AGENTS_WORKFLOW.md` and read `docs/AGENT_MEMORY.md` for project-specific learnings.
