# T-019: Debug UI Refactoring - Modular Architecture

## Goal
Refactor the debug UI from a monolithic 1500+ line HTML file into a clean, modular, reusable architecture that can be shared with the future party tracker UI.

## Current State Problems

### Architecture Issues
1. **Monolithic file**: Single 1500+ line `debug.html` with all code inline
2. **No separation of concerns**: HTML, CSS, and JavaScript all mixed
3. **Tight coupling**: Components directly manipulate each other's state
4. **Code duplication**: Similar patterns repeated for each status table
5. **Hard to test**: No module boundaries or testable units
6. **Inconsistent patterns**: Different panels use different update mechanisms

### Specific Pain Points
- **Status tables**: Audio, Occupancy, Encoder, Button, Ring all follow similar patterns but implemented separately
- **Chart management**: Modular signal plotting logic embedded in main class
- **MQTT handling**: Message routing logic deeply nested in `handleDebugMessage`
- **State management**: Global state scattered across multiple properties
- **Configuration**: Signal definitions, mode names, etc. hardcoded throughout

## Proposed Architecture

### Directory Structure
```
services/ui/
├── static/
│   ├── index.html                 # Landing page
│   ├── debug.html                 # Debug UI (refactored)
│   ├── party.html                 # Future party tracker UI
│   ├── css/
│   │   ├── common.css            # Shared styles
│   │   ├── debug.css             # Debug-specific styles
│   │   └── components/           # Component-specific styles
│   │       ├── status-table.css
│   │       ├── led-ring.css
│   │       └── chart-panel.css
│   └── js/
│       ├── lib/                  # External dependencies
│       │   └── chart.bundle.min.js
│       ├── core/                 # Core utilities (reusable)
│       │   ├── mqtt-client.js    # MQTT WebSocket handling
│       │   ├── state-manager.js  # Centralized state management
│       │   ├── config.js         # Constants, mode names, schemas
│       │   └── utils.js          # Helper functions
│       ├── components/           # Reusable UI components
│       │   ├── base-component.js     # Abstract base class
│       │   ├── status-table.js       # Generic status table component
│       │   ├── led-ring-viz.js       # LED ring visualization
│       │   ├── signal-chart.js       # Modular signal plotting
│       │   ├── mqtt-debugger.js      # MQTT message log
│       │   └── connection-status.js  # Connection indicators
│       └── pages/                # Page-specific orchestration
│           ├── debug-app.js      # Debug UI main app
│           └── party-app.js      # Future party tracker app
```

### Core Principles

#### 1. Component-Based Architecture
**Base Component Pattern**:
```javascript
// components/base-component.js
class BaseComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.state = {};
        this.init();
    }
    
    init() {} // Override in subclass
    update(data) {} // Override in subclass
    render() {} // Override in subclass
    destroy() {} // Cleanup
}
```

**Generic Status Table**:
```javascript
// components/status-table.js
class StatusTable extends BaseComponent {
    constructor(containerId, config) {
        super(containerId);
        this.config = config; // {signals, tooltips, formatters, nodeColumn}
    }
    
    update(nodesData) {
        // Generic table rendering for any node-based data
        // Automatically handles: sorting, tooltips, formatting
    }
}
```

**Usage Example**:
```javascript
// Audio status table
const audioTable = new StatusTable('audioStatusTable', {
    signals: ['rms', 'zcr', 'low', 'mid', 'high'],
    tooltips: CONFIG.AUDIO_TOOLTIPS,
    formatters: {
        rms: (v) => v.toFixed(6),
        zcr: (v) => v.toFixed(6),
        // ...
    },
    nodeColumn: true
});

// Occupancy status table (reuses same component!)
const occupancyTable = new StatusTable('occupancyTable', {
    signals: ['occupied', 'activity', 'transitions'],
    tooltips: CONFIG.OCCUPANCY_TOOLTIPS,
    formatters: {
        occupied: (v) => v ? '✅ YES' : '⬜ NO',
        activity: (v) => (v * 100).toFixed(1) + '%',
        transitions: (v) => v
    },
    nodeColumn: true
});
```

#### 2. Centralized State Management
```javascript
// core/state-manager.js
class StateManager {
    constructor() {
        this.state = {
            nodes: {},        // Per-node data: {node1: {audio: {}, occupancy: {}, ...}}
            signals: [],      // Active chart signals
            connection: {},   // WS/MQTT status
            config: {}        // User preferences
        };
        this.subscribers = new Map();
    }
    
    subscribe(path, callback) {
        // path: 'nodes.node1.audio.rms' or 'signals'
        // callback called when that path changes
    }
    
    update(path, value) {
        // Update state and notify subscribers
    }
    
    get(path) {
        // Retrieve state value by path
    }
}
```

