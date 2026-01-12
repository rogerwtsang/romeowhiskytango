# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

### Development Commands

**Run the GUI application:**
```bash
python gui.py
```

**Run tests:**
```bash
pytest                    # All tests
pytest tests/             # Test directory only
pytest -v                 # Verbose output
pytest tests/baseball_mc_tests.py  # Single file
```

**Code quality:**
```bash
ruff check .              # Linting
black .                   # Auto-formatting
mypy .                    # Type checking
```

**Validation scripts:**
```bash
python scripts/validate_simulation.py      # Validate against historical data
python scripts/run_validation_suite.py     # Full validation suite
```

## Project Architecture

This is a **Monte Carlo baseball simulator** using Bayesian statistical methods to optimize batting order lineups. The architecture follows a **layered monolith** pattern with hierarchical simulation execution.

### Core Layers (Bottom-Up)

1. **Data Layer** (`src/data/`): FanGraphs/pybaseball integration, CSV processing
   - `scraper.py`: `get_team_batting_stats(team, season)` - fetch player data
   - `processor.py`: `create_player_from_stats(stats_df_row)` - create Player objects

2. **Models Layer** (`src/models/`): Domain objects and probability calculations
   - `player.py`: Player dataclass with statistics and calculated probabilities
   - `probability.py`: Slash line decomposition (BA/OBP/SLG → PA outcomes), Bayesian smoothing for hit distributions
   - `position.py`: FieldingPosition (10 defensive positions)
   - `baserunning.py`, `stolen_bases.py`, `sacrifice_fly.py`, `errors.py`: Specialized event modeling

3. **Engine Layer** (`src/engine/`): Core game simulation
   - `pa_generator.py`: `PAOutcomeGenerator` - stochastic PA outcome generation with numpy RandomState
   - `inning.py`: `simulate_half_inning()` - simulate until 3 outs
   - `game.py`: `simulate_game()` - 9-inning game
   - `game_state.py`: Bases, outs, score tracking

4. **Simulation Layer** (`src/simulation/`): Multi-iteration orchestration
   - `season.py`: `simulate_season()` - 162 games with lineup rotation
   - `batch.py`: `run_simulations()` - N iterations with statistical aggregation

5. **Presentation Layer** (`src/gui/`): Tkinter desktop application
   - 9 tabs: Setup, Lineup, Baserunning, Errors, Distribution, Validation, Output, Run, Compare
   - `utils/simulation_runner.py`: Background thread execution with progress callbacks
   - `utils/results_manager.py`: In-memory cache (max 10 results) for comparison

### Critical Data Flow

**Simulation Execution:**
```
GUI (Run Tab) → SimulationRunner.run_in_thread() → batch.run_simulations()
→ For each iteration (1-10,000):
  → season.simulate_season() (162 games)
    → game.simulate_game() (9 innings)
      → inning.simulate_half_inning() (until 3 outs)
        → pa_generator.generate_outcome() (each PA)
→ Results → ResultsManager → Compare Tab
```

**Player Data Loading:**
```
Setup Tab → scraper.get_team_batting_stats(team, year)
→ processor.create_player_from_stats()
→ probability.decompose_slash_line() (calculate PA probabilities)
→ Available for lineup building
```

### Key Abstractions

- **Player**: Dataclass representing player stats with calculated PA outcome probabilities
- **PAOutcomeGenerator**: Encapsulates numpy RandomState for reproducible stochastic outcomes
- **SimulationRunner**: Threading wrapper for GUI responsiveness (progress callbacks via queue)
- **ResultsManager**: In-memory result storage with comparison capabilities
- **FieldingPosition**: Frozen dataclass for type-safe position representation

## Configuration

All simulation parameters are centralized in `config.py`:

**Key toggles:**
- `ENABLE_STOLEN_BASES`, `ENABLE_SACRIFICE_FLIES`, `ENABLE_PROBABILISTIC_BASERUNNING`, `ENABLE_ERRORS_WILD_PITCHES`

**Probability parameters:**
- `ISO_THRESHOLDS`: Classify hitters as singles/balanced/power
- `HIT_DISTRIBUTIONS`: Hit type probabilities (1B/2B/3B/HR) by hitter class
- `BAYESIAN_PRIOR_WEIGHT = 100`: Smoothing strength for small samples
- `DEFAULT_K_PCT = 0.220`: League average strikeout rate

