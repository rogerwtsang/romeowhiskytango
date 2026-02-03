# Phase 4: Results Visualization - Research

**Researched:** 2026-02-03
**Domain:** Statistical visualization with matplotlib embedded in Tkinter for Monte Carlo simulation results
**Confidence:** HIGH

## Summary

Research focused on enhancing the existing matplotlib-based visualization in the ResultsPanel to better communicate Monte Carlo simulation insights. The project already has matplotlib (>=3.7.0) and FigureCanvasTkAgg integration working correctly in results_panel.py and compare_tab.py. The primary enhancement opportunity is adding more informative chart types (KDE overlays, enhanced histograms, convergence plots) and potentially interactive features.

The standard approach builds on the existing matplotlib+Tkinter integration using FigureCanvasTkAgg. Key improvements include: (1) adding kernel density estimation (KDE) overlays to histograms for smoother distribution visualization, (2) using seaborn's statistical plotting functions on top of matplotlib for enhanced aesthetics, (3) adding confidence interval shading with fill_between(), and (4) considering mplcursors for hover tooltips on data points.

**Primary recommendation:** Enhance the existing matplotlib infrastructure with seaborn statistical overlays (histplot with kde=True), confidence interval shading, and optional mplcursors hover annotations. Avoid adding new dependencies unless absolutely necessary; seaborn is recommended as the single optional addition for its statistical visualization strength.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| matplotlib | 3.7.0+ (already in requirements.txt) | Base plotting and Tkinter embedding | Industry standard, already integrated with FigureCanvasTkAgg |
| numpy | 1.24.0+ (already in requirements.txt) | Statistical calculations | Already used for percentiles, mean, std |
| scipy | 1.10.0+ (already in requirements.txt) | Statistical functions | Already used for confidence intervals |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| seaborn | 0.13.0+ | Statistical visualization | Histogram+KDE overlays, enhanced box plots, violin plots |
| mplcursors | 0.6+ | Interactive hover annotations | Optional: if interactive tooltips are desired |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| seaborn | pure matplotlib | seaborn reduces code, provides better defaults for statistics; pure matplotlib requires more manual styling |
| mplcursors | custom motion_notify_event handler | mplcursors is simpler API; custom handler gives more control but more code |
| matplotlib+tkinter | plotly/dash | plotly requires web browser, adds complexity; matplotlib keeps everything in single desktop app |

**Installation:**
```bash
# Seaborn is recommended for statistical visualization
pip install seaborn>=0.13.0

# Optional: for hover annotations
pip install mplcursors>=0.6
```

## Architecture Patterns

### Recommended Project Structure
```
src/gui/
├── dashboard/
│   ├── results_panel.py        # Enhance existing (add chart types)
│   └── ...
├── widgets/
│   ├── chart_widget.py         # NEW: Reusable chart component
│   ├── histogram_chart.py      # NEW: Histogram with KDE overlay
│   ├── comparison_chart.py     # NEW: Side-by-side/overlay distributions
│   └── ...
└── utils/
    ├── chart_utils.py          # NEW: Chart creation helpers
    └── ...
```

### Pattern 1: Reusable Chart Widget
**What:** Encapsulate matplotlib figure creation and management in a reusable widget
**When to use:** Any chart that may be displayed in multiple contexts (ResultsPanel, CompareTab)
**Example:**
```python
# Source: Derived from matplotlib official documentation
# https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ChartWidget(ttk.Frame):
    """Reusable matplotlib chart container for Tkinter."""

    def __init__(self, parent, figsize=(6, 4), dpi=100, **kwargs):
        super().__init__(parent, **kwargs)

        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear(self):
        """Clear the axes and redraw."""
        self.ax.clear()
        self.canvas.draw()

    def refresh(self):
        """Redraw canvas after plot updates."""
        self.figure.tight_layout()
        self.canvas.draw()

    def cleanup(self):
        """Proper cleanup to avoid memory leaks."""
        self.figure.clf()
        self.figure.clear()
        self.canvas.get_tk_widget().destroy()
```

