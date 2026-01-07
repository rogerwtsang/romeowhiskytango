# Monte Carlo Baseball Simulator - Development Roadmap

## Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Core Simulation Engine | Complete | 0.1.0 |
| GUI Application (8 tabs) | Complete | 0.1.0 |
| Results Manager | Complete | 0.2.0 |
| Model Validation | Complete | 0.3.0 |
| Compare Tab | Complete | 0.4.0 |
| Lineup Optimization | Planned | - |

---

## Completed Work

### Sprint 1: Foundation (Complete)
- [x] **Task A1**: Results Manager (`src/gui/utils/results_manager.py`)
- [x] **Task A2**: Save Results button in Run tab
- [x] **Task B1**: Optimizer configuration in `config.py`

### Validation Track (Complete)
- [x] **Task V1**: Roster Consistency Analyzer
- [x] **Task V2**: Validation Dataset Preparation
- [x] **Task V3**: Validation Simulation
- [x] Model validated at 1.6% error (2024 Dodgers: 855 simulated vs 842 actual)

### Sprint 2: Compare Tab (Complete)
- [x] **Task A5**: Compare Tab UI Shell
- [x] **Task A6**: Results Selection UI (2-4 lineups)
- [x] **Task A7**: Side-by-Side Statistics Table
- [x] **Task A8**: Box Plot Comparison
- [x] Summary Cards with baseline difference
- [x] Distribution histograms (overlaid)
- [x] Effect size analysis (Cohen's d)

---

## Upcoming Sprints

### Sprint 3: Position-Level Tracking
**Goal**: Track contributions by batting order slot AND fielding position

| Task | Description | Files | Est. Time |
|------|-------------|-------|-----------|
| A3 | Add position tracking to season simulation | `src/simulation/season.py` | 1-2 hrs |
| A4 | Aggregate position stats in batch simulation | `src/simulation/batch.py` | 30 min |
| A10 | Position contribution breakdown charts | `src/gui/tabs/compare_tab.py` | 1-2 hrs |

**Two Distinct Position Concepts**:

1. **Batting Order Position** (1-9): The slot in the lineup
   - Purpose: Analyze batting order effectiveness
   - Question answered: "Does batting 3rd produce more runs than batting 7th?"
   - Use case: Lineup optimization

2. **Fielding Position** (C, 1B, 2B, SS, 3B, LF, CF, RF, DH): Defensive role
   - Purpose: Roster building, platoon considerations
   - Question answered: "How do my outfielders compare to my infielders offensively?"
   - Use case: Roster construction, position flexibility analysis

**Implementation Notes**:
- Track stats automatically (always on, no toggle)
- Track both batting order slot AND fielding position when runs scored
- Return `batting_order_stats[1-9]` and `fielding_position_stats[pos]` dicts
- Add two charts in Compare tab: one for batting order, one for fielding position

### Sprint 4: Optimization Core
**Goal**: Build the optimization algorithm infrastructure

| Task | Description | Files | Est. Time |
|------|-------------|-------|-----------|
| B2 | Optimization Results Class | `src/optimization/results.py` | 30 min |
| B3 | Exhaustive Search Algorithm | `src/optimization/exhaustive.py` | 2 hrs |
| B4 | Genetic Algorithm | `src/optimization/genetic.py` | 3 hrs |
| B5 | Optimizer Wrapper | `src/optimization/optimizer.py` | 1 hr |

**Design Decisions**:
- **Exhaustive**: Try all 9! = 362,880 permutations when roster ≤ 10 players
- **Genetic Algorithm**: For larger rosters
  - Population: 50 lineups
  - Generations: 100 (configurable)
  - Tournament selection (size=3)
  - Order crossover (OX)
  - Swap mutation (rate=0.1)
  - Elitism: keep top 10%

### Sprint 5: Optimization GUI
**Goal**: Create user interface for lineup optimization

| Task | Description | Files | Est. Time |
|------|-------------|-------|-----------|
| B6 | Optimization Tab UI Shell | `src/gui/tabs/optimization_tab.py` | 1 hr |
| B7 | Wire Up Optimization Execution | `src/gui/tabs/optimization_tab.py` | 1-2 hrs |
| B8 | Results Display (Top 10) | `src/gui/tabs/optimization_tab.py` | 1 hr |
| B9 | "Apply to Lineup Tab" button | `lineup_tab.py`, `optimization_tab.py` | 1 hr |

**UI Layout**:
```
[Method: Auto/Exhaustive/Genetic]  [Objective: Max Mean Runs]
[Simulation Quality: ====|======== ] Fast <-> Accurate

[START OPTIMIZATION]  [STOP]

Progress: [===============>        ] 65%
Best so far: 845.2 runs/season

Top 10 Results:
1. 847.3 runs | Lineup: Betts, Freeman, ...
2. 846.1 runs | Lineup: ...

[APPLY TO LINEUP TAB]
```

### Sprint 6: Polish & Enhancements
**Goal**: Additional visualizations and exports

| Task | Description | Files | Est. Time |
|------|-------------|-------|-----------|
| A9 | Violin Plot Comparison | `compare_tab.py` | 1 hr |
| A12 | Excel Export with Formatting | `src/gui/utils/excel_exporter.py` | 2 hrs |
| B11 | Convergence Plot (GA) | `optimization_tab.py` | 1 hr |
| B12 | Result Caching | `optimizer.py` | 1 hr |

### Sprint 7: Quick Wins
**Goal**: Quality of life improvements

| Task | Description | Files | Est. Time |
|------|-------------|-------|-----------|
| C1 | Simulation Convergence Plot | `run_tab.py` | 1 hr |
| C2 | Tooltips for GUI Controls | Multiple | 1 hr |
| C3 | Preset Configuration Save/Load | `src/gui/utils/presets.py` | 1-2 hrs |

---

## Architecture Overview

### File Structure
```
montecarlo_baseball/
├── gui.py                      # Main GUI entry point
├── config.py                   # Central configuration
├── src/
│   ├── data/                   # Data acquisition
│   ├── models/                 # Player models, probability
│   ├── engine/                 # Game simulation
│   ├── simulation/             # Season/batch orchestration
│   ├── optimization/           # [PLANNED] Optimization algorithms
│   │   ├── optimizer.py
│   │   ├── exhaustive.py
│   │   ├── genetic.py
│   │   └── results.py
│   └── gui/
│       ├── tabs/               # 9 GUI tabs
│       ├── widgets/            # Custom components
│       └── utils/              # Results manager, config
├── scripts/                    # Validation scripts
├── data/                       # Cached data, validation results
└── docs/                       # Documentation
```

### Data Flow
```
User Input (GUI) → Validate → Create config dict →
→ Pass to simulation_runner (thread) → Run simulation →
→ Results via queue → Update GUI results tab →
→ Save to ResultsManager → Compare in Compare tab
```

### Threading Pattern
```python
class SimulationRunner:
    def run_in_thread(self, lineup, config_dict, callback):
        # Spawns worker thread
        # Sends progress updates via queue
        # GUI polls queue every 100ms
```

---

## Configuration Parameters

### Optimization Settings (in `config.py`)
```python
OPT_EXHAUSTIVE_THRESHOLD = 10    # Use exhaustive if roster <= this
OPT_GA_POPULATION_SIZE = 50
OPT_GA_GENERATIONS = 100
OPT_GA_MUTATION_RATE = 0.1
OPT_GA_TOURNAMENT_SIZE = 3
OPT_GA_ELITISM_RATE = 0.10
OPT_GA_NO_IMPROVEMENT_STOP = 20
OPT_DEFAULT_SIMS_PER_LINEUP = 1000
OPT_EXHAUSTIVE_SIMS = 100
OPT_GA_SIMS_INITIAL = 1000
OPT_GA_SIMS_FINAL = 5000
OPT_PRIMARY_OBJECTIVE = 'mean_runs'
OPT_ENABLE_CACHE = True
OPT_MAX_CACHE_SIZE = 10000
```

---

## Future Enhancements (Post-Sprint 7)

### Model Improvements
- [ ] Opponent/pitching integration for win/loss tracking
- [ ] Platoon splits (L/R batter-pitcher matchups)
- [ ] Situational hitting (count-based outcomes)
- [ ] Park factors (ballpark adjustments)
- [ ] Advanced baserunning with speed ratings

### Technical Improvements
- [ ] CLI implementation (`main.py`)
- [ ] Performance optimization (vectorization, parallelization)
- [ ] Comprehensive test suite
- [ ] Web interface

---

## Quick Reference: Task IDs

### Track A: Results Visualization
- A1-A2: Results Manager (DONE)
- A3-A4: Position Tracking
- A5-A7: Compare Tab basics (DONE)
- A8-A10: Comparison charts (A8 DONE)
- A11-A12: Export features

### Track B: Optimization
- B1: Config (DONE)
- B2-B5: Core algorithms
- B6-B9: GUI
- B10-B12: Polish

### Track C: Quick Wins
- C1-C3: UI improvements

---

*Last updated: 2025-01-07*
