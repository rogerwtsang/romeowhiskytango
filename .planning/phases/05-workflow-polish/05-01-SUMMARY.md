---
phase: 05-workflow-polish
plan: 01
subsystem: gui-layout
tags: [tkinter, window-sizing, seed-control, ux-polish]
requires: [phase-04]
provides:
  - SeedControl widget with lock/unlock toggle
  - Responsive window sizing based on screen dimensions
  - 250px minimum width constraint on config panel
  - Default simulations changed to 2000
affects: [05-02, 05-03]
tech-stack:
  added: []
  patterns:
    - Screen-relative window sizing with winfo_screenwidth/height
    - Lock/unlock toggle widget pattern for seed control
    - PanedWindow minimum width enforcement via Configure binding
key-files:
  created:
    - src/gui/widgets/seed_control.py
  modified:
    - gui.py
    - src/gui/dashboard/setup_panel.py
    - src/gui/dashboard/main_dashboard.py
    - src/gui/widgets/__init__.py
decisions: []
metrics:
  duration: 3 min
  completed: 2026-02-07
---

# Phase 5 Plan 1: Window Sizing and Seed Control Summary

**One-liner:** SeedControl widget with lock/unlock toggle, responsive window sizing at half screen width, and 2000 default simulations

## What Was Built

### SeedControl Widget (src/gui/widgets/seed_control.py)

New widget class implementing the lock/unlock seed control pattern from RESEARCH.md Pattern 3:

- **Unlocked state (default):** Entry is greyed out (disabled), seed randomizes on each `get_seed()` call
- **Locked state:** Entry is editable, seed remains fixed
- **Visual feedback:** Button text changes between "Locked" and "Unlocked"
- **Methods:** `get_seed()`, `is_locked()`, `set_seed()`, `set_locked()`

### Window Sizing (gui.py)

Replaced hardcoded `1200x800` geometry with screen-relative sizing:

```python
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = screen_width // 2
window_height = screen_height
root.geometry(f"{window_width}x{window_height}+0+0")
```

Window now opens at left edge, half screen width, full height.

### Setup Panel Updates (setup_panel.py)

- Integrated SeedControl widget replacing old checkbox/entry pattern
- Changed default simulation count from 1000 to 2000
- Removed obsolete `_on_seed_toggle()` method
- Updated `get_config()` to use `self.seed_control.get_seed()`

### Minimum Width Constraint (main_dashboard.py)

Added 250px minimum width enforcement on left config panel:

```python
self._min_left_width = 250
self.main_paned.bind('<Configure>', self._enforce_min_left_width)
```

Uses Configure event binding per RESEARCH.md Pattern 5.

## Key Changes

| File | Change |
|------|--------|
| src/gui/widgets/seed_control.py | New SeedControl widget class |
| src/gui/widgets/__init__.py | Added SeedControl to exports |
| gui.py | Screen-relative window sizing |
| src/gui/dashboard/setup_panel.py | SeedControl integration, 2000 default sims |
| src/gui/dashboard/main_dashboard.py | 250px minimum left panel width |

## Technical Decisions

None required - all implementation followed RESEARCH.md patterns.

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Hash | Description |
|------|-------------|
| f14d025 | feat(05-01): create SeedControl widget with lock/unlock toggle |
| bcdf44e | feat(05-01): update window sizing and simulation defaults |

## Verification Status

- [x] SeedControl imports successfully
- [x] Screen size calculation works correctly
- [x] Setup panel and main dashboard import without errors

## Next Phase Readiness

Phase 5 Plan 2 (Lineup Panel Enhancements) can proceed. The SeedControl widget is complete and the window sizing foundation is in place.

**No blockers identified.**