### Pattern 2: Histogram with KDE Overlay
**What:** Enhanced histogram showing both discrete bins and smooth density curve
**When to use:** Distribution visualization for simulation results
**Example:**
```python
# Source: https://seaborn.pydata.org/tutorial/distributions.html
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def create_histogram_with_kde(ax, data, label=None, color='steelblue',
                               show_mean=True, show_median=True):
    """
    Create histogram with KDE overlay and reference lines.

    Args:
        ax: matplotlib Axes object
        data: array-like of values
        label: optional label for legend
        color: fill color for histogram
        show_mean: add vertical mean line
        show_median: add vertical median line
    """
    # Seaborn histplot with KDE
    sns.histplot(
        data,
        kde=True,
        ax=ax,
        color=color,
        alpha=0.7,
        edgecolor='black',
        linewidth=0.5,
        label=label,
        stat='density'  # Normalize for comparison
    )

    # Reference lines
    if show_mean:
        mean_val = np.mean(data)
        ax.axvline(mean_val, color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {mean_val:.1f}')

    if show_median:
        median_val = np.median(data)
        ax.axvline(median_val, color='green', linestyle=':',
                   linewidth=2, label=f'Median: {median_val:.1f}')

    ax.legend()
    ax.grid(True, alpha=0.3)
```

### Pattern 3: Confidence Interval Shading
**What:** Shaded region showing confidence bounds around central estimate
**When to use:** Visualizing uncertainty in convergence plots or time series
**Example:**
```python
# Source: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.fill_between.html
import numpy as np
import matplotlib.pyplot as plt

def plot_with_confidence_interval(ax, x, y, ci_lower, ci_upper,
                                   label=None, color='steelblue'):
    """
    Plot line with shaded confidence interval.

    Args:
        ax: matplotlib Axes
        x: x-axis values
        y: central values (mean)
        ci_lower: lower CI bound
        ci_upper: upper CI bound
        label: legend label
        color: line and fill color
    """
    ax.plot(x, y, color=color, linewidth=2, label=label)
    ax.fill_between(
        x, ci_lower, ci_upper,
        color=color,
        alpha=0.2,
        label='95% CI'
    )
    ax.legend()
    ax.grid(True, alpha=0.3)
```

### Pattern 4: Multiple Distribution Comparison
**What:** Overlay or side-by-side comparison of two distributions
**When to use:** Compare mode with two lineups
**Example:**
```python
# Source: https://seaborn.pydata.org/tutorial/distributions.html
import seaborn as sns
import numpy as np

def compare_distributions(ax, data1, data2, label1='Lineup A',
                          label2='Lineup B', colors=None):
    """
    Compare two distributions with overlaid KDE plots.

    Args:
        ax: matplotlib Axes
        data1: first distribution data
        data2: second distribution data
        label1: label for first distribution
        label2: label for second distribution
        colors: tuple of (color1, color2)
    """
    if colors is None:
        colors = ('#4682B4', '#FF7F50')  # Steel Blue, Coral

    # Overlaid KDE plots with filled areas
    sns.kdeplot(data1, ax=ax, fill=True, alpha=0.5,
                color=colors[0], label=label1)
    sns.kdeplot(data2, ax=ax, fill=True, alpha=0.5,
                color=colors[1], label=label2)

    # Add mean lines
    ax.axvline(np.mean(data1), color=colors[0], linestyle='--',
               linewidth=2, alpha=0.8)
    ax.axvline(np.mean(data2), color=colors[1], linestyle='--',
               linewidth=2, alpha=0.8)

    ax.set_xlabel('Runs per Season')
    ax.set_ylabel('Density')
    ax.legend()
    ax.grid(True, alpha=0.3)
```

### Pattern 5: Effect Size Visualization
**What:** Visual representation of Cohen's d between two groups
**When to use:** Comparison mode to show practical significance
**Example:**
```python
# Source: Based on statistical best practices
import numpy as np

def add_effect_size_annotation(ax, data1, data2, x_position=0.95):
    """
    Add Cohen's d annotation to comparison plot.

    Args:
        ax: matplotlib Axes
        data1: first group data
        data2: second group data
        x_position: relative x position for annotation (0-1)
    """
    # Calculate Cohen's d
    mean1, mean2 = np.mean(data1), np.mean(data2)
    n1, n2 = len(data1), len(data2)
    var1, var2 = np.var(data1, ddof=1), np.var(data2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0

    # Interpret magnitude
    abs_d = abs(d)
    if abs_d < 0.2:
        magnitude = 'Negligible'
    elif abs_d < 0.5:
        magnitude = 'Small'
    elif abs_d < 0.8:
        magnitude = 'Medium'
    else:
        magnitude = 'Large'

    # Add text annotation
    ax.text(
        x_position, 0.95,
        f"Cohen's d: {d:.3f}\n({magnitude} effect)",
        transform=ax.transAxes,
        ha='right', va='top',
        fontsize=10,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    )
```

