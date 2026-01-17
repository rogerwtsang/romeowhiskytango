# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-10)

**Core value:** Visual clarity — simulation results must be easy to understand at a glance
**Current focus:** Phase 2 — Statistical Robustness

## Current Position

Phase: 2 of 6 (Statistical Robustness)
Plan: 2 of 2
Status: Phase complete
Last activity: 2026-01-17 — Completed 02-02-PLAN.md

Progress: ████████░░ 80%

## Performance Metrics

**Velocity:**
- Total plans completed: 4
- Average duration: 4.0 min
- Total execution time: 0.27 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-type-safety | 2/2 | 8 min | 4 min |
| 02-statistical-robustness | 2/2 | 9 min | 4.5 min |

**Recent Trend:**
- Last 3 plans: 4 min, 3 min, 6 min
- Trend: Consistent execution speed (~4 min average)

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

Last session: 2026-01-17 21:24:43
Stopped at: Completed 02-02-PLAN.md (Phase 2 complete)
Resume file: None
