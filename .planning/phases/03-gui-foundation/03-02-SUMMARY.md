---
phase: 03-gui-foundation
plan: 02
subsystem: ui
tags: [tkinter, ttk, gui, dashboard, configuration]

# Dependency graph
requires:
  - phase: 03-01
    provides: CollapsibleFrame widget for expandable sections
provides:
  - SetupPanel consolidating team/season config with assumptions subsection
  - Single panel for all simulation configuration (baserunning, errors, distribution)
  - Collapsible Assumptions section to maximize workspace
affects: [03-03-main-dashboard, future-dashboard-integration]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Grid geometry manager with weight configuration for responsive layouts"
    - "CollapsibleFrame composition for space-efficient configuration"
    - "LabeledSlider reuse for consistent slider controls"

key-files:
  created:
    - src/gui/dashboard/setup_panel.py
  modified:
    - src/gui/dashboard/__init__.py

key-decisions:
  - "Consolidated 4 separate tabs (Setup, Baserunning, Errors, Distribution) into single panel"
  - "Used grid geometry manager throughout instead of pack for responsive layout"
  - "Placed Assumptions in CollapsibleFrame to allow users to hide when not needed"

patterns-established:
  - "Configuration panels use grid with columnconfigure(0, weight=1) for horizontal expansion"
  - "LabeledSlider used for all numeric inputs with continuous ranges"
  - "Team/Season at top, Simulation params below, Assumptions collapsible at bottom"

# Metrics
duration: 3min
completed: 2026-01-19
---

# Phase 03 Plan 02: Setup Panel Summary

**SetupPanel consolidates team/season configuration with collapsible Assumptions subsection containing baserunning, errors, and distribution settings**

## Performance

- **Duration:** 3 minutes
- **Started:** 2026-01-19T00:12:05Z
- **Completed:** 2026-01-19T00:15:47Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Consolidated 4 separate tabs into single unified SetupPanel
- Created collapsible Assumptions subsection reducing navigation overhead
- Migrated all baserunning controls (stolen bases, advancement aggression, sacrifice flies)
- Migrated all errors & wild pitches controls (enable toggle, rate slider with explanation)
- Migrated all hit distribution controls (ISO thresholds, 3 profiles, league average, Bayesian smoothing)
- Implemented responsive grid layout with proper weight configuration

## Task Commits

Each task was committed atomically:

1. **Task 1: Create SetupPanel with team configuration** - `f0773b2` (feat)
2. **Task 2: Create dashboard package and export SetupPanel** - `99f4215` (feat)

## Files Created/Modified
- `src/gui/dashboard/setup_panel.py` - Consolidated setup panel (700+ lines) with team config, sim params, and assumptions
- `src/gui/dashboard/__init__.py` - Added SetupPanel to dashboard package exports

## Decisions Made

**1. Grid layout throughout**
- Used grid geometry manager instead of pack for consistent responsive behavior
- Configured columnconfigure(0, weight=1) on all containers for horizontal expansion
- Avoids mixing geometry managers (RESEARCH.md Pitfall 3)

**2. Assumptions in CollapsibleFrame**
- Placed all assumptions (baserunning, errors, distribution) in collapsible section
- Allows users to hide assumptions when focusing on team selection or lineup building
- Follows CONTEXT.md guidance: "Assumptions subsection should live under Setup"

**3. Distribution profile sections preserved**
- Kept 3 hit distribution profiles (singles/balanced/power) plus league average
- Preserved real-time total percentage validation with color coding
- Maintains existing configuration flexibility from distribution_tab.py

## Deviations from Plan

None - plan executed exactly as written.

All controls migrated from setup_tab.py, baserunning_tab.py, errors_tab.py, and distribution_tab.py as specified. Grid layout used consistently with proper weights. CollapsibleFrame composition for Assumptions section implemented per plan requirements.

## Issues Encountered

**Minor mypy type issues (expected and acceptable)**
- 4 false positives on widget.configure(state=...) - tkinter widgets support state but mypy stubs are incomplete
- These match the existing deferred mypy errors in STATE.md for GUI modules
- Does not affect functionality - verified via successful instantiation tests

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for next phase:**
- SetupPanel complete and exportable from dashboard package
- All team configuration and assumptions controls consolidated
- Panel uses responsive grid layout suitable for dashboard integration
- CollapsibleFrame allows space-efficient presentation

**For Phase 03-03 (Main Dashboard):**
- SetupPanel can be integrated into dashboard layout
- get_config() method provides all configuration values for simulation
- set_data_loaded_callback() enables roster coordination with lineup panels
- Assumptions section can be collapsed to maximize lineup/results workspace

---
*Phase: 03-gui-foundation*
*Completed: 2026-01-19*