#### 3. MQTT Message Routing
```javascript
// core/mqtt-client.js
class MQTTClient {
    constructor(url, stateManager) {
        this.ws = new WebSocket(url);
        this.stateManager = stateManager;
        this.handlers = new Map(); // topic pattern -> handler function
    }
    
    registerHandler(pattern, handler) {
        // pattern: 'party/+/+/audio/features'
        // handler: (nodeId, domain, signal, payload) => {}
        this.handlers.set(pattern, handler);
    }
    
    routeMessage(topic, payload) {
        // Parse topic, match pattern, call appropriate handler
        // Handler updates state via stateManager
    }
}
```

#### 4. Configuration as Data
```javascript
// core/config.js
export const CONFIG = {
    RING_MODES: {
        0: 'OFF',
        1: 'IDLE_BREATHING',
        2: 'AUDIO_REACTIVE',
        3: 'RAINBOW',
        4: 'AURORA',
        5: 'OCCUPANCY_PULSE'
    },
    
    AUDIO_SIGNALS: ['rms', 'zcr', 'low', 'mid', 'high'],
    
    AUDIO_TOOLTIPS: {
        rms: 'Root Mean Square - overall loudness (0.0001-0.01)',
        zcr: 'Zero-Crossing Rate - frequency content indicator',
        // ...
    },
    
    SIGNAL_PATHS: {
        audio: ['audio.rms', 'audio.zcr', 'audio.low', 'audio.mid', 'audio.high'],
        occupancy: ['occupancy.occupied', 'occupancy.activity', 'occupancy.transitions'],
        encoder: ['encoder.pos', 'encoder.delta']
    },
    
    TOPIC_PATTERNS: {
        AUDIO_FEATURES: 'party/+/+/audio/features',
        OCCUPANCY_STATE: 'party/+/+/occupancy/state',
        RING_STATE: 'party/+/+/ring/state',
        // ...
    }
};
```

### Implementation Strategy

#### Phase 1: Extract Core Utilities ✓
**Goal**: Create reusable foundation (no UI changes yet)

**Tasks**:
1. Create directory structure
2. Extract `core/config.js` with all constants
3. Extract `core/utils.js` with helper functions (RGB decode, tooltip positioning, etc.)
4. Extract `core/state-manager.js` with centralized state
5. Extract `core/mqtt-client.js` with message routing
6. **Validation**: Debug UI still works identically

#### Phase 2: Component Extraction ✓
**Goal**: Modularize UI components

**Tasks**:
1. Create `components/base-component.js` abstract class
2. Extract `components/status-table.js` - generic table renderer
3. Refactor Audio Status to use StatusTable
4. Refactor Occupancy Status to use StatusTable
5. Refactor Encoder & Button Status to use StatusTable *(unify with others)*
6. Extract `components/led-ring-viz.js` for ring visualization
7. Extract `components/signal-chart.js` for modular plotting
8. Extract `components/mqtt-debugger.js` for message log
9. Extract `components/connection-status.js` for indicators
10. **Validation**: Debug UI still works identically

#### Phase 3: Page Orchestration ✓
**Goal**: Clean separation of concerns

**Tasks**:
1. Create `pages/debug-app.js` as main orchestrator
2. Instantiate components, wire up state subscriptions
3. Handle component lifecycle (init, update, destroy)
4. Reduce `debug.html` to minimal template + script imports
5. **Validation**: Debug UI still works identically

#### Phase 4: CSS Refactoring ✓
**Goal**: Modular, maintainable styles

**Tasks**:
1. Extract `css/common.css` for shared styles
2. Extract component-specific CSS files
3. Use CSS custom properties (variables) for theming
4. Ensure consistent spacing, colors, typography
5. **Validation**: Debug UI looks identical

#### Phase 5: Future-Proofing ✓
**Goal**: Prepare for expansion

**Tasks**:
1. Add node type detection (ESP32 vs RPi)
2. Dynamic signal discovery (auto-populate signal selector)
3. Pluggable component system (easy to add new panels)
4. Schema-driven rendering (define signals in config, render automatically)
5. **Validation**: Can add new node type without code changes

### Specific Improvements

#### Encoder & Button Status Consolidation
**Current**: Custom cards with inline styles
**Proposed**: Use StatusTable with custom formatters

```javascript
const encoderTable = new StatusTable('encoderStatus', {
    signals: ['pos', 'delta'],
    tooltips: CONFIG.ENCODER_TOOLTIPS,
    formatters: {
        pos: (v) => v,
        delta: (v) => v > 0 ? `+${v}` : v
    },
    nodeColumn: true,
    groupBy: 'node' // Rows per node instead of signals per row
});

const buttonTable = new StatusTable('buttonStatus', {
    signals: ['pressed', 'event', 'last_event_ts'],
    tooltips: CONFIG.BUTTON_TOOLTIPS,
    formatters: {
        pressed: (v) => v ? '🔴 PRESSED' : '⚪ RELEASED',
        event: (v) => v,
        last_event_ts: (v) => new Date(v).toLocaleTimeString()
    },
    nodeColumn: true,
    groupBy: 'node'
});
```

This unifies the pattern while maintaining current functionality.

### Benefits

