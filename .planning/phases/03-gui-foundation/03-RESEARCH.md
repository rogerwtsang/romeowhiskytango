# Phase 3: GUI Foundation - Research

**Researched:** 2026-01-18
**Domain:** Tkinter dashboard layouts and consolidated UI patterns
**Confidence:** HIGH

## Summary

Research focused on best practices for transforming a 9-tab Tkinter application into a unified dashboard layout with resizable panels, collapsible sections, and dynamic panel creation. The standard approach uses native Tkinter widgets (ttk.PanedWindow for resizable panels, ttk.LabelFrame for card-based grouping, grid geometry manager for responsive layouts) combined with proper state management and widget lifecycle handling.

The Tkinter ecosystem provides robust support for dashboard-style interfaces without requiring third-party libraries. The ttk themed widget set offers modern appearance through built-in themes ('clam', 'alt', 'default'), with optional enhancement via libraries like ttkbootstrap for more polished aesthetics. Critical considerations include memory leak prevention during dynamic widget creation/destruction, proper use of grid weights for responsive layouts, and JSON-based state persistence for session restoration.

**Primary recommendation:** Use ttk.PanedWindow as the root container for major dashboard sections, ttk.LabelFrame for collapsible/card-based panels, grid geometry manager with weight configuration for responsive layouts, and implement proper widget destruction patterns to avoid memory leaks.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| tkinter | Python 3.10+ stdlib | GUI framework | Built into Python, cross-platform, no dependencies |
| tkinter.ttk | Python 3.10+ stdlib | Themed widgets | Modern appearance, native look-and-feel, styling separation |
| json | Python stdlib | State persistence | Simple, human-readable config storage |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ttkbootstrap | 1.10+ | Modern theming | Optional: If enhanced visual polish desired (Bootstrap-inspired themes) |
| matplotlib | 3.7.0+ (already used) | Charts/visualizations | Already in project for results display |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PanedWindow | Manual Frame + Splitter | PanedWindow is native, handles all resize logic, manual approach requires complex event handling |
| JSON persistence | pickle/shelve | JSON is human-readable, version-control friendly, safer; pickle has security concerns |
| Native ttk themes | ttkbootstrap/CustomTkinter | Native themes are dependency-free and platform-native; custom libs add visual polish but increase complexity |

**Installation:**
```bash
# Core - already installed (stdlib)
# No additional dependencies required

# Optional enhancement
pip install ttkbootstrap  # Only if enhanced theming desired
```

## Architecture Patterns

### Recommended Project Structure
```
src/gui/
├── dashboard/           # New dashboard implementation
│   ├── main_dashboard.py       # Root dashboard container
│   ├── setup_panel.py          # Setup panel (collapsible)
│   ├── lineup_panel.py         # Lineup panel(s) - dynamically created
│   └── results_panel.py        # Results display panel
├── widgets/             # Reusable widgets (existing)
│   ├── collapsible_frame.py    # NEW: Collapsible container
│   ├── summary_card.py          # Existing card widget
│   └── ...
└── utils/               # Utilities (existing)
    ├── config_manager.py        # Existing - extend for session state
    └── ...
```

### Pattern 1: Resizable Dashboard with PanedWindow
**What:** ttk.PanedWindow container with weighted panes for major sections
**When to use:** Primary dashboard structure where users need to adjust panel sizes
**Example:**
```python
# Source: https://tkdocs.com/tutorial/complex.html
import tkinter as tk
from tkinter import ttk

class Dashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Vertical PanedWindow for main layout
        self.main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Top section: Setup panel (collapsible)
        self.setup_frame = ttk.LabelFrame(self.main_paned, text="Setup", padding=10)
        self.main_paned.add(self.setup_frame, weight=0)  # Fixed initial size

        # Middle section: Horizontal split for Lineup/Results
        self.content_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.content_paned, weight=1)  # Takes remaining space

        # Lineup panel(s)
        self.lineup_frame = ttk.LabelFrame(self.content_paned, text="Lineup", padding=10)
        self.content_paned.add(self.lineup_frame, weight=1)

        # Results panel
        self.results_frame = ttk.LabelFrame(self.content_paned, text="Results", padding=10)
        self.content_paned.add(self.results_frame, weight=1)
```

