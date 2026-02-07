# Phase 5: Workflow Polish - Research

**Researched:** 2026-02-07
**Domain:** Tkinter UI polish, layout optimization, visual hierarchy
**Confidence:** HIGH

## Summary

This research investigates the Tkinter patterns needed to implement Phase 5 workflow polish features. The phase focuses on reducing friction through better defaults, improving visual hierarchy with spreadsheet-like lineup panels, implementing drag-and-drop reordering, and adding new visualization capabilities (radar charts, distribution overlays).

The existing codebase already uses ttk widgets, grid geometry manager, PanedWindow for resizable panels, and matplotlib for charts. The phase builds on these foundations without introducing new dependencies.

**Primary recommendation:** Use ttk.Treeview for the spreadsheet-like lineup panel (it already supports columns, selection, and can be configured for row reordering with mouse bindings), leverage matplotlib's polar projection for radar charts, and extend the existing chart_utils module with multi-distribution overlay functions.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| tkinter/ttk | Built-in | GUI framework | Already in use, no change |
| matplotlib | 3.7+ | Charts/visualization | Already in use for histograms |
| seaborn | 0.12+ | Statistical plots | Already in use for KDE overlays |
| numpy | 1.24+ | Data manipulation | Already in use for statistics |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| random | Built-in | Seed generation | Random seed when unlocked |
| tkinter.dnd | Built-in | Drag-drop (experimental) | NOT recommended - use mouse bindings |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| tk.Listbox | ttk.Treeview | Treeview supports columns; use for lineup panel |
| tkinter.dnd | Mouse event bindings | Mouse bindings more reliable, dnd module experimental |
| TkinterDnD2 | Mouse event bindings | External dependency unnecessary for simple reorder |

**Installation:**
```bash
# No new dependencies required
```

## Architecture Patterns

### Recommended Project Structure
```
src/gui/
├── dashboard/
│   ├── lineup_panel.py     # Refactor to Treeview-based panel
│   ├── setup_panel.py      # Add seed lock/unlock, default changes
│   └── results_panel.py    # Move histogram/contributions to Visuals
├── widgets/
│   ├── lineup_treeview.py  # NEW: Spreadsheet-like lineup widget
│   ├── seed_control.py     # NEW: Seed display with lock toggle
│   └── radar_chart.py      # NEW: Radar chart widget
└── utils/
    └── chart_utils.py      # Add multi-distribution overlay functions
```

### Pattern 1: Treeview for Spreadsheet-Like Display
**What:** Use ttk.Treeview with columns for tabular player data display
**When to use:** Any read-only tabular data with selectable rows
**Example:**
```python
# Source: https://tkdocs.com/tutorial/tree.html
import tkinter as tk
from tkinter import ttk

class LineupTreeview(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Define columns (excluding the implicit #0 tree column)
        columns = ('position', 'name', 'avg', 'obp', 'slg')

        self.tree = ttk.Treeview(self, columns=columns, show='headings')

        # Configure column headings
        self.tree.heading('position', text='Pos')
        self.tree.heading('name', text='Player')
        self.tree.heading('avg', text='AVG')
        self.tree.heading('obp', text='OBP')
        self.tree.heading('slg', text='SLG')

        # Configure column widths
        self.tree.column('position', width=50, anchor='center')
        self.tree.column('name', width=150, anchor='w')
        self.tree.column('avg', width=60, anchor='center')
        self.tree.column('obp', width=60, anchor='center')
        self.tree.column('slg', width=60, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
```

### Pattern 2: Drag-and-Drop Reordering with Mouse Bindings
**What:** Implement insert-style reordering using mouse events (not swap)
**When to use:** Reordering items in Listbox or Treeview
**Example:**
```python
# Source: https://apidemos.com/tkinter/tkinter-listbox/tkinter-drag-and-drop-the-items-in-the-listbox.html
class DraggableListbox(tk.Listbox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<Button-1>', self._on_press)
        self.bind('<B1-Motion>', self._on_motion)
        self.bind('<ButtonRelease-1>', self._on_release)
        self._drag_start_index = None
        self._drag_data = None

    def _on_press(self, event):
        """Start drag operation."""
        self._drag_start_index = self.nearest(event.y)
        if self._drag_start_index >= 0:
            self._drag_data = self.get(self._drag_start_index)

    def _on_motion(self, event):
        """Show insertion point during drag."""
        if self._drag_data is None:
            return
        # Update visual indicator (cursor, highlight line)
        target_index = self.nearest(event.y)
        # Could show insertion line indicator here

    def _on_release(self, event):
        """Complete drag - INSERT at target (not swap)."""
        if self._drag_data is None:
            return
        target_index = self.nearest(event.y)
        if target_index != self._drag_start_index:
            # Remove from old position
            self.delete(self._drag_start_index)
            # Insert at new position (insert behavior, not swap)
            self.insert(target_index, self._drag_data)
        self._drag_data = None
        self._drag_start_index = None
```

