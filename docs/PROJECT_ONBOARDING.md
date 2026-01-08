# Baseball Monte Carlo Simulation - Project Onboarding

**Version:** 0.4.0
**Last Updated:** January 2025
**Status:** Active Development - Validation Complete, Optimization Phase Beginning

---

## Welcome Back / Welcome Aboard

This document brings everyone up to speed on the Baseball Monte Carlo Simulation project after the holiday break. Whether you're returning to the project or joining as a new intern, this will give you the context you need to contribute immediately.

---

## What This Project Does

We're building a **Monte Carlo simulation engine** that answers a fundamental baseball analytics question:

> **Can we determine the optimal batting order arrangement across a full 162-game season?**

The simulator takes real player statistics (batting average, on-base percentage, slugging) and runs thousands of simulated seasons to analyze how different lineup configurations affect run production.

---

## Current State of the Project

### Completed Milestones

| Sprint | Status | Description |
|--------|--------|-------------|
| **Validation Track** | Done | Model validated at **1.6% error** against 2024 Dodgers |
| **Sprint 1** | Done | Results Manager, Save functionality, Optimization config |
| **Sprint 2** | Done | Compare tab for side-by-side lineup analysis |

### Version History
- **v0.4.0** (Current) - Compare & Analyze tab with distribution overlays
- **v0.3.0** - Validation framework complete
- **v0.2.0** - Results manager and save functionality
- **v0.1.0** - Core simulation engine and 8-tab GUI

---

## How the Model Works

### The Probability Engine

The simulation converts player slash lines (BA/OBP/SLG) into plate appearance outcomes:

```
Player Stats: .280/.350/.450

1. Calculate outcome probabilities:
   - P(OUT)  = 1 - OBP = 0.650 (65.0%)
   - P(WALK) = OBP - BA = 0.070 (7.0%)
   - P(HIT)  = BA = 0.280 (28.0%)

2. Distribute hits by type (using ISO = SLG - BA):
   - Singles, Doubles, Triples, HRs
   - Uses Bayesian smoothing for small sample sizes
```

### Key Model Components

| Component | File | Purpose |
|-----------|------|---------|
| **PA Outcome Generator** | `src/engine/pa_generator.py` | Random outcome based on player probabilities |
| **Hit Distribution** | `src/models/probability.py` | Bayesian-smoothed 1B/2B/3B/HR splits |
| **Baserunning** | `src/models/baserunning.py` | Probabilistic runner advancement |
| **Stolen Bases** | `src/models/stolen_bases.py` | Player-specific SB/CS rates |
| **Sacrifice Flies** | `src/models/sacrifice_fly.py` | Runner on 3rd scores on flyout |
| **Errors** | `src/models/errors.py` | Defensive errors advance runners |

### Bayesian Smoothing

For players with limited data, we blend their actual hit distribution with league averages:

```python
# Prior equivalent to 100 at-bats of league average data
smoothed = (league_avg * 100 + player_actual * player_hits) / (100 + player_hits)
```

This prevents extreme distributions from low sample sizes while still respecting player tendencies as data accumulates.

---

## Model Accuracy & Validation

### Headline Result: 1.6% Error

We validated against the 2024 Los Angeles Dodgers (chosen for roster consistency):

| Metric | Value |
|--------|-------|
| **Simulated Runs** | 855.4 +/- 42.6 |
| **Actual Runs** | 842 |
| **Error** | +13.4 runs (+1.6%) |
| **95% CI** | [772, 936] - Actual is within |
| **Assessment** | EXCELLENT (<5% error) |

### Why This Matters

A 1.6% error means the model accurately captures the run-scoring dynamics of a full MLB season. This gives us confidence that lineup optimization comparisons will be meaningful, not just noise.

### Known Limitations

1. **No opponent modeling** - All games assume average pitching
2. **No platoon splits** - L/R matchups not considered
3. **No park factors** - All stadiums treated equally
4. **No clutch situations** - No situational hitting adjustments

These are acceptable for comparative lineup analysis but mean absolute run predictions should be interpreted with some caution.

---

## Configurable Parameters

The model includes sliders/controls for adjusting simulation behavior. These are accessible via the GUI tabs:

### Baserunning Tab

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| **SB Attempt Frequency** | 0.0-3.0 | 1.0 | Multiplier for stolen base attempts |
| **1st to 3rd on Single** | 0-100% | 28% | Extra-base advancement probability |
| **1st to Home on Double** | 0-100% | 60% | Runner scores from first |
| **2nd to Home on Double** | 0-100% | 98% | Runner scores from second |

**Presets available:** Conservative, Average, Aggressive

### Errors Tab

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| **Error Rate per PA** | 0-5% | 1.5% | ~1 error per 67 plate appearances |

### Why These Matter

The aggression parameters significantly affect run scoring. An aggressive team might score 5-10% more runs than a conservative team with identical players. This allows modeling different managerial styles.

---

## Project Architecture

```
montecarlo_baseball/
├── src/
│   ├── data/           # Player data from Baseball Reference
│   ├── models/         # Probability calculations, baserunning logic
│   ├── engine/         # PA/inning/game simulation
│   ├── simulation/     # Season and batch orchestration
│   ├── analysis/       # Results comparison
│   └── gui/            # 8-tab Tkinter application
│       ├── tabs/       # Setup, Lineup, Run, Compare, etc.
│       ├── widgets/    # Reusable components (LabeledSlider, etc.)
│       └── utils/      # ResultsManager, config management
├── scripts/            # Validation and analysis utilities
├── tests/              # Unit tests (pytest)
├── config.py           # Central configuration
├── gui.py              # GUI entry point
└── main.py             # CLI entry point (TODO)
```

---

## Running the Application

### GUI (Recommended)

```bash
python gui.py
```

**Workflow:**
1. **Setup Tab** - Select team and season
2. **Lineup Tab** - Build 9-player lineup (drag-and-drop)
3. **Baserunning/Errors Tabs** - Adjust parameters (optional)
4. **Run Tab** - Execute simulation (10,000 iterations recommended)
5. **Compare Tab** - Compare saved lineup results

### Validation Suite

```bash
python scripts/run_validation_suite.py --season 2024 --top-n 5
```

---

## Immediate Next Steps (Sprints 3-7)

| Sprint | Focus | Status |
|--------|-------|--------|
| **Sprint 3** | Position-level contribution tracking | In Progress |
| **Sprint 4** | Exhaustive lineup optimizer (<10 players) | Planned |
| **Sprint 5** | Genetic algorithm optimizer (>10 players) | Planned |
| **Sprint 6** | Enhanced visualizations (violin plots) | Planned |
| **Sprint 7** | Export improvements (Excel with formatting) | Planned |

### What Needs Attention Now

1. **Position-level tracking** - Which batting position contributes most to run production?
2. **Optimizer engine** - Begin implementing exhaustive search for small rosters
3. **Test coverage** - Core engine needs more comprehensive unit tests

---

## Key Files to Familiarize Yourself With

| File | Priority | Description |
|------|----------|-------------|
| `config.py` | High | All tunable parameters in one place |
| `src/models/probability.py` | High | Core probability calculations |
| `src/engine/pa_generator.py` | High | Heart of the simulation |
| `src/gui/tabs/run_tab.py` | Medium | Main simulation interface |
| `src/gui/tabs/compare_tab.py` | Medium | New comparison features |
| `scripts/run_validation_suite.py` | Medium | Validation workflow |

---

## Development Environment

### Dependencies

```bash
pip install -r requirements.txt
```

Key packages:
- `pybaseball` - Data from Baseball Reference/FanGraphs
- `numpy`, `pandas`, `scipy` - Statistical calculations
- `matplotlib` - Visualizations
- `pytest` - Testing
- `ruff`, `black`, `mypy` - Code quality

### Running Tests

```bash
pytest tests/
```

---

## Questions to Ask

If you're new to the project, here are good questions to explore:

1. How does the Bayesian prior weight (100) affect hit distributions for rookies vs veterans?
2. Why did we choose the Dodgers for validation? (Hint: roster consistency)
3. What's the difference between exhaustive search and genetic algorithm optimization?
4. How do the baserunning aggression sliders affect expected runs per game?

---

## Contact & Resources

- **CHANGELOG.md** - Detailed version history
- **README.md** - Installation and usage guide
- **docs/VALIDATION_TRACK_SUMMARY.md** - Validation methodology
- **GitHub Issues** - Bug reports and feature requests

---

*Welcome to the team. Let's find the optimal lineup.*
