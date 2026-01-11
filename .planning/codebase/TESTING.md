# Testing Patterns

**Analysis Date:** 2026-01-10

## Test Framework

**Runner:**
- pytest 7.4.0+
- Config: No explicit `pytest.ini` or `pyproject.toml`

**Assertion Library:**
- pytest built-in assert
- Standard Python assertions

**Run Commands:**
```bash
pytest                              # Run all tests
pytest tests/                       # Run test directory
pytest tests/baseball_mc_tests.py   # Single file
pytest -v                           # Verbose output
```

## Test File Organization

**Location:**
- `tests/` directory (separate from source)
- Not co-located with source files

**Naming:**
- `*_tests.py` or `test_*.py` pattern
- `verify_*.py` for verification scripts

**Structure:**
```
tests/
├── __init__.py
├── baseball_mc_tests.py    # Main test suite (5,889 bytes)
├── test_new_features.py    # Feature validation (2,928 bytes)
└── verify_option_c.py      # Feature verification (1,837 bytes)
```

## Test Structure

**Suite Organization:**
```python
import pytest
from src.models.player import Player

@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    return Player(
        name="Test Player",
        ba=0.280,
        obp=0.350,
        slg=0.450,
        iso=0.170,
        pa=500
    )

def test_walk_bases_empty():
    """Test that walk advances batter to first with bases empty."""
    # arrange / act / assert
    pass  # TODO: Implement
```

**Patterns:**
- pytest fixtures for test data
- Descriptive docstrings on test functions
- Many tests are stubs with `pass` and TODO comments

## Mocking

**Framework:**
- No explicit mocking library detected
- Standard Python mocking available via `unittest.mock`

**Current Usage:**
- Limited mocking in tests
- Direct function calls without mocks

## Fixtures and Factories

**Test Data:**
```python
@pytest.fixture
def sample_player():
    """Create a sample player for testing."""
    return Player(
        name="Test Player",
        ba=0.280,
        obp=0.350,
        slg=0.450,
        iso=0.170,
        pa=500
    )
```

**Location:**
- Fixtures defined in test files
- No shared fixtures file

## Coverage

**Requirements:**
- No enforced coverage target
- No coverage tooling configured

**Configuration:**
- Not detected (`pytest-cov` not in requirements)

## Test Types

**Unit Tests:**
- `tests/baseball_mc_tests.py` - Core simulation tests
- Status: Mostly stubs (19 TODO placeholders)
- Categories:
  - Hit distribution tests
  - Baserunning tests
  - Probability tests

**Integration Tests:**
- `tests/test_new_features.py` - End-to-end feature validation
- Manual simulation runs with result comparison

**E2E Tests:**
- Not automated
- Manual GUI testing

## Test Coverage Gaps

**Critical paths untested:**
- Probability calculations (`src/models/probability.py`)
- Baserunning advancement (`src/models/baserunning.py`)
- Constraint validation (`src/gui/utils/constraint_validator.py`)
- End-to-end game simulation

**Test Statistics:**
```
tests/baseball_mc_tests.py: 225 lines, ~70% stubs
tests/test_new_features.py: 70 lines
tests/verify_option_c.py: 45 lines
Total: ~340 lines of test code
```

## Common Patterns

**Async Testing:**
- Not applicable (synchronous code)

**Error Testing:**
```python
def test_invalid_input():
    """Test error handling for invalid input."""
    # Not implemented - most tests are stubs
    pass
```

**Module-Level Testing:**
Many modules include `if __name__ == "__main__"` blocks:
```python
# src/models/probability.py (lines 241-329)
if __name__ == "__main__":
    # Direct execution for manual testing
    player = Player(...)
    result = calculate_hit_distribution(player)
    print(result)
```

## Validation Scripts

Standalone validation in `scripts/`:
- `validate_simulation.py` - Validation against 2024 historical data
- `prepare_validation_data.py` - Prepare test datasets
- `run_validation_suite.py` - Automated validation runner
- `analyze_roster_consistency.py` - Identify stable rosters

## Recommendations

**Missing Tools:**
- `pytest-cov` for coverage measurement
- `hypothesis` for property-based testing
- CI/CD pipeline (GitHub Actions)

**Priority Improvements:**
1. Implement 19 stubbed test functions
2. Add coverage measurement
3. Create fixtures file for shared test data
4. Add integration tests for simulation pipeline

---

*Testing analysis: 2026-01-10*
*Update when test patterns change*