### Pattern 2: Collapsible Panel
**What:** LabelFrame with toggle button to show/hide content
**When to use:** Setup/Assumptions section that should maximize workspace when hidden
**Example:**
```python
# Source: https://www.geeksforgeeks.org/python/collapsible-pane-in-tkinter-python/
class CollapsibleFrame(ttk.Frame):
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)

        # Header with toggle button
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X, pady=(0, 2))

        self.toggle_btn = ttk.Button(
            self.header,
            text="▼ " + text,
            command=self.toggle,
            width=20
        )
        self.toggle_btn.pack(side=tk.LEFT)

        # Content frame
        self.content = ttk.Frame(self, padding=10)
        self.content.pack(fill=tk.BOTH, expand=True)

        self.collapsed = False

    def toggle(self):
        if self.collapsed:
            self.content.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text=self.toggle_btn['text'].replace('▶', '▼'))
        else:
            self.content.pack_forget()
            self.toggle_btn.config(text=self.toggle_btn['text'].replace('▼', '▶'))
        self.collapsed = not self.collapsed
```

### Pattern 3: Dynamic Panel Creation/Removal
**What:** Add/remove panels for comparison mode without memory leaks
**When to use:** Compare mode toggle that creates second lineup panel
**Example:**
```python
# Source: https://www.plus2net.com/python/tkinter-dynamic-entry.php
class DashboardManager:
    def __init__(self, parent):
        self.parent = parent
        self.lineup_panels = []  # Track active panels

    def add_lineup_panel(self):
        """Add a new lineup panel for comparison"""
        panel = LineupPanel(self.content_paned)
        self.content_paned.add(panel, weight=1)
        self.lineup_panels.append(panel)
        return panel

    def remove_lineup_panel(self, panel):
        """Remove a lineup panel and clean up"""
        if panel in self.lineup_panels:
            # Remove from paned window
            self.content_paned.forget(panel)
            # Destroy widget to free memory
            panel.destroy()
            # Remove from tracking list
            self.lineup_panels.remove(panel)
```

### Pattern 4: Grid Layout with Weight Configuration
**What:** Responsive grid layout that resizes with window
**When to use:** Interior panel layouts (lineup details, results display)
**Example:**
```python
# Source: https://www.pythontutorial.net/tkinter/tkinter-grid/
class LineupPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)  # Main content column
        self.columnconfigure(1, weight=0)  # Control buttons column
        self.rowconfigure(0, weight=0)     # Header
        self.rowconfigure(1, weight=1)     # Content (expands)
        self.rowconfigure(2, weight=0)     # Footer/controls

        # Header
        ttk.Label(self, text="Batting Order", font=('TkDefaultFont', 12, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(0, 10)
        )

        # Content area (expands)
        self.content = ttk.Frame(self)
        self.content.grid(row=1, column=0, sticky='nsew', padx=(0, 5))

        # Control buttons
        self.controls = ttk.Frame(self)
        self.controls.grid(row=1, column=1, sticky='ns')

        # Footer with Run button
        self.run_btn = ttk.Button(self, text="▶ Run Simulation")
        self.run_btn.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
```

### Pattern 5: Inline Progress Indicator
**What:** ttk.Progressbar placed near action button for contextual feedback
**When to use:** Run Simulation button with progress display
**Example:**
```python
# Source: https://www.pythontutorial.net/tkinter/tkinter-progressbar/
class LineupPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Footer with controls
        footer = ttk.Frame(self)
        footer.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # Run button
        self.run_btn = ttk.Button(footer, text="▶ Run Simulation", command=self.run)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(footer, mode='determinate', length=200)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress.pack_forget()  # Hide initially

        # Progress label
        self.progress_label = ttk.Label(footer, text="")
        self.progress_label.pack(side=tk.LEFT, padx=(10, 0))

    def update_progress(self, current, total):
        """Update progress during simulation"""
        if not self.progress.winfo_viewable():
            self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, after=self.run_btn)

        percentage = (current / total) * 100
        self.progress['value'] = percentage
        self.progress_label.config(text=f"{percentage:.1f}%")
        self.update()  # Force UI update
```

