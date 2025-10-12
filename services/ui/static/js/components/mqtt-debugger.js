/**
 * MQTT Debugger Component
 * Real-time MQTT message log with filtering
 */

import { BaseComponent } from './base-component.js';

export class MQTTDebugger extends BaseComponent {
    constructor(containerId, stateManager, maxMessages = 50) {
        super(containerId, stateManager);
        this.maxMessages = maxMessages;
        this.messages = []; // {timestamp, topic, payload}
        this.filter = '';
        this.filterInput = null;
        this.clearBtn = null;
        this.logElement = null;
    }

    init() {
        super.init();
        this.renderControls();
        this.logElement = this.container.querySelector('.mqtt-log');
    }

    setupSubscriptions() {
        // This component receives messages directly via addMessage()
        // rather than subscribing to state
    }

    /**
     * Render filter controls
     */
    renderControls() {
        const html = `
            <div class="mqtt-controls">
                <input type="text" 
                       id="mqttFilter" 
                       placeholder="Filter topics (substring or regex)..." 
                       class="filter-input">
                <button id="mqttClear" class="time-btn">Clear</button>
            </div>
            <div class="mqtt-log" id="mqttDebugger"></div>
        `;
        
        this.setHTML(html);
        
        // Setup event listeners
        this.filterInput = this.$('#mqttFilter');
        this.clearBtn = this.$('#mqttClear');
        
        if (this.filterInput) {
            this.filterInput.addEventListener('input', (e) => {
                this.filter = e.target.value;
                this.render();
            });
        }
        
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => {
                this.clear();
            });
        }
    }

    /**
     * Add a message to the log
     * @param {string} topic - MQTT topic
     * @param {object} payload - Message payload
     */
    addMessage(topic, payload) {
        const timestamp = new Date();
        this.messages.unshift({ timestamp, topic, payload });
        
        // Trim to max messages
        if (this.messages.length > this.maxMessages) {
            this.messages = this.messages.slice(0, this.maxMessages);
        }
        
        this.renderMessage(timestamp, topic, payload);
    }

    /**
     * Render a single message (prepend to log)
     * @param {Date} timestamp - Message timestamp
     * @param {string} topic - MQTT topic
     * @param {object} payload - Message payload
     */
    renderMessage(timestamp, topic, payload) {
        if (!this.logElement) return;
        
        // Check filter
        if (this.filter && !this.matchFilter(topic)) {
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'mqtt-message';
        
        const timeStr = timestamp.toLocaleTimeString();
        messageDiv.innerHTML = `
            <div class="mqtt-timestamp">${timeStr}</div>
            <div class="mqtt-topic">${this.escapeHtml(topic)}</div>
            <div class="mqtt-payload">${this.formatPayload(payload)}</div>
        `;
        
        this.logElement.insertBefore(messageDiv, this.logElement.firstChild);
        
        // Trim displayed messages
        while (this.logElement.children.length > this.maxMessages) {
            this.logElement.removeChild(this.logElement.lastChild);
        }
    }

    /**
     * Check if topic matches filter
     * @param {string} topic - Topic to check
     * @returns {boolean} True if matches
     */
    matchFilter(topic) {
        if (!this.filter) return true;
        
        try {
            const regex = new RegExp(this.filter);
            return regex.test(topic);
        } catch (error) {
            // If regex fails, fall back to substring match
            return topic.includes(this.filter);
        }
    }

    /**
     * Format payload for display
     * @param {object} payload - Payload object
     * @returns {string} Formatted HTML
     */
    formatPayload(payload) {
        try {
            return this.escapeHtml(JSON.stringify(payload, null, 2));
        } catch (error) {
            return this.escapeHtml(String(payload));
        }
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} str - String to escape
     * @returns {string} Escaped string
     */
    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    /**
     * Render all messages (used when filter changes)
     */
    render() {
        if (!this.logElement) return;
        
        this.logElement.innerHTML = '';
        
        this.messages.forEach(({ timestamp, topic, payload }) => {
            this.renderMessage(timestamp, topic, payload);
        });
    }

    /**
     * Clear all messages
     */
    clear() {
        this.messages = [];
        if (this.logElement) {
            this.logElement.innerHTML = '';
        }
    }
}

export default MQTTDebugger;

