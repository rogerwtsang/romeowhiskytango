---
phase: 03-gui-foundation
plan: 05
subsystem: ui
tags: [tkinter, ttk, dashboard, panedwindow, widget-lifecycle]

# Dependency graph
requires:
  - phase: 03-02
    provides: SetupPanel with consolidated configuration
  - phase: 03-03
    provides: LineupPanel with inline simulation controls
  - phase: 03-04
    provides: ResultsPanel with summary and details sections
provides:
  - MainDashboard container with resizable PanedWindow layout
  - Compare mode toggle creating/destroying second lineup panel
  - Simulation execution wiring from lineup to results
  - Dashboard state management for session persistence
affects: [03-06-visual-polish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PanedWindow for resizable dashboard layout (vertical then horizontal)"
    - "Widget lifecycle: forget() then destroy() to prevent memory leaks"
    - "Dynamic panel creation with proper reference tracking"
    - "Result normalization from simulation format to display format"

key-files:
  created:
    - src/gui/dashboard/main_dashboard.py
  modified:
    - src/gui/dashboard/__init__.py
    - gui.py

key-decisions:
  - "Use nested PanedWindows (vertical main, horizontal content) for 3-section layout"
  - "Compare mode limited to exactly 2 lineups (not N lineups) for simplicity"
  - "First lineup panel gets Compare button, second does not"
  - "Normalize simulation results to standard format before passing to ResultsPanel"
  - "Dashboard owns data loading callback and distributes roster to lineup panels"

patterns-established:
  - "PanedWindow.insert(position, widget, weight=1) for dynamic panel insertion"
  - "Proper widget destruction: content_paned.forget(panel) → panel.destroy() → list.remove(panel)"
  - "Lambda callbacks with panel reference: lambda: self._run_simulation(panel)"
  - "Result normalization layer between simulation output and UI display"

# Metrics
duration: 3min
completed: 2026-01-19
---

# Phase 3 Plan 5: Setup Hooks & Run Integration Summary

**MainDashboard replaces 9-tab notebook with resizable PanedWindow layout, wiring SetupPanel → LineupPanel → SimulationRunner → ResultsPanel in unified workspace**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-19T12:32:27Z
- **Completed:** 2026-01-19T12:35:29Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- MainDashboard container assembles all panels with nested PanedWindow (vertical: Setup|Content, horizontal: Lineup|Results)
- Compare mode toggle creates/destroys second lineup panel with proper widget lifecycle (forget→destroy→remove)
- Simulation execution fully wired: LineupPanel.on_run → MainDashboard._run_simulation → SimulationRunner → ResultsPanel.display_results
- Result normalization from run_simulations() output format to ResultsPanel standard format
- Entry point (gui.py) simplified to create single MainDashboard instance (removed 143 lines of tab coordination code)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create MainDashboard with PanedWindow layout and compare mode** - `54c8dfe` (feat)
2. **Task 3: Update dashboard package exports** - `96b398a` (feat)
3. **Task 2: Update gui.py to use MainDashboard** - `518c526` (feat)

## Files Created/Modified
- `src/gui/dashboard/main_dashboard.py` - Main dashboard container with resizable layout, compare mode, simulation execution wiring
- `src/gui/dashboard/__init__.py` - Added MainDashboard export as primary package export
- `gui.py` - Replaced 9-tab notebook with MainDashboard, removed tab coordination logic (143 lines deleted)

## Decisions Made

**PanedWindow nesting strategy:**
- Nested PanedWindows (vertical main split into horizontal content) provides 3-section layout with independent resize control
- Setup panel uses weight=0 (fixed initial size), content uses weight=1 (expands)
- Content paned splits lineups and results with weight=1 (equal initial split)

**Compare mode implementation:**
- Limited to exactly 2 lineups (not N lineups) for simpler state management
- First lineup panel receives on_compare callback, second does not (prevents infinite compare toggling)
- Widget destruction follows RESEARCH.md Pitfall 1: forget() then destroy() then list.remove()

**Callback architecture:**
- Lambda callbacks capture panel reference: `lambda: self._run_simulation(panel)` allows same handler for multiple panels
- Progress callbacks update specific panel that triggered simulation
- Completion callbacks normalize results and display in shared ResultsPanel

**Result normalization:**
- Created `_normalize_results()` method to transform run_simulations() output to ResultsPanel standard format
- Extracts nested summary.runs fields into flat dict with standard keys (mean, std, ci_lower, ci_upper, distribution)
- Calculates missing statistics if not provided (min/max/median/percentiles from distribution)

**Data loading:**
- Dashboard owns data loading callback from SetupPanel
- Dashboard distributes roster to all existing lineup panels (handles compare mode where 2 panels exist)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Type narrowing for lineup validation**
- **Found during:** Task 1 (MainDashboard._run_simulation implementation)
- **Issue:** LineupPanel.get_lineup_data() returns List[Optional[Player]], but SimulationRunner.run_in_thread() expects List[Player]. Direct pass caused mypy error.
- **Fix:** Added validation check `if not all(lineup_data)` then list comprehension to filter out None values, plus assertion `assert len(lineup) == 9` to narrow type for mypy
- **Files modified:** src/gui/dashboard/main_dashboard.py
- **Verification:** mypy src/gui/dashboard/main_dashboard.py shows no errors
- **Committed in:** 54c8dfe (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Auto-fix necessary for type safety. No scope creep - validation was implicit in plan's requirement to validate lineup before running.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Dashboard fully functional with resizable panels, compare mode, and simulation execution
- Ready for visual polish (phase 03-06): loading indicators, empty states, visual feedback
- All panel integration complete, no blockers

**Note for next phase:** Compare mode button location (header of first lineup panel) is functional but may benefit from more prominent placement during visual polish phase.

---
*Phase: 03-gui-foundation*
*Completed: 2026-01-19*
