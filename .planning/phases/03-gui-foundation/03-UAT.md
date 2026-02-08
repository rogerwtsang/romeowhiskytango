---
status: complete
phase: 03-gui-foundation
source: 03-01-SUMMARY.md, 03-02-SUMMARY.md, 03-03-SUMMARY.md, 03-04-SUMMARY.md, 03-05-SUMMARY.md, 03-06-SUMMARY.md
started: 2026-01-28T15:30:00Z
updated: 2026-02-05T00:00:00Z
completed: 2026-02-05T00:00:00Z
---

## Current Test

number: 4
name: Compare Mode Toggle
expected: |
  Click Compare button on first lineup panel. Second LineupPanel appears alongside first.
  Compare button disappears from second panel.
awaiting: user response

## Tests

### 1. CollapsibleFrame Toggle
expected: Clicking header button toggles content visibility. Visual indicator changes (▼/▶).
result: pass
verified: "Automated test confirms toggle works: expanded -> collapsed -> expanded state transitions correctly"

### 2. Assumptions Panel Collapse Layout
expected: When Assumptions section is collapsed in SetupPanel, surrounding panels resize to fill the empty space. Layout remains responsive.
result: issue
reported: "Panels should adjust and fill in the empty space when 'Assumptions' is closed."
severity: minor

### 3. Run Simulation from Dashboard
expected: Click Run button in LineupPanel. Progress indicator appears showing iteration count. Simulation completes with results displayed in ResultsPanel: mean runs/season, standard deviation, 95% confidence interval, and histogram in Details section.
result: fixed
reported: "Error upon completion of a simulation: 'Simulation failed: unsupported format string passed to NoneType.__format__'; mean runs/season and standard deviation are filled in, but no confidence intervals are displayed and no histograms are displayed. Terminal output: 'Error saving GUI config: Object of type Player is not JSON serializable' Failed to save configuration."
fix: "Fixed two bugs in main_dashboard.py: (1) _normalize_results() now correctly extracts ci_lower/ci_upper from runs['ci_95'] tuple instead of non-existent direct keys; (2) get_dashboard_state() now serializes Player objects to names (strings) for JSON compatibility, and _restore_session() converts names back to Players using roster lookup."
severity: blocker

### 4. Compare Mode Toggle
expected: Click Compare button on first lineup panel. Second LineupPanel appears alongside first. Compare button disappears from second panel.
result: pass
verified: "User confirmed working properly"

### 5. Compare Mode Remove
expected: Click Compare button again (on first panel) to disable compare mode. Second panel is removed cleanly. Layout returns to single lineup.
result: pass
verified: "User confirmed working properly"

### 6. Results Panel Summary Display
expected: After simulation completes, ResultsPanel shows always-visible summary: mean runs/season, standard deviation, 95% CI, and iteration count.
result: pass
verified: "User confirmed working properly"

### 7. Results Panel Details Section
expected: Expand Details section in ResultsPanel. Histogram displays run distribution. Additional statistics (min/max/median/percentiles) visible.
result: pass
verified: "User confirmed working properly"

### 8. Session Restoration Prompt
expected: Close application, reopen. Prompt appears asking to restore previous session if one exists.
result: pass
verified: "User confirmed working properly"

### 9. Session State Restoration
expected: Choose "Yes" on restoration prompt. Previous setup collapse state, compare mode, lineup data, and pane positions are restored.
result: pass
verified: "User confirmed working properly"

### 10. Resizable PanedWindow Layout
expected: Drag dividers between Setup/Content and Lineup/Results areas. Panels resize smoothly with minimum sizes respected.
result: pass
verified: "User confirmed working properly"

## Summary

total: 10
passed: 9
issues: 1
pending: 0
skipped: 0

Note: Test 1 passed (automated), Test 3 blocker fixed and verified (automated). Tests 4-10 passed (user verified 2026-02-05). One minor issue (Assumptions resize) accepted as-is.

## Gaps

- truth: "When Assumptions section is collapsed, surrounding panels resize to fill empty space"
  status: accepted
  reason: "User reported: Panels should adjust and fill in the empty space when 'Assumptions' is closed."
  severity: minor
  test: 2
  resolution: "Accepted as-is - minor cosmetic issue, user approved moving forward"
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "Simulation completes with results displayed: mean, std, 95% CI, histogram"
  status: fixed
  reason: "User reported: Error upon completion - 'Simulation failed: unsupported format string passed to NoneType.__format__'; mean/std filled in, no CI or histogram. Terminal: 'Object of type Player is not JSON serializable'"
  severity: blocker
  test: 3
  root_cause: "Two bugs in main_dashboard.py: (1) _normalize_results() expected ci_lower/ci_upper as direct keys but they're in ci_95 tuple; (2) get_dashboard_state() returned Player objects (not JSON serializable)"
  fix: "Fixed _normalize_results() to extract CI from ci_95 tuple, and get_dashboard_state() to serialize Players as names"
  artifacts: ["src/gui/dashboard/main_dashboard.py"]
  missing: []
  debug_session: ""
