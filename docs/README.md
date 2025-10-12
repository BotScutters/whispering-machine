# Whispering Machine Documentation

This directory contains all the documentation needed for agent-led development of the Whispering Machine project.

## 📋 Quick Start for Agents

**Before starting any work, read these files in order:**

1. [`AGENTS_GUIDE.md`](./AGENTS_GUIDE.md) - Project overview and quick start
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md) - System design and data flow
3. [`TICKETS.md`](./TICKETS.md) - Available work items with acceptance criteria
4. [`AGENT_MEMORY.md`](./AGENT_MEMORY.md) - Known issues and lessons learned
5. [`CODING_STANDARDS.md`](./CODING_STANDARDS.md) - Code style and patterns

## 📁 Documentation Structure

### Core Documentation
- **`ARCHITECTURE.md`** - System design, data flow, and technical constraints
- **`AGENTS_GUIDE.md`** - Mission, principles, and development workflow
- **`AGENTS_WORKFLOW.md`** - Step-by-step process for agent development
- **`TICKETS.md`** - Well-scoped work items ready for implementation
- **`TASKS.md`** - High-level MVP requirements and acceptance criteria

### Standards & Guidelines
- **`CODING_STANDARDS.md`** - Python style, formatting, and best practices
- **`AGENT_MEMORY.md`** - Project-specific learnings and gotchas
- **`SENSOR_REFERENCE.md`** - Sensor signals, tuning, and technical details
- **`ROADMAP.md`** - High-level project phases and milestones
- **`CURRENT_PRIORITIES.md`** - Current development status and next steps
- **`DEVELOPMENT_SCRIPTS.md`** - Development commands and scripts reference

### Decision Records
- **`DECISIONS/`** - Architecture Decision Records (ADRs)
  - `ADR-0001-mqtt-topics.md` - MQTT topic naming conventions

## 🚀 Development Workflow

1. **Read the basics** - Start with `AGENTS_GUIDE.md` and `ARCHITECTURE.md`
2. **Pick a ticket** - Choose from `TICKETS.md` based on current priorities
3. **Understand constraints** - Review `AGENT_MEMORY.md` for known issues
4. **Follow standards** - Apply `CODING_STANDARDS.md` patterns
5. **Test thoroughly** - Use provided testing guidelines
6. **Document learnings** - Update `AGENT_MEMORY.md` with new insights

## 🔧 Key Commands

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
```

> **Note**: See [`DEVELOPMENT_SCRIPTS.md`](./DEVELOPMENT_SCRIPTS.md) for complete command reference and troubleshooting.

## 📊 Project Status

- **Current Phase**: MVP development
- **Active Tickets**: See `TICKETS.md`
- **Known Issues**: See `AGENT_MEMORY.md`
- **Next Milestone**: See `ROADMAP.md`

## 🤝 Contributing

- Keep PRs small and focused
- Update documentation when adding features
- Test locally before submitting
- Follow the workflow in `AGENTS_WORKFLOW.md`

---

*This documentation is maintained by the development team. Update it as the project evolves.*