### Pattern 3: Seed Control Widget
**What:** Entry box with lock/unlock toggle and visual indicator
**When to use:** Random seed configuration with randomize-by-default behavior
**Example:**
```python
import random

class SeedControl(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # State: locked (editable, fixed) or unlocked (randomized each run)
        self.locked = False

        # Seed entry
        self.seed_entry = ttk.Entry(self, width=12)
        self.seed_entry.pack(side=tk.LEFT, padx=(0, 5))
        self._update_entry_state()

        # Lock toggle button
        self.lock_btn = ttk.Button(self, text="Unlock", width=8, command=self._toggle_lock)
        self.lock_btn.pack(side=tk.LEFT)

        # Generate initial random seed
        self._randomize_seed()

    def _toggle_lock(self):
        self.locked = not self.locked
        self._update_entry_state()
        if not self.locked:
            self._randomize_seed()

    def _update_entry_state(self):
        if self.locked:
            self.seed_entry.configure(state='normal')
            self.lock_btn.configure(text="Locked")
        else:
            self.seed_entry.configure(state='disabled')
            self.lock_btn.configure(text="Unlocked")

    def _randomize_seed(self):
        """Generate new random seed (called on each Run when unlocked)."""
        new_seed = random.randint(0, 2**31 - 1)
        self.seed_entry.configure(state='normal')
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(new_seed))
        if not self.locked:
            self.seed_entry.configure(state='disabled')

    def get_seed(self) -> int:
        """Get current seed value, randomizing if unlocked."""
        if not self.locked:
            self._randomize_seed()
        return int(self.seed_entry.get())
```

### Pattern 4: Window Sizing to Screen Dimensions
**What:** Set window to half-width, full-height based on screen
**When to use:** Application startup
**Example:**
```python
# Source: https://www.geeksforgeeks.org/getting-screens-height-and-width-using-tkinter-python/
def configure_window_size(root: tk.Tk):
    """Set window to half screen width, full screen height."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    window_width = screen_width // 2
    window_height = screen_height

    # Position at left edge
    x_position = 0
    y_position = 0

    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
```

### Pattern 5: Minimum Panel Width Constraint
**What:** Ensure panels don't shrink below usable size
**When to use:** PanedWindow layouts with resizable sections
**Example:**
```python
class ConstrainedPanedWindow(ttk.PanedWindow):
    def __init__(self, parent, min_left_width=250, **kwargs):
        super().__init__(parent, **kwargs)
        self.min_left_width = min_left_width
        self.bind('<Configure>', self._enforce_min_width)

    def _enforce_min_width(self, event=None):
        """Prevent left pane from shrinking below minimum."""
        try:
            current_pos = self.sashpos(0)
            if current_pos < self.min_left_width:
                self.sashpos(0, self.min_left_width)
        except tk.TclError:
            pass  # Ignore if sash doesn't exist yet
```

### Pattern 6: Radar Chart with Matplotlib
**What:** Polar plot for multi-variable player comparison
**When to use:** Comparing player profiles across dimensions (OBP, SLG, K%, etc.)
**Example:**
```python
# Source: https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

def create_radar_chart(ax, categories: list, values_dict: dict, title: str = None):
    """
    Create radar chart comparing multiple players.

    Args:
        ax: Matplotlib Axes with polar projection
        categories: List of stat names ['OBP', 'SLG', 'K%', ...]
        values_dict: {player_name: [value1, value2, ...]}
        title: Optional chart title
    """
    num_vars = len(categories)

    # Calculate angle for each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Complete the loop

    # Plot each player
    colors = plt.cm.Set2(np.linspace(0, 1, len(values_dict)))
    for (name, values), color in zip(values_dict.items(), colors):
        values_plot = values + values[:1]  # Complete the loop
        ax.plot(angles, values_plot, 'o-', linewidth=2, label=name, color=color)
        ax.fill(angles, values_plot, alpha=0.25, color=color)

    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)

    if title:
        ax.set_title(title)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
```

