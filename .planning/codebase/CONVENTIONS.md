# Coding Conventions

**Analysis Date:** 2026-01-10

## Naming Patterns

**Files:**
- snake_case for all Python files (`player.py`, `game_state.py`)
- `*_tab.py` for GUI tab components (`setup_tab.py`, `lineup_tab.py`)
- `*_manager.py` for coordinator classes (`config_manager.py`)
- Test files: `test_*.py` or `*_tests.py`

**Functions:**
- snake_case for all functions (`calculate_hit_distribution`, `run_simulations`)
- `simulate_*()` for simulation functions (`simulate_season`, `simulate_game`)
- `check_*()` for boolean checks (`check_sacrifice_fly`, `check_steal_opportunities`)
- `get_*()` for data retrieval (`get_team_batting_stats`)
- `_private_method()` with single underscore prefix

**Variables:**
- snake_case for variables (`pa_probs`, `hit_dist`, `batter_idx`)
- Descriptive names (`bases_before`, `bases_after`, `total_runs`)
- UPPER_SNAKE_CASE for constants in `config.py`

**Classes:**
- PascalCase for all classes (`Player`, `GameState`, `PAOutcomeGenerator`)
- No I-prefix for interfaces
- Tab classes: `*Tab` suffix (`SetupTab`, `LineupTab`)

**Types:**
- PascalCase for type aliases
- Extensive use of type hints throughout

## Code Style

**Formatting:**
- 4 spaces indentation (standard Python)
- Double quotes for strings and docstrings
- No semicolons
- Tools: black (formatter), ruff (linter)

**Linting:**
- ruff for fast linting
- mypy for type checking
- Run: `ruff check .`, `mypy .`

**Module Headers:**
```python
# ============================================================================
# src/models/player.py
# ============================================================================
"""Module docstring here."""
```

## Import Organization

**Order:**
1. Standard library imports
2. Third-party imports
3. Local imports

**Example:**
```python
from typing import Dict, Tuple, Optional
import numpy as np
import pandas as pd
import config
from src.models.player import Player
```

**Grouping:**
- Blank line between groups
- No blank lines within groups

## Error Handling

**Patterns (Current):**
- Bare `except:` with fallback (should be improved)
- Console print for errors
- GUI messagebox for user-facing errors

**Recommended:**
- Specific exception types
- Structured error logging
- Error boundaries at layer transitions

## Logging

**Framework:**
- Console print statements only
- No structured logging

**Patterns:**
- `print(f"...")` for progress updates
- No debug/info/warning levels

## Comments

**When to Comment:**
- Complex algorithms (Bayesian smoothing)
- Non-obvious business logic
- Configuration parameter explanations

**Docstring Format:**
Google-style with Args/Returns sections:
```python
def calculate_hit_distribution(
    player: Player,
    league_avg_dist: Optional[Dict[str, float]] = None,
    min_hits_threshold: int = 100
) -> Dict[str, float]:
    """Calculate hit type distribution using actual counts with Bayesian smoothing.

    Args:
        player: Player object with hit count data
        league_avg_dist: League average distribution (fallback)
        min_hits_threshold: Minimum hits to trust player data

    Returns:
        Dictionary with probabilities for each hit type.
        Keys: '1B', '2B', '3B', 'HR'
    """
```

**TODO Comments:**
- Format: `# TODO: description`
- Many incomplete TODOs in `main.py` and `tests/`

## Function Design

**Size:**
- Most functions under 50 lines
- Some large functions in GUI tabs (potential refactor targets)

**Parameters:**
- Type hints for all parameters
- Optional parameters with defaults
- Dataclasses for complex parameter groups

**Return Values:**
- Explicit return types
- Dict returns for simulation results
- Tuple returns for multi-value (e.g., `(attempt_rate, success_rate)`)

## Module Design

**Exports:**
- `__init__.py` in all packages
- Re-exports for public API

**Patterns:**
- One class per file (mostly)
- Related functions grouped in single file
- Constants in `config.py`

## Dataclass Usage

Heavy use of Python dataclasses:
```python
@dataclass
class Player:
    """Represents a baseball player with statistics."""
    name: str
    ba: float
    obp: float
    slg: float
    # ...

@dataclass(frozen=True)
class FieldingPosition:
    """Immutable position representation."""
    code: int
    abbrev: str
    name: str
    type: str
```

## Configuration Constants

Located in `config.py`:
```python
# Simulation parameters
N_SIMULATIONS = 10000
N_GAMES_PER_SEASON = 162
RANDOM_SEED = 42

# Feature toggles
ENABLE_STOLEN_BASES = True
ENABLE_SACRIFICE_FLIES = True

# Thresholds
ISO_THRESHOLDS = {'low': 0.100, 'high': 0.200}
DEFAULT_K_PCT = 0.220
```

---

*Convention analysis: 2026-01-10*
*Update when patterns change*