### Pattern 6: Session State Persistence
**What:** JSON-based session state storage for dashboard configuration
**When to use:** Session restoration on startup
**Example:**
```python
# Source: https://www.pythonforbiginners.com/2025/06/save-and-load-theme-preference-in.html
class SessionManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.session_file = config_manager.config_dir / 'last_session.json'

    def save_session(self, dashboard_state):
        """Save current dashboard state"""
        state = {
            'setup_collapsed': dashboard_state['setup_collapsed'],
            'paned_positions': {
                'main_vertical': dashboard_state['main_paned_pos'],
                'content_horizontal': dashboard_state['content_paned_pos']
            },
            'active_lineups': [
                lineup.serialize() for lineup in dashboard_state['lineup_panels']
            ],
            'compare_mode': dashboard_state['compare_mode']
        }

        with open(self.session_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load_session(self):
        """Load last session state"""
        if not self.session_file.exists():
            return None

        with open(self.session_file, 'r') as f:
            return json.load(f)

    def prompt_restore_session(self, parent):
        """Prompt user to restore last session"""
        from tkinter import messagebox

        if self.session_file.exists():
            return messagebox.askyesno(
                "Restore Session",
                "Restore your last session?",
                parent=parent
            )
        return False
```

### Anti-Patterns to Avoid
- **Mixing geometry managers:** Don't use pack(), grid(), and place() on widgets within the same parent frame
- **Creating widgets without tracking:** Always maintain references to dynamically created widgets in a list/dict for proper cleanup
- **Direct color configuration on ttk widgets:** Don't use `bg=`, `fg=` on ttk widgets; use ttk.Style instead
- **Continuous widget recreation:** Don't recreate widgets on every update; create once and update content (prevents memory leaks)
- **Blocking UI during long operations:** Always use threading (existing SimulationRunner pattern) to keep UI responsive

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Resizable panel dividers | Manual mouse event handling with Frame borders | ttk.PanedWindow | Handles all resize logic, drag cursor, min/max sizes, cross-platform behavior |
| Progress bar visualization | Canvas-based custom drawing | ttk.Progressbar | Native look, determinate/indeterminate modes, theme integration |
| State persistence format | Custom binary format or pickle | JSON with ConfigManager | Human-readable, version-control friendly, no security risks, already in codebase |
| Widget state management during updates | Manual enable/disable of individual widgets | Widget state hierarchy with parent.winfo_children() | Automatic propagation, less error-prone |
| Responsive layouts | Manual window resize event handlers | grid() with weight configuration | Automatic, declarative, handles all edge cases |

**Key insight:** Tkinter's built-in widget set is more capable than it appears. PanedWindow, ttk theming, and grid weights handle complex layout scenarios that often lead developers to seek third-party frameworks. The ecosystem has matured significantly; prefer stdlib solutions unless specific visual requirements demand enhancement libraries.

## Common Pitfalls

### Pitfall 1: Memory Leaks from Improper Widget Destruction
**What goes wrong:** Dynamically created widgets persist in memory even after being removed from display
**Why it happens:** `.pack_forget()` or `.grid_forget()` only hide widgets; they don't destroy the widget object or break parent references
**How to avoid:**
1. Always call `.destroy()` when removing widgets permanently
2. Clear references from tracking lists/dicts
3. For PanedWindow, use `.forget(widget)` then `.destroy()` on the widget
**Warning signs:** Memory usage steadily increases when toggling compare mode multiple times

```python
# BAD
def remove_panel(self, panel):
    self.paned_window.forget(panel)  # Widget still in memory!

# GOOD
def remove_panel(self, panel):
    self.paned_window.forget(panel)
    panel.destroy()  # Free memory
    if panel in self.panels:
        self.panels.remove(panel)  # Clear tracking reference
```

