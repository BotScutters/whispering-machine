/**
 * Debug App Orchestrator
 * Main application logic for debug UI
 */

import { StateManager } from '../core/state-manager.js';
import { MQTTClient, StandardHandlers } from '../core/mqtt-client.js';
import { CONFIG } from '../core/config.js';
import { StatusTable } from '../components/status-table.js';
import { LEDRingViz } from '../components/led-ring-viz.js';
import { SignalChart } from '../components/signal-chart.js';
import { MQTTDebugger } from '../components/mqtt-debugger.js';
import { ConnectionStatus } from '../components/connection-status.js';

export class DebugApp {
    constructor() {
        this.stateManager = new StateManager();
        this.mqttClient = null;
        this.components = {};
        this.chart = null; // Chart.js instance (passed from HTML)
        this.discoveredNodes = new Set(); // Track all discovered nodes
    }

    /**
     * Initialize the application
     * @param {Chart} chartInstance - Chart.js instance from debug.html
     */
    async init(chartInstance) {
        console.log('[DebugApp] Initializing...');
        
        this.chart = chartInstance;
        
        // Initialize all components
        this.initComponents();
        
        // Setup MQTT client
        this.setupMQTT();
        
        // Setup UI event handlers
        this.setupEventHandlers();
        
        // Load saved configuration
        this.loadConfiguration();
        
        console.log('[DebugApp] Initialized successfully');
    }

    /**
     * Initialize all UI components
     */
    initComponents() {
        // Audio Status Table
        this.components.audioTable = new StatusTable('audioStatusTable', this.stateManager, {
            signals: CONFIG.SIGNALS.AUDIO,
            tooltips: CONFIG.TOOLTIPS.audio,
            formatters: {
                rms: (v) => v.toFixed(6),
                zcr: (v) => v.toFixed(6),
                low: (v) => v.toFixed(6),
                mid: (v) => v.toFixed(6),
                high: (v) => v.toFixed(6)
            },
            statePath: 'nodes.*.audio'
        });
        this.components.audioTable.init();

        // Occupancy Status Table
        this.components.occupancyTable = new StatusTable('occupancyTable', this.stateManager, {
            signals: CONFIG.SIGNALS.OCCUPANCY,
            tooltips: CONFIG.TOOLTIPS.occupancy,
            formatters: {
                occupied: (v) => v ? '✅ YES' : '⬜ NO',
                activity: (v) => (v * 100).toFixed(1) + '%',
                transitions: (v) => v
            },
            statePath: 'nodes.*.occupancy'
        });
        this.components.occupancyTable.init();

        // Encoder & Button Status Table (unified)
        this.components.encoderButtonTable = new StatusTable('encoderButtonStatus', this.stateManager, {
            signals: ['encoder.pos', 'encoder.delta', 'button.pressed', 'button.event'],
            tooltips: {
                'encoder.pos': CONFIG.TOOLTIPS.encoder.pos,
                'encoder.delta': CONFIG.TOOLTIPS.encoder.delta,
                'button.pressed': CONFIG.TOOLTIPS.button.pressed,
                'button.event': CONFIG.TOOLTIPS.button.event
            },
            formatters: {
                'encoder.pos': (v) => v,
                'encoder.delta': (v) => v > 0 ? `+${v}` : v,
                'button.pressed': (v) => v ? '🔴 PRESSED' : '⚪ RELEASED',
                'button.event': (v) => v || '--'
            },
            statePath: 'nodes.*',
            multiDomain: true // Special flag for cross-domain signals
        });
        this.components.encoderButtonTable.init();

        // LED Ring Visualizer
        this.components.ledRingViz = new LEDRingViz('ledRingContainer', this.stateManager);
        this.components.ledRingViz.init();

        // Signal Chart
        this.components.signalChart = new SignalChart('signalPlotContainer', this.stateManager, this.chart);
        this.components.signalChart.init();

        // MQTT Debugger
        this.components.mqttDebugger = new MQTTDebugger('mqttDebuggerContainer', this.stateManager);
        this.components.mqttDebugger.init();

        // Connection Status
        this.components.connectionStatus = new ConnectionStatus('connectionStatus', this.stateManager);
        this.components.connectionStatus.init();
    }