### Pattern 7: Multi-Distribution Overlay
**What:** Overlay 2-4 distribution histograms for lineup comparison
**When to use:** Comparing runs distributions of multiple lineups
**Example:**
```python
def create_multi_overlay(ax, data_dict: dict, bins: int = 30, title: str = None):
    """
    Overlay multiple distributions with transparency.

    Args:
        ax: Matplotlib Axes
        data_dict: {label: data_array} for each lineup
        bins: Number of histogram bins
        title: Optional title
    """
    # Limit to 4 distributions for clarity
    colors = ['steelblue', 'coral', 'forestgreen', 'darkorchid']

    # Calculate common bin edges
    all_data = np.concatenate(list(data_dict.values()))
    bin_edges = np.histogram_bin_edges(all_data, bins=bins)

    for i, (label, data) in enumerate(data_dict.items()):
        color = colors[i % len(colors)]
        ax.hist(
            data,
            bins=bin_edges,
            alpha=0.4,
            color=color,
            edgecolor=color,
            linewidth=1.5,
            histtype='stepfilled',
            label=f"{label} (mean: {np.mean(data):.1f})"
        )

    ax.set_xlabel('Runs per Season')
    ax.set_ylabel('Frequency')
    ax.set_xlim(0, None)
    ax.legend()
    ax.grid(True, alpha=0.3)
    if title:
        ax.set_title(title)
```

### Anti-Patterns to Avoid
- **Using tkinter.dnd module:** Experimental and will be deprecated; use mouse event bindings instead
- **Swap-based reordering:** Decision specifies insert behavior (dragged item moves to target position, others shift)
- **StringVar for button text:** Can cause memory leaks; use button.config(text=...) directly (already noted in codebase)
- **Global seaborn theme:** Call sns.set_theme() globally affects all charts; pass ax explicitly instead
- **Hardcoded pixel dimensions:** Use winfo_screenwidth()/height() for responsive sizing

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tabular data display | Custom frame with labels | ttk.Treeview | Built-in columns, selection, scrolling |
| Sortable columns | Custom sort logic | Treeview heading command | Built-in, handles click-to-sort |
| Distribution overlay | Multiple separate charts | chart_utils.create_comparison_overlay | Already implemented, extend for N distributions |
| Radar charts | Custom polar math | matplotlib polar projection | Official API handles geometry |
| Responsive layout | Manual resize handlers | grid columnconfigure weight | Built-in responsive behavior |
| Random seed generation | Custom algorithm | random.randint() | Standard, cryptographically unnecessary for simulation |

**Key insight:** Tkinter and matplotlib already provide the building blocks. The phase is about assembly and configuration, not new widget development.

## Common Pitfalls

### Pitfall 1: PanedWindow Sash Position Timing
**What goes wrong:** Setting sashpos() before window is mapped raises TclError
**Why it happens:** Widget geometry isn't calculated until window appears
**How to avoid:** Delay sash configuration with after_idle() or bind to <Map> event
**Warning signs:** TclError: invalid window path or sash index out of range

### Pitfall 2: Treeview Selection During Drag
**What goes wrong:** Selection changes during drag-and-drop confuse operation
**Why it happens:** Default selection behavior conflicts with drag state
**How to avoid:** Capture selection at ButtonPress, restore after ButtonRelease
**Warning signs:** Items swap unexpectedly, wrong item gets moved

### Pitfall 3: Distribution Overlay Bin Mismatch
**What goes wrong:** Histograms use different bin edges, making comparison unfair
**Why it happens:** Each histogram calculates its own optimal bins
**How to avoid:** Calculate common bin edges from concatenated data before plotting
**Warning signs:** Histograms appear shifted when they shouldn't be

### Pitfall 4: Radar Chart Data Normalization
**What goes wrong:** Stats with different scales (e.g., OBP 0.300 vs HR 30) distort chart
**Why it happens:** Raw values used directly on same axes
**How to avoid:** Normalize to percentile ranks or 0-1 scale before plotting
**Warning signs:** One dimension dominates, others nearly invisible

### Pitfall 5: Random Seed State Confusion
**What goes wrong:** User expects reproducibility but gets different results
**Why it happens:** Seed randomized on Run when user didn't realize it was unlocked
**How to avoid:** Clear visual distinction between locked/unlocked states, show current seed value
**Warning signs:** Same configuration produces different results on repeated runs

### Pitfall 6: Canvas Scrolling in Collapsible Frame
**What goes wrong:** Mousewheel scrolls wrong canvas when multiple scrollable regions
**Why it happens:** bind_all() affects all canvases, not just the one under mouse
**How to avoid:** Use <Enter>/<Leave> to bind/unbind mousewheel per canvas (already implemented in setup_panel.py)
**Warning signs:** Scrolling in one panel affects another

## Code Examples

Verified patterns from official sources:

### Typical Batting Order Position Calculation
```python
# Calculate typical batting order slot from games started data
# User decision: Show calculated typical position from games at each slot
def calculate_typical_slot(games_by_slot: dict) -> int:
    """
    Calculate typical batting order position from games started.

    Args:
        games_by_slot: {1: games_in_1st, 2: games_in_2nd, ...9: games_in_9th}

    Returns:
        Most common batting order slot (1-9), or 0 if no data
    """
    if not games_by_slot:
        return 0
    return max(games_by_slot.keys(), key=lambda k: games_by_slot.get(k, 0))
```