### Pitfall 2: StringVar Memory Leaks with Frequent Updates
**What goes wrong:** Rapidly updating tk.StringVar variables (e.g., progress labels) causes memory consumption to grow without release
**Why it happens:** Internal Tcl command references accumulate when StringVar objects are updated frequently
**How to avoid:**
1. Use direct label configuration (`label.config(text=...)`) instead of StringVar for frequently updated text
2. If StringVar is necessary, reuse the same instance rather than creating new ones
3. For progress indicators, update at reasonable intervals (not every iteration)
**Warning signs:** Memory usage grows during simulation even though simulation data is bounded

```python
# BAD
self.progress_var = tk.StringVar()
self.progress_label = ttk.Label(self, textvariable=self.progress_var)
# Later, in tight loop:
self.progress_var.set(f"{i}/{total}")  # Creates Tcl command leak

# GOOD
self.progress_label = ttk.Label(self, text="")
# Later, in loop (with throttling):
if i % 100 == 0:  # Update every 100 iterations
    self.progress_label.config(text=f"{i}/{total}")  # Direct config, no leak
```

### Pitfall 3: Mixing Geometry Managers in Same Parent
**What goes wrong:** Widgets disappear, layout breaks, or application hangs
**Why it happens:** pack(), grid(), and place() have conflicting layout algorithms; using multiple in same container creates undefined behavior
**How to avoid:**
1. Choose one geometry manager per container (grid recommended for dashboard)
2. Use nested frames if you need different managers for different sections
3. Document geometry manager choice at top of class
**Warning signs:** Widgets not appearing, "can't use geometry manager" exceptions, mysterious layout bugs

```python
# BAD
parent = ttk.Frame(root)
ttk.Label(parent, text="Label").pack()  # Using pack
ttk.Button(parent, text="Button").grid(row=0, column=0)  # ERROR: mixing with grid!

# GOOD
parent = ttk.Frame(root)
# Use grid throughout
ttk.Label(parent, text="Label").grid(row=0, column=0)
ttk.Button(parent, text="Button").grid(row=1, column=0)

# OR use nested frames
parent = ttk.Frame(root)
frame1 = ttk.Frame(parent)
frame1.pack(side=tk.TOP)
ttk.Label(frame1, text="Label").pack()  # pack within frame1

frame2 = ttk.Frame(parent)
frame2.pack(side=tk.BOTTOM)
ttk.Button(frame2, text="Button").grid(row=0, column=0)  # grid within frame2
```

