# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-10)

**Core value:** Visual clarity — simulation results must be easy to understand at a glance
**Current focus:** Phase 5 — Workflow Polish

## Current Position

Phase: 5 of 7 (Workflow Polish)
Plan: 4 of 4 (Team/Roster/Lineup Hierarchy) - COMPLETE
Status: Phase complete
Last activity: 2026-02-07 — Completed 05-04-PLAN.md (Team/Roster/Lineup hierarchy)

Progress: ████████████████████ 100% (21/21 plans across phases)

## Performance Metrics

**Velocity:**
- Total plans completed: 18
- Average duration: 3.0 min
- Total execution time: 0.9 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-type-safety | 2/2 | 8 min | 4 min |
| 02-statistical-robustness | 2/2 | 9 min | 4.5 min |
| 03-gui-foundation | 7/7 | 25 min | 3.6 min |
| 03.1-cleanup-planning-docs | 1/1 | 2.3 min | 2.3 min |
| 04-results-visualization | 4/4 | 15 min | 3.75 min |
| 05-workflow-polish | 4/4 | 13 min | 3.25 min |

**Recent Trend:**
- Last 3 plans: 3 min, 3 min, 4 min
- Trend: Consistent 3-4 minute pace for workflow polish

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Dashboard-style UI selected over form-heavy tabs
- Defer lineup optimizer to future milestone
- Fix type errors before statistical improvements
- Use BasesState type alias instead of Dict[str, Optional[Player]] for better type inference
- Rename variables to avoid shadowing instead of using type: ignore comments
- Use assert statements after validation checks to narrow types for mypy
- Use separate variable names (_arr suffix) for numpy arrays vs original lists
- Add explicit None checks before arithmetic operations on optional values
- Audit methodology: Code review against ANALYSIS_NOTES.md and statistical theory, not diagnostic simulations
- K% clamping identified as band-aid fix requiring logging, not fundamental flaw
- HIT_DISTRIBUTIONS constants reasonable but empirically unvalidated
- Weighted average Bayesian smoothing adequate for practical purposes, Dirichlet prior would be theoretically superior
- Beta-binomial shrinkage identified as theoretically optimal for stolen base success rates (consistent with hit distribution smoothing)
- Player speed modulation via SB attempt rate proxy recommended over uniform baserunning probabilities
- LEAGUE_AVG_HIT_DISTRIBUTION identified as outdated (5% HR vs modern 10-13%), needs update with pybaseball
- Documentation gaps prioritized as medium priority - critical for maintainability but lower impact than statistical fixes
- Use direct button.config(text=...) instead of StringVar to avoid memory leaks (RESEARCH.md Pitfall 2)
- Store section text as instance variable (_text) for consistent toggle behavior in CollapsibleFrame
- Grid layout with explicit weight configuration (columnconfigure/rowconfigure) for responsive panel layouts
- Inline progress indicators initially hidden, shown dynamically on first update_progress() call
- Include self.update() in update_progress() to force UI refresh during background thread execution
- Results panel has always-visible summary (mean, std, CI, iterations) for quick reference
- Details section initially collapsed to save space, user expands as needed
- Histogram migrated from run_tab.py for consistency across dashboard
- Additional statistics (min/max/median/percentiles) in details section only
- ResultsPanel.display_results() accepts normalized result_data dict with standard keys
- Consolidated 4 separate tabs (Setup, Baserunning, Errors, Distribution) into single SetupPanel
- Used grid geometry manager throughout SetupPanel instead of pack for responsive layout
- Placed Assumptions in CollapsibleFrame to allow users to hide when not needed
- MainDashboard uses nested PanedWindows (vertical main, horizontal content) for 3-section resizable layout
- Compare mode limited to exactly 2 lineups (not N) for simpler state management
- First lineup panel gets Compare button, second does not (prevents infinite toggle)
- Widget destruction follows forget() → destroy() → list.remove() pattern to prevent memory leaks
- Lambda callbacks with panel reference enable same handler for multiple panels
- Result normalization layer transforms run_simulations() output to ResultsPanel standard format
- Session state stored as JSON in last_session.json for human readability
- Paned sash positions stored as absolute pixels (not percentages)
- Restoration prompt shown on startup if session exists
- Setup collapse state restored by checking current state before toggling
- Remove orphan/duplicate planning files directly (git history provides archival)
- Retain ahead-of-schedule research (Phase 7) and document as deferred
- Implicit verification acceptable for completed phases (no explicit checkpoint execution needed)
- Use sns.histplot(kde=True) for combined histogram+KDE visualization
- chart_utils: Always pass ax parameter explicitly to seaborn, never use sns.set_theme()
- chart_utils: Clip x-axis to 0 minimum for runs distributions
- PlayerContributionChart uses figsize=(5,3) vs histogram (8,5) for visual hierarchy
- Contribution chart shows placeholder until optimizer phase provides data
- Use Wilson score interval for win probability CI (more accurate for proportions than normal approximation)
- Define win probability as proportion of seasons exceeding league average runs (4.5 runs/game)
- RISP conversion displays '--' placeholder since game engine doesn't track this data
- LOB tracking uses existing total_lob from season.py (no engine changes needed)
- Graceful degradation: Display '--' when metric data unavailable
- Canvas with scrollable frame for dynamic widget lists (vs. Listbox for text-only)
- Lambda callback factories to capture loop variables in closures
- Text tags for styled output (swap=blue, added=green, removed=red)
- Compact swap notation (e.g., '3<->4') for simple position swaps in diff view
- Use ttk.Treeview for spreadsheet-like lineup display (not Listbox)
- Mouse event bindings for drag-drop (not experimental tkinter.dnd)
- INSERT behavior on drag-drop: target position, others shift (not swap)
- Typical slot column shows '--' when games_by_slot data unavailable
- Combobox dropdown for lineup navigation (simple MVP over tree view)
- Store lineups in {team}_{season}.json files for organization
- Show team display name in simulation panel title for context

### Roadmap Evolution

- Phase 3.1 inserted after Phase 3: Cleanup planning docs - consolidate and recommend removals (COMPLETED 2026-01-25)
- Phase 7 researched ahead of schedule (2026-01-25), deferred until Phases 4-6 complete

### Deferred Issues

None yet.

### Blockers/Concerns

**Deferred:**
- 5 remaining mypy errors in GUI modules (lineup_tab.py, compare_tab.py) - low priority, can be addressed in future phase if needed
- Missing empirical sources for HIT_DISTRIBUTIONS, ISO_THRESHOLDS, LEAGUE_AVG_HIT_DISTRIBUTION - documentation debt, not functional issues
- Outdated league averages bias low-hit players toward lower HR rates - clear remediation path via pybaseball
- 11 statistical issues identified in 02-FINDINGS.md - prioritized for future implementation (3 high, 5 medium, 3 low)
- Player speed modulation for baserunning not implemented - uniform probabilities cause 3-7 runs/season error per player
- No Bayesian shrinkage on stolen base success rate - small-sample players get unrealistic 100% or 0% rates

## Session Continuity

Last session: 2026-02-07 21:15:00
Stopped at: Completed 05-04-PLAN.md (Team/Roster/Lineup hierarchy)
Resume file: None
