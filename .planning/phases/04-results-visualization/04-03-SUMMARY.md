---
phase: 04-results-visualization
plan: 03
subsystem: gui
tags: [visualization, chart, tkinter, matplotlib, seaborn]
completed: 2026-02-04
duration: 3 min
status: complete

dependency-graph:
  requires: ["04-01"]
  provides: ["player-contribution-chart-widget"]
  affects: ["04-04", "05-optimization"]

tech-stack:
  added: []
  patterns:
    - horizontal-bar-chart
    - toggle-button-views
    - placeholder-pattern-for-future-data

files:
  created:
    - src/gui/widgets/player_contribution_chart.py
  modified:
    - src/gui/widgets/__init__.py
    - src/gui/dashboard/results_panel.py

decisions:
  - id: chart-smaller-than-histogram
    summary: "figsize=(5,3) vs histogram's (8,5) for visual hierarchy"
    rationale: "Per user decision, charts secondary to numeric summaries"
---

# Phase 4 Plan 3: Player Contribution Chart Summary

**One-liner:** Horizontal bar chart widget for visualizing run contributions by lineup slot or player name with toggle views.

## What Was Done

### Task 1: Create PlayerContributionChart widget
Created `src/gui/widgets/player_contribution_chart.py` with:
- `PlayerContributionChart` class extending `ttk.Frame`
- Toggle buttons for switching between "By Slot" (1st-9th) and "By Player" (names) views
- Horizontal bar chart using matplotlib with seaborn `Blues_d` color palette
- Gradient coloring from low to high contribution values
- Value labels on each bar
- Placeholder message "Contribution data not yet available" when data is None
- figsize=(5, 3) to maintain visual hierarchy below histogram (8, 5)

### Task 2: Integrate PlayerContributionChart into ResultsPanel
Updated `src/gui/dashboard/results_panel.py`:
- Added import for `PlayerContributionChart`
- Created "Player Contributions" LabelFrame in details section (row 2)
- Connected `display_results()` to extract and pass `contributions` data
- Connected `clear_results()` to reset chart to placeholder state

## Key Design Decisions

1. **Placeholder pattern:** Since per-slot/per-player contribution tracking is NOT currently implemented in the game engine or batch.py, the widget shows a placeholder message. This prepares the UI for future optimizer phase data.

2. **Visual hierarchy:** Used figsize=(5, 3) vs histogram's (8, 5) to honor user decision "Charts secondary to numeric summaries."

3. **Toggle view pattern:** Radio-button style toggle (slot vs player) using ttk.Button state management rather than actual radiobuttons for cleaner appearance.

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | e101546 | feat(04-03): create PlayerContributionChart widget |
| 2 | 30b459f | feat(04-03): integrate PlayerContributionChart into ResultsPanel |

## Files Changed

| File | Change |
|------|--------|
| src/gui/widgets/player_contribution_chart.py | Created (220 lines) |
| src/gui/widgets/__init__.py | Added export |
| src/gui/dashboard/results_panel.py | Added chart section and data flow |

## Verification Results

All verifications passed:
- mypy type check: Success (no errors in target files)
- Widget import: OK
- Placeholder mode: OK
- Mock data mode: OK
- View toggle: OK
- Full import chain: OK

## Next Phase Readiness

Ready for 04-04 (Summary Panel). The PlayerContributionChart widget is complete and integrated. Currently shows placeholder until contribution tracking is added to the simulation engine in a future optimizer phase.
