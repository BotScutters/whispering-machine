# Whisper Integration Reference

## Deployment (External to This Repo)

### Service
**faster-whisper** by LinuxServer.io  
- **GitHub**: https://github.com/linuxserver/docker-faster-whisper
- **Deployment**: Installed via UnRAID Community Apps
- **Port**: 10300 (exposed to host)
- **Protocol**: Wyoming (WebSocket-based voice assistant protocol)

### Configuration (UnRAID)
- **Model**: `tiny-int8` (recommended starting point)
- **Hardware**: CPU (i7-13700K, ~8 cores available)
- **Language**: `en`
- **Beam Size**: 1 (faster, acceptable accuracy for party chatter)

### Performance Expectations
| Model      | Size   | Latency (est.) | Accuracy | Use Case                 |
|------------|--------|----------------|----------|--------------------------|
| tiny-int8  | ~40MB  | 1-2s           | Good     | Quick party transcription|
| base-int8  | ~80MB  | 2-4s           | Better   | Important conversations  |
| small-int8 | ~150MB | 4-8s           | Best     | High-accuracy needs      |

**Note**: Latency estimates for 2-5 second audio clips on i7-13700K with ~8 cores

---

## Hardware Context

### Available GPUs
1. **RTX 4070**: Allocated to Windows VM → unavailable to Docker
2. **Quadro M2000** (Maxwell): Available but dated, poor performance expected
3. **CPU**: i7-13700K (16 cores, ~8 available after VM allocation)

### Chosen Approach: CPU
- **Why**: Sufficient performance for tiny/base models
- **Why not GPU**: M2000 Maxwell architecture predates faster-whisper optimizations
- **Why not whisper.cpp**: faster-whisper has better Docker integration and Wyoming protocol

---

## API Integration (Future: T-020)

### Wyoming Protocol Basics
- **Transport**: WebSocket
- **Endpoint**: `ws://localhost:10300/`
- **Request**: Audio data + config
- **Response**: Transcribed text

### Integration Architecture

```
ESP32 Audio Clip (WAV, 2-5s)
  ↓ HTTP POST
Transcriber Service (this repo)
  ↓ Wyoming WebSocket
faster-whisper (external)
  ↓ Transcript
Transcriber Service
  ↓ MQTT publish
party/<house>/<node>/speech/transcript
  ↓
Aggregator → UI → User
```

### Transcriber Service (To Be Built)
**Location**: `services/transcriber/`

**Responsibilities**:
- Accept HTTP POST with WAV audio from ESP32
- Queue clips (handle bursts)
- Forward to Whisper via Wyoming protocol
- Parse transcript response
- Publish to MQTT: `party/<house>/<node>/speech/transcript`
- Handle errors, retries, timeouts

**MQTT Message Schema**:
```json
{
  "text": "hello there",
  "confidence": 0.95,
  "duration_ms": 2340,
  "model": "tiny-int8",
  "ts_ms": 1234567890
}
```

### ESP32 Audio Clip Recording (To Be Built)
**Location**: `firmware/wm_node/src/audio_clip.{cpp,h}`

**Triggers**:
- Button press (manual capture)
- RMS spike > threshold (loud event)
- Voice activity detection (ZCR pattern)

**Implementation**:
- Record 2-5 second WAV to SPIFFS/buffer
- HTTP POST to `http://<server>:8000/api/transcribe`
- Include: node ID, trigger reason, timestamp
- Delete after successful upload

**Constraints**:
- Max 1 clip per 10 seconds (avoid spam)
- Max 5 retries on network failure
- No continuous recording (privacy)

---

## Testing Whisper Service

### 1. Health Check
```bash
curl http://localhost:10300/health
# Expected: some health status response
```

### 2. Test with Audio File
You'll need to use Wyoming protocol format. For now, test that the service is running and models are loaded.

### 3. Check Logs
```bash
# If installed via UnRAID, check container logs via UI
# Or via CLI:
docker logs faster-whisper --tail 50
```

Expected: Model loading confirmation, ready to accept connections

---

## Configuration Reference

### Environment Variables (faster-whisper)
- `WHISPER_MODEL=tiny-int8` - Start small, test performance
- `WHISPER_BEAM=1` - Speed over accuracy
- `WHISPER_LANG=en` - English language
- `LOCAL_ONLY=true` - Use bundled models, no HuggingFace download

### Upgrade Path
If transcription quality insufficient:
1. `tiny-int8` → `base-int8` (2x slower, better accuracy)
2. `base-int8` → `small-int8` (2x slower again, best accuracy)

**Trade-off**: Each step up doubles latency but improves accuracy significantly.

---

## Integration TODO (See T-020 in TICKETS.md)

When ready to implement:
1. Create `services/transcriber/` with FastAPI app
2. Implement Wyoming WebSocket client
3. Add audio clip recording to ESP32 firmware
4. Create MQTT schema for transcripts
5. Add transcript display to debug UI
6. Test end-to-end with real audio clips

**Current Status**: Whisper service deployed and ready, integration pending.

---

## Network Access

### From This Repo's Services
- **Endpoint**: `http://host.docker.internal:10300/` (from inside Docker)
- **Or**: `http://localhost:10300/` (if on same network)
- **Or**: `http://<unraid-ip>:10300/` (from ESP32)

### From ESP32
- **Endpoint**: `http://<unraid-ip>:10300/`
- **Via Transcriber**: ESP32 → `http://<unraid-ip>:8000/api/transcribe` → Transcriber → Whisper

**Note**: ESP32 posts to transcriber service, which handles Whisper communication.

---

## Performance Monitoring

### Metrics to Track (Future)
- Clip upload time (ESP32 → Transcriber)
- Transcription latency (Transcriber → Whisper → result)
- End-to-end latency (clip recorded → transcript published)
- Error rate (failed transcriptions)
- Queue depth (clips waiting)

### Target SLAs
- **Latency**: < 5 seconds end-to-end (clip → MQTT transcript)
- **Availability**: > 99% (graceful degradation if Whisper down)
- **Accuracy**: Sufficient to understand party conversation context

---

## Future Enhancements

- Multiple language support (auto-detect or per-node config)
- Speaker diarization (who said what)
- Keyword extraction (highlight interesting phrases)
- Sentiment analysis (positive/negative mood)
- Wake word detection (only transcribe after "hey party")


