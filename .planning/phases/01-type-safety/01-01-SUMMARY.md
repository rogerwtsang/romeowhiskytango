---
phase: 01-type-safety
plan: 01
subsystem: core-simulation
tags: [mypy, type-safety, numpy, python]

# Dependency graph
requires:
  - phase: 00-initialization
    provides: Codebase structure and initial planning
provides:
  - Type-safe None checks in pa_generator, baserunning, batch, constraint_validator
  - Mypy passing on 4 critical simulation files
  - Clear error messages for missing/invalid player data
affects: [01-type-safety, testing, simulation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Assert statements for mypy type narrowing in conditional branches"
    - "Explicit None validation before dictionary indexing"
    - "Separate variable names for list vs ndarray types"

key-files:
  created: []
  modified:
    - src/engine/pa_generator.py
    - src/models/baserunning.py
    - src/simulation/batch.py
    - src/gui/utils/constraint_validator.py

key-decisions:
  - "Use assert statements after validation checks to narrow types for mypy"
  - "Use separate variable names (_arr suffix) for numpy arrays vs original lists"
  - "Add explicit None checks before arithmetic operations on optional values"

patterns-established:
  - "Pattern 1: Use assert with explanatory comment after validation to help mypy track control flow"
  - "Pattern 2: Validate optional dictionary values before use, return clear error messages"
  - "Pattern 3: Keep list and array variables distinct to avoid type confusion"

# Metrics
duration: 4min
completed: 2026-01-17
---

# Phase 01 Plan 01: Critical Type Error Fixes Summary

**Fixed 4 critical type errors preventing crashes on None values and probabilistic baserunning edge cases**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-17T18:11:52Z
- **Completed:** 2026-01-17T18:16:09Z
- **Tasks:** 4
- **Files modified:** 4

## Accomplishments
- Eliminated type errors in 4 core simulation files
- Added clear error messages when player data is incomplete
- Fixed mypy union-attr errors on RandomState.random() calls
- Resolved list/ndarray type confusion in batch statistics

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix pa_generator.py None indexing** - `91334df` (fix)
2. **Task 2: Fix baserunning.py rng Optional handling** - `8923d07` (fix)
3. **Task 3: Fix batch.py list/ndarray type confusion** - `f5594a9` (fix)
4. **Task 4: Fix constraint_validator.py None comparisons** - `787970c` (fix)

## Files Created/Modified
- `src/engine/pa_generator.py` - Added None check for player.pa_probs before dictionary indexing
- `src/models/baserunning.py` - Added assert statements to narrow rng type in probabilistic branches
- `src/simulation/batch.py` - Separated list and ndarray variables to fix type confusion
- `src/gui/utils/constraint_validator.py` - Added None validation before position arithmetic

## Decisions Made

1. **Assert placement for type narrowing**: After validation checks that raise ValueError, add assert statements to help mypy's control flow analysis understand the type has been narrowed. This is cleaner than type: ignore comments.

2. **Variable naming convention for arrays**: Use `_arr` suffix for numpy arrays when converting from lists, keeping original list variables intact. This prevents reassignment type errors.

3. **Explicit None checks before operations**: Always validate optional values from dictionary.get() before arithmetic or comparisons, with descriptive error messages.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all fixes applied cleanly as specified in the plan.

## Next Phase Readiness

- Core simulation files now pass mypy type checking
- Ready for remaining type safety improvements in Phase 1
- No blockers for subsequent plans in this phase
- Foundation established for type-safe simulation execution

---
*Phase: 01-type-safety*
*Completed: 2026-01-17*
