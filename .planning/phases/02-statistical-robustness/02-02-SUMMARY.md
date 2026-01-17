---
phase: 02-statistical-robustness
plan: 02
subsystem: statistical-modeling
tags: [bayesian-statistics, probability-theory, baseball-analytics, model-audit]

# Dependency graph
requires:
  - phase: 02-01
    provides: Probability and hit distribution audit findings (Part 1)
provides:
  - Complete statistical model audit covering all 7 ANALYSIS_NOTES.md issues
  - Baserunning advancement analysis with player speed gap identification
  - Special events analysis (stolen bases, sacrifice flies, errors)
  - 11 issues documented and prioritized by impact (3 critical, 5 documentation, 3 simplifications)
  - Estimated accuracy gain: 10-25 runs/season (1-3% improvement potential)
affects: [03-position-tracking, 04-lineup-optimization, future-statistical-refinements]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Beta-binomial conjugate prior recommendation for binomial outcomes (SB success rate)"
    - "Player-specific speed modulation pattern for baserunning probabilities"
    - "Configuration constant documentation standard (source + year range + methodology)"

key-files:
  created:
    - .planning/phases/02-statistical-robustness/02-FINDINGS.md
  modified:
    - .planning/phases/02-statistical-robustness/02-FINDINGS-DRAFT.md

key-decisions:
  - "Beta-binomial shrinkage identified as theoretically optimal approach for stolen base success rates (consistent with hit distribution smoothing)"
  - "Player speed modulation via SB attempt rate proxy recommended over uniform baserunning probabilities"
  - "LEAGUE_AVG_HIT_DISTRIBUTION identified as outdated (5% HR vs modern 10-13%), needs update with pybaseball"
  - "Documentation gaps prioritized as medium priority - critical for maintainability but lower impact than statistical fixes"

patterns-established:
  - "Statistical audit methodology: Code review against theoretical soundness + empirical grounding + edge case handling + documentation quality"
  - "Issue categorization by impact: Critical (5-15 runs), Medium (3-7 runs), Low (<3 runs) with effort estimates"
  - "Recommendation format: High/Medium/Low priority with specific implementation approach and effort estimate"

# Metrics
duration: 6min
completed: 2026-01-17
---

# Phase 2 Plan 2: Statistical Audit Completion Summary

**Comprehensive statistical model audit identifying 11 issues across probability, hit distributions, baserunning, and special events with prioritized recommendations for 10-25 runs/season accuracy gain**

## Performance

- **Duration:** 6 minutes
- **Started:** 2026-01-17T21:18:29Z
- **Completed:** 2026-01-17T21:24:43Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Completed baserunning advancement probability analysis with realism assessment (28% 1st-to-3rd reasonable but lacks source)
- Identified player speed gap: uniform probabilities cause 60% error for fast runners, 87% error for slow runners (3-7 runs/season impact)
- Analyzed stolen base modeling: no Bayesian shrinkage (player with 5/5 SB gets 100% vs realistic 88.9% with beta-binomial)
- Evaluated sacrifice fly modeling: fixed 35% flyout percentage ignores 25-55% player variation (5-10 runs/season for extremes)
- Finalized comprehensive findings document with 11 issues categorized by priority and impact

## Task Commits

Each task was committed atomically:

1. **Task 1-3: Complete statistical audit** - `c76b899` (docs)
   - Audited baserunning advancement model
   - Audited special events (stolen bases, sacrifice flies, errors)
   - Finalized findings document with summary

**Plan metadata:** (included in task commit)

## Files Created/Modified

- `.planning/phases/02-statistical-robustness/02-FINDINGS-DRAFT.md` - Extended with baserunning and special events analysis (Part 2)
- `.planning/phases/02-statistical-robustness/02-FINDINGS.md` - Complete final findings document (1343 lines, status: final)

## Decisions Made

1. **Beta-binomial shrinkage for SB success rate** - Identified as high-priority fix (Issue #1) to create statistical consistency with hit distribution approach; conjugate prior (3 successes, 1 failure) recommended

2. **Player-speed modulation approach** - SB attempt rate recommended as speed proxy for baserunning (Issue #4); fast runners should have 40-50% 1st-to-3rd rate vs uniform 28%

3. **Documentation priority assessment** - Missing empirical sources for HIT_DISTRIBUTIONS, BASERUNNING_AGGRESSION, LEAGUE_AVG categorized as medium priority; critical for maintainability but lower accuracy impact than statistical fixes

4. **LEAGUE_AVG_HIT_DISTRIBUTION needs update** - Current 5% HR rate appears outdated; modern MLB (2015-2024) is 10-13%; biases low-hit players toward lower HR rates when used as Bayesian prior

## Deviations from Plan

None - plan executed exactly as written.

All tasks completed as specified:
- Task 1: Baserunning advancement analysis with realism assessment, source documentation gap, player speed handling issue
- Task 2: Special events analysis covering stolen bases (shrinkage gap, opportunity model), sacrifice flies (flyout %, K% handling), errors
- Task 3: Final findings document created with frontmatter update, comprehensive summary section, all 11 issues documented

## Issues Encountered

None - audit proceeded smoothly with all model components analyzed as planned.

## Next Phase Readiness

**Phase 2 Complete** - Statistical robustness audit finished with comprehensive findings.

**Deliverables ready:**
- Complete audit findings document (02-FINDINGS.md) with 11 issues documented
- Prioritized recommendations (High: 3 issues, Medium: 5 issues, Low: 3 issues)
- Estimated accuracy improvement: 10-25 runs/season (1-3% of typical team totals)

**For future phases (Phase 3+):**

**High-priority statistical fixes ready for implementation:**
1. K% clamping logging (Issue #2) - 10 minutes, immediate diagnostic value
2. Beta-binomial shrinkage for SB (Issue #1) - 1-2 hours, high correctness gain
3. Player-speed baserunning modulation (Issue #4) - 2-3 hours, significant accuracy improvement

**Documentation sprint ready:**
4. Document all config.py constant sources (Issues #3, #6, #7, #8) - 2-3 hours total
5. Update LEAGUE_AVG_HIT_DISTRIBUTION with modern data - 1-2 hours
6. Empirically validate HIT_DISTRIBUTIONS - 2-3 hours

**No blockers for next phase.**

**Key insights for Phase 3 (Position Tracking):**
- Current model tracks batting order slot, not fielding position (documented in 02-FINDINGS.md)
- Position-level tracking needed for lineup optimization (affects which slots players can occupy)
- Statistical fixes can be implemented in parallel with position tracking work

---
*Phase: 02-statistical-robustness*
*Completed: 2026-01-17*