### Year Selection Global Toggle with Per-Player Override
```python
# Decision: Global toggle with per-player override option
class YearSelector(ttk.Frame):
    def __init__(self, parent, available_years: list):
        super().__init__(parent)

        self.available_years = sorted(available_years, reverse=True)

        # Mode: 'single', 'career', 'range'
        self.mode_var = tk.StringVar(value='single')

        ttk.Radiobutton(self, text="Single Year", variable=self.mode_var,
                        value='single', command=self._on_mode_change).pack(anchor='w')
        ttk.Radiobutton(self, text="Career", variable=self.mode_var,
                        value='career', command=self._on_mode_change).pack(anchor='w')
        ttk.Radiobutton(self, text="Year Range", variable=self.mode_var,
                        value='range', command=self._on_mode_change).pack(anchor='w')

        # Year selectors (shown/hidden based on mode)
        self.year_combo = ttk.Combobox(self, values=self.available_years, state='readonly', width=6)
        self.year_start = ttk.Combobox(self, values=self.available_years, state='readonly', width=6)
        self.year_end = ttk.Combobox(self, values=self.available_years, state='readonly', width=6)
```

### Meaningful Axis Lower Bounds
```python
# Decision: Axis limits should be meaningful, not zero-based when inappropriate
def calculate_axis_lower_bound(data: np.ndarray, percentile: float = 1.0) -> float:
    """
    Calculate meaningful lower bound for axis.

    Uses 1st percentile minus padding to show all data while
    avoiding wasted space from zero-origin.

    Args:
        data: Array of values
        percentile: Lower percentile to use (default: 1st)

    Returns:
        Lower bound value for axis
    """
    lower = np.percentile(data, percentile)
    data_range = np.max(data) - lower
    # Add 5% padding below minimum
    return max(0, lower - data_range * 0.05)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| tk.Listbox for tables | ttk.Treeview | Always (Treeview is standard for tabular data) | Better column support, selection, styling |
| tkinter.dnd for drag-drop | Mouse event bindings | Ongoing (dnd is experimental) | More reliable, no deprecation risk |
| Hardcoded window size | Screen-relative sizing | Best practice | Adapts to different monitors |
| StringVar for labels | Direct widget.config() | Known issue in project | Prevents memory leaks |

**Deprecated/outdated:**
- `tkinter.dnd`: Experimental, will be deprecated when replaced with Tk DND

## Open Questions

Things that couldn't be fully resolved:

1. **Maximum lineups for distribution overlay**
   - What we know: More than 4 overlapping histograms becomes visually cluttered
   - What's unclear: User's actual comparison needs (2? 3? 4?)
   - Recommendation: Default to 4 max, research suggests 2-3 for clarity. Claude's discretion per decision.

2. **Typical batting order position data source**
   - What we know: pybaseball provides some lineup data, FanGraphs has games-by-position
   - What's unclear: Exact API/data structure for games started at each slot
   - Recommendation: May require additional data fetching or calculation from game logs

3. **Team/Roster/Lineup navigation UI**
   - What we know: Hierarchy is Team > Roster > Lineup, multiple lineups per roster
   - What's unclear: Whether tree view, tabs, or dropdowns best fits the workflow
   - Recommendation: Tree view most naturally represents hierarchy; Claude's discretion per decision

## Sources

### Primary (HIGH confidence)
- [TkDocs Treeview Tutorial](https://tkdocs.com/tutorial/tree.html) - Column configuration, item manipulation
- [Python Tkinter Documentation](https://docs.python.org/3/library/tkinter.ttk.html) - ttk.Treeview API
- [Matplotlib Radar Chart](https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html) - RadarAxes implementation
- [Matplotlib Multi-Histogram](https://matplotlib.org/stable/gallery/statistics/histogram_multihist.html) - Overlay techniques
- [tkinter.dnd Documentation](https://docs.python.org/3/library/tkinter.dnd.html) - Confirms experimental status

### Secondary (MEDIUM confidence)
- [GeeksforGeeks Screen Size](https://www.geeksforgeeks.org/getting-screens-height-and-width-using-tkinter-python/) - winfo_screenwidth/height usage
- [APIDemos Drag-Drop Listbox](https://apidemos.com/tkinter/tkinter-listbox/tkinter-drag-and-drop-the-items-in-the-listbox.html) - Mouse binding pattern
- Existing codebase patterns in `src/gui/` - Verified current implementation

### Tertiary (LOW confidence)
- None - all findings verified with official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing dependencies, verified with official docs
- Architecture: HIGH - Patterns from official Tkinter/matplotlib documentation
- Pitfalls: HIGH - Known issues documented in official sources and codebase

**Research date:** 2026-02-07
**Valid until:** 60 days (stable technologies, no breaking changes expected)