    /**
     * Setup MQTT client and message handlers
     */
    setupMQTT() {
        const wsUrl = `ws://${window.location.host}/ws/debug`;
        this.mqttClient = new MQTTClient(wsUrl, this.stateManager);
        
        const handlers = new StandardHandlers(this.stateManager);

        // Register handlers for each topic pattern
        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.AUDIO_FEATURES,
            (nodeId, payload, topic) => {
                this.discoverNode(nodeId);
                handlers.handleAudioFeatures(nodeId, payload);
                this.components.mqttDebugger.addMessage(topic, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.OCCUPANCY_STATE,
            (nodeId, payload, topic) => {
                this.discoverNode(nodeId);
                handlers.handleOccupancyState(nodeId, payload);
                this.components.mqttDebugger.addMessage(topic, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.RING_STATE,
            (nodeId, payload, topic) => {
                this.discoverNode(nodeId);
                handlers.handleRingState(nodeId, payload);
                this.components.mqttDebugger.addMessage(topic, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.ENCODER,
            (nodeId, payload, topic) => {
                console.log('[DebugApp] Encoder message:', topic, nodeId, payload);
                this.discoverNode(nodeId);
                handlers.handleEncoder(nodeId, payload);
                this.components.mqttDebugger.addMessage(topic, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.BUTTON,
            (nodeId, payload, topic) => {
                this.discoverNode(nodeId);
                handlers.handleButton(nodeId, payload);
                this.components.mqttDebugger.addMessage(topic, payload);
            }
        );

        this.mqttClient.registerHandler(
            CONFIG.TOPIC_PATTERNS.HEARTBEAT,
            (nodeId, payload, topic) => {
                this.discoverNode(nodeId);
                handlers.handleHeartbeat(nodeId, payload);
                // Don't add heartbeats to debugger (too noisy)
            }
        );

        // Connect
        this.mqttClient.connect();
    }

    /**
     * Setup UI event handlers (buttons, inputs, etc.)
     */
    setupEventHandlers() {
        // Time range buttons
        const timeButtons = document.querySelectorAll('.time-btn[data-duration]');
        timeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const duration = parseInt(btn.dataset.duration);
                this.components.signalChart.setTimeRange(duration);
                
                // Update active button
                timeButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });

        // Log scale toggle
        const logScaleBtn = document.getElementById('logScaleBtn');
        if (logScaleBtn) {
            logScaleBtn.addEventListener('click', () => {
                this.stateManager.update('config.logScale', !this.stateManager.get('config.logScale'));
                logScaleBtn.textContent = this.stateManager.get('config.logScale') ? '📊 Log' : '📊 Linear';
            });
        }

        // Add signal button
        const addSignalBtn = document.getElementById('addSignalBtn');
        const nodeSelector = document.getElementById('nodeSelector');
        const signalSelector = document.getElementById('signalSelector');
        
        if (addSignalBtn && nodeSelector && signalSelector) {
            addSignalBtn.addEventListener('click', () => {
                const node = nodeSelector.value;
                const path = signalSelector.value;
                
                if (node && path) {
                    this.components.signalChart.addSignal(node, path);
                    this.renderSignalList();
                }
            });
        }

        // Populate signal selector
        this.populateSignalSelector();
    }

    /**
     * Populate signal selector with available signals
     */
    populateSignalSelector() {
        const signalSelector = document.getElementById('signalSelector');
        if (!signalSelector) return;

        let html = '<option value="">Select Signal...</option>';
        
        Object.entries(CONFIG.SIGNAL_PATHS).forEach(([group, signals]) => {
            html += `<optgroup label="${this.capitalize(group)}">`;
            signals.forEach(({ value, label }) => {
                html += `<option value="${value}">${label}</option>`;
            });
            html += '</optgroup>';
        });

        signalSelector.innerHTML = html;
    }

    /**
     * Track discovered node
     * @param {string} nodeId - Node identifier
     */
    discoverNode(nodeId) {
        if (!this.discoveredNodes.has(nodeId)) {
            this.discoveredNodes.add(nodeId);
            this.updateNodeSelector();
        }
    }

    /**
     * Update node selector with discovered nodes
     */
    updateNodeSelector() {
        const nodeSelector = document.getElementById('nodeSelector');
        if (!nodeSelector) return;

        const nodes = Array.from(this.discoveredNodes).sort();
        const currentValue = nodeSelector.value;

        nodeSelector.innerHTML = '<option value="">Select Node...</option>';
        nodes.forEach(nodeId => {
            const opt = document.createElement('option');
            opt.value = nodeId;
            opt.textContent = nodeId;
            nodeSelector.appendChild(opt);
        });

        if (currentValue && nodes.includes(currentValue)) {
            nodeSelector.value = currentValue;
        }
    }

    /**
     * Render active signal list
     */
    renderSignalList() {
        const container = document.getElementById('activeSignals');
        if (!container) return;

        const signals = this.components.signalChart.getActiveSignals();
        
        if (signals.length === 0) {
            container.innerHTML = '<p style="color:#888">No signals selected</p>';
            return;
        }

        let html = '';
        signals.forEach(signal => {
            html += `
                <div class="signal-tag ${signal.visible ? '' : 'hidden'}">
                    <span class="signal-color" style="background:${signal.color}" 
                          onclick="window.debugApp.changeSignalColor('${signal.key}')"></span>
                    <span class="signal-name" onclick="window.debugApp.toggleSignal('${signal.key}')">${signal.key}</span>
                    <span class="signal-remove" onclick="window.debugApp.removeSignal('${signal.key}')">×</span>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    /**
     * Public API for signal management (called from onclick handlers)
     */
    toggleSignal(key) {
        this.components.signalChart.toggleSignal(key);
        this.renderSignalList();
    }

    removeSignal(key) {
        this.components.signalChart.removeSignal(key);
        this.renderSignalList();
    }

    changeSignalColor(key) {
        // Cycle through color palette
        const signals = this.components.signalChart.getActiveSignals();
        const signal = signals.find(s => s.key === key);
        if (signal) {
            const currentIdx = CONFIG.CHART.COLOR_PALETTE.indexOf(signal.color);
            const nextIdx = (currentIdx + 1) % CONFIG.CHART.COLOR_PALETTE.length;
            const newColor = CONFIG.CHART.COLOR_PALETTE[nextIdx];
            this.components.signalChart.changeColor(key, newColor);
            this.renderSignalList();
        }
    }

    /**
     * Load saved configuration
     */
    loadConfiguration() {
        // Load signal configuration
        this.components.signalChart.loadConfig();
        this.renderSignalList();

        // Subscribe to node changes to update selector
        this.stateManager.subscribe('nodes', () => {
            this.updateNodeSelector();
            this.renderSignalList(); // Update signal list when nodes change
        });
        
        // Initial node selector update
        this.updateNodeSelector();
    }

    /**
     * Helper: Capitalize string
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    /**
     * Destroy application and cleanup
     */
    destroy() {
        if (this.mqttClient) {
            this.mqttClient.close();
        }

        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
    }
}

// Export singleton instance
export default DebugApp;

