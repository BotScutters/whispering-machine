/**
 * Status Table Component
 * Generic table renderer for node-based status data
 */

import { BaseComponent } from './base-component.js';
import { attachTooltips } from '../core/utils.js';

export class StatusTable extends BaseComponent {
    /**
     * @param {string} containerId - Container element ID
     * @param {StateManager} stateManager - State manager
     * @param {object} config - Configuration
     * @param {string[]} config.signals - Signal names to display
     * @param {object} config.tooltips - Tooltips for each signal
     * @param {object} config.formatters - Formatter functions for each signal
     * @param {boolean} config.nodeColumn - Show nodes as columns (default: true)
     * @param {string} config.groupBy - 'signal' (default) or 'node'
     * @param {string} config.statePath - State path to subscribe to (e.g., 'nodes.*.audio')
     */
    constructor(containerId, stateManager, config) {
        super(containerId, stateManager);
        this.config = {
            signals: config.signals || [],
            tooltips: config.tooltips || {},
            formatters: config.formatters || {},
            nodeColumn: config.nodeColumn !== false,
            groupBy: config.groupBy || 'signal',
            statePath: config.statePath || 'nodes'
        };
        this.data = {}; // nodeId -> signal data
        this.lastStructure = null; // For detecting structural changes
    }

    setupSubscriptions() {
        // Subscribe to node data updates
        this.subscribe(this.config.statePath, (newValue, oldValue, path) => {
            // Extract node ID from path (e.g., 'nodes.node1.audio' -> 'node1')
            const pathParts = path.split('.');
            if (pathParts.length >= 2) {
                const nodeId = pathParts[1];
                this.updateNodeData(nodeId, newValue);
            }
        });
    }

    /**
     * Update data for a specific node
     * @param {string} nodeId - Node identifier
     * @param {object} data - Signal data
     */
    updateNodeData(nodeId, data) {
        this.data[nodeId] = data;
        this.render();
    }

    /**
     * Render table
     */
    render() {
        if (!this.container) return;

        const nodes = Object.keys(this.data).sort();
        
        if (nodes.length === 0) {
            this.setHTML('<p style="color:#888">No data yet...</p>');
            return;
        }

        // Check if structure changed (avoid full rebuild on value changes)
        const currentStructure = nodes.join(',');
        const structureChanged = this.lastStructure !== currentStructure;

        if (this.config.groupBy === 'node') {
            this.renderByNode(nodes, structureChanged);
        } else {
            this.renderBySignal(nodes, structureChanged);
        }

        this.lastStructure = currentStructure;
    }

    /**
     * Render table grouped by signal (signals as rows, nodes as columns)
     */
    renderBySignal(nodes, structureChanged) {
        if (structureChanged) {
            // Full rebuild
            let html = '<table class="status-table"><thead><tr><th>Signal</th>';
            nodes.forEach(node => {
                html += `<th>${node}</th>`;
            });
            html += '</tr></thead><tbody>';

            this.config.signals.forEach(signal => {
                html += `<tr><td class="signal-name tooltip">${signal}`;
                if (this.config.tooltips[signal]) {
                    html += `<span class="tooltiptext">${this.config.tooltips[signal]}</span>`;
                }
                html += '</td>';
                
                nodes.forEach(node => {
                    html += `<td data-node="${node}" data-signal="${signal}">--</td>`;
                });
                
                html += '</tr>';
            });

            html += '</tbody></table>';
            this.setHTML(html);
            attachTooltips(this.container);
        }

        // Update values only
        this.config.signals.forEach(signal => {
            nodes.forEach(node => {
                const cell = this.$(`td[data-node="${node}"][data-signal="${signal}"]`);
                if (cell) {
                    const value = this.data[node]?.[signal];
                    cell.textContent = this.formatValue(signal, value);
                }
            });
        });
    }

    /**
     * Render table grouped by node (nodes as rows, signals as columns)
     */
    renderByNode(nodes, structureChanged) {
        if (structureChanged) {
            // Full rebuild
            let html = '<table class="status-table"><thead><tr><th>Node</th>';
            this.config.signals.forEach(signal => {
                html += `<th class="tooltip">${signal}`;
                if (this.config.tooltips[signal]) {
                    html += `<span class="tooltiptext">${this.config.tooltips[signal]}</span>`;
                }
                html += '</th>';
            });
            html += '</tr></thead><tbody>';

            nodes.forEach(node => {
                html += `<tr><td class="signal-name">${node}</td>`;
                this.config.signals.forEach(signal => {
                    html += `<td data-node="${node}" data-signal="${signal}">--</td>`;
                });
                html += '</tr>';
            });

            html += '</tbody></table>';
            this.setHTML(html);
            attachTooltips(this.container);
        }

        // Update values only
        nodes.forEach(node => {
            this.config.signals.forEach(signal => {
                const cell = this.$(`td[data-node="${node}"][data-signal="${signal}"]`);
                if (cell) {
                    const value = this.data[node]?.[signal];
                    cell.textContent = this.formatValue(signal, value);
                }
            });
        });
    }

    /**
     * Format value using configured formatter or default
     * @param {string} signal - Signal name
     * @param {*} value - Value to format
     * @returns {string} Formatted value
     */
    formatValue(signal, value) {
        if (value === undefined || value === null) {
            return '--';
        }

        const formatter = this.config.formatters[signal];
        if (formatter && typeof formatter === 'function') {
            try {
                return formatter(value);
            } catch (error) {
                console.error(`Error formatting ${signal}:`, error);
                return String(value);
            }
        }

        // Default formatting
        if (typeof value === 'number') {
            return value.toFixed(6);
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        return String(value);
    }
}

export default StatusTable;

