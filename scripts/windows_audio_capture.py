#!/usr/bin/env python3
"""
Windows Audio Capture Service
Captures audio from Windows microphone and sends to WSL2 MQTT broker
"""

import pyaudio
import wave
import json
import time
import requests
import threading
import queue
import os
from datetime import datetime

# Configuration
MQTT_BROKER_HOST = "192.168.8.103"  # Windows host IP on whispernet
MQTT_BROKER_PORT = 1883
HOUSE_ID = "hidden_house"
AUDIO_CHUNK_DURATION_MS = 3000  # 3 seconds
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FORMAT = pyaudio.paInt16

class WindowsAudioCapture:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.audio_queue = queue.Queue()
        self.running = False
        
    def list_audio_devices(self):
        """List available audio devices"""
        print("Available audio devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  {i}: {info['name']} (channels: {info['maxInputChannels']})")
    
    def capture_audio_chunk(self, device_index=0):
        """Capture a chunk of audio"""
        try:
            stream = self.audio.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=int(AUDIO_SAMPLE_RATE * AUDIO_CHUNK_DURATION_MS / 1000)
            )
            
            print(f"Capturing audio from device {device_index}...")
            frames = stream.read(int(AUDIO_SAMPLE_RATE * AUDIO_CHUNK_DURATION_MS / 1000))
            stream.stop_stream()
            stream.close()
            
            return frames
            
        except Exception as e:
            print(f"Error capturing audio: {e}")
            return None
    
    def send_to_whisper(self, audio_data):
        """Send audio data to Whisper service via WSL2"""
        try:
            # For now, just simulate a transcript
            # In production, this would send to the actual Whisper service
            transcript = {
                "text": f"Audio captured at {datetime.now().strftime('%H:%M:%S')} - {len(audio_data)} bytes",
                "confidence": 0.85,
                "timestamp": int(time.time() * 1000),
                "source": "windows_mic"
            }
            
            # Send to MQTT broker
            self.send_to_mqtt(transcript)
            
        except Exception as e:
            print(f"Error sending to Whisper: {e}")
    
    def send_to_mqtt(self, transcript):
        """Send transcript to MQTT broker"""
        try:
            # Use mosquitto_pub to send to MQTT
            topic = f"party/{HOUSE_ID}/macbook/speech/transcript"
            payload = json.dumps(transcript)
            
            # Use subprocess to call mosquitto_pub
            import subprocess
            result = subprocess.run([
                "mosquitto_pub",
                "-h", MQTT_BROKER_HOST,
                "-p", str(MQTT_BROKER_PORT),
                "-t", topic,
                "-m", payload
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Sent transcript: {transcript['text'][:50]}...")
            else:
                print(f"Failed to send to MQTT: {result.stderr}")
                
        except Exception as e:
            print(f"Error sending to MQTT: {e}")
    
    def run(self):
        """Main capture loop"""
        print("Starting Windows Audio Capture...")
        self.list_audio_devices()
        
        device_index = int(input("Enter device index (default 0): ") or "0")
        
        self.running = True
        while self.running:
            try:
                print("Capturing audio chunk...")
                audio_data = self.capture_audio_chunk(device_index)
                
                if audio_data:
                    # Send to Whisper service
                    self.send_to_whisper(audio_data)
                
                # Wait before next capture
                time.sleep(5)  # Capture every 5 seconds
                
            except KeyboardInterrupt:
                print("Stopping audio capture...")
                self.running = False
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(5)
        
        self.audio.terminate()

if __name__ == "__main__":
    capture = WindowsAudioCapture()
    capture.run()
