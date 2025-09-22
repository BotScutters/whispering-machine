# Development Scripts (Docker-based)

This document describes the `dev.sh` script system used for development commands in the Whispering Machine project. This script provides a Docker-based alternative to Makefile for environments where `make` and Python tools are not available (such as UnRAID).

## Quick Reference

### Main Environment
```bash
./dev.sh up          # Start main development environment (services)
./dev.sh down        # Stop main development environment
./dev.sh logs        # Show logs from main services
```

### Development Tools
```bash
./dev.sh dev-up      # Start development tools containers
./dev.sh dev-down    # Stop development tools containers
./dev.sh shell       # Interactive shell in development container
```

### Code Quality
```bash
./dev.sh fmt         # Format Python code using Docker
./dev.sh lint        # Lint Python code using Docker
```

### MQTT Testing
```bash
./dev.sh pub-noise   # Publish test data to MQTT using Docker
./dev.sh sub-all     # Subscribe to all MQTT topics using Docker
```

### Utilities
```bash
./dev.sh clean       # Clean up all environments
./dev.sh help        # Show help message
```

## Detailed Commands

### Main Environment Management

#### `./dev.sh up`
Starts the main development environment (application services).
- Uses `infra/docker-compose.yml`
- Starts aggregator, UI, and MQTT broker services
- Provides access URLs for UI and MQTT broker

#### `./dev.sh down`
Stops the main development environment.
- Stops application services only
- Preserves volumes for data persistence

#### `./dev.sh logs`
Shows real-time logs from main development services.
- Uses `docker compose logs -f` for continuous output
- Shows logs from application services

### Development Tools Management

#### `./dev.sh dev-up`
Starts development tools containers.
- Uses `infra/docker-compose.dev.yml`
- Starts containers for formatting, linting, and MQTT testing
- Contains Python tools, mosquitto-clients, and other dev utilities

#### `./dev.sh dev-down`
Stops development tools containers.
- Stops dev tools containers only
- Main application services continue running

#### `./dev.sh shell`
Opens an interactive shell in the development container.
- Provides access to all development tools
- Mounts project directory at `/app`
- Useful for manual operations and debugging

### Code Quality (Docker-based)

#### `./dev.sh fmt`
Formats all Python code using Docker containers.
- Runs Black formatter with 88-character line length
- Runs Ruff linter with auto-fix
- Sorts imports with isort
- All operations performed in isolated Docker container
- No local Python tools required

#### `./dev.sh lint`
Lints Python code using Docker containers.
- Runs Ruff linter to check code quality
- Reports issues without fixing them
- All operations performed in isolated Docker container
- Useful for CI/CD pipelines

### MQTT Testing (Docker-based)

#### `./dev.sh pub-noise`
Publishes test data to MQTT topics using Docker containers.
- Uses mosquitto-clients from Docker container
- Publishes audio features to `party/house1/kitchen/audio/features`
- Publishes occupancy state to `party/house1/kitchen/occupancy/state`
- Uses current timestamp for realistic data
- Connects to MQTT broker via Docker network

#### `./dev.sh sub-all`
Subscribes to all MQTT topics using Docker containers.
- Uses mosquitto-clients from Docker container
- Subscribes to `party/+/+/+/+` pattern
- Shows real-time messages from all nodes
- Connects to MQTT broker via Docker network

### Utilities

#### `./dev.sh clean`
Performs a complete cleanup of all environments.
- Stops both main and development environments
- Removes volumes (data will be lost)
- Runs `docker system prune -f` to clean up unused resources

## Prerequisites

### Required Tools
- **Docker**: For container management
- **Docker Compose**: Either `docker-compose` or `docker compose`

### No Local Tools Required
This Docker-based approach eliminates the need for local installations:
- **No Python required** - All Python tools run in containers
- **No pip/pip3 required** - Tools are pre-installed in containers
- **No mosquitto-clients required** - MQTT tools run in containers
- **No make required** - Script provides all functionality

## Installation

1. Make the script executable:
   ```bash
   chmod +x dev.sh
   ```

2. Build development tools containers:
   ```bash
   ./dev.sh dev-up
   ```

3. Verify installation:
   ```bash
   ./dev.sh help
   ```

## Usage Examples

### Starting Development
```bash
# Start development tools containers
./dev.sh dev-up

# Start main application services
./dev.sh up

# Check if services are running
./dev.sh logs

# Test MQTT connectivity
./dev.sh sub-all
```

### Code Development
```bash
# Format code before committing (using Docker)
./dev.sh fmt

# Check for linting issues (using Docker)
./dev.sh lint

# Enter development container for manual work
./dev.sh shell

# Test with sample data (using Docker)
./dev.sh pub-noise
```

### Debugging
```bash
# Monitor MQTT messages (using Docker)
./dev.sh sub-all

# Check service logs
./dev.sh logs

# Interactive debugging in container
./dev.sh shell

# Clean restart
./dev.sh clean
./dev.sh dev-up
./dev.sh up
```

## Troubleshooting

### Docker Issues
- Ensure Docker is running: `docker --version`
- Check Docker Compose: `docker compose version` or `docker-compose --version`
- Verify permissions: `sudo usermod -aG docker $USER` (may require logout/login)
- Check if containers are running: `docker ps`

### Development Container Issues
- Ensure dev containers are built: `./dev.sh dev-up`
- Check container logs: `docker logs whispering-machine-dev`
- Rebuild containers if needed: `./dev.sh dev-down && ./dev.sh dev-up`

### MQTT Issues
- Ensure main environment is running: `./dev.sh up`
- Check if MQTT broker is running: `./dev.sh logs`
- Test connectivity using Docker: `./dev.sh pub-noise`
- Verify MQTT broker container: `docker ps | grep mosquitto`

### Code Quality Issues
- All formatting/linting now runs in Docker containers
- No local Python tools required
- If containers fail, rebuild: `./dev.sh dev-down && ./dev.sh dev-up`
- Check container logs: `docker logs whispering-machine-formatter`

## Integration with CI/CD

The script commands can be used in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Format and lint code
  run: |
    ./dev.sh fmt
    ./dev.sh lint
```

## Docker Architecture

The development system uses two separate Docker Compose files:

### Main Environment (`infra/docker-compose.yml`)
- Application services (aggregator, UI, MQTT broker)
- Production-like environment for testing
- Network: `whispering-machine_default`

### Development Tools (`infra/docker-compose.dev.yml`)
- Development utilities and tools
- Python tools, mosquitto-clients, git, etc.
- Network: `whispering-machine-dev`
- Mounts project directory at `/app`

## Customization

The script can be customized by editing `dev.sh`:
- Modify Docker Compose file path
- Change MQTT broker host/port
- Add new commands for project-specific needs
- Customize formatting rules
- Add Docker-based formatting alternatives

## Migration from Makefile

If you previously used Makefile commands, here's the mapping:

| Makefile Command | dev.sh Command |
|------------------|----------------|
| `make up`        | `./dev.sh up`  |
| `make down`      | `./dev.sh down` |
| `make logs`      | `./dev.sh logs` |
| `make fmt`       | `./dev.sh fmt` |
| `make lint`      | `./dev.sh lint` |
| `make pub-noise` | `./dev.sh pub-noise` |