**Baserunning aggression:**
- `BASERUNNING_AGGRESSION['single_1st_to_3rd']`: Probability runner advances 1st→3rd on single
- `BASERUNNING_AGGRESSION['double_1st_scores']`: Probability runner on 1st scores on double

**Optimization (future Sprint 4-5):**
- `OPT_EXHAUSTIVE_THRESHOLD = 10`: Use exhaustive search when roster ≤ 10 players
- `OPT_GA_*`: Genetic algorithm parameters (population size, generations, mutation rate)

## Coding Conventions

**Style:**
- Python 3.10+, type hints throughout
- 4 spaces, double quotes, snake_case functions/variables, PascalCase classes
- Tools: `black` (formatter), `ruff` (linter), `mypy` (type checker)

**Naming patterns:**
- `simulate_*()` for simulation functions
- `check_*()` for boolean checks
- `get_*()` for data retrieval
- `*_tab.py` for GUI tab components
- `*_manager.py` for coordinator classes

**Module headers:**
```python
# ============================================================================
# src/models/player.py
# ============================================================================
"""Module docstring here."""
```

**Docstrings:** Google-style with Args/Returns sections

## Testing

**Framework:** pytest 7.4.0+

**Current state:** Many tests are stubs with TODO comments. Priority: implement stubbed tests in `tests/baseball_mc_tests.py` (19 TODO placeholders).

**Coverage gaps:**
- Probability calculations (`src/models/probability.py`)
- Baserunning advancement (`src/models/baserunning.py`)
- Constraint validation (`src/gui/utils/constraint_validator.py`)
- End-to-end game simulation

**Validation:** Standalone scripts in `scripts/` for historical data validation (2024 Dodgers: 1.6% error).

## Important Patterns

**Entry points:**
- `gui.py`: GUI application (primary)
- `main.py`: CLI (stub, incomplete - contains TODOs only)

**State management:**
- File-based: All data in `data/` directory (git-ignored)
- In-memory: ResultsManager (10-result cache)
- GUI config: `~/.montecarlo_baseball/` via ConfigManager

**Error handling:**
- Many bare `except:` clauses (improvement needed)
- Console print statements (no structured logging)
- GUI errors via tkinter messagebox

**Threading:**
- `SimulationRunner` spawns background thread for long-running simulations
- Progress callbacks: `progress_callback(current, total)`
- GUI polls queue every 100ms for updates

## Current Development Phase

**Completed (v0.4.1):**
- ✅ Core simulation engine with K% (strikeout rate) modeling
- ✅ 8-tab GUI application
- ✅ Results Manager & Compare Tab
- ✅ Model validated (1.6% error on 2024 Dodgers)

**Active Development:**
See `docs/ROADMAP.md` for full roadmap. Key upcoming work:
- Sprint 3: Position-level tracking (batting order slot vs. fielding position)
- Sprint 4-5: Lineup optimization (exhaustive search + genetic algorithm)
- Sprint 6-7: Enhanced visualizations, Excel export, UI polish

## Special Notes

**Probability decomposition:** The model uses `decompose_slash_line()` to convert BA/OBP/SLG into discrete PA outcome probabilities (WALK, STRIKEOUT, OUT, HIT), then determines hit types (1B/2B/3B/HR) using Bayesian-smoothed distributions based on player ISO and actual hit counts.

**Strikeout modeling (v0.4.1):** STRIKEOUT is a distinct outcome separate from OUT. Strikeouts cannot produce sacrifice flies (no ball in play). Player-specific K% loaded from FanGraphs data with `DEFAULT_K_PCT` fallback.

**Reproducibility:** All stochastic processes use numpy RandomState with configurable seed (`RANDOM_SEED` in config.py).

**Data source:** Primary data from Baseball Reference via `pybaseball` library. Target team: 2025 Toronto Blue Jays.

**No database:** All data stored as CSV files in `data/` directory (git-ignored).

## Quick Context Files

For deep architectural understanding, see `.planning/codebase/`:
- `ARCHITECTURE.md`: Layered architecture, data flow, key abstractions
- `STRUCTURE.md`: Directory layout, file organization
- `CONVENTIONS.md`: Naming patterns, code style, docstring format
- `TESTING.md`: Test framework, patterns, coverage gaps
