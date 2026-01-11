# Architecture

**Analysis Date:** 2026-01-10

## Pattern Overview

**Overall:** Layered Monolith with Simulation Engine Architecture

**Key Characteristics:**
- Desktop GUI application (Tkinter)
- Hierarchical simulation engine (batch → season → game → inning → PA)
- File-based state (CSV storage, no database)
- Synchronous execution with background thread for simulations

## Layers

**Presentation Layer (GUI):**
- Purpose: User interface for configuration and results display
- Contains: Tkinter tabs, widgets, dialogs
- Location: `gui.py`, `src/gui/`
- Depends on: Simulation layer, utilities
- Used by: End user

**Simulation Orchestration Layer:**
- Purpose: Coordinate multi-season, multi-game simulations
- Contains: Batch runner, season aggregation
- Location: `src/simulation/batch.py`, `src/simulation/season.py`
- Depends on: Engine layer
- Used by: GUI via SimulationRunner

**Engine Layer:**
- Purpose: Core game simulation logic
- Contains: Game, inning, plate appearance simulation
- Location: `src/engine/`
- Depends on: Models layer
- Used by: Simulation layer

**Models Layer:**
- Purpose: Domain objects and probability calculations
- Contains: Player, probabilities, baserunning, positions
- Location: `src/models/`
- Depends on: config.py, numpy
- Used by: Engine layer, Data layer

**Data Layer:**
- Purpose: External data acquisition and transformation
- Contains: Web scraping, CSV processing
- Location: `src/data/`
- Depends on: pybaseball, pandas
- Used by: GUI for player data

## Data Flow

**Simulation Execution:**

1. User configures lineup in GUI (Lineup Tab)
2. User clicks "Run Simulation" (Run Tab)
3. `SimulationRunner.run_in_thread()` spawns background thread
4. `batch.py::run_simulations()` orchestrates iterations
5. For each iteration (1-10,000):
   - `season.py::simulate_season()` runs 162 games
   - `game.py::simulate_game()` simulates 9 innings
   - `inning.py::simulate_half_inning()` until 3 outs
   - `pa_generator.py::generate_outcome()` determines each PA
6. Results aggregated and returned to GUI
7. `ResultsManager` stores results for comparison

**Player Data Loading:**

1. Setup Tab triggers data fetch
2. `scraper.py::get_team_batting_stats()` calls pybaseball API
3. `processor.py::create_player_from_stats()` creates Player objects
4. `probability.py::decompose_slash_line()` calculates PA probabilities
5. Players available for lineup building

**State Management:**
- File-based: All data in `data/` directory
- In-memory: Simulation results in `ResultsManager` (10-result cache)
- GUI config: `~/.montecarlo_baseball/` via `ConfigManager`

## Key Abstractions

**Player:**
- Purpose: Core domain entity with stats and probabilities
- Location: `src/models/player.py`
- Pattern: Dataclass with calculated fields

**PAOutcomeGenerator:**
- Purpose: Stochastic plate appearance outcome generation
- Location: `src/engine/pa_generator.py`
- Pattern: Encapsulates numpy RandomState for reproducibility

**SimulationRunner:**
- Purpose: Background thread execution for GUI responsiveness
- Location: `src/gui/utils/simulation_runner.py`
- Pattern: Threading wrapper with progress callbacks

**ResultsManager:**
- Purpose: Store and compare simulation results
- Location: `src/gui/utils/results_manager.py`
- Pattern: In-memory cache (max 10 results)

**FieldingPosition:**
- Purpose: Type-safe position representation
- Location: `src/models/position.py`
- Pattern: Frozen dataclass (immutable)

## Entry Points

**GUI Entry:**
- Location: `gui.py`
- Triggers: User launches application
- Responsibilities: Initialize Tkinter, create tabs, start mainloop

**CLI Entry (Stub):**
- Location: `main.py`
- Status: Incomplete (TODO comments only)

**Validation Scripts:**
- Location: `scripts/`
- Purpose: Standalone validation and analysis

## Error Handling

**Strategy:** Exceptions bubble up, caught at boundaries

**Patterns:**
- Bare `except:` with fallback (data loading)
- Console output for errors
- GUI shows error dialogs via tkinter messagebox

**Issues:**
- Many bare `except:` clauses silently swallow errors
- No structured error logging

## Cross-Cutting Concerns

**Logging:**
- Console print statements only
- No structured logging framework

**Validation:**
- Minimal input validation
- `ConstraintValidator` for lineup rules

**Configuration:**
- Centralized in `config.py`
- Constants only (no environment-based config)

**Threading:**
- `SimulationRunner` manages background execution
- Progress callbacks via `progress_callback(current, total)`

---

*Architecture analysis: 2026-01-10*
*Update when major patterns change*
