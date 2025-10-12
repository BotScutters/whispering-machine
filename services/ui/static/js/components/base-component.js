/**
 * Base Component
 * Abstract base class for all UI components
 */

export class BaseComponent {
    /**
     * @param {string} containerId - DOM element ID for this component
     * @param {StateManager} stateManager - Reference to state manager
     */
    constructor(containerId, stateManager = null) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.stateManager = stateManager;
        this.subscriptions = []; // Array of unsubscribe functions
        this.isInitialized = false;
        
        if (!this.container) {
            console.warn(`[${this.constructor.name}] Container #${containerId} not found`);
        }
    }

    /**
     * Initialize component (called after construction)
     * Override in subclass for custom initialization
     */
    init() {
        if (this.isInitialized) {
            console.warn(`[${this.constructor.name}] Already initialized`);
            return;
        }
        
        this.isInitialized = true;
        this.setupSubscriptions();
        this.render();
    }

    /**
     * Setup state subscriptions
     * Override in subclass to subscribe to relevant state paths
     */
    setupSubscriptions() {
        // Override in subclass
    }

    /**
     * Subscribe to state changes
     * @param {string} path - State path to subscribe to
     * @param {Function} callback - Callback function
     */
    subscribe(path, callback) {
        if (!this.stateManager) {
            console.warn(`[${this.constructor.name}] No state manager available for subscription`);
            return;
        }
        
        const unsubscribe = this.stateManager.subscribe(path, callback);
        this.subscriptions.push(unsubscribe);
    }

    /**
     * Update component with new data
     * Override in subclass for custom update logic
     * @param {*} data - New data
     */
    update(data) {
        // Override in subclass
        this.render();
    }

    /**
     * Render component to DOM
     * Override in subclass for custom rendering
     */
    render() {
        // Override in subclass
    }

    /**
     * Show component
     */
    show() {
        if (this.container) {
            this.container.style.display = '';
        }
    }

    /**
     * Hide component
     */
    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }

    /**
     * Enable component
     */
    enable() {
        if (this.container) {
            this.container.classList.remove('disabled');
        }
    }

    /**
     * Disable component
     */
    disable() {
        if (this.container) {
            this.container.classList.add('disabled');
        }
    }

    /**
     * Destroy component and clean up
     */
    destroy() {
        // Unsubscribe from all state subscriptions
        this.subscriptions.forEach(unsubscribe => unsubscribe());
        this.subscriptions = [];
        
        // Clear container
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        this.isInitialized = false;
    }

    /**
     * Helper: Create DOM element from HTML string
     * @param {string} html - HTML string
     * @returns {HTMLElement} DOM element
     */
    createElement(html) {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    }

    /**
     * Helper: Set container HTML
     * @param {string} html - HTML string
     */
    setHTML(html) {
        if (this.container) {
            this.container.innerHTML = html;
        }
    }

    /**
     * Helper: Append HTML to container
     * @param {string} html - HTML string
     */
    appendHTML(html) {
        if (this.container) {
            const element = this.createElement(html);
            this.container.appendChild(element);
        }
    }

    /**
     * Helper: Query selector within container
     * @param {string} selector - CSS selector
     * @returns {HTMLElement|null} Element or null
     */
    $(selector) {
        return this.container ? this.container.querySelector(selector) : null;
    }

    /**
     * Helper: Query selector all within container
     * @param {string} selector - CSS selector
     * @returns {NodeList} NodeList of elements
     */
    $$(selector) {
        return this.container ? this.container.querySelectorAll(selector) : [];
    }
}

export default BaseComponent;