### Pitfall 4: Forgetting Grid Weight Configuration
**What goes wrong:** Widgets don't resize with window; empty space appears instead of widgets expanding
**Why it happens:** Default weight is 0 (don't expand); at least one row and one column must have weight > 0 for expansion
**How to avoid:**
1. Configure weights immediately after grid layout setup
2. Use weight=1 for expandable rows/columns, weight=0 for fixed-size
3. Apply weights to the container, not the widgets
**Warning signs:** Resizing window shows gray space instead of widgets expanding

```python
# BAD
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)
ttk.Label(frame, text="Content").grid(row=0, column=0, sticky='nsew')
# Resizing window does nothing - no weights set!

# GOOD
frame = ttk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)
frame.columnconfigure(0, weight=1)  # Column expands
frame.rowconfigure(0, weight=1)     # Row expands
ttk.Label(frame, text="Content").grid(row=0, column=0, sticky='nsew')
# Now resizing window expands the label
```

### Pitfall 5: Not Using Sticky with Grid
**What goes wrong:** Widgets appear centered in their grid cells with unused space around them
**Why it happens:** Default sticky is '' (centered); widgets need sticky to fill cell or align to edges
**How to avoid:**
1. Use sticky='nsew' for widgets that should fill entire cell
2. Use sticky='w' or sticky='e' for left/right alignment
3. Use sticky='n' or sticky='s' for top/bottom alignment
4. Combine directions: sticky='ew' for horizontal fill, sticky='ns' for vertical fill
**Warning signs:** Widgets appear small and centered despite having large grid cells

```python
# BAD
ttk.Button(parent, text="Button").grid(row=0, column=0)
# Button appears small and centered in cell

# GOOD
ttk.Button(parent, text="Button").grid(row=0, column=0, sticky='ew')
# Button fills cell horizontally

# Or for full cell fill
ttk.Frame(parent).grid(row=0, column=0, sticky='nsew')
```

### Pitfall 6: Threading without update() for Progress
**What goes wrong:** Progress indicators don't update during long-running operations in background threads
**Why it happens:** Tkinter event loop doesn't process pending updates unless explicitly told
**How to avoid:**
1. Call `self.update()` or `self.update_idletasks()` after updating progress widgets
2. Existing SimulationRunner pattern already handles this; apply same pattern to new progress displays
3. Throttle updates (every N iterations) to avoid performance overhead
**Warning signs:** Progress bar stuck at 0% until simulation completes, then jumps to 100%

```python
# BAD
def update_progress(self, current, total):
    percentage = (current / total) * 100
    self.progress['value'] = percentage
    # Progress bar doesn't visually update until simulation completes!

# GOOD
def update_progress(self, current, total):
    percentage = (current / total) * 100
    self.progress['value'] = percentage
    self.update()  # Force Tkinter to process pending display updates
```

## Code Examples

Verified patterns from official sources:

### Complete Dashboard Structure
```python
# Source: Based on https://tkdocs.com/tutorial/complex.html and project patterns
import tkinter as tk
from tkinter import ttk

class MainDashboard(ttk.Frame):
    """Single-page dashboard replacing 9-tab structure"""

    def __init__(self, parent, config_manager, results_manager, sim_runner):
        super().__init__(parent)
        self.config_manager = config_manager
        self.results_manager = results_manager
        self.sim_runner = sim_runner

        # State tracking
        self.lineup_panels = []
        self.compare_mode = False

        self._create_layout()
        self._prompt_session_restore()

    def _create_layout(self):
        """Create main dashboard layout"""
        # Main vertical split: Setup at top, content below
        self.main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Setup panel (collapsible)
        self.setup_panel = CollapsibleFrame(self.main_paned, text="Setup & Assumptions")
        self.main_paned.add(self.setup_panel, weight=0)
        self._populate_setup_panel()

        # Content area: horizontal split for lineup(s) and results
        self.content_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.content_paned, weight=1)

        # Initial single lineup panel
        lineup_panel = self._create_lineup_panel()
        self.content_paned.add(lineup_panel, weight=1)

        # Results panel
        self.results_panel = ResultsPanel(self.content_paned, results_manager=self.results_manager)
        self.content_paned.add(self.results_panel, weight=1)

    def _create_lineup_panel(self):
        """Create a lineup panel (reused for compare mode)"""
        panel = LineupPanel(
            self.content_paned,
            on_run=self._run_simulation,
            on_compare=self.toggle_compare_mode
        )
        self.lineup_panels.append(panel)
        return panel

    def toggle_compare_mode(self):
        """Toggle between single and comparison mode"""
        self.compare_mode = not self.compare_mode

        if self.compare_mode:
            # Add second lineup panel
            panel = self._create_lineup_panel()
            self.content_paned.insert(1, panel, weight=1)
        else:
            # Remove second lineup panel
            if len(self.lineup_panels) > 1:
                panel = self.lineup_panels[1]
                self.content_paned.forget(panel)
                panel.destroy()
                self.lineup_panels.remove(panel)

    def save_session(self):
        """Save current dashboard state"""
        state = {
            'setup_collapsed': self.setup_panel.collapsed,
            'compare_mode': self.compare_mode,
            'lineups': [panel.get_lineup_data() for panel in self.lineup_panels]
        }

        session_file = self.config_manager.config_dir / 'last_session.json'
        with open(session_file, 'w') as f:
            json.dump(state, f, indent=2)
```

### Collapsible Frame Widget
```python
# Source: https://www.geeksforgeeks.org/python/collapsible-pane-in-tkinter-python/
class CollapsibleFrame(ttk.Frame):
    """Frame with collapsible content section"""

    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)

        self.collapsed = False

        # Header with toggle button
        self.header = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.header.pack(fill=tk.X, pady=(0, 2))

        self.toggle_btn = ttk.Button(
            self.header,
            text=f"▼ {text}",
            command=self.toggle,
            width=20
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5, pady=2)

        # Content frame
        self.content = ttk.Frame(self, padding=10, relief=tk.SUNKEN, borderwidth=1)
        self.content.pack(fill=tk.BOTH, expand=True)

    def toggle(self):
        """Toggle content visibility"""
        if self.collapsed:
            self.content.pack(fill=tk.BOTH, expand=True)
            self.toggle_btn.config(text=self.toggle_btn['text'].replace('▶', '▼'))
        else:
            self.content.pack_forget()
            self.toggle_btn.config(text=self.toggle_btn['text'].replace('▼', '▶'))
        self.collapsed = not self.collapsed

    def get_content_frame(self):
        """Get the content frame for adding widgets"""
        return self.content
```

### Grid Layout with Weights
```python
# Source: https://www.pythontutorial.net/tkinter/tkinter-grid/
class LineupPanel(ttk.Frame):
    """Panel for lineup configuration and simulation control"""

    def __init__(self, parent, on_run=None, on_compare=None):
        super().__init__(parent, padding=10)
        self.on_run = on_run
        self.on_compare = on_compare

        # Configure grid weights
        self.columnconfigure(0, weight=1)  # Main content
        self.columnconfigure(1, weight=0)  # Controls
        self.rowconfigure(0, weight=0)     # Header
        self.rowconfigure(1, weight=1)     # Lineup (expands)
        self.rowconfigure(2, weight=0)     # Run controls

        # Header with title and compare button
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        ttk.Label(header, text="Batting Order", font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)

        if on_compare:
            ttk.Button(header, text="Compare Mode", command=on_compare).pack(side=tk.RIGHT)

        # Lineup builder (reuse existing widget)
        self.lineup_builder = LineupBuilder(self)
        self.lineup_builder.grid(row=1, column=0, sticky='nsew', padx=(0, 5))

        # Player controls
        controls = ttk.Frame(self)
        controls.grid(row=1, column=1, sticky='ns')

        ttk.Button(controls, text="Add →", width=10).pack(pady=2)
        ttk.Button(controls, text="↑ Move Up", width=10).pack(pady=2)
        ttk.Button(controls, text="↓ Move Down", width=10).pack(pady=2)
        ttk.Button(controls, text="✕ Remove", width=10).pack(pady=2)

        # Run controls footer
        footer = ttk.Frame(self)
        footer.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        self.run_btn = ttk.Button(footer, text="▶ Run Simulation", command=self._on_run)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Progress (initially hidden)
        self.progress = ttk.Progressbar(footer, mode='determinate', length=200)
        self.progress_label = ttk.Label(footer, text="")

    def update_progress(self, current, total):
        """Update inline progress indicator"""
        if not self.progress.winfo_viewable():
            self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.progress_label.pack(side=tk.LEFT, padx=(10, 0))

        percentage = (current / total) * 100
        self.progress['value'] = percentage
        self.progress_label.config(text=f"{percentage:.0f}%")
        self.update()

    def hide_progress(self):
        """Hide progress indicator"""
        self.progress.pack_forget()
        self.progress_label.pack_forget()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tab-based navigation (ttk.Notebook) | Single-page dashboard with resizable panels | 2020s trend toward unified dashboards | Reduces navigation overhead, allows simultaneous view of related data |
| Direct widget configuration (bg=, fg=) | ttk.Style-based theming | ttk introduction (Python 2.7/3.1) | Separation of concerns, consistent theming, native look-and-feel |
| Manual frame resizing with mouse events | ttk.PanedWindow | ttk standardization | Cross-platform consistency, less code, better UX |
| pickle for config storage | JSON | Security awareness increase (2010s) | Human-readable, version-control friendly, no code execution risks |
| Custom progress indicators | ttk.Progressbar with determinate mode | ttk themed widgets | Native appearance, less code, platform consistency |

**Deprecated/outdated:**
- Using Tkinter widgets instead of ttk equivalents (affects theming and appearance consistency)
- Per-widget color configuration on ttk widgets (doesn't work; use ttk.Style instead)
- Creating new StringVar instances for each update (memory leak; reuse or use direct config)

## Open Questions

Things that couldn't be fully resolved:

1. **PanedWindow sash position persistence**
   - What we know: PanedWindow provides `.sashpos(index)` to query and set sash positions
   - What's unclear: Whether positions should be stored as absolute pixels or percentage of window size for cross-session reliability
   - Recommendation: Store as percentage of parent width/height; recalculate on restore based on current window geometry

2. **Optimal comparison mode UX pattern**
   - What we know: User context specifies "explicit Compare Mode toggle/button" and "full side-by-side with difference indicators"
   - What's unclear: Whether comparison should allow 2+ lineups or restrict to exactly 2
   - Recommendation: Start with exactly 2 lineups (simpler state management); can expand to N lineups in future phase if needed

3. **Results panel detail level**
   - What we know: Current run_tab shows text results + histogram in separate tabs; user wants "balance information density and visual clarity"
   - What's unclear: Whether to show both simultaneously or use collapsible sections within Results panel
   - Recommendation: Use collapsible sections (Summary always visible, Details/Charts collapsible) to maximize key metrics visibility while allowing deep dives

## Sources

### Primary (HIGH confidence)
- [Python tkinter.ttk documentation](https://docs.python.org/3/library/tkinter.ttk.html) - Official ttk widget reference
- [TkDocs: Styles and Themes](https://tkdocs.com/tutorial/styles.html) - Authoritative ttk styling guide
- [TkDocs: Organizing Complex Interfaces](https://tkdocs.com/tutorial/complex.html) - PanedWindow and layout patterns
- [TkDocs: Grid Geometry Manager](http://tkdocs.com/tutorial/grid.html) - Grid configuration best practices

### Secondary (MEDIUM confidence)
- [Tkinter Best Practices: Optimizing Performance and Code Structure](https://medium.com/tomtalkspython/tkinter-best-practices-optimizing-performance-and-code-structure-c49d1919fbb4) - Code organization patterns
- [Collapsible Pane in Tkinter | Python - GeeksforGeeks](https://www.geeksforgeeks.org/python/collapsible-pane-in-tkinter-python/) - Collapsible frame implementation
- [Python Tkinter Toplevel Widget: Creating Dynamic Windows - Bomberbot](https://www.bomberbot.com/python/python-tkinter-toplevel-widget-creating-dynamic-windows/) - Dynamic widget creation
- [Learn Python: Save and Load Theme Preference in Tkinter](https://www.pythonforbiginners.com/2025/06/save-and-load-theme-preference-in.html) - Session persistence pattern (2025)
- [Mastering Tkinter's Grid Method: Comprehensive Guide](https://www.bomberbot.com/python/mastering-tkinters-grid-method-a-comprehensive-guide-for-python-gui-developers/) - Grid weights and sticky

### Tertiary (LOW confidence - flagged for validation)
- [GitHub - Dream-Pixels-Forge/TkModernThemes](https://github.com/Dream-Pixels-Forge/TkModernThemes) - Modern theme library (2025) - Not verified for stability
- [Memory Leak with Frequent Updates to tk.StringVar](https://github.com/python/cpython/issues/123193) - Known issue, no official fix timeline

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Python stdlib components with extensive documentation
- Architecture patterns: HIGH - Verified with official TkDocs and Python documentation
- Pitfalls: HIGH - Documented in official bug trackers and community knowledge bases
- Code examples: HIGH - Based on official documentation and verified patterns

**Research date:** 2026-01-18
**Valid until:** 60 days (stable stdlib, slow-moving changes)
