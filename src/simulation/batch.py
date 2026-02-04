# ============================================================================
# src/simulation/batch.py
# ============================================================================
"""Batch simulation runner."""

from typing import List, Dict, Callable, Optional
import numpy as np
from scipy.stats import norm
from src.models.player import Player
from src.simulation.season import simulate_season
from src.engine.pa_generator import PAOutcomeGenerator
import config


def _calculate_win_probability(
    season_runs_arr: np.ndarray,
    n_games: int,
    n_iterations: int
) -> Dict[str, float]:
    """Calculate win probability with Wilson score confidence interval.

    Win probability is defined as the proportion of simulated seasons
    that exceed league average runs (4.5 runs/game).

    Args:
        season_runs_arr: Array of season run totals
        n_games: Games per season
        n_iterations: Number of iterations

    Returns:
        Dictionary with mean, ci_lower, ci_upper
    """
    # League average ~4.5 runs/game
    league_avg_runs = 4.5 * n_games
    wins_above_avg = np.sum(season_runs_arr >= league_avg_runs)
    p_hat = wins_above_avg / n_iterations

    # Wilson score interval for 95% CI (more accurate for proportions)
    z = norm.ppf(0.975)  # 1.96 for 95% CI
    n = n_iterations
    denominator = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denominator
    spread = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n) / denominator
    ci_lower = max(0.0, center - spread)
    ci_upper = min(1.0, center + spread)

    return {
        'mean': float(p_hat),
        'ci_lower': float(ci_lower),
        'ci_upper': float(ci_upper)
    }


