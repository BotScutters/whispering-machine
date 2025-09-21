# Agents Guide
Mission: deliver a live "party tracker" dashboard; MVP-first; resilient offline.
Guardrails: remote nodes send features (no continuous raw audio). Fabrication allowed but marked in UI.
Run: `docker compose -f infra/docker-compose.yml up -d`
Schemas in /schemas; topic base `party/<HOUSE_ID>/...`
