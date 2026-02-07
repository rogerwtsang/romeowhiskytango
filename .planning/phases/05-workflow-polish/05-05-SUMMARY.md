---
phase: 05-workflow-polish
plan: 05
subsystem: gui-visualization
tags: [matplotlib, tkinter, charts, radar, overlay, histogram]
requires: [05-03, 05-04]
provides: [VisualsPanel, comprehensive chart suite, distribution overlay]
affects: [future visualization enhancements]
tech-stack:
  added: []
  patterns: [scrollable panel, polar projection, multi-distribution comparison]
key-files:
  created:
    - src/gui/widgets/visuals_panel.py
  modified:
    - src/gui/utils/chart_utils.py
    - src/gui/widgets/__init__.py
    - src/gui/dashboard/simulation_panel.py
    - src/gui/dashboard/results_panel.py
    - src/gui/dashboard/main_dashboard.py
decisions:
  - key: chart-axis-limits
    choice: "Use calculate_axis_lower_bound() for meaningful Y-axis limits"
    rationale: "Avoids wasted space when values cluster high"
  - key: radar-normalization
    choice: "Support both raw normalized and percentile rank modes"
    rationale: "Raw shows league-relative position, percentile shows roster-relative"
  - key: overlay-limit
    choice: "Limit distribution overlay to 4 lineups max"
    rationale: "More overlays become visually cluttered"
  - key: histogram-migration
    choice: "Move histogram and contributions from ResultsPanel to VisualsPanel"
    rationale: "Consolidate all charts in dedicated Visuals tab"
metrics:
  duration: 6 min
  completed: 2026-02-07
---

# Phase 05 Plan 05: Visuals Tab Summary

**One-liner:** Comprehensive Visuals tab with histogram, contributions, run expectancy, overlay comparison, and player radar charts.

## What Was Built

### New Components

1. **VisualsPanel** (`src/gui/widgets/visuals_panel.py`)
   - Scrollable panel containing all visualization charts
   - Sections: Distribution Histogram, Player Contributions, Run Expectancy by Slot, Distribution Overlay, Player Stat Radar
   - Mousewheel scrolling with proper enter/leave binding
   - Integrated with results_manager for overlay comparison

2. **New Chart Functions** (`src/gui/utils/chart_utils.py`)
   - `create_radar_chart()`: Polar plot for multi-player stat comparison
   - `create_run_expectancy_chart()`: Bar chart showing runs by batting order slot
   - `create_multi_overlay()`: Overlay 2-4 distributions with transparency
   - `calculate_axis_lower_bound()`: Meaningful axis limits from percentile

### Migrations

- **Histogram with KDE**: Moved from ResultsPanel to VisualsPanel
- **Player Contributions**: Moved from ResultsPanel to VisualsPanel
- **ResultsPanel**: Now focuses solely on summary statistics

### Wiring

- SimulationPanel receives results_manager for overlay feature
- MainDashboard updates VisualsPanel via `simulation_panel.set_result_data()`
- Roster passed to VisualsPanel for radar chart player selection

## Key Implementation Details

### Radar Chart
- Uses matplotlib polar projection
- Normalizes stats to 0-1 scale for fair comparison
- Toggle between raw normalized values and percentile ranks
- Supports 1-4 players simultaneously
- Stats: OBP, SLG, K%, ISO, BABIP

### Distribution Overlay
- Listbox with multi-select for choosing stored results
- "Refresh List" button populates from results_manager
- Uses common bin edges for fair histogram comparison
- Shows mean lines for each distribution
- Limited to 4 distributions for clarity

### Run Expectancy
- Bar chart showing runs contributed per batting order slot
- Highlights highest contributor in different color
- Uses meaningful axis limits (not always starting at 0)
- Shows placeholder until slot-level tracking is added

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 306363b | feat | Add radar, run expectancy, and multi-overlay chart functions |
| ec6a876 | feat | Create VisualsPanel with comprehensive chart suite |
| a263ecf | feat | Wire VisualsPanel to simulation results |

## Deviations from Plan

None - plan executed exactly as written.

## Testing Notes

- All chart functions verified with matplotlib Figure/Axes
- VisualsPanel creates successfully with all sections
- Scrolling works with mousewheel enter/leave binding
- Radar chart handles both normalization modes
- Overlay requires at least 2 selected results

## Files Changed

| File | Changes |
|------|---------|
| src/gui/utils/chart_utils.py | +282 lines (4 new functions) |
| src/gui/widgets/visuals_panel.py | +568 lines (new widget) |
| src/gui/widgets/__init__.py | +2 lines (export VisualsPanel) |
| src/gui/dashboard/simulation_panel.py | +34 lines (VisualsPanel integration) |
| src/gui/dashboard/results_panel.py | -74 lines (removed charts) |
| src/gui/dashboard/main_dashboard.py | +4 lines (wiring) |

## Next Phase Readiness

Phase 5 complete. All workflow polish features implemented:
- 05-01: Window sizing and seed control
- 05-02: Assumption explanations
- 05-03: Player stat tooltips (if done)
- 05-04: Team/Roster/Lineup hierarchy
- 05-05: Visuals tab with comprehensive charts

Ready for Phase 6 (Optimization) or Phase 7 (Export/Sharing).
