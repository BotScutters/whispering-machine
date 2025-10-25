/**
 * Core Configuration
 * Centralized constants, schemas, and configuration data
 */

export const CONFIG = {
    // LED Ring Modes
    RING_MODES: {
        0: 'OFF',
        1: 'IDLE_BREATHING',
        2: 'AUDIO_REACTIVE',
        3: 'RAINBOW',
        4: 'AURORA',
        5: 'OCCUPANCY_PULSE'
    },

    // Signal Definitions
    SIGNALS: {
        AUDIO: ['rms', 'zcr', 'low', 'mid', 'high'],
        OCCUPANCY: ['occupied', 'activity', 'transitions'],
        ENCODER: ['pos', 'delta'],
        BUTTON: ['pressed', 'event']
    },

    // Signal Paths for Chart Selector
    SIGNAL_PATHS: {
        audio: [
            { value: 'audio.rms', label: 'RMS (loudness)' },
            { value: 'audio.zcr', label: 'ZCR (zero-crossing rate)' },
            { value: 'audio.low', label: 'Low Band (0-300Hz)' },
            { value: 'audio.mid', label: 'Mid Band (300-3000Hz)' },
            { value: 'audio.high', label: 'High Band (3000Hz+)' }
        ],
        occupancy: [
            { value: 'occupancy.occupied', label: 'Occupied (0/1)' },
            { value: 'occupancy.activity', label: 'Activity (0.0-1.0)' },
            { value: 'occupancy.transitions', label: 'Transitions (per sec)' }
        ],
        encoder: [
            { value: 'encoder.pos', label: 'Position' },
            { value: 'encoder.delta', label: 'Delta' }
        ]
    },

    // Tooltips
    TOOLTIPS: {
        audio: {
            rms: 'Root Mean Square - overall loudness (typical: 0.0001-0.01)<br>Higher values = louder sound<br><strong>Use:</strong> Volume detection, audio reactivity',
            zcr: 'Zero-Crossing Rate - frequency content indicator (typical: 0.0-0.3)<br>Higher values = more high-frequency content<br><strong>Use:</strong> Speech detection, audio classification',
            low: 'Low frequency band energy (0-300 Hz, typical: 0.0-0.02)<br>Bass, rumble, low-pitched sounds<br><strong>Use:</strong> Bass detection, subwoofer control',
            mid: 'Mid frequency band energy (300-3000 Hz, typical: 0.0-0.05)<br>Speech, most musical instruments<br><strong>Use:</strong> Voice detection, melody tracking',
            high: 'High frequency band energy (3000+ Hz, typical: 0.0-0.01)<br>Treble, cymbals, consonants<br><strong>Use:</strong> Brightness detection, clarity monitoring'
        },
        occupancy: {
            occupied: 'Boolean occupancy state - true when motion detected',
            activity: 'Activity level 0.0-1.0 based on motion over last 10 seconds',
            transitions: 'Number of motion state changes in last second'
        },
        encoder: {
            pos: 'Absolute encoder position',
            delta: 'Change in position since last update'
        },
        button: {
            pressed: 'Current button state (true = pressed)',
            event: 'Last button event type (press/release)'
        }
    },

    // MQTT Topic Patterns
    TOPIC_PATTERNS: {
        AUDIO_FEATURES: /^party\/[^/]+\/([^/]+)\/audio\/features$/,
        OCCUPANCY_STATE: /^party\/[^/]+\/([^/]+)\/occupancy\/state$/,
        RING_STATE: /^party\/[^/]+\/([^/]+)\/ring\/state$/,
        ENCODER: /^party\/[^/]+\/([^/]+)\/input\/encoder$/,
        BUTTON: /^party\/[^/]+\/([^/]+)\/input\/button$/,
        HEARTBEAT: /^party\/[^/]+\/([^/]+)\/sys\/heartbeat$/,
        LLM_OBSERVATIONS: /^party\/[^/]+\/llm_agent\/observations\/observation$/,
        LLM_TRANSCRIPTS: /^party\/[^/]+\/llm_agent\/transcripts\/transcript$/
    },

    // Chart Configuration
    CHART: {
        TIME_RANGES: [
            { value: 5, label: '5s' },
            { value: 30, label: '30s' },
            { value: 60, label: '1m' },
            { value: 300, label: '5m' },
            { value: 3600, label: '1h' }
        ],
        DEFAULT_TIME_RANGE: 30,
        COLOR_PALETTE: [
            '#00ff88', // Green
            '#ff8800', // Orange
            '#ff0044', // Red
            '#0088ff', // Blue
            '#00ffff', // Cyan
            '#ff00ff', // Pink
            '#88ff00', // Lime
            '#ffaa00', // Amber
            '#8800ff', // Purple
            '#ff0088', // Magenta
            '#00ffaa', // Teal
            '#ff4400'  // Deep Orange
        ],
        UPDATE_INTERVAL: 300, // ms
        MAX_DATA_AGE: 3600000 // 1 hour in ms
    },

    // WebSocket Configuration
    WS: {
        RECONNECT_DELAY: 1000,
        HEARTBEAT_INTERVAL: 30000
    },

    // LocalStorage Keys
    STORAGE: {
        SIGNAL_CONFIG: 'whispering_machine_signal_config',
        CHART_TIME_RANGE: 'whispering_machine_time_range',
        LOG_SCALE: 'whispering_machine_log_scale'
    }
};

export default CONFIG;

