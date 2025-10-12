/**
 * Signal Chart Component
 * Modular time-series chart for plotting any numeric signal from any node
 */

import { BaseComponent } from './base-component.js';
import { getNestedValue, getNestedValueAsNumber } from '../core/utils.js';
import { CONFIG } from '../core/config.js';

export class SignalChart extends BaseComponent {
    constructor(containerId, stateManager, chartInstance) {
        super(containerId, stateManager);
        this.chart = chartInstance; // Chart.js instance
        this.activeSignals = new Map(); // key -> {node, path, color, visible, data}
        this.timeRange = CONFIG.CHART.DEFAULT_TIME_RANGE;
        this.logScale = false;
        this.colorIndex = 0;
        this.updateInterval = null;
    }

    init() {
        super.init();
        // Start periodic chart updates
        this.updateInterval = setInterval(() => {
            this.updateChart();
        }, CONFIG.CHART.UPDATE_INTERVAL);
    }

    setupSubscriptions() {
        // Subscribe to any node data updates using wildcards for each domain
        const domains = ['audio', 'occupancy', 'encoder', 'ring'];
        domains.forEach(domain => {
            this.subscribe(`nodes.*.${domain}`, (newValue) => {
                // Any node data changed, update signal data
                this.updateSignalData();
            });
        });

        // Subscribe to config changes
        this.subscribe('config.timeRange', (newValue) => {
            this.timeRange = newValue || CONFIG.CHART.DEFAULT_TIME_RANGE;
            this.updateChart();
        });

        this.subscribe('config.logScale', (newValue) => {
            this.logScale = newValue || false;
            this.toggleLogScale();
        });
    }

    /**
     * Add a signal to the chart
     * @param {string} node - Node ID
     * @param {string} path - Signal path (e.g., 'audio.rms')
     * @param {string} color - Optional color (auto-assigned if not provided)
     * @returns {string} Signal key
     */
    addSignal(node, path, color = null) {
        const key = `${node}/${path}`;
        
        if (this.activeSignals.has(key)) {
            console.warn(`Signal ${key} already exists`);
            return key;
        }

        const signalColor = color || this.getNextColor();
        
        this.activeSignals.set(key, {
            node,
            path,
            color: signalColor,
            visible: true,
            data: [] // {x: Date, y: number}
        });

        this.updateChart();
        this.saveConfig();
        
        return key;
    }

    /**
     * Remove a signal from the chart
     * @param {string} key - Signal key (node/path)
     */
    removeSignal(key) {
        this.activeSignals.delete(key);
        this.updateChart();
        this.saveConfig();
    }

    /**
     * Toggle signal visibility
     * @param {string} key - Signal key
     */
    toggleSignal(key) {
        const signal = this.activeSignals.get(key);
        if (signal) {
            signal.visible = !signal.visible;
            this.updateChart();
        }
    }

    /**
     * Change signal color
     * @param {string} key - Signal key
     * @param {string} color - New color
     */
    changeColor(key, color) {
        const signal = this.activeSignals.get(key);
        if (signal) {
            signal.color = color;
            this.updateChart();
            this.saveConfig();
        }
    }

    /**
     * Set time range
     * @param {number} seconds - Time range in seconds
     */
    setTimeRange(seconds) {
        this.timeRange = seconds;
        if (this.stateManager) {
            this.stateManager.update('config.timeRange', seconds);
        }
        this.updateChart();
    }

    /**
     * Toggle log scale
     */
    toggleLogScale() {
        if (!this.chart) return;

        const yAxis = this.chart.options.scales.y;
        yAxis.type = this.logScale ? 'logarithmic' : 'linear';
        
        this.chart.update('none');
    }

    /**
     * Update signal data from current state
     */
    updateSignalData() {
        const now = new Date();
        const maxAge = CONFIG.CHART.MAX_DATA_AGE;

        this.activeSignals.forEach((signal, key) => {
            const nodeData = this.stateManager?.get(`nodes.${signal.node}`);
            if (!nodeData) {
                console.log(`[SignalChart] No data for node ${signal.node}`);
                return;
            }

            const value = getNestedValueAsNumber(nodeData, signal.path);
            if (value !== null && value !== undefined) {
                signal.data.push({ x: now, y: value });
                console.log(`[SignalChart] Added data point for ${key}: ${value}`);
                
                // Trim old data
                const cutoff = new Date(now.getTime() - maxAge);
                signal.data = signal.data.filter(d => d.x >= cutoff);
            } else {
                console.log(`[SignalChart] No value for ${key} (path: ${signal.path})`);
            }
        });
    }

    /**
     * Update chart with current data
     */
    updateChart() {
        if (!this.chart) return;

        const now = new Date();
        const cutoff = new Date(now.getTime() - this.timeRange * 1000);

        // Build datasets from active signals (sorted alphabetically)
        const datasets = [];
        const sortedSignals = Array.from(this.activeSignals.entries())
            .sort((a, b) => a[0].localeCompare(b[0]));

        sortedSignals.forEach(([key, signal]) => {
            if (!signal.visible) return;

            const filteredData = signal.data.filter(d => d.x >= cutoff);
            datasets.push({
                label: key,
                data: filteredData,
                borderColor: signal.color,
                backgroundColor: 'transparent',
                tension: 0.1,
                parsing: {
                    xAxisKey: 'x',
                    yAxisKey: 'y'
                }
            });
        });

        this.chart.data.datasets = datasets;

        // Keep x-axis time range consistent
        if (this.chart.options?.scales?.x) {
            this.chart.options.scales.x.min = cutoff;
            this.chart.options.scales.x.max = now;
        }

        this.chart.update('none');
    }

    /**
     * Get next color from palette
     * @returns {string} Color
     */
    getNextColor() {
        const color = CONFIG.CHART.COLOR_PALETTE[this.colorIndex % CONFIG.CHART.COLOR_PALETTE.length];
        this.colorIndex++;
        return color;
    }

    /**
     * Get all active signals
     * @returns {Array} Array of signal objects
     */
    getActiveSignals() {
        return Array.from(this.activeSignals.entries()).map(([key, signal]) => ({
            key,
            ...signal
        }));
    }

    /**
     * Save configuration to localStorage
     */
    saveConfig() {
        const config = Array.from(this.activeSignals.entries()).map(([key, signal]) => ({
            node: signal.node,
            path: signal.path,
            color: signal.color
        }));

        try {
            localStorage.setItem(CONFIG.STORAGE.SIGNAL_CONFIG, JSON.stringify(config));
        } catch (error) {
            console.error('Error saving signal config:', error);
        }
    }

    /**
     * Load configuration from localStorage
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem(CONFIG.STORAGE.SIGNAL_CONFIG);
            if (saved) {
                const config = JSON.parse(saved);
                config.forEach(({ node, path, color }) => {
                    this.addSignal(node, path, color);
                });
            }
        } catch (error) {
            console.error('Error loading signal config:', error);
        }
    }

    /**
     * Clear all signals
     */
    clearSignals() {
        this.activeSignals.clear();
        this.updateChart();
        this.saveConfig();
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        super.destroy();
    }
}

export default SignalChart;

