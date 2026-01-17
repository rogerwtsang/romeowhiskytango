---
phase: 02-statistical-robustness
plan: 01
subsystem: statistical-modeling
tags: [probability, bayesian-smoothing, hit-distributions, iso-thresholds, k-pct, documentation]

# Dependency graph
requires:
  - phase: 01-type-safety
    provides: Clean mypy baseline for statistical work
provides:
  - Comprehensive audit of probability decomposition mathematics
  - Documentation of missing empirical sources for HIT_DISTRIBUTIONS constants
  - Assessment of Bayesian smoothing approach with prior_weight analysis
  - Identification of silent K% clamping behavior
  - Recommendations for high/medium/low priority improvements
affects: [02-02, future-statistical-refinement, config-documentation]

# Tech tracking
tech-stack:
  added: []
  patterns: [statistical-audit-methodology, findings-documentation]

key-files:
  created: [.planning/phases/02-statistical-robustness/02-FINDINGS-DRAFT.md]
  modified: []

key-decisions:
  - "Audit methodology: Code review against ANALYSIS_NOTES.md and statistical theory, not diagnostic simulations"
  - "Document structure: Organized by component (probability decomposition, hit distributions) with consistent assessment criteria"
  - "K% clamping identified as band-aid fix requiring logging, not fundamental flaw"
  - "HIT_DISTRIBUTIONS constants reasonable but empirically unvalidated"
  - "Weighted average Bayesian smoothing adequate for practical purposes, Dirichlet prior would be theoretically superior"

patterns-established:
  - "Statistical audit format: Mathematical soundness → Edge cases → Documentation → Empirical grounding"
  - "Recommendation prioritization: High (logging, documentation) → Medium (empirical validation) → Low (theoretical refinements)"

# Metrics
duration: 3min
completed: 2026-01-17
---

# Phase 02 Plan 01: Statistical Robustness Audit Summary

**Comprehensive statistical audit of probability decomposition and hit distribution modeling with identification of missing empirical sources and K% clamping behavior**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-17T21:12:44Z
- **Completed:** 2026-01-17T21:15:55Z
- **Tasks:** 3 (all auto-type)
- **Files modified:** 1

## Accomplishments

- Created 475-line audit findings document covering probability calculations and hit distributions
- Assessed mathematical soundness of BA/OBP/SLG → PA outcome decomposition (formulas correct)
- Identified silent K% clamping behavior as band-aid fix requiring logging
- Documented missing empirical sources for HIT_DISTRIBUTIONS, ISO_THRESHOLDS, LEAGUE_AVG_HIT_DISTRIBUTION, DEFAULT_K_PCT
- Evaluated Bayesian smoothing approach (prior_weight=100 reasonable but not rigorously justified)
- Identified outdated LEAGUE_AVG_HIT_DISTRIBUTION (appears pre-2015, doesn't reflect modern HR rates)
- Provided prioritized recommendations (high: logging/documentation, medium: empirical validation, low: theoretical refinements)

## Task Commits

Each task was committed atomically:

1. **All tasks (audit and documentation)** - `0602517` (docs)

**Plan metadata:** (pending - will be committed with SUMMARY and STATE updates)

## Files Created/Modified

- `.planning/phases/02-statistical-robustness/02-FINDINGS-DRAFT.md` - Statistical audit findings for probability decomposition and hit distributions with assessment criteria and prioritized recommendations

## Decisions Made

**Audit Approach:**
- Focus on code review against ANALYSIS_NOTES.md and statistical theory rather than diagnostic simulations
- Assess each component using four criteria: mathematical soundness, documentation quality, edge case handling, empirical grounding

**K% Clamping Assessment:**
- Identified silent clamping (lines 145-147, 152-154 in probability.py) as band-aid fix for data quality issues
- Determined clamping is statistically inappropriate (sets all outs to strikeouts, eliminates sacrifice flies)
- Recommended logging/warning rather than removing clamping (data validation needed upstream)

**HIT_DISTRIBUTIONS Constants:**
- Values appear reasonable (80% singles for singles hitters, 19% HR for power hitters)
- No empirical source documented - cannot validate without historical data
- Recommended empirical validation using pybaseball to query 2015-2024 MLB data bucketed by ISO

**Bayesian Smoothing:**
- Weighted average approach (prior_weight=100) is mathematically correct
- 100 pseudo-hits represents ~30-40 games of data, reasonable stabilization point
- Dirichlet-Multinomial conjugate prior would be theoretically superior but weighted average adequate for practical use

**League Averages:**
- LEAGUE_AVG_HIT_DISTRIBUTION (75% 1B, 5% HR) appears outdated (pre-2015)
- Modern MLB HR rate ~10-13% of hits, not 5%
- Recommended update to 2015-2024 actual averages

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - audit proceeded smoothly with comprehensive analysis of all specified components.

## Next Phase Readiness

**Ready for Plan 02-02:**
- Probability and hit distribution audit complete
- Methodology established for baserunning and special events audit
- ANALYSIS_NOTES.md issues #2, #3, #7 addressed in findings
- Recommendations organized by priority (high/medium/low)

**No blockers identified.**

**Concerns for future phases:**
- Missing empirical sources represent documentation debt, not functional issues
- K% clamping may affect small subset of players with data quality issues
- Outdated league averages bias low-hit players toward lower HR rates
- All issues have clear remediation paths (logging, documentation, empirical validation)

---
*Phase: 02-statistical-robustness*
*Completed: 2026-01-17*