#### Immediate
- **Maintainability**: Easy to find and fix bugs
- **Readability**: Each file has single, clear purpose
- **Testability**: Components can be unit tested
- **Consistency**: All panels follow same patterns

#### Long-Term
- **Reusability**: Components shared between debug and party UIs
- **Extensibility**: Add new node types/signals with config changes only
- **Scalability**: Easy to add new panels/features
- **Collaboration**: Multiple people can work on different components

### Acceptance Criteria

**Functional**:
- ✅ Debug UI looks and behaves identically to current version
- ✅ All existing features work (charts, tables, MQTT log, etc.)
- ✅ Configuration stored in localStorage still works
- ✅ WebSocket connections and updates still work
- ✅ No regression in performance

**Structural**:
- ✅ No single file > 300 lines (except generated/vendor code)
- ✅ All components extend BaseComponent or use clear interface
- ✅ State management centralized in StateManager
- ✅ MQTT routing centralized in MQTTClient
- ✅ All constants/config in core/config.js
- ✅ Zero code duplication for status table rendering

**Future-Ready**:
- ✅ Can add new node type by adding config entry only
- ✅ Can add new signal panel with < 50 lines of code
- ✅ Components can be imported into party tracker UI
- ✅ Encoder/Button status follows same pattern as other tables

### Testing Plan

**Manual Testing** (after each phase):
1. Hard-refresh browser, verify all panels render
2. Test MQTT message flow (audio, occupancy, encoder, ring)
3. Test modular chart (add/remove signals, change time window, log scale)
4. Test MQTT debugger (filter, clear)
5. Test connection status indicators
6. Test localStorage persistence (reload page, config preserved)
7. Test with node1 offline (graceful handling)
8. Test with both nodes active (proper per-node updates)

**Regression Checklist**:
- [ ] Audio status table updates in real-time
- [ ] Occupancy status table shows activity/transitions
- [ ] LED ring visualizer shows correct colors with glow
- [ ] Encoder & button status shows per-node state
- [ ] Modular chart plots any signal, sorted alphabetically
- [ ] Time window controls work (5s, 30s, 1m, 5m, 1h)
- [ ] Log scale toggle works
- [ ] MQTT debugger shows all messages, filter works
- [ ] Connection indicators show correct status
- [ ] Tooltips stay within window bounds
- [ ] Signal config persists across reloads

### Non-Goals (Out of Scope)

- ❌ Changing debug UI functionality or appearance (except minor consistency fixes)
- ❌ Building the party tracker UI (separate ticket)
- ❌ Backend/aggregator changes
- ❌ Firmware changes
- ❌ Adding new features to debug UI
- ❌ TypeScript conversion (stay with vanilla JS)
- ❌ Build system (no webpack/vite, keep simple)

### Estimated Effort

- **Phase 1**: 3-4 hours (core utilities)
- **Phase 2**: 6-8 hours (component extraction)
- **Phase 3**: 2-3 hours (page orchestration)
- **Phase 4**: 2-3 hours (CSS refactoring)
- **Phase 5**: 2-3 hours (future-proofing)
- **Total**: ~15-20 hours of focused work

### Success Metrics

**Before**: 1 file, 1500+ lines, hard to maintain
**After**: ~15 files, avg 100 lines each, easy to maintain

**Before**: Adding new signal panel = 200+ lines, lots of copy-paste
**After**: Adding new signal panel = 20 lines (config + instantiation)

**Before**: Supporting new node type = scattered changes across file
**After**: Supporting new node type = add config entry, auto-discovered

---

## Implementation Notes

### Key Design Decisions

1. **Vanilla JavaScript**: No framework to keep it simple and fast
2. **ES6 Modules**: Use `<script type="module">` for clean imports
3. **Class-based components**: Clear inheritance and lifecycle
4. **Observer pattern**: State changes trigger component updates automatically
5. **Configuration over code**: Prefer data-driven rendering

### Example: Adding a New Status Panel

**Before** (current monolithic approach):
```javascript
// Add ~150 lines of code directly in debug.html:
// - HTML structure
// - Update method with custom logic
// - Event handlers
// - Tooltip setup
// - Sorting logic
// etc.
```

**After** (modular approach):
```javascript
// 1. Add config (5 lines)
export const MY_NEW_SIGNALS = ['signal1', 'signal2', 'signal3'];
export const MY_NEW_TOOLTIPS = { ... };

// 2. Instantiate component (8 lines)
const myNewPanel = new StatusTable('myNewPanelContainer', {
    signals: CONFIG.MY_NEW_SIGNALS,
    tooltips: CONFIG.MY_NEW_TOOLTIPS,
    formatters: { ... },
    nodeColumn: true
});

// 3. Subscribe to state updates (3 lines)
stateManager.subscribe('nodes.*.mynewdomain', (data) => {
    myNewPanel.update(data);
});

// Done! Total: ~16 lines
```

### Migration Strategy

- Start with small, low-risk extractions (utils, config)
- Test thoroughly after each phase
- Keep git commits granular (easy to revert if needed)
- Maintain backward compatibility throughout
- Only merge when all tests pass


