#!/usr/bin/env python3
"""
Run simulations for validation teams and compare to actual season performance.

Usage:
    python scripts/validate_simulation.py --team LAD --season 2024
    python scripts/validate_simulation.py --team LAD --season 2024 --iterations 10000
    python scripts/validate_simulation.py --load-csv data/validation/validation_LAD_2024.csv
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pandas as pd
from src.data.scraper import get_team_batting_stats, prepare_player_stats
from src.data.processor import prepare_roster
from src.simulation.batch import run_simulations
import config


def load_validation_data(team: str, season: int):
    """
    Load validation dataset from CSV.

    Args:
        team: Team abbreviation
        season: Season year

    Returns:
        Prepared DataFrame
    """
    csv_path = Path(f'data/validation/validation_{team}_{season}.csv')

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Validation data not found: {csv_path}\n"
            f"Run: python scripts/prepare_validation_data.py --team {team} --season {season}"
        )

    return pd.read_csv(csv_path)


def get_actual_runs(team: str, season: int):
    """
    Get actual runs scored by team in a season.

    Args:
        team: Team abbreviation
        season: Season year

    Returns:
        Actual runs scored (int) or None if not available
    """
    from pybaseball import team_batting

    try:
        team_results = team_batting(season)
        team_row = team_results[team_results['Team'] == team]

        if not team_row.empty and 'R' in team_row.columns:
            return int(team_row['R'].values[0])
    except:
        pass

    return None


def validate_against_actual_results(
    team: str,
    season: int,
    n_iterations: int = 10000,
    n_games: int = 162,
    random_seed: int = 42,
    verbose: bool = True
):
    """
    Run simulation for a team and compare to their actual season performance.

    Args:
        team: Team abbreviation
        season: Season year
        n_iterations: Number of simulations to run
        n_games: Games per season
        random_seed: Random seed for reproducibility
        verbose: Print progress messages

    Returns:
        Dictionary with validation results
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"VALIDATION SIMULATION: {team} {season}")
        print(f"{'='*70}\n")

    # Load validation data
    if verbose:
        print("Loading validation dataset...")

    try:
        roster_df = load_validation_data(team, season)
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return None

    if verbose:
        print(f"  ✓ Loaded {len(roster_df)} players")

    # Convert to Player objects
    if verbose:
        print("Creating lineup...")

    roster = prepare_roster(roster_df)

    # Create lineup from top 9 players by PA
    lineup = sorted(roster, key=lambda p: p.pa, reverse=True)[:9]

    if verbose:
        print(f"  ✓ Created lineup from top 9 players by PA:")
        for i, player in enumerate(lineup, 1):
            print(f"     {i}. {player.name:20s} {player.pa:3d} PA | {player.ba:.3f}/{player.obp:.3f}/{player.slg:.3f}")

    # Get actual runs
    if verbose:
        print(f"\nFetching actual results...")

    actual_runs = get_actual_runs(team, season)

    if actual_runs:
        if verbose:
            print(f"  ✓ Actual runs scored: {actual_runs}")
    else:
        if verbose:
            print(f"  ⚠ Could not fetch actual runs")

    # Run simulation
    if verbose:
        print(f"\nRunning {n_iterations:,} simulations ({n_games} games each)...")
        print("This may take a few minutes...\n")

    results = run_simulations(
        lineup=lineup,
        n_iterations=n_iterations,
        n_games=n_games,
        random_seed=random_seed,
        verbose=1 if verbose else 0
    )

    # Extract simulated statistics
    simulated_runs_mean = results['summary']['runs']['mean']
    simulated_runs_median = results['summary']['runs']['median']
    simulated_runs_std = results['summary']['runs']['std']
    simulated_runs_ci = results['summary']['runs']['ci_95']
    simulated_runs_min = results['summary']['runs']['min']
    simulated_runs_max = results['summary']['runs']['max']

    # Calculate validation metrics
    if actual_runs:
        error = simulated_runs_mean - actual_runs
        error_abs = abs(error)
        error_pct = (error / actual_runs) * 100
        within_ci = simulated_runs_ci[0] <= actual_runs <= simulated_runs_ci[1]

        # Calculate percentile of actual result
        raw_runs = results['raw_data']['season_runs']
        actual_percentile = (sum(r <= actual_runs for r in raw_runs) / len(raw_runs)) * 100
    else:
        error = None
        error_abs = None
        error_pct = None
        within_ci = None
        actual_percentile = None

    # Create validation result
    validation_result = {
        'team': team,
        'season': season,
        'n_iterations': n_iterations,
        'n_games': n_games,
        'lineup': [p.name for p in lineup],
        'simulated_mean': simulated_runs_mean,
        'simulated_median': simulated_runs_median,
        'simulated_std': simulated_runs_std,
        'simulated_ci_95': simulated_runs_ci,
        'simulated_min': simulated_runs_min,
        'simulated_max': simulated_runs_max,
        'actual_runs': actual_runs,
        'error': error,
        'error_abs': error_abs,
        'error_pct': error_pct,
        'within_95ci': within_ci,
        'actual_percentile': actual_percentile
    }

    # Print results
    if verbose:
        print(f"\n{'='*70}")
        print("VALIDATION RESULTS")
        print(f"{'='*70}\n")

        print("Simulated Results:")
        print(f"  Mean runs:        {simulated_runs_mean:7.1f}")
        print(f"  Median runs:      {simulated_runs_median:7.1f}")
        print(f"  Std dev:          {simulated_runs_std:7.1f}")
        print(f"  95% CI:           [{simulated_runs_ci[0]:.1f}, {simulated_runs_ci[1]:.1f}]")
        print(f"  Range:            {simulated_runs_min} - {simulated_runs_max}")

        if actual_runs:
            print(f"\nActual Results:")
            print(f"  Actual runs:      {actual_runs:7d}")

            print(f"\nValidation Metrics:")
            print(f"  Error:            {error:+7.1f} runs ({error_pct:+.1f}%)")
            print(f"  Absolute error:   {error_abs:7.1f} runs")
            print(f"  Within 95% CI:    {'✓ YES' if within_ci else '✗ NO'}")
            print(f"  Actual percentile: {actual_percentile:.1f}th percentile of simulations")

            # Assessment
            print(f"\n{'='*70}")
            print("ASSESSMENT")
            print(f"{'='*70}\n")

            if error_abs < actual_runs * 0.05:
                print("✓ EXCELLENT: Error within 5% of actual")
            elif error_abs < actual_runs * 0.10:
                print("✓ GOOD: Error within 10% of actual")
            elif error_abs < actual_runs * 0.15:
                print("⚠ ACCEPTABLE: Error within 15% of actual")
            else:
                print("✗ POOR: Error exceeds 15% of actual")

            if within_ci:
                print("✓ WELL-CALIBRATED: Actual result within 95% confidence interval")
            else:
                if actual_runs < simulated_runs_ci[0]:
                    print("⚠ OVER-PREDICTION: Actual result below 95% CI")
                else:
                    print("⚠ UNDER-PREDICTION: Actual result above 95% CI")

        print(f"\n{'='*70}\n")

    return validation_result