### Anti-Patterns to Avoid
- **Recreating Figure/Canvas on every update:** Create once, update data via `set_data()` or `clear()` then redraw
- **Not calling canvas.draw() after updates:** Changes won't appear without explicit draw
- **Mixing seaborn figures with manual axes:** Pass axes explicitly to seaborn functions (`ax=ax` parameter)
- **Using pyplot (plt.) functions in embedded GUI:** Use object-oriented API with Figure and Axes objects
- **Creating matplotlib figures without cleanup:** Always call `fig.clf()` and `destroy()` to prevent memory leaks

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Histogram with smooth density | Custom kernel density with numpy convolution | `sns.histplot(data, kde=True)` | seaborn handles bandwidth selection, edge effects |
| Statistical comparison overlays | Manual alpha blending calculations | seaborn's `hue` parameter | Automatic color palette, legends |
| Confidence interval shading | Custom Polygon patches | `ax.fill_between()` | Built-in, handles edge cases |
| Interactive cursor annotations | Custom motion_notify_event handler | `mplcursors.cursor(hover=True)` | 3 lines vs 30+ lines |
| Violin plots | Custom KDE + mirroring + box stats | `ax.violinplot()` or `sns.violinplot()` | Complex stats, symmetric rendering handled |
| Canvas cleanup | Manual gc.collect() calls | `fig.clf(); canvas.get_tk_widget().destroy()` | Proper Tkinter integration |

**Key insight:** matplotlib 3.7+ and seaborn 0.13+ have mature statistical visualization capabilities. The existing code in compare_tab.py already uses histograms and box plots correctly; enhancement should extend rather than replace.

## Common Pitfalls

### Pitfall 1: Memory Leaks from Figure Recreation
**What goes wrong:** Memory usage grows continuously when updating charts
**Why it happens:** Creating new Figure objects without destroying old ones; tkinter keeps references
**How to avoid:**
1. Reuse Figure/Axes objects instead of recreating
2. Use `ax.clear()` to reset, then redraw
3. When destroying widgets: `fig.clf(); fig.clear(); canvas.get_tk_widget().destroy()`
**Warning signs:** Memory usage increases with each simulation run; app slows over time

```python
# BAD - creates new figure every update
def update_chart(self, data):
    self.figure = Figure()  # Memory leak!
    self.canvas = FigureCanvasTkAgg(self.figure, master=self)
    # ...

# GOOD - reuse existing figure
def update_chart(self, data):
    self.ax.clear()  # Clear axes, keep figure
    # ... plot new data ...
    self.canvas.draw()  # Refresh
```

### Pitfall 2: Blocking UI During Plot Rendering
**What goes wrong:** UI freezes while complex charts render
**Why it happens:** matplotlib rendering is synchronous; complex plots (many points, KDE) take time
**How to avoid:**
1. Limit data points plotted (subsample if >10k points)
2. Use simpler visualization for large datasets (histogram vs scatter)
3. Show progress indicator while rendering
**Warning signs:** UI becomes unresponsive during chart updates

### Pitfall 3: Inconsistent Figure Sizing Across Displays
**What goes wrong:** Charts appear too small or too large on different monitors
**Why it happens:** Fixed DPI/figsize doesn't account for display scaling
**How to avoid:**
1. Use relative sizing with `pack(fill=tk.BOTH, expand=True)`
2. Let figure resize with container rather than fixing figsize
3. Set figure DPI appropriately (100 for standard, lower for HiDPI)
**Warning signs:** Charts look wrong on colleague's monitors; text illegible at certain sizes

### Pitfall 4: Seaborn Overwriting Matplotlib State
**What goes wrong:** Seaborn styling bleeds into other plots or global matplotlib config changes
**Why it happens:** Seaborn's `set_theme()` modifies matplotlib rcParams globally
**How to avoid:**
1. Use `sns.set_theme()` carefully or avoid it for embedded use
2. Pass axes explicitly: `sns.histplot(data, ax=ax)` not `sns.histplot(data)`
3. Use context managers: `with sns.axes_style('whitegrid'):`
**Warning signs:** Non-seaborn plots look different after seaborn is imported

```python
# BAD - affects all matplotlib globally
sns.set_theme()  # Modifies rcParams!

# GOOD - explicit axes, no global state
fig, ax = plt.subplots()
sns.histplot(data, ax=ax)  # Uses existing axes
```

### Pitfall 5: Misusing KDE for Bounded Data
**What goes wrong:** KDE shows impossible values (negative runs, >100% probability)
**Why it happens:** KDE assumes unbounded, continuous distributions; baseball runs are bounded
**How to avoid:**
1. Use histogram as primary, KDE as supplementary
2. Clip KDE visually: `ax.set_xlim(0, None)` to hide negative region
3. Consider that slight extrapolation is acceptable for visual smoothing
**Warning signs:** Distribution curves extend into negative territory or beyond logical bounds

