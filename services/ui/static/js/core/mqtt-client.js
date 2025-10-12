/**
 * MQTT Client
 * WebSocket-based MQTT message handling with routing
 */

import { CONFIG } from './config.js';
import { matchTopic, parseTopic } from './utils.js';

export class MQTTClient {
    constructor(url, stateManager) {
        this.url = url;
        this.stateManager = stateManager;
        this.ws = null;
        this.handlers = new Map(); // pattern -> handler function
        this.reconnectTimer = null;
        this.isConnected = false;
    }

    /**
     * Connect to WebSocket
     */
    connect() {
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => {
                console.log('[MQTT] WebSocket connected');
                this.isConnected = true;
                this.stateManager.update('connection.ws', true);
                
                if (this.reconnectTimer) {
                    clearTimeout(this.reconnectTimer);
                    this.reconnectTimer = null;
                }
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.routeMessage(data);
                } catch (error) {
                    console.error('[MQTT] Error parsing message:', error);
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('[MQTT] WebSocket error:', error);
                this.isConnected = false;
                this.stateManager.update('connection.ws', false);
            };
            
            this.ws.onclose = () => {
                console.log('[MQTT] WebSocket closed');
                this.isConnected = false;
                this.stateManager.update('connection.ws', false);
                
                // Attempt reconnect
                this.reconnectTimer = setTimeout(() => {
                    console.log('[MQTT] Attempting reconnect...');
                    this.connect();
                }, CONFIG.WS.RECONNECT_DELAY);
            };
        } catch (error) {
            console.error('[MQTT] Connection error:', error);
            this.isConnected = false;
            this.stateManager.update('connection.ws', false);
        }
    }

    /**
     * Register a message handler for a topic pattern
     * @param {RegExp} pattern - Topic pattern regex
     * @param {Function} handler - Handler function(nodeId, payload, fullTopic)
     */
    registerHandler(pattern, handler) {
        this.handlers.set(pattern, handler);
    }

    /**
     * Route incoming message to appropriate handler
     * @param {object} data - Message data {topic, payload}
     */
    routeMessage(data) {
        const { topic, payload } = data;
        
        // Mark MQTT as connected when we receive messages
        if (!this.stateManager.get('connection.mqtt')) {
            this.stateManager.update('connection.mqtt', true);
        }
        
        // Update message count
        const count = this.stateManager.get('ui.messageCount') || 0;
        this.stateManager.batchUpdate({
            'ui.messageCount': count + 1,
            'ui.lastUpdate': new Date()
        });
        
        // Try each registered handler
        let handled = false;
        for (const [pattern, handler] of this.handlers) {
            const nodeId = matchTopic(topic, pattern);
            if (nodeId) {
                try {
                    handler(nodeId, payload, topic);
                    handled = true;
                } catch (error) {
                    console.error(`[MQTT] Handler error for pattern ${pattern}:`, error);
                }
            }
        }
        
        if (!handled) {
            // console.log('[MQTT] Unhandled topic:', topic);
        }
    }

    /**
     * Send message (if needed for future bidirectional communication)
     * @param {string} topic - MQTT topic
     * @param {object} payload - Message payload
     */
    publish(topic, payload) {
        if (this.isConnected && this.ws) {
            try {
                this.ws.send(JSON.stringify({ topic, payload }));
            } catch (error) {
                console.error('[MQTT] Publish error:', error);
            }
        } else {
            console.warn('[MQTT] Cannot publish, not connected');
        }
    }

    /**
     * Close connection
     */
    close() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.isConnected = false;
        this.stateManager.update('connection.ws', false);
    }
}

/**
 * Standard message handlers for common topics
 */
export class StandardHandlers {
    constructor(stateManager) {
        this.stateManager = stateManager;
    }

    /**
     * Handle audio features message
     */
    handleAudioFeatures(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.audio`, payload);
    }

    /**
     * Handle occupancy state message
     */
    handleOccupancyState(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.occupancy`, payload);
    }

    /**
     * Handle ring state message
     */
    handleRingState(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.ring`, payload);
    }

    /**
     * Handle encoder input message
     */
    handleEncoder(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.encoder`, payload);
    }

    /**
     * Handle button input message
     */
    handleButton(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.button`, payload);
    }

    /**
     * Handle heartbeat message
     */
    handleHeartbeat(nodeId, payload) {
        this.stateManager.update(`nodes.${nodeId}.heartbeat`, payload);
    }
}

export default MQTTClient;

