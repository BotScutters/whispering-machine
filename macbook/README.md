# MacBook Party Interface Setup

This directory contains the Docker Compose configuration for running the Whispering Machine party interface on a MacBook.

## Quick Start

1. **Copy environment configuration**:
   ```bash
   cp env.example .env
   # Edit .env with your specific values
   ```

2. **Start all services**:
   ```bash
   docker compose up -d
   ```

3. **Access the party interface**:
   - Open http://localhost:8000/party in your browser
   - For 7" touchscreen: http://localhost:8000/party (full-screen mode)

## Services

- **mosquitto**: MQTT broker (ports 1883 internal, 1884 host)
- **aggregator**: Processes sensor data from ESP32 nodes
- **ui**: FastAPI server with party interface
- **audio_bridge**: Captures MacBook mic, sends to Whisper, publishes transcripts
- **llm_agent**: Generates intelligent observations from sensor data

## Configuration

### Required Environment Variables

- `WHISPER_URL`: Tailscale IP of your unRAID faster-whisper service
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: For LLM observations

### Optional Environment Variables

- `HOUSE_ID`: MQTT topic prefix (default: houseA)
- `AUDIO_DEVICE_INDEX`: MacBook audio device (default: 0)
- `LLM_PROVIDER`: openai or anthropic (default: openai)
- `LLM_MODEL`: Model to use (default: gpt-3.5-turbo)

## MacBook-Specific Considerations

### Closed-Lid Operation

The system is designed to work with the MacBook lid closed:

1. **Audio Capture**: macOS should continue capturing audio with lid closed
2. **Display**: External monitor becomes primary display
3. **Power**: MacBook stays awake and connected

### Testing Closed-Lid Operation

```bash
# Start services
docker compose up -d

# Close MacBook lid
# Wait 30 minutes
# Reopen lid - services should still be running

# Check service health
docker ps
docker logs macbook_audio_bridge --tail 20
```

### External Display Setup

For 7" touchscreen:

1. **Connect external display** via HDMI/USB-C
2. **Set as primary display** in System Preferences
3. **Configure resolution** to 1024x600 (or native resolution)
4. **Disable internal display** (optional)
5. **Disable screen saver** and sleep

### Power Management

To prevent MacBook from sleeping:

```bash
# Disable sleep (requires password)
sudo pmset -a sleep 0 displaysleep 0

# Re-enable after party
sudo pmset -a sleep 10 displaysleep 10
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker logs macbook_mosquitto
docker logs macbook_aggregator
docker logs macbook_ui
docker logs macbook_audio_bridge
docker logs macbook_llm_agent

# Check service health
docker ps
```

### Audio Issues

```bash
# List available audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# Test audio capture
docker logs macbook_audio_bridge --tail 50
```

### MQTT Issues

```bash
# Test MQTT broker
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t '#' -v
```

### Whisper Connection Issues

```bash
# Test Tailscale connectivity
ping 100.x.x.x  # Your unRAID Tailscale IP

# Test Whisper endpoint
curl http://100.x.x.x:10300/health
```

## Party Night Checklist

### Pre-Party Setup

- [ ] Copy `env.example` to `.env` and configure
- [ ] Test all services: `docker compose up -d`
- [ ] Verify audio capture: `docker logs macbook_audio_bridge`
- [ ] Test Whisper connection: Check transcript MQTT topics
- [ ] Test closed-lid operation for 30+ minutes
- [ ] Configure external display as primary
- [ ] Disable sleep and screen saver
- [ ] Test touchscreen input (if applicable)

### Party Night

- [ ] Start services: `docker compose up -d`
- [ ] Close MacBook lid
- [ ] Verify external display shows party interface
- [ ] Check that ESP32 nodes are connected
- [ ] Monitor logs: `docker logs -f macbook_audio_bridge`
- [ ] Have emergency restart script ready

### Emergency Procedures

```bash
# Quick restart
docker compose restart

# Full restart
docker compose down && docker compose up -d

# Check service status
docker ps
docker logs macbook_audio_bridge --tail 20
```

## Performance Expectations

### MacBook Resources

- **CPU**: ~30-50% usage (varies by model)
- **RAM**: ~500MB-1GB total
- **Network**: Minimal (MQTT + occasional Whisper calls)
- **Storage**: ~2GB for Docker images

### Runtime

- **Expected**: 6+ hours continuous operation
- **Battery**: Depends on MacBook model and power settings
- **Heat**: Should remain manageable with lid closed

## Security Notes

- **API Keys**: Store in `.env` file (gitignored)
- **Network**: Uses Tailscale for secure Whisper connection
- **Local**: All services run locally on MacBook
- **Privacy**: Audio is processed locally, only transcripts sent to Whisper

## Support

For issues specific to MacBook operation:

1. Check Docker logs for service errors
2. Verify macOS audio permissions
3. Test Tailscale connectivity
4. Check power management settings
5. Verify external display configuration

See main project documentation in `docs/` for general troubleshooting.
