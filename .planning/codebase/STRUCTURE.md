# Codebase Structure

**Analysis Date:** 2026-01-10

## Directory Layout

```
montecarlo-baseball/
├── main.py                 # CLI entry point (stub, incomplete)
├── gui.py                  # GUI entry point, MonteCarloBaseballGUI class
├── config.py               # Global configuration constants
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── CHANGELOG.md            # Version history
│
├── src/                    # Application source code
│   ├── data/              # Data acquisition and transformation
│   ├── models/            # Domain objects and probability logic
│   ├── engine/            # Simulation engine (game/inning/PA)
│   ├── simulation/        # Orchestration (batch/season)
│   └── gui/               # Tkinter GUI components
│
├── tests/                  # Test suite
├── scripts/                # Standalone utility scripts
├── data/                   # Data files (git-ignored)
├── notebooks/              # Jupyter notebooks
├── docs/                   # Documentation
└── .planning/              # Project planning artifacts
```

## Directory Purposes

**src/data/**
- Purpose: Data acquisition from external sources
- Contains: Web scraping, CSV processing
- Key files:
  - `scraper.py` - pybaseball integration, `get_team_batting_stats()`
  - `processor.py` - DataFrame to Player objects, `create_player_from_stats()`

**src/models/**
- Purpose: Domain objects and business logic
- Contains: Player, probabilities, baserunning, positions
- Key files:
  - `player.py` - Player dataclass with stats and probabilities
  - `probability.py` - Slash line decomposition, Bayesian smoothing
  - `position.py` - FieldingPosition dataclass (10 positions)
  - `baserunning.py` - Runner advancement logic
  - `stolen_bases.py` - SB/CS rate modeling
  - `sacrifice_fly.py` - Sacrifice fly detection
  - `errors.py` - Error/WP advancement

**src/engine/**
- Purpose: Hierarchical game simulation
- Contains: Game, inning, PA outcome generation
- Key files:
  - `pa_generator.py` - PAOutcomeGenerator class
  - `inning.py` - `simulate_half_inning()`
  - `game.py` - `simulate_game()` (9 innings)
  - `game_state.py` - Game state representation

**src/simulation/**
- Purpose: Simulation orchestration
- Contains: Season and batch aggregation
- Key files:
  - `season.py` - `simulate_season()` (162 games)
  - `batch.py` - `run_simulations()` (N iterations)

**src/gui/**
- Purpose: Tkinter desktop interface
- Subdirectories:
  - `tabs/` - 9 tab components
  - `widgets/` - Reusable UI components
  - `utils/` - Managers and helpers

**src/gui/tabs/**
- `setup_tab.py` - Team/season configuration
- `lineup_tab.py` - Drag-and-drop lineup builder
- `baserunning_tab.py` - Probabilistic advancement settings
- `errors_tab.py` - Error rate configuration
- `distribution_tab.py` - Hit distribution tuning
- `validation_tab.py` - Model validation
- `output_tab.py` - Output format settings
- `run_tab.py` - Simulation execution and visualization
- `compare_tab.py` - Side-by-side result comparison

**src/gui/widgets/**
- `lineup_builder.py` - Drag-and-drop lineup UI
- `player_list.py` - Searchable player list
- `comparison_table.py` - Result comparison table
- `constraint_dialog.py` - Constraint configuration
- `labeled_slider.py` - Reusable slider component
- `summary_card.py` - Result summary display

**src/gui/utils/**
- `simulation_runner.py` - Background thread executor
- `results_manager.py` - Store/retrieve up to 10 results
- `config_manager.py` - Persist GUI settings to disk
- `constraint_validator.py` - Validate lineup constraints

## Key File Locations

**Entry Points:**
- `gui.py` - GUI application launcher
- `main.py` - CLI launcher (stub)

**Configuration:**
- `config.py` - All simulation parameters
- `requirements.txt` - Python dependencies

**Core Simulation:**
- `src/simulation/batch.py::run_simulations()` - Main orchestrator
- `src/simulation/season.py::simulate_season()` - Season runner
- `src/engine/game.py::simulate_game()` - Game runner
- `src/engine/inning.py::simulate_half_inning()` - Inning runner
- `src/engine/pa_generator.py::PAOutcomeGenerator` - Outcome generator

**Player Data & Probability:**
- `src/data/scraper.py::get_team_batting_stats()` - Fetch from pybaseball
- `src/data/processor.py::create_player_from_stats()` - Create Player objects
- `src/models/probability.py::decompose_slash_line()` - Calculate PA probabilities

**Testing:**
- `tests/baseball_mc_tests.py` - Main test suite (mostly stubs)
- `tests/test_new_features.py` - Feature validation
- `scripts/validate_simulation.py` - Model validation

## Naming Conventions

**Files:**
- snake_case for all Python files
- `*_tab.py` - GUI tab components
- `*_manager.py` - Manager/coordinator classes

**Directories:**
- Lowercase, organized by responsibility
- `src/{data,models,engine,simulation,gui}/`

**Special Patterns:**
- `__init__.py` in all packages
- Module headers: `# ============================================================================`

## Where to Add New Code

**New Feature:**
- Primary code: Appropriate layer in `src/`
- Tests: `tests/`
- Config if needed: `config.py`

**New Tab:**
- Implementation: `src/gui/tabs/{name}_tab.py`
- Register in: `gui.py`

**New Simulation Logic:**
- Models: `src/models/`
- Engine changes: `src/engine/`
- Orchestration: `src/simulation/`

**New Widget:**
- Implementation: `src/gui/widgets/{name}.py`
- Export from: `src/gui/widgets/__init__.py`

## Special Directories

**data/**
- Purpose: CSV data storage
- Subdirectories: `raw/`, `processed/`, `analysis/`, `validation/`
- Committed: No (git-ignored)

**notebooks/**
- Purpose: Exploratory analysis
- Committed: Yes

**.planning/**
- Purpose: GSD project planning
- Committed: Yes

---

*Structure analysis: 2026-01-10*
*Update when directory structure changes*
