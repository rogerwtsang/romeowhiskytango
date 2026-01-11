# Codebase Concerns

**Analysis Date:** 2026-01-10

## Tech Debt

**Bare except clauses (silent error swallowing):**
- Issue: Multiple bare `except:` statements that silently catch all exceptions
- Files:
  - `src/simulation/batch.py:244-245`
  - `src/simulation/season.py:82-83`
  - `src/engine/inning.py:148-149`
  - `src/engine/game.py:158-159`
  - `src/data/processor.py:204-205`
  - `src/gui/tabs/errors_tab.py:78-79`
  - `src/gui/tabs/baserunning_tab.py:178, 189, 200`
  - `src/gui/tabs/setup_tab.py:199`
  - `scripts/validate_simulation.py:64`
- Why: Quick fallback implementation without proper error handling
- Impact: Data loading failures, API errors, and type errors silently ignored; debugging very difficult
- Fix approach: Replace with specific exception types (`FileNotFoundError`, `ValueError`, etc.)

**Hardcoded dataset references:**
- Issue: "blue_jays" hardcoded in 7+ locations instead of using config
- Files:
  - `src/data/processor.py:203, 206`
  - `src/data/scraper.py:412, 416, 434, 437`
  - `src/engine/game.py:157, 159`
  - `src/engine/inning.py:147, 149`
  - `src/simulation/season.py:81, 83`
  - `src/simulation/batch.py:243, 245`
- Why: Rapid prototyping with specific team
- Impact: Cannot easily switch teams; fragile deployment
- Fix approach: Extract team name to `config.py` constant; parameterize data loading functions

**Duplicate data loading fallback pattern:**
- Issue: Same try/except fallback pattern repeated 6 times
- Files: `batch.py`, `season.py`, `inning.py`, `game.py`, `processor.py`
- Pattern:
  ```python
  try:
      df = load_data('blue_jays_2025_prepared.csv', 'processed')
  except:
      df = load_data('blue_jays_2024_prepared.csv', 'processed')
  ```
- Fix approach: Extract to `_load_data_with_fallback()` helper function

## Known Bugs

**Incomplete CLI entry point:**
- Symptoms: `main.py` has 4 TODO comments, no implementation
- Trigger: Running `python main.py`
- File: `main.py:16-19`
- Workaround: Use `python gui.py` for GUI instead
- Root cause: CLI development abandoned in favor of GUI
- Fix: Either complete implementation or remove file

## Security Considerations

**Relative path file operations:**
- Risk: `load_data()` uses relative paths `"data/{data_type}/{filename}"`
- File: `src/data/scraper.py:254`
- Current mitigation: None
- Recommendations: Use absolute paths based on project root; validate file existence before reading

**No input validation on CSV loading:**
- Risk: `pd.read_csv()` called without file existence check
- File: `src/data/scraper.py:254-256`
- Current mitigation: None
- Recommendations: Add `os.path.exists()` check; validate DataFrame structure after load

## Performance Bottlenecks

**Large GUI tab files:**
- Problem: Single classes handling too many responsibilities
- Files:
  - `src/gui/tabs/compare_tab.py`: 738 lines, 23 methods
  - `src/gui/tabs/lineup_tab.py`: 587 lines
  - `src/gui/tabs/run_tab.py`: 415 lines
- Measurement: Not performance-critical, but maintainability issue
- Cause: All comparison logic in single class
- Improvement path: Extract sub-components (e.g., comparison chart as separate widget)

**No simulation result caching:**
- Problem: Full re-simulation required for any parameter change
- File: `src/gui/utils/results_manager.py`
- Current: Only 10 results cached in memory
- Improvement path: Add disk-based result caching by configuration hash

## Fragile Areas

**Data loading pipeline:**
- File: `src/data/scraper.py`, `src/data/processor.py`
- Why fragile: External API dependency (pybaseball), bare except clauses, hardcoded paths
- Common failures: API changes, missing files, network errors (all silently caught)
- Safe modification: Add proper error handling first; parameterize file paths
- Test coverage: No automated tests

**Probability calculations:**
- File: `src/models/probability.py`
- Why fragile: Complex Bayesian smoothing logic with magic numbers
- Common failures: Division by zero, incorrect probability sums
- Safe modification: Add unit tests for edge cases before changes
- Test coverage: No automated tests (only `if __name__ == "__main__"` block)

## Dependencies at Risk

**pybaseball:**
- Risk: External dependency for all data fetching; API could change
- Impact: All player data loading would break
- Migration plan: Abstract data source behind interface; add fallback to local CSV only

## Missing Critical Features

**Structured logging:**
- Problem: Only `print()` statements, no log levels
- Current workaround: Console output
- Blocks: Production debugging, log aggregation
- Implementation complexity: Low (add Python logging module)

**Error recovery in simulation:**
- Problem: Exceptions may leave simulation in inconsistent state
- Current workaround: Full restart
- Blocks: Long-running simulation reliability
- Implementation complexity: Medium

## Test Coverage Gaps

**Probability calculations:**
- What's not tested: `calculate_hit_distribution()`, `decompose_slash_line()`
- File: `src/models/probability.py`
- Risk: Core simulation logic could have bugs
- Priority: High
- Difficulty to test: Low (pure functions with clear inputs/outputs)

**Baserunning advancement:**
- What's not tested: `advance_runners()`, all runner movement logic
- File: `src/models/baserunning.py`
- Risk: Incorrect game simulation results
- Priority: High
- Difficulty to test: Low

**19 stubbed test functions:**
- What's not tested: All tests in `tests/baseball_mc_tests.py` are stubs
- Risk: No regression protection
- Priority: High
- Difficulty to test: Medium (need to implement all stubs)

## Summary Table

| Category | Severity | Count | Primary Files |
|----------|----------|-------|---------------|
| Bare Except | High | 11 | 6 files |
| Hardcoded Strings | High | 14+ | 6 files |
| Test Stubs | High | 19 | `tests/baseball_mc_tests.py` |
| Missing Validation | Medium | 5+ | 4 files |
| Large Functions | Medium | 6 | GUI tabs |
| Duplicate Patterns | Low | 6 | 5 files |
| Missing Docs | Medium | 3+ | 3 files |

---

*Concerns audit: 2026-01-10*
*Update as issues are fixed or new ones discovered*
