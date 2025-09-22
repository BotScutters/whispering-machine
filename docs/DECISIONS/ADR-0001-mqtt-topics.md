# ADR-0001: MQTT Topic & Payload Conventions
- Use `party/<house>/<node>/<domain>/<signal>`
- Examples:
  - `party/houseA/kitchen/audio/features`
  - `party/houseA/bath1/occupancy/state`
- Payloads must include `ts_ms` and be compact JSON.
- Reason: easy routing, house scoping, node traceability.
