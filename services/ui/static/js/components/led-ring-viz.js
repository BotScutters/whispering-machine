/**
 * LED Ring Visualizer Component
 * Renders LED ring state with per-node circular visualization
 */

import { BaseComponent } from './base-component.js';
import { decodeRGB, boostSaturation, rgbToString } from '../core/utils.js';
import { CONFIG } from '../core/config.js';

export class LEDRingViz extends BaseComponent {
    constructor(containerId, stateManager) {
        super(containerId, stateManager);
        this.ringData = {}; // nodeId -> ring state
    }

    setupSubscriptions() {
        // Subscribe to ring state updates for all nodes
        this.subscribe('nodes.*.ring', (newValue, oldValue, path) => {
            const nodeId = path.split('.')[1];
            this.ringData[nodeId] = newValue;
            this.render();
        });
    }

    render() {
        if (!this.container) return;

        const nodes = Object.keys(this.ringData).sort();
        
        if (nodes.length === 0) {
            this.setHTML('<p style="color:#888">No ring data yet...</p>');
            return;
        }

        // Build table with columns for each node
        let html = '<table class="status-table"><thead><tr><th>Metric</th>';
        nodes.forEach(node => {
            html += `<th>${node}</th>`;
        });
        html += '</tr></thead><tbody>';

        // LED Ring visualization row
        html += '<tr><td class="signal-name">Ring</td>';
        nodes.forEach(node => {
            html += '<td>' + this.renderRing(this.ringData[node]) + '</td>';
        });
        html += '</tr>';

        // Mode row
        html += '<tr><td class="signal-name">Mode</td>';
        nodes.forEach(node => {
            const mode = this.ringData[node]?.mode || 0;
            html += `<td>${CONFIG.RING_MODES[mode] || mode}</td>`;
        });
        html += '</tr>';

        // Brightness row
        html += '<tr><td class="signal-name">Brightness</td>';
        nodes.forEach(node => {
            const brightness = this.ringData[node]?.brightness || 0;
            html += `<td>${(brightness * 100).toFixed(0)}%</td>`;
        });
        html += '</tr>';

        // Speed row
        html += '<tr><td class="signal-name">Speed</td>';
        nodes.forEach(node => {
            const speed = this.ringData[node]?.speed || 1.0;
            html += `<td>${speed.toFixed(2)}x</td>`;
        });
        html += '</tr>';

        html += '</tbody></table>';
        this.setHTML(html);
    }

    /**
     * Render individual ring visualization
     * @param {object} ringState - Ring state data
     * @returns {string} SVG HTML string
     */
    renderRing(ringState) {
        if (!ringState) return '<svg width="120" height="120"></svg>';

        const pixels = ringState.pixels || [];
        const pixelCount = ringState.pixel_count || pixels.length || 8;

        let svg = '<svg width="120" height="120" viewBox="0 0 120 120" style="transform:rotate(-90deg)">';
        svg += '<circle cx="60" cy="60" r="50" fill="none" stroke="#333" stroke-width="1"/>';

        for (let i = 0; i < pixelCount; i++) {
            const angle = (i / pixelCount) * 2 * Math.PI;
            const x = 60 + Math.cos(angle) * 50;
            const y = 60 + Math.sin(angle) * 50;

            // Decode RGB from 32-bit color value
            const colorVal = pixels[i] !== undefined ? pixels[i] : 0;
            let { r, g, b } = decodeRGB(colorVal);

            // Boost saturation for visibility while preserving hue
            if (r + g + b > 0) {
                const boosted = boostSaturation(r, g, b);
                r = boosted.r;
                g = boosted.g;
                b = boosted.b;
                const brightness = boosted.brightness;

                const color = rgbToString(r, g, b);
                const glowIntensity = brightness * 8;
                const glow = brightness > 0.1 ? `drop-shadow(0 0 ${glowIntensity}px ${color})` : '';

                svg += `<circle cx="${x}" cy="${y}" r="5" fill="${color}" style="filter:${glow}"/>`;
            } else {
                svg += `<circle cx="${x}" cy="${y}" r="5" fill="#111"/>`;
            }
        }

        svg += '</svg>';
        return svg;
    }
}

export default LEDRingViz;

