# Monte Carlo Baseball Simulator

## What This Is

A desktop application for simulating baseball seasons using Monte Carlo methods. Users build batting lineups from real MLB player statistics, run thousands of season simulations, and compare results to optimize lineup decisions. The simulator uses player-specific probability models derived from batting statistics (BA, OBP, SLG, K%, SB/CS) with Bayesian smoothing for small sample sizes.

## Core Value

**Visual clarity** — simulation results must be easy to understand at a glance. Charts, metrics, and comparisons should communicate insights immediately without requiring interpretation effort.

## Requirements

### Validated

<!-- Existing functionality confirmed working -->

- ✓ Monte Carlo simulation engine (batch → season → game → inning → PA hierarchy) — existing
- ✓ Player data fetching via pybaseball (Baseball Reference/FanGraphs) — existing
- ✓ Bayesian hit distribution smoothing for small sample sizes — existing
- ✓ Slash line decomposition to PA outcome probabilities — existing
- ✓ Strikeout rate (K%) integration in probability model — existing
- ✓ Stolen base attempt/success modeling — existing
- ✓ Sacrifice fly detection — existing
- ✓ Probabilistic baserunning advancement — existing
- ✓ Error/wild pitch advancement modeling — existing
- ✓ Multi-lineup comparison with statistical analysis — existing
- ✓ Reproducible simulations via random seed — existing

### Active

<!-- Current scope — building toward these -->

**Model Cleanup (Statistical Robustness)**
- [ ] Fix 30+ type safety errors (prevents crashes in critical paths)
- [ ] Add Bayesian shrinkage to stolen base success rate
- [ ] Add warning when K% is clamped due to exceeding total outs
- [ ] Document empirical sources for hit distribution constants
- [ ] Add player-speed modifier to baserunning aggression

**GUI Redesign (Dashboard-Style)**
- [ ] Consolidate 9 tabs into fewer, focused views (merge related settings)
- [ ] Dashboard-style layout with cards, charts, metrics prominently displayed
- [ ] Reduce clicks/steps to run a simulation
- [ ] Clean visual hierarchy with proper spacing and typography
- [ ] Results visualization that communicates insights at a glance

**Test Coverage**
- [ ] Implement 19 stubbed pytest functions
- [ ] Add integration tests for simulation pipeline

### Out of Scope

<!-- Explicit boundaries -->

- Lineup optimization via genetic algorithm — defer to future milestone (complex feature, not needed for core workflow)
- Web or mobile version — staying desktop Tkinter for now
- Multi-team comparison — single team focus for v1
- Real-time game simulation — batch simulation only

## Context

**Existing Codebase:**
- Python 3.13+ with Tkinter GUI
- ~57 Python files in `src/`
- Layered architecture: data → models → engine → simulation → GUI
- pybaseball for MLB data, numpy/pandas/scipy for computation
- Current GUI has 9 tabs that can be consolidated

**Technical Debt Identified:**
- 30+ mypy type errors (see `.planning/ANALYSIS_NOTES.md`)
- Stolen base success rate lacks Bayesian shrinkage (unlike hit distribution)
- Hardcoded constants without documented sources
- 19 test stubs never implemented

**Codebase Map:** `.planning/codebase/` (7 documents)

## Constraints

- **Tech Stack**: Python + Tkinter (flexible on adding libraries if needed)
- **Data Source**: pybaseball API (public, no auth required)
- **Functionality**: All existing simulation capabilities must be preserved

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dashboard-style UI | User prioritizes visual clarity; cards/charts communicate insights faster than form-heavy tabs | — Pending |
| Consolidate tabs | 9 tabs is too fragmented; merge related settings (Baserunning + Errors + Distribution → Model Settings) | — Pending |
| Fix type errors first | Critical path crashes (pa_generator, baserunning) block reliable simulation | — Pending |
| Defer lineup optimizer | Complex feature not needed for core "build → run → compare" workflow | ✓ Good |

---
*Last updated: 2026-01-10 after initialization*