## Code Examples

Verified patterns from official sources:

### Enhanced Histogram (Based on existing results_panel.py)
```python
# Source: Enhanced from project's results_panel.py
import numpy as np
import seaborn as sns

def create_enhanced_histogram(ax, distribution, mean=None, median=None,
                               title='Distribution of Runs per Season'):
    """
    Create enhanced histogram with KDE overlay.

    Args:
        ax: matplotlib Axes
        distribution: array of simulation results
        mean: optional pre-computed mean
        median: optional pre-computed median
        title: chart title
    """
    ax.clear()

    if not distribution or len(distribution) == 0:
        ax.text(0.5, 0.5, 'No data to display',
                ha='center', va='center', transform=ax.transAxes,
                fontsize=12, color='gray')
        ax.set_xticks([])
        ax.set_yticks([])
        return

    # Seaborn histogram with KDE
    sns.histplot(
        distribution,
        kde=True,
        ax=ax,
        color='steelblue',
        alpha=0.7,
        edgecolor='black',
        linewidth=0.5,
        stat='count'  # Keep frequency, not density
    )

    # Calculate if not provided
    if mean is None:
        mean = np.mean(distribution)
    if median is None:
        median = np.median(distribution)

    # Reference lines
    ax.axvline(mean, color='red', linestyle='--', linewidth=2,
               label=f'Mean: {mean:.1f}')
    ax.axvline(median, color='green', linestyle=':', linewidth=2,
               label=f'Median: {median:.1f}')

    ax.set_xlabel('Runs per Season')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
```

### Comparison Overlay Chart
```python
# Source: https://seaborn.pydata.org/tutorial/distributions.html
import numpy as np
import seaborn as sns

def create_comparison_overlay(ax, data1, data2, label1, label2):
    """
    Create overlaid distribution comparison.

    Args:
        ax: matplotlib Axes
        data1: first lineup's distribution
        data2: second lineup's distribution
        label1: name of first lineup
        label2: name of second lineup
    """
    ax.clear()

    colors = ['#4682B4', '#FF7F50']  # Steel Blue, Coral

    # Overlaid histograms with step (clearer than bars)
    sns.histplot(data1, ax=ax, color=colors[0], alpha=0.5,
                 label=label1, element='step', stat='density')
    sns.histplot(data2, ax=ax, color=colors[1], alpha=0.5,
                 label=label2, element='step', stat='density')

    # Add mean indicators
    mean1, mean2 = np.mean(data1), np.mean(data2)
    ax.axvline(mean1, color=colors[0], linestyle='--', linewidth=2)
    ax.axvline(mean2, color=colors[1], linestyle='--', linewidth=2)

    # Difference annotation
    diff = mean1 - mean2
    ax.annotate(
        f'Difference: {diff:+.1f} runs/season',
        xy=(0.5, 0.95), xycoords='axes fraction',
        ha='center', va='top',
        fontsize=10,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8)
    )

    ax.set_xlabel('Runs per Season')
    ax.set_ylabel('Density')
    ax.set_title('Distribution Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
```

### Convergence Plot (New Chart Type)
```python
# Source: Monte Carlo simulation best practices
import numpy as np

def create_convergence_plot(ax, distribution, title='Convergence Check'):
    """
    Show running mean convergence as simulations accumulate.

    Args:
        ax: matplotlib Axes
        distribution: array of simulation results (in order)
        title: chart title
    """
    ax.clear()

    if not distribution or len(distribution) < 2:
        ax.text(0.5, 0.5, 'Insufficient data',
                ha='center', va='center', transform=ax.transAxes)
        return

    n = len(distribution)
    iterations = np.arange(1, n + 1)

    # Running statistics
    running_mean = np.cumsum(distribution) / iterations
    running_std = np.array([np.std(distribution[:i+1]) for i in range(n)])

    # 95% CI bounds (approximate)
    ci_width = 1.96 * running_std / np.sqrt(iterations)
    ci_lower = running_mean - ci_width
    ci_upper = running_mean + ci_width

    # Plot
    ax.plot(iterations, running_mean, 'b-', linewidth=2, label='Running Mean')
    ax.fill_between(iterations, ci_lower, ci_upper, alpha=0.2, color='blue',
                    label='95% CI')

    # Final value line
    final_mean = running_mean[-1]
    ax.axhline(final_mean, color='red', linestyle='--', alpha=0.7,
               label=f'Final: {final_mean:.1f}')

    ax.set_xlabel('Number of Iterations')
    ax.set_ylabel('Mean Runs per Season')
    ax.set_title(title)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Set x-axis to show iteration count appropriately
    if n > 1000:
        ax.set_xscale('log')
        ax.set_xlabel('Number of Iterations (log scale)')
```