def export_validation_results(results: list, filename: str = 'validation_results.csv'):
    """
    Export validation results to CSV.

    Args:
        results: List of validation result dictionaries
        filename: Output filename
    """
    # Flatten results for CSV export
    flattened = []

    for r in results:
        if r is None:
            continue

        flattened.append({
            'team': r['team'],
            'season': r['season'],
            'n_iterations': r['n_iterations'],
            'simulated_mean': round(r['simulated_mean'], 1),
            'simulated_median': round(r['simulated_median'], 1),
            'simulated_std': round(r['simulated_std'], 1),
            'simulated_ci_low': round(r['simulated_ci_95'][0], 1),
            'simulated_ci_high': round(r['simulated_ci_95'][1], 1),
            'actual_runs': r['actual_runs'],
            'error': round(r['error'], 1) if r['error'] is not None else None,
            'error_pct': round(r['error_pct'], 2) if r['error_pct'] is not None else None,
            'within_95ci': r['within_95ci'],
            'actual_percentile': round(r['actual_percentile'], 1) if r['actual_percentile'] is not None else None
        })

    df = pd.DataFrame(flattened)

    output_path = Path('data/validation') / filename
    df.to_csv(output_path, index=False)

    print(f"\n✓ Validation results saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run validation simulation')
    parser.add_argument('--team', type=str, help='Team abbreviation (e.g., LAD, STL)')
    parser.add_argument('--season', type=int, help='Season year')
    parser.add_argument('--iterations', type=int, default=10000, help='Number of simulations (default: 10,000)')
    parser.add_argument('--games', type=int, default=162, help='Games per season (default: 162)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')

    args = parser.parse_args()

    if not args.team or not args.season:
        parser.print_help()
        return 1

    verbose = not args.quiet

    # Run validation
    result = validate_against_actual_results(
        team=args.team.upper(),
        season=args.season,
        n_iterations=args.iterations,
        n_games=args.games,
        random_seed=args.seed,
        verbose=verbose
    )

    if result and args.export:
        export_validation_results([result])

    return 0


if __name__ == '__main__':
    sys.exit(main())
