/**
 * State Manager
 * Centralized state management with observer pattern
 */

import { getNestedValue, setNestedValue } from './utils.js';

export class StateManager {
    constructor() {
        this.state = {
            nodes: {},           // Per-node data: {node1: {audio: {}, occupancy: {}, ...}}
            signals: [],         // Active chart signals
            connection: {
                ws: false,
                mqtt: false
            },
            config: {
                timeRange: 30,
                logScale: false
            },
            ui: {
                messageCount: 0,
                lastUpdate: null
            }
        };
        
        this.subscribers = new Map(); // path -> Set of callbacks
    }

    /**
     * Subscribe to state changes at a specific path
     * @param {string} path - Dot-separated path or wildcard (e.g., 'nodes.*.audio')
     * @param {Function} callback - Called with (newValue, oldValue, fullPath)
     * @returns {Function} Unsubscribe function
     */
    subscribe(path, callback) {
        if (!this.subscribers.has(path)) {
            this.subscribers.set(path, new Set());
        }
        this.subscribers.get(path).add(callback);
        
        // Return unsubscribe function
        return () => {
            const subs = this.subscribers.get(path);
            if (subs) {
                subs.delete(callback);
                if (subs.size === 0) {
                    this.subscribers.delete(path);
                }
            }
        };
    }

    /**
     * Update state at path and notify subscribers
     * @param {string} path - Dot-separated path
     * @param {*} value - New value
     */
    update(path, value) {
        const oldValue = getNestedValue(this.state, path);
        setNestedValue(this.state, path, value);
        
        // Notify exact path subscribers
        this.notifySubscribers(path, value, oldValue);
        
        // Notify wildcard subscribers
        this.notifyWildcardSubscribers(path, value, oldValue);
    }

    /**
     * Get state value at path
     * @param {string} path - Dot-separated path
     * @returns {*} State value
     */
    get(path) {
        return getNestedValue(this.state, path);
    }

    /**
     * Get entire state (use cautiously)
     * @returns {object} Full state object
     */
    getAll() {
        return this.state;
    }

    /**
     * Batch update multiple paths
     * @param {object} updates - Map of path -> value
     */
    batchUpdate(updates) {
        Object.entries(updates).forEach(([path, value]) => {
            this.update(path, value);
        });
    }

    /**
     * Notify subscribers for exact path match
     */
    notifySubscribers(path, newValue, oldValue) {
        const subs = this.subscribers.get(path);
        if (subs) {
            subs.forEach(callback => {
                try {
                    callback(newValue, oldValue, path);
                } catch (error) {
                    console.error(`Error in subscriber for path ${path}:`, error);
                }
            });
        }
    }

    /**
     * Notify wildcard subscribers (e.g., 'nodes.*.audio' matches 'nodes.node1.audio')
     */
    notifyWildcardSubscribers(path, newValue, oldValue) {
        const pathParts = path.split('.');
        
        this.subscribers.forEach((subs, pattern) => {
            if (pattern.includes('*')) {
                const patternParts = pattern.split('.');
                
                if (this.matchWildcardPattern(pathParts, patternParts)) {
                    subs.forEach(callback => {
                        try {
                            callback(newValue, oldValue, path);
                        } catch (error) {
                            console.error(`Error in wildcard subscriber for pattern ${pattern}:`, error);
                        }
                    });
                }
            }
        });
    }

    /**
     * Check if path matches wildcard pattern
     * @param {string[]} pathParts - Actual path parts
     * @param {string[]} patternParts - Pattern parts (may contain *)
     * @returns {boolean} True if matches
     */
    matchWildcardPattern(pathParts, patternParts) {
        if (patternParts.length !== pathParts.length) return false;
        
        for (let i = 0; i < patternParts.length; i++) {
            if (patternParts[i] !== '*' && patternParts[i] !== pathParts[i]) {
                return false;
            }
        }
        
        return true;
    }

    /**
     * Clear all state (useful for reset/logout)
     */
    clear() {
        this.state = {
            nodes: {},
            signals: [],
            connection: { ws: false, mqtt: false },
            config: { timeRange: 30, logScale: false },
            ui: { messageCount: 0, lastUpdate: null }
        };
        this.notifyAllSubscribers();
    }

    /**
     * Notify all subscribers (for clear/reset)
     */
    notifyAllSubscribers() {
        this.subscribers.forEach((subs, path) => {
            const value = this.get(path);
            subs.forEach(callback => {
                try {
                    callback(value, null, path);
                } catch (error) {
                    console.error(`Error notifying subscriber for path ${path}:`, error);
                }
            });
        });
    }
}

export default StateManager;

