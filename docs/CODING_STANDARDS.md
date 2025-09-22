# Coding Standards

## Python Standards
- **Version**: Python 3.10+
- **Style**: Google style guide
- **Line Length**: 88 characters
- **Type Hints**: Required for all function signatures and class attributes
- **Docstrings**: Google format for all public functions and classes

## Code Formatting
- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **isort**: Import organization
- Run `./dev.sh fmt` before committing

## AsyncIO & Concurrency
- **Prefer asyncio**: Use async/await patterns for I/O operations
- **MQTT Clients**: All MQTT interactions should be async
- **WebSocket**: Use async handlers for real-time updates
- **Background Tasks**: Use asyncio.create_task() for concurrent operations

## Data Validation
- **Pydantic Models**: Use for all MQTT payload validation
- **Schema Location**: Define schemas in `/schemas` directory
- **Error Handling**: Validate inputs at service boundaries
- **Type Safety**: Use TypedDict for complex data structures

## Logging
- **Format**: Structured JSON logs to stdout
- **Level**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **Context**: Include service name, timestamp, and relevant IDs
- **Example**: `{"level": "INFO", "service": "aggregator", "ts": "2025-01-27T10:30:00Z", "msg": "Connected to MQTT broker"}`

## Error Handling
- **Graceful Degradation**: Services should continue operating with reduced functionality
- **Retry Logic**: Implement exponential backoff for transient failures
- **Circuit Breakers**: For external service dependencies
- **Monitoring**: Log errors with sufficient context for debugging

## Testing
- **Unit Tests**: For business logic and data transformations
- **Integration Tests**: For MQTT message flows and service interactions
- **Manual Testing**: Use mosquitto_pub/sub for MQTT validation
- **Visual Testing**: Screenshots/GIFs for UI changes
