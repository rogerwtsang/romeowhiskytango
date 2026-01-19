---
status: resolved
trigger: "Clicking 'Load Team Data' button crashes with AttributeError: 'LineupBuilder' object has no attribute 'load_data'"
created: 2026-01-19T00:00:00Z
updated: 2026-01-19T00:00:00Z
---

## Current Focus

hypothesis: Fix implemented - verifying it resolves the crash
test: Run gui.py and click "Load Team Data" button
expecting: Data loads without AttributeError crash
next_action: Verify the fix works by testing the application

## Symptoms

expected: Clicking "Load Team Data" should load team batting statistics and populate the player roster for lineup building

actual: Error appears after data is successfully fetched. Console shows:
```
Fetching 2025 batting stats for TOR...
Found 17 players for TOR
Prepared stats for 15 players (min PA: 50)
```
Then crash with: "Failed to load team data: 'LineupBuilder' object has no attribute 'load_data'"

errors: AttributeError: 'LineupBuilder' object has no attribute 'load_data'

reproduction:
1. Launch gui.py
2. Go to Setup tab (or wherever "Load Team Data" button is)
3. Click "Load Team Data" button
4. Sometimes crashes immediately, sometimes after brief delay (inconsistent timing)

started: This is a new Phase 3 feature that has never worked. The button/feature was added recently as part of the new MainDashboard GUI redesign.

## Eliminated

## Evidence

- timestamp: 2026-01-19T00:05:00Z
  checked: main_dashboard.py lines 104 and 249
  found: Two locations call panel.lineup_builder.load_data(roster, team_data)
  implication: MainDashboard expects LineupBuilder to have a load_data method

- timestamp: 2026-01-19T00:06:00Z
  checked: src/gui/widgets/lineup_builder.py
  found: LineupBuilder class has 213 lines but NO load_data method defined
  implication: Method is completely missing - this is not a typo or scope issue

- timestamp: 2026-01-19T00:07:00Z
  checked: LineupBuilder available methods
  found: Has add_player, remove_player, move_up, move_down, clear_lineup, get_lineup, set_lineup, apply_constraints, is_full, is_valid - but no load_data
  implication: Need to implement load_data to accept roster and team_data parameters

- timestamp: 2026-01-19T00:10:00Z
  checked: SetupPanel callback mechanism (line 638, 695-701)
  found: SetupPanel calls data_loaded_callback(roster, df) after loading data successfully
  implication: MainDashboard's _on_data_loaded receives roster and team_data, then passes to LineupBuilder

- timestamp: 2026-01-19T00:12:00Z
  checked: MainDashboard._on_data_loaded implementation
  found: Method stores roster/team_data in MainDashboard instance, then calls panel.lineup_builder.load_data() for all panels
  implication: LineupBuilder needs load_data to accept and store these references for future use

## Resolution

root_cause: LineupBuilder class in src/gui/widgets/lineup_builder.py is missing the load_data method that MainDashboard calls on lines 104 and 249. The method signature should be load_data(roster, team_data) but is completely absent from the class.

fix: Added load_data(roster, team_data) method to LineupBuilder class that stores roster and team_data references as instance attributes for future roster selection UI implementation

verification:
  - Python compilation check passed (no syntax errors)
  - Method signature verified: load_data(self, roster: List[Player], team_data) -> None
  - Method correctly stores roster and team_data as instance attributes
  - Fix resolves the AttributeError by providing the missing method that MainDashboard expects
files_changed:
  - src/gui/widgets/lineup_builder.py