### Proper Canvas Cleanup
```python
# Source: https://github.com/matplotlib/matplotlib/issues/24820
# Memory leak prevention pattern

class ChartPanel(ttk.Frame):
    """Panel with proper matplotlib cleanup."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.figure = None
        self.canvas = None
        self._create_chart()

        # Bind cleanup on destroy
        self.bind('<Destroy>', self._on_destroy)

    def _create_chart(self):
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _on_destroy(self, event):
        """Proper cleanup to prevent memory leaks."""
        if event.widget == self:
            if self.figure is not None:
                self.figure.clf()
                self.figure.clear()
            if self.canvas is not None:
                self.canvas.get_tk_widget().destroy()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pyplot state machine (`plt.hist()`) | Object-oriented API (`ax.hist()`) | Long-standing best practice | Required for embedded GUI; cleaner code |
| `tight_layout()` manual call | `layout="constrained"` or `Figure(constrained_layout=True)` | matplotlib 3.6+ | Automatic, handles colorbars and legends |
| Manual subplots (`add_subplot(2,2,1)`) | `subplot_mosaic()` with ASCII art | matplotlib 3.3+ | More intuitive complex layouts |
| Basic histograms | Histogram + KDE overlay | seaborn popularized | Better distribution visualization |
| Manual error bars for CI | `fill_between()` shaded regions | matplotlib convention | Cleaner, more interpretable |

**Deprecated/outdated:**
- `pylab` interface: Avoid; use explicit matplotlib imports
- `tight_layout()` with constrained_layout: Don't mix; choose one
- Seaborn `distplot()`: Deprecated in seaborn 0.11; use `histplot()` or `displot()`

## Open Questions

Things that couldn't be fully resolved:

1. **mplcursors performance with many points**
   - What we know: mplcursors works well for scatter/line plots
   - What's unclear: Performance impact on histograms with 10k+ points
   - Recommendation: Add as optional feature; test with realistic data volumes before committing

2. **Seaborn as required vs optional dependency**
   - What we know: Seaborn adds ~15MB, provides significant statistical visualization improvements
   - What's unclear: Whether the aesthetic/functional benefits justify adding another dependency
   - Recommendation: Add seaborn to requirements.txt; the statistical visualization benefits align with "visual clarity" value

3. **Convergence plot value for end users**
   - What we know: Convergence plots are standard in Monte Carlo to verify sufficient iterations
   - What's unclear: Whether typical users care about convergence or just want results
   - Recommendation: Include as optional/collapsible chart in details section; power users will appreciate it

## Sources

### Primary (HIGH confidence)
- [Matplotlib Embedding in Tk documentation](https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html) - Official FigureCanvasTkAgg patterns
- [Seaborn Distribution Tutorial](https://seaborn.pydata.org/tutorial/distributions.html) - histplot, kdeplot, comparison patterns
- [Matplotlib fill_between documentation](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.fill_between.html) - Confidence interval shading

### Secondary (MEDIUM confidence)
- [mplcursors hover documentation](https://mplcursors.readthedocs.io/en/stable/examples/hover.html) - Interactive annotations
- [TkDocs Matplotlib Integration](https://tkdocs.com/) - Tkinter best practices
- [GeeksforGeeks: How to embed Matplotlib charts in Tkinter GUI](https://www.geeksforgeeks.org/python/how-to-embed-matplotlib-charts-in-tkinter-gui/) - Integration patterns
- [Matplotlib Memory Leak Issues](https://github.com/matplotlib/matplotlib/issues/24820) - FigureCanvasTkAgg cleanup

### Tertiary (LOW confidence)
- Various Stack Overflow discussions on matplotlib+tkinter memory management - patterns vary, verify with project testing

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - matplotlib already in use, seaborn is well-documented addition
- Architecture patterns: HIGH - based on official documentation and existing project code
- Pitfalls: HIGH - documented in official bug trackers and multiple verified sources
- Code examples: HIGH - based on official documentation and tested project patterns

**Research date:** 2026-02-03
**Valid until:** 60 days (matplotlib and seaborn are stable, slow-moving libraries)
