/**
 * Party App Orchestrator
 * Touchscreen-optimized unreliable narrator interface
 */

import { StateManager } from '../core/state-manager.js';
import { MQTTClient, StandardHandlers } from '../core/mqtt-client.js';
import { CONFIG } from '../core/config.js';

export class PartyApp {
    constructor() {
        this.stateManager = new StateManager();
        this.mqttClient = null;
        this.chart = null; // Chart.js instance (passed from HTML)
        this.transcripts = [];
        this.observations = [];
        this.maxItems = 50; // Max items to keep in memory
        this.startTime = Date.now();
        this.debugMode = false;
        
        // Status tracking
        this.status = {
            mqtt: false,
            whisper: false,
            llm: false,
            nodes: {}
        };
    }

    /**
     * Initialize the party application
     * @param {Chart} chartInstance - Chart.js instance from party.html
     */
    async init(chartInstance) {
        console.log('[PartyApp] Initializing party mode...');
        
        this.chart = chartInstance;
        
        // Setup MQTT client
        this.setupMQTT();
        
        // Setup UI updates
        this.setupUIUpdates();
        
        // Start status monitoring
        this.startStatusMonitoring();
        
        // Start uptime counter
        this.startUptimeCounter();
        
        console.log('[PartyApp] Party mode initialized successfully');
    }

