# Technology Stack

**Analysis Date:** 2026-01-10

## Languages

**Primary:**
- Python 3.13.5 - All application code

**Secondary:**
- None detected

## Runtime

**Environment:**
- Python 3.13.5
- No version pinning file found (`.python-version` not detected)

**Package Manager:**
- pip with `requirements.txt`
- No lockfile (minimum versions only)

## Frameworks

**Core:**
- Tkinter (built-in) - Desktop GUI application
  - Entry: `gui.py`
  - 9-tab interface in `src/gui/tabs/`

**Testing:**
- pytest 7.4.0+ - Test framework (`tests/`)

**Build/Dev:**
- ruff 0.8.0+ - Fast Python linter
- black 24.0.0+ - Code formatter
- mypy 1.11.0+ - Type checker
- jupyter 1.0.0+ - Notebook support

## Key Dependencies

**Critical:**
- pybaseball 2.2.7+ - MLB data source (FanGraphs, Baseball Reference)
  - Used in: `src/data/scraper.py`
  - Functions: `batting_stats()`, `team_batting()`, `playerid_lookup()`
- numpy 1.24.0+ - Monte Carlo probability calculations
  - Used in: `src/engine/pa_generator.py`, `src/simulation/batch.py`
- pandas 2.0.0+ - Data manipulation and processing
  - Used in: `src/data/processor.py`, `src/data/scraper.py`
- scipy 1.10.0+ - Statistical functions

**Infrastructure:**
- matplotlib 3.7.0+ - Data visualization for histograms and plots
  - Used in: `src/gui/tabs/output_tab.py`

## Configuration

**Environment:**
- No environment variables required
- Configuration via `config.py` constants only
- No `.env` files detected

**Build:**
- `requirements.txt` - Python dependencies

**Key Configuration File:**
- `config.py` - Central configuration
  - Simulation: `N_SIMULATIONS=10000`, `N_GAMES_PER_SEASON=162`
  - Base-running toggles: `ENABLE_STOLEN_BASES`, `ENABLE_SACRIFICE_FLIES`
  - Hit distribution: `ISO_THRESHOLDS`, `HIT_DISTRIBUTIONS`
  - Optimization: GA parameters, Bayesian smoothing

## Platform Requirements

**Development:**
- Any platform with Python 3.13+
- No external dependencies (no Docker, no database)

**Production:**
- Desktop application (Tkinter GUI)
- Local filesystem for data storage (`data/` directory)
- No deployment infrastructure required

---

*Stack analysis: 2026-01-10*
*Update after major dependency changes*
