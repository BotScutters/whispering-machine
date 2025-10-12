/**
 * Utility Functions
 * Reusable helper functions
 */

/**
 * Decode RGB color from 32-bit integer
 * @param {number} colorVal - 32-bit color value (0x00RRGGBB)
 * @returns {{r: number, g: number, b: number}} RGB components
 */
export function decodeRGB(colorVal) {
    return {
        r: (colorVal >> 16) & 0xFF,
        g: (colorVal >> 8) & 0xFF,
        b: colorVal & 0xFF
    };
}

/**
 * Convert RGB to CSS color string
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255)
 * @param {number} b - Blue (0-255)
 * @returns {string} CSS rgb() string
 */
export function rgbToString(r, g, b) {
    return `rgb(${r},${g},${b})`;
}

/**
 * Boost RGB saturation for better visibility while preserving hue
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255)
 * @param {number} b - Blue (0-255)
 * @param {number} factor - Saturation boost factor (default: 0.8)
 * @returns {{r: number, g: number, b: number, brightness: number}}
 */
export function boostSaturation(r, g, b, factor = 0.8) {
    const maxChannel = Math.max(r, g, b);
    const brightness = maxChannel / 255;
    
    if (maxChannel > 0) {
        r = Math.min(255, Math.round(r * (255 / maxChannel) * factor));
        g = Math.min(255, Math.round(g * (255 / maxChannel) * factor));
        b = Math.min(255, Math.round(b * (255 / maxChannel) * factor));
    }
    
    return { r, g, b, brightness };
}

/**
 * Position tooltip within window bounds
 * @param {HTMLElement} element - Element to position tooltip relative to
 * @param {HTMLElement} tooltip - Tooltip element
 */
export function positionTooltip(element, tooltip) {
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    // Try to position above element
    let top = rect.top - tooltipRect.height - 10;
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    
    // Keep within window bounds horizontally
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    // If no room above, show below
    if (top < 10) {
        top = rect.bottom + 10;
    }
    
    tooltip.style.top = top + 'px';
    tooltip.style.left = left + 'px';
}

/**
 * Attach tooltips to elements with tooltip class
 * @param {HTMLElement} container - Container element to search within
 */
export function attachTooltips(container) {
    setTimeout(() => {
        container.querySelectorAll('.tooltip').forEach(el => {
            const tooltip = el.querySelector('.tooltiptext');
            if (tooltip) {
                el.addEventListener('mouseenter', () => {
                    positionTooltip(el, tooltip);
                });
            }
        });
    }, 100);
}

/**
 * Get nested property from object by path
 * @param {object} obj - Object to traverse
 * @param {string} path - Dot-separated path (e.g., 'audio.rms')
 * @returns {*} Value at path or null
 */
export function getNestedValue(obj, path) {
    const parts = path.split('.');
    let result = obj;
    
    for (const part of parts) {
        if (result === undefined || result === null) return null;
        result = result[part];
    }
    
    return result;
}

/**
 * Get nested value and convert to number for plotting
 * @param {object} obj - Object to traverse
 * @param {string} path - Dot-separated path
 * @returns {number|null} Numeric value or null
 */
export function getNestedValueAsNumber(obj, path) {
    const result = getNestedValue(obj, path);
    
    if (result === undefined || result === null) return null;
    
    // Convert boolean to number for plotting
    if (typeof result === 'boolean') return result ? 1 : 0;
    if (typeof result === 'number') return result;
    
    return null;
}

/**
 * Set nested property in object by path
 * @param {object} obj - Object to modify
 * @param {string} path - Dot-separated path
 * @param {*} value - Value to set
 */
export function setNestedValue(obj, path, value) {
    const parts = path.split('.');
    const last = parts.pop();
    let current = obj;
    
    console.log(`[setNestedValue] path=${path}, parts=[${parts.join(', ')}], last=${last}`);
    
    for (const part of parts) {
        if (!(part in current)) {
            console.log(`[setNestedValue] Creating ${part} in current object`);
            current[part] = {};
        }
        current = current[part];
        console.log(`[setNestedValue] Moved to ${part}, current is now:`, current);
    }
    
    console.log(`[setNestedValue] Setting ${last} =`, value);
    current[last] = value;
    console.log(`[setNestedValue] Final current:`, current);
}

/**
 * Parse MQTT topic to extract components
 * @param {string} topic - MQTT topic (e.g., 'party/houseA/node1/audio/features')
 * @returns {{house: string, node: string, domain: string, signal: string} | null}
 */
export function parseTopic(topic) {
    const parts = topic.split('/');
    if (parts.length < 5) return null;
    
    return {
        house: parts[1],
        node: parts[2],
        domain: parts[3],
        signal: parts[4]
    };
}

/**
 * Format timestamp to local time string
 * @param {number} ts_ms - Unix timestamp in milliseconds
 * @returns {string} Formatted time string
 */
export function formatTimestamp(ts_ms) {
    return new Date(ts_ms).toLocaleTimeString();
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function calls
 * @param {Function} func - Function to throttle
 * @param {number} limit - Minimum time between calls in ms
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Check if topic matches pattern
 * @param {string} topic - MQTT topic
 * @param {RegExp} pattern - Topic pattern regex
 * @returns {string|null} Matched node ID or null
 */
export function matchTopic(topic, pattern) {
    const match = topic.match(pattern);
    return match ? match[1] : null;
}

export default {
    decodeRGB,
    rgbToString,
    boostSaturation,
    positionTooltip,
    attachTooltips,
    getNestedValue,
    getNestedValueAsNumber,
    setNestedValue,
    parseTopic,
    formatTimestamp,
    debounce,
    throttle,
    matchTopic
};