def run_simulations(
    lineup: List[Player],
    n_iterations: int = config.N_SIMULATIONS,
    n_games: int = config.N_GAMES_PER_SEASON,
    random_seed: int = config.RANDOM_SEED,
    verbose: int = config.VERBOSITY,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> Dict:
    """Run multiple season simulations and aggregate results.

    Args:
        lineup: List of 9 Player objects in batting order
        n_iterations: Number of seasons to simulate
        n_games: Games per season
        random_seed: Random seed for reproducibility
        verbose: Verbosity level (0=silent, 1=progress, 2=debug)
        progress_callback: Optional callback function(current, total) for progress updates

    Returns:
        Dictionary with aggregated statistics across all simulations
    """
    if verbose >= 1:
        print(f"Running {n_iterations:,} season simulations...")
        print(f"Games per season: {n_games}")
        print(f"Random seed: {random_seed}\n")

    # Initialize PA generator with seed
    pa_gen = PAOutcomeGenerator(random_state=random_seed)

    # Collect results
    season_runs = []
    season_hits = []
    season_walks = []
    season_sb = []
    season_cs = []
    season_sf = []
    season_lob = []

    # Track progress
    progress_points = [int(n_iterations * p) for p in [0.25, 0.5, 0.75, 1.0]]

    for i in range(n_iterations):
        # Simulate season
        result = simulate_season(lineup, pa_gen, n_games)

        season_runs.append(result['total_runs'])
        season_hits.append(result['total_hits'])
        season_walks.append(result['total_walks'])
        season_sb.append(result.get('total_sb', 0))
        season_cs.append(result.get('total_cs', 0))
        season_sf.append(result.get('total_sf', 0))
        season_lob.append(result.get('total_lob', 0))

        # Progress updates
        if verbose >= 1 and (i + 1) in progress_points:
            pct = ((i + 1) / n_iterations) * 100
            print(f"  Progress: {i+1:,}/{n_iterations:,} ({pct:.0f}%)")

        # Call progress callback if provided (every 100 iterations)
        if progress_callback and (i % 100 == 0 or i == n_iterations - 1):
            progress_callback(i + 1, n_iterations)

    if verbose >= 1:
        print("\nSimulation complete!\n")

    # Convert to numpy arrays for statistics
    season_runs_arr = np.array(season_runs)
    season_hits_arr = np.array(season_hits)
    season_walks_arr = np.array(season_walks)
    season_sb_arr = np.array(season_sb)
    season_cs_arr = np.array(season_cs)
    season_sf_arr = np.array(season_sf)
    season_lob_arr = np.array(season_lob)

    # Calculate statistics
    summary = {
        'n_simulations': n_iterations,
        'n_games_per_season': n_games,

        # Run statistics
        'runs': {
            'mean': float(np.mean(season_runs_arr)),
            'std': float(np.std(season_runs_arr)),
            'median': float(np.median(season_runs_arr)),
            'min': int(np.min(season_runs_arr)),
            'max': int(np.max(season_runs_arr)),
            'percentiles': {
                '5th': float(np.percentile(season_runs_arr, 5)),
                '25th': float(np.percentile(season_runs_arr, 25)),
                '50th': float(np.percentile(season_runs_arr, 50)),
                '75th': float(np.percentile(season_runs_arr, 75)),
                '95th': float(np.percentile(season_runs_arr, 95))
            },
            'ci_95': (
                float(np.percentile(season_runs_arr, 2.5)),
                float(np.percentile(season_runs_arr, 97.5))
            )
        },

        # Hit statistics
        'hits': {
            'mean': float(np.mean(season_hits_arr)),
            'std': float(np.std(season_hits_arr)),
            'median': float(np.median(season_hits_arr))
        },

        # Walk statistics
        'walks': {
            'mean': float(np.mean(season_walks_arr)),
            'std': float(np.std(season_walks_arr)),
            'median': float(np.median(season_walks_arr))
        },

        # Stolen base statistics
        'stolen_bases': {
            'mean': float(np.mean(season_sb_arr)),
            'std': float(np.std(season_sb_arr)),
            'median': float(np.median(season_sb_arr))
        },

        'caught_stealing': {
            'mean': float(np.mean(season_cs_arr)),
            'std': float(np.std(season_cs_arr)),
            'median': float(np.median(season_cs_arr))
        },

        # Sacrifice fly statistics
        'sacrifice_flies': {
            'mean': float(np.mean(season_sf_arr)),
            'std': float(np.std(season_sf_arr)),
            'median': float(np.median(season_sf_arr))
        },

        # Derived statistics
        'runs_per_game': {
            'mean': float(np.mean(season_runs_arr) / n_games),
            'std': float(np.std(season_runs_arr) / n_games)
        },

        # Win probability: proportion of seasons above league average runs
        # League average ~4.5 runs/game * n_games = expected season runs
        'win_probability': _calculate_win_probability(season_runs_arr, n_games, n_iterations),

        # LOB per game from tracked season totals
        'lob_per_game': {
            'mean': float(np.mean(season_lob_arr) / n_games),
            'std': float(np.std(season_lob_arr) / n_games)
        },

        # RISP data is NOT currently tracked in game engine
        # Placeholder with None - GUI handles gracefully
        'risp_conversion': None  # TODO: Add RISP tracking to game engine in future phase
    }

    # Store raw data for further analysis
    raw_data = {
        'season_runs': season_runs,
        'season_hits': season_hits,
        'season_walks': season_walks,
        'season_sb': season_sb,
        'season_cs': season_cs,
        'season_sf': season_sf,
        'season_lob': season_lob
    }

    return {
        'summary': summary,
        'raw_data': raw_data,
        'lineup': [{'name': p.name, 'ba': p.ba, 'obp': p.obp, 'slg': p.slg} for p in lineup]
    }


def print_simulation_results(results: Dict):
    """Pretty print simulation results.

    Args:
        results: Results dictionary from run_simulations
    """
    summary = results['summary']

    print("="*80)
    print("SIMULATION RESULTS")
    print("="*80)

    print(f"\nSimulation Parameters:")
    print(f"  Iterations: {summary['n_simulations']:,}")
    print(f"  Games per season: {summary['n_games_per_season']}")

    print(f"\nLineup:")
    for i, player in enumerate(results['lineup'], 1):
        print(f"  {i}. {player['name']}: {player['ba']:.3f}/{player['obp']:.3f}/{player['slg']:.3f}")

    print(f"\n" + "-"*80)
    print("RUNS PER SEASON")
    print("-"*80)

    runs = summary['runs']
    print(f"  Mean:       {runs['mean']:7.1f}")
    print(f"  Median:     {runs['median']:7.1f}")
    print(f"  Std Dev:    {runs['std']:7.1f}")
    print(f"  Min:        {runs['min']:7d}")
    print(f"  Max:        {runs['max']:7d}")

    print(f"\n  Percentiles:")
    print(f"    5th:      {runs['percentiles']['5th']:7.1f}")
    print(f"    25th:     {runs['percentiles']['25th']:7.1f}")
    print(f"    50th:     {runs['percentiles']['50th']:7.1f}")
    print(f"    75th:     {runs['percentiles']['75th']:7.1f}")
    print(f"    95th:     {runs['percentiles']['95th']:7.1f}")

    print(f"\n  95% Confidence Interval:")
    print(f"    [{runs['ci_95'][0]:.1f}, {runs['ci_95'][1]:.1f}]")

    print(f"\n  Runs per game: {summary['runs_per_game']['mean']:.2f} ± {summary['runs_per_game']['std']:.2f}")

    print(f"\n" + "-"*80)
    print("OTHER STATISTICS")
    print("-"*80)

    print(f"  Hits per season:  {summary['hits']['mean']:.1f} ± {summary['hits']['std']:.1f}")
    print(f"  Walks per season: {summary['walks']['mean']:.1f} ± {summary['walks']['std']:.1f}")

    if 'stolen_bases' in summary:
        sb_mean = summary['stolen_bases']['mean']
        cs_mean = summary['caught_stealing']['mean']
        sb_pct = sb_mean / (sb_mean + cs_mean) * 100 if (sb_mean + cs_mean) > 0 else 0
        print(f"  Stolen bases:     {sb_mean:.1f} ± {summary['stolen_bases']['std']:.1f}")
        print(f"  Caught stealing:  {cs_mean:.1f} ± {summary['caught_stealing']['std']:.1f}")
        print(f"  SB success rate:  {sb_pct:.1f}%")

    if 'sacrifice_flies' in summary:
        print(f" Sacrifice flies: {summary['sacrifice_flies']['mean']:.1f} ± {summary['sacrifice_flies']['std']:.1f}")

    print("\n" + "="*80)


if __name__ == "__main__":
    # Test batch simulation
    import sys
    sys.path.insert(0, '.')
    from src.data.scraper import load_data
    from src.data.processor import prepare_lineup

    print("=== Testing Batch Simulation ===\n")

    # Load test data
    try:
        df = load_data('blue_jays_2025_prepared.csv', 'processed')
    except:
        df = load_data('blue_jays_2024_prepared.csv', 'processed')

    # Create lineup
    lineup = prepare_lineup(df)
    print(f"Created lineup with {len(lineup)} players\n")

    # Run smaller test first (1,000 iterations)
    print("--- Quick Test: 1,000 simulations ---\n")
    results = run_simulations(
        lineup,
        n_iterations=1000,
        n_games=162,
        random_seed=42,
        verbose=1
    )

    print_simulation_results(results)

    # Optional: Run full 10,000 simulation test
    print("\n\n" + "="*80)
    user_input = input("Run full 10,000 simulation test? (y/n): ")

    if user_input.lower() == 'y':
        print("\n--- Full Test: 10,000 simulations ---\n")
        results_full = run_simulations(
            lineup,
            n_iterations=10000,
            n_games=162,
            random_seed=42,
            verbose=1
        )

        print_simulation_results(results_full)

        # Compare to 1,000 iteration results
        print("\n" + "="*80)
        print("CONVERGENCE CHECK")
        print("="*80)

        mean_1k = results['summary']['runs']['mean']
        mean_10k = results_full['summary']['runs']['mean']
        diff = abs(mean_10k - mean_1k)
        pct_diff = (diff / mean_10k) * 100

        print(f"\nMean runs (1,000 iterations):  {mean_1k:.1f}")
        print(f"Mean runs (10,000 iterations): {mean_10k:.1f}")
        print(f"Difference: {diff:.1f} runs ({pct_diff:.2f}%)")

        if pct_diff < 1.0:
            print("\n✓ Results converged (< 1% difference)")
        else:
            print(f"\n⚠ Results not fully converged ({pct_diff:.2f}% difference)")

    print("\n" + "="*80)
    print("✓ Batch simulation tests complete")
