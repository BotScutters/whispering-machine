/**
 * Connection Status Component
 * Displays WebSocket and MQTT connection status
 */

import { BaseComponent } from './base-component.js';

export class ConnectionStatus extends BaseComponent {
    constructor(containerId, stateManager) {
        super(containerId, stateManager);
        this.wsConnected = false;
        this.mqttConnected = false;
    }

    setupSubscriptions() {
        // Subscribe to connection state changes
        this.subscribe('connection.ws', (newValue) => {
            this.wsConnected = newValue;
            this.render();
        });

        this.subscribe('connection.mqtt', (newValue) => {
            this.mqttConnected = newValue;
            this.render();
        });
    }

    render() {
        if (!this.container) return;

        const wsStatus = this.wsConnected ? 'connected' : 'disconnected';
        const mqttStatus = this.mqttConnected ? 'connected' : 'disconnected';

        const html = `
            <div class="indicator ${wsStatus}" title="WebSocket ${wsStatus}">
                <span class="indicator-label">WS</span>
                <span class="indicator-dot"></span>
            </div>
            <div class="indicator ${mqttStatus}" title="MQTT ${mqttStatus}">
                <span class="indicator-label">MQTT</span>
                <span class="indicator-dot"></span>
            </div>
        `;

        this.setHTML(html);
    }
}

export default ConnectionStatus;

