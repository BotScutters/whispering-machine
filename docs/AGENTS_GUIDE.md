# Agents Guide

## Mission
Deliver a live "party tracker" dashboard that provides real-time insights into house activity through sensor data aggregation and visualization.

## Core Principles
- **MVP-first**: Focus on essential features that demonstrate value
- **Resilient offline**: System continues functioning even with network interruptions
- **Privacy by design**: Remote nodes send features only, no continuous raw audio streaming
- **Fabrication transparency**: Any simulated/synthetic data must be clearly marked in UI

## Quick Start
```bash
# Start development tools containers
./dev.sh dev-up

# Start main application services
./dev.sh up

# Check MQTT messages (using Docker)
./dev.sh sub-all

# Publish test data (using Docker)
./dev.sh pub-noise

# Format code (using Docker)
./dev.sh fmt

# View logs
./dev.sh logs

# Interactive development shell
./dev.sh shell
```

## Key Concepts
- **House ID**: Unique identifier for each installation (e.g., "house1", "house2")
- **Node**: Physical sensor unit (e.g., "kitchen", "living_room", "bathroom")
- **Domain**: Data category (e.g., "audio", "occupancy", "environment")
- **Signal**: Specific measurement (e.g., "features", "state", "lux")

## Architecture Overview
1. **Sensors** (ESP32/ESPHome) → publish to MQTT topics
2. **Aggregator** (Python) → validates, processes, and publishes unified state
3. **UI** (FastAPI + WebSocket) → serves dashboard and pushes real-time updates
4. **LED Daemon** (Raspberry Pi) → drives visual effects based on mood

## Development Workflow
1. Read `docs/ARCHITECTURE.md` for system design
2. Pick a ticket from `docs/TICKETS.md`
3. Implement with small, focused PRs
4. Test locally and document results
5. Update `docs/AGENT_MEMORY.md` with learnings

## Schemas & Validation
- MQTT schemas in `/schemas` directory
- Topic base: `party/<HOUSE_ID>/<node>/<domain>/<signal>`
- All payloads must include `ts_ms` timestamp
- Use Pydantic models for validation