    /**
     * Setup MQTT client and message handlers
     */
    setupMQTT() {
        const wsUrl = `ws://${window.location.host}/ws/party`;
        this.mqttClient = new MQTTClient(wsUrl, this.stateManager);
        
        const handlers = new StandardHandlers(this.stateManager);

        // Register handlers for each topic pattern
        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.AUDIO_FEATURES,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleAudioFeatures(nodeId, payload);
                this.updateAudioChart(payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.OCCUPANCY_STATE,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleOccupancyState(nodeId, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.RING_STATE,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleRingState(nodeId, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.ENCODER,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleEncoder(nodeId, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.BUTTON,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleButton(nodeId, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.HEARTBEAT,
            (nodeId, payload, topic) => {
                this.updateNodeStatus(nodeId, 'active');
                handlers.handleHeartbeat(nodeId, payload);
            }
        );

        // Register handlers for new party-specific topics
        this.mqttClient.registerHandler(
            'party/+/macbook/speech/transcript',
            (nodeId, payload, topic) => {
                this.handleTranscript(payload);
            }
        );

        this.mqttClient.registerHandler(
            'party/+/llm_agent/observations/observation',
            (nodeId, payload, topic) => {
                this.handleObservation(payload);
            }
        );

        // Connect
        this.mqttClient.connect();
        
        // Update MQTT status
        this.mqttClient.on('connect', () => {
            this.status.mqtt = true;
            this.updateStatusIndicators();
        });
        
        this.mqttClient.on('disconnect', () => {
            this.status.mqtt = false;
            this.updateStatusIndicators();
        });
    }

    /**
     * Setup UI update subscriptions
     */
    setupUIUpdates() {
        // Subscribe to state changes for real-time updates
        this.stateManager.subscribe('nodes', () => {
            this.updateSensorDisplay();
        });

        this.stateManager.subscribe('system_status', () => {
            this.updateSystemStatus();
        });
    }

    /**
     * Handle transcript messages
     */
    handleTranscript(payload) {
        try {
            const transcript = {
                timestamp: new Date().toLocaleTimeString(),
                text: payload.text || payload.transcript || 'Unknown transcript',
                confidence: payload.confidence || 0,
                source: payload.source || 'macbook'
            };

            this.transcripts.unshift(transcript);
            
            // Keep only recent transcripts
            if (this.transcripts.length > this.maxItems) {
                this.transcripts = this.transcripts.slice(0, this.maxItems);
            }

            this.updateTranscriptDisplay();
            this.status.whisper = true;
            this.updateStatusIndicators();
            
        } catch (error) {
            console.error('Error handling transcript:', error);
        }
    }

    /**
     * Handle LLM observation messages
     */
    handleObservation(payload) {
        try {
            const observation = {
                timestamp: new Date().toLocaleTimeString(),
                text: payload.text || payload.observation || 'Unknown observation',
                mood: payload.mood || 'neutral',
                source: payload.source || 'llm_agent'
            };

            this.observations.unshift(observation);
            
            // Keep only recent observations
            if (this.observations.length > this.maxItems) {
                this.observations = this.observations.slice(0, this.maxItems);
            }

            this.updateObservationDisplay();
            this.status.llm = true;
            this.updateStatusIndicators();
            
        } catch (error) {
            console.error('Error handling observation:', error);
        }
    }

    /**
     * Update transcript display
     */
    updateTranscriptDisplay() {
        const container = document.getElementById('observationsDisplay');
        if (!container) return;

        if (this.transcripts.length === 0) {
            container.innerHTML = `
                <div class="content-text">Listening...</div>
            `;
            return;
        }

        let html = '';
        this.transcripts.slice(0, 10).forEach(transcript => {
            html += `
                <div class="content-text">${transcript.text}</div>
                <div class="timestamp">${transcript.timestamp}</div>
            `;
        });

        container.innerHTML = html;
    }

    /**
     * Update observation display
     */
    updateObservationDisplay() {
        const container = document.getElementById('observationsDisplay');
        if (!container) return;

        if (this.observations.length === 0) {
            container.innerHTML = `
                <div class="content-text">Observing...</div>
            `;
            return;
        }

        let html = '';
        this.observations.slice(0, 8).forEach(observation => {
            html += `
                <div class="content-text">${observation.text}</div>
                <div class="timestamp">${observation.timestamp}</div>
            `;
        });

        container.innerHTML = html;
    }

    /**
     * Update sensor display
     */
    updateSensorDisplay() {
        const nodes = this.stateManager.get('nodes') || {};
        const activeNodes = Object.keys(nodes).filter(nodeId => 
            nodes[nodeId] && nodes[nodeId].status === 'active'
        );

        // Update node cards
        for (let i = 1; i <= 3; i++) {
            const nodeId = `node${i}`;
            const nodeData = nodes[nodeId];
            
            const valueEl = document.getElementById(`${nodeId}Value`);
            const statusEl = document.getElementById(`${nodeId}Status`);
            
            if (valueEl && statusEl) {
                if (nodeData && nodeData.status === 'active') {
                    const audioData = nodeData.audio?.features;
                    if (audioData) {
                        valueEl.textContent = audioData.rms ? audioData.rms.toFixed(3) : '--';
                    } else {
                        valueEl.textContent = 'ACTIVE';
                    }
                    statusEl.textContent = 'ACTIVE';
                    statusEl.className = 'sensor-status active';
                } else {
                    valueEl.textContent = '--';
                    statusEl.textContent = 'OFFLINE';
                    statusEl.className = 'sensor-status offline';
                }
            }
        }

        // Update active nodes count
        const activeNodesEl = document.getElementById('activeNodes');
        if (activeNodesEl) {
            activeNodesEl.textContent = `${activeNodes.length}/3`;
        }
    }

    /**
     * Update audio chart
     */
    updateAudioChart(payload) {
        if (!this.chart) return;

        const now = new Date();
        const rms = payload.rms || 0;

        // Add new data point
        this.chart.data.datasets[0].data.push({
            x: now,
            y: rms
        });

        // Keep only last 100 points
        if (this.chart.data.datasets[0].data.length > 100) {
            this.chart.data.datasets[0].data.shift();
        }

        this.chart.update('none');
    }

    /**
     * Update status indicators
     */
    updateStatusIndicators() {
        const indicators = {
            ws: document.getElementById('wsStatus'),
            mqtt: document.getElementById('mqttStatus'),
            whisper: document.getElementById('whisperStatus'),
            llm: document.getElementById('llmStatus')
        };

        Object.entries(indicators).forEach(([key, element]) => {
            if (element) {
                if (this.status[key]) {
                    element.classList.add('connected');
                    element.classList.remove('disconnected');
                } else {
                    element.classList.add('disconnected');
                    element.classList.remove('connected');
                }
            }
        });
    }

    /**
     * Update system status
     */
    updateSystemStatus() {
        const systemStatus = this.stateManager.get('system_status') || 'unknown';
        const statusEl = document.getElementById('systemStatus');
        
        if (statusEl) {
            statusEl.textContent = systemStatus.toUpperCase();
            
            // Update body class based on status
            document.body.classList.remove('error-state', 'warning-state');
            if (systemStatus === 'offline') {
                document.body.classList.add('error-state');
            } else if (systemStatus === 'degraded') {
                document.body.classList.add('warning-state');
            }
        }
    }

    /**
     * Update node status
     */
    updateNodeStatus(nodeId, status) {
        this.status.nodes[nodeId] = {
            status: status,
            lastSeen: Date.now()
        };
    }

    /**
     * Start status monitoring
     */
    startStatusMonitoring() {
        setInterval(() => {
            const now = Date.now();
            const timeout = 30000; // 30 seconds

            // Check if services are still active
            Object.keys(this.status.nodes).forEach(nodeId => {
                const node = this.status.nodes[nodeId];
                if (now - node.lastSeen > timeout) {
                    node.status = 'offline';
                }
            });

            // Update displays
            this.updateSensorDisplay();
            this.updateStatusIndicators();
        }, 5000);
    }

    /**
     * Start uptime counter
     */
    startUptimeCounter() {
        setInterval(() => {
            const uptimeEl = document.getElementById('uptime');
            if (uptimeEl) {
                const uptime = Date.now() - this.startTime;
                const hours = Math.floor(uptime / 3600000);
                const minutes = Math.floor((uptime % 3600000) / 60000);
                const seconds = Math.floor((uptime % 60000) / 1000);
                
                uptimeEl.textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }

    /**
     * Add glitch effect to text
     */
    addGlitchEffect(text) {
        if (this.debugMode) return text;
        
        // Randomly add glitch characters
        const glitchChars = ['█', '▓', '▒', '░', '▄', '▀', '▌', '▐'];
        let result = text;
        
        if (Math.random() < 0.1) { // 10% chance of glitch
            const pos = Math.floor(Math.random() * text.length);
            const glitchChar = glitchChars[Math.floor(Math.random() * glitchChars.length)];
            result = text.substring(0, pos) + glitchChar + text.substring(pos + 1);
        }
        
        return result;
    }

    /**
     * Handle tap interaction
     */
    handleTap() {
        console.log('Tap detected');
        // Add subtle visual feedback
        document.body.style.background = '#0f0f0f';
        setTimeout(() => {
            document.body.style.background = '#0a0a0a';
        }, 100);
    }

    /**
     * Trigger Konami code easter egg
     */
    triggerKonamiCode() {
        console.log('Konami code activated!');
        // Add special visual effect
        document.body.style.background = 'linear-gradient(45deg, #0a0a0a, #001a0a, #0a0a0a)';
        setTimeout(() => {
            document.body.style.background = '#0a0a0a';
        }, 1000);
        
        // Trigger any special functionality
        this.stateManager.update('konami_activated', true);
    }

    /**
     * Destroy application and cleanup
     */
    destroy() {
        if (this.mqttClient) {
            this.mqttClient.close();
        }
    }
}

// Export singleton instance
export default PartyApp;
