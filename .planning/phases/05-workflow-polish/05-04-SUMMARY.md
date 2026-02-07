---
phase: 05-workflow-polish
plan: 04
subsystem: gui-data-model
tags: [team, roster, lineup, persistence, tkinter]

dependency-graph:
  requires:
    - 05-01 (window sizing and seed control)
  provides:
    - Team/Roster/Lineup data model hierarchy
    - Team-specific lineup persistence
    - Lineup navigation UI
    - Team nickname support
  affects:
    - 06-* (export features may leverage lineup persistence)

tech-stack:
  added: []
  patterns:
    - Dataclass hierarchy for domain modeling
    - Team-specific JSON file storage
    - Callback-based UI event handling
    - Combobox for saved lineup navigation

key-files:
  created:
    - src/gui/models/__init__.py
    - src/gui/models/team_roster.py
  modified:
    - src/gui/utils/config_manager.py
    - src/gui/dashboard/setup_panel.py
    - src/gui/dashboard/simulation_panel.py
    - src/gui/dashboard/main_dashboard.py

decisions:
  - id: simple-dropdown-navigation
    choice: "Combobox dropdown for lineup navigation"
    rationale: "Plan allowed Claude discretion; dropdown is simpler MVP than tree view"
  - id: team-specific-storage
    choice: "Store lineups in {team}_{season}.json files"
    rationale: "Keeps lineups organized by team/season, easy to find and manage"
  - id: title-display-name
    choice: "Show team display name in simulation panel title"
    rationale: "Provides clear context for which team is active"

metrics:
  duration: 4 min
  completed: 2026-02-07
---

# Phase 5 Plan 04: Team/Roster/Lineup Hierarchy Summary

Team/Roster/Lineup data model with lineup persistence and navigation UI.

## What Was Built

### Data Model (src/gui/models/team_roster.py)

Three dataclasses forming a hierarchy:

1. **Team**: Collection of loaded players with stats
   - code, full_name, season, nickname
   - display_name property (nickname or "YYYY Full Name")
   - players list, rosters list

2. **Roster**: Subset of team eligible for batting order
   - name, players list, lineups list
   - add_lineup(), get_lineup(), remove_lineup()

3. **Lineup**: Specific 9-player batting order
   - name, players (9-slot list), created_at
   - is_complete(), to_dict()

### Lineup Persistence (config_manager.py)

Team-specific lineup storage:
- `save_team_lineup(team_code, season, lineup_name, player_names)`
- `load_team_lineups(team_code, season)` -> List of lineup dicts
- `delete_team_lineup(team_code, season, lineup_name)`
- `get_team_lineup_names(team_code, season)` -> List of names

Storage location: `~/.montecarlo_baseball/lineups/{team}_{season}.json`

### Navigation UI (simulation_panel.py)

Header controls added:
- Lineup dropdown showing saved lineups for current team/season
- Load button to restore selected lineup
- Save button with name prompt dialog
- Delete button to remove selected lineup

### Team Integration (main_dashboard.py)

- Creates Team object on data load
- Connects lineup save/load/delete callbacks
- Updates all panels with lineup names when team changes
- Displays team name (with nickname) in panel title

### Setup Panel Updates

- Added "Nickname (optional)" field for custom team names
- `get_team_nickname()` and `get_team_full_name()` accessors

## Implementation Notes

### Design Decisions

1. **Simple Dropdown vs Tree View**: Plan allowed Claude discretion. Dropdown is simpler MVP - tree view could be added later if needed.

2. **Team-Specific Storage**: Each team/season gets its own JSON file. Prevents lineup collisions across teams.

3. **Callback Pattern**: Save/Load/Delete use lambda callbacks with panel reference, allowing same handler for multiple panels in compare mode.

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| 1 | aa42886 | Team/Roster/Lineup data model |
| 2 | 796d23d | Lineup persistence and navigation UI |

## Verification

All success criteria met:
- Team/Roster/Lineup hierarchy correctly represents relationships
- Lineups persist to disk and reload across sessions
- Team nicknames display instead of default when set
- Lineup dropdown allows switching between saved lineups
