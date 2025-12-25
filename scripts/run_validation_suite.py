#!/usr/bin/env python3
"""
Complete validation suite runner.

This script runs the full validation workflow:
1. Analyze roster consistency to find stable teams
2. Prepare validation datasets for top teams
3. Run simulations and compare to actual results

Usage:
    python scripts/run_validation_suite.py --season 2024 --top-n 5
    python scripts/run_validation_suite.py --start 2020 --end 2024 --top-n 3
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pandas as pd
from analyze_roster_consistency import analyze_roster_consistency, find_most_consistent_teams
from prepare_validation_data import prepare_validation_dataset
from validate_simulation import validate_against_actual_results, export_validation_results
import time


def run_full_validation_suite(
    season: int,
    top_n: int = 5,
    n_iterations: int = 10000,
    verbose: bool = True
):
    """
    Run complete validation suite for a single season.

    Args:
        season: Season year to validate
        top_n: Number of top consistent teams to validate
        n_iterations: Simulations per team
        verbose: Print progress messages

    Returns:
        List of validation results
    """
    if verbose:
        print(f"\n{'#'*70}")
        print(f"COMPLETE VALIDATION SUITE: {season} Season")
        print(f"{'#'*70}\n")

    # Step 1: Analyze roster consistency
    if verbose:
        print("STEP 1: Analyzing roster consistency...")
        print("-" * 70)

    consistency_df = analyze_roster_consistency(season, verbose=verbose)

    if consistency_df.empty:
        print("✗ No consistency data available")
        return []

    # Get top N most consistent teams
    top_teams = find_most_consistent_teams(consistency_df, top_n=top_n)

    if verbose:
        print(f"\nSelected {len(top_teams)} teams for validation:")
        for i, row in enumerate(top_teams.itertuples(), 1):
            print(f"  {i}. {row.team} - {row.total_players} players")

    # Step 2: Prepare validation datasets
    if verbose:
        print(f"\n{'#'*70}")
        print("STEP 2: Preparing validation datasets...")
        print("-" * 70 + "\n")

    validation_data = []
    for row in top_teams.itertuples():
        try:
            data = prepare_validation_dataset(
                team=row.team,
                season=season,
                min_pa=100,
                verbose=verbose
            )
            validation_data.append(data)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            if verbose:
                print(f"✗ Error preparing {row.team}: {str(e)}\n")

    if not validation_data:
        print("✗ No validation datasets prepared")
        return []

    # Step 3: Run validation simulations
    if verbose:
        print(f"\n{'#'*70}")
        print("STEP 3: Running validation simulations...")
        print("-" * 70 + "\n")

    validation_results = []
    for data in validation_data:
        try:
            result = validate_against_actual_results(
                team=data['team'],
                season=season,
                n_iterations=n_iterations,
                n_games=162,
                random_seed=42,
                verbose=verbose
            )
            validation_results.append(result)
        except Exception as e:
            if verbose:
                print(f"✗ Error validating {data['team']}: {str(e)}\n")

    # Print summary
    if verbose and validation_results:
        print(f"\n{'#'*70}")
        print("VALIDATION SUITE SUMMARY")
        print(f"{'#'*70}\n")

        print(f"Season:         {season}")
        print(f"Teams tested:   {len(validation_results)}")
        print(f"Simulations:    {n_iterations:,} per team\n")

        print("Results:")
        print("-" * 70)
        print(f"{'Team':<6} {'Actual':>7} {'Simulated':>10} {'Error':>10} {'Error %':>10} {'Within CI':>10}")
        print("-" * 70)

        for r in validation_results:
            if r and r['actual_runs']:
                within = '✓' if r['within_95ci'] else '✗'
                print(f"{r['team']:<6} {r['actual_runs']:>7} "
                      f"{r['simulated_mean']:>10.1f} "
                      f"{r['error']:>10.1f} "
                      f"{r['error_pct']:>9.1f}% "
                      f"{within:>10}")

        print("-" * 70)

        # Overall assessment
        valid_results = [r for r in validation_results if r and r['actual_runs']]
        if valid_results:
            avg_error_pct = sum(abs(r['error_pct']) for r in valid_results) / len(valid_results)
            within_ci_count = sum(1 for r in valid_results if r['within_95ci'])
            ci_pct = (within_ci_count / len(valid_results)) * 100

            print(f"\nOverall Performance:")
            print(f"  Average absolute error:  {avg_error_pct:.1f}%")
            print(f"  Within 95% CI:           {within_ci_count}/{len(valid_results)} ({ci_pct:.0f}%)")

            if avg_error_pct < 5.0:
                print(f"\n  ✓ EXCELLENT MODEL ACCURACY")
            elif avg_error_pct < 10.0:
                print(f"\n  ✓ GOOD MODEL ACCURACY")
            else:
                print(f"\n  ⚠ MODEL NEEDS CALIBRATION")

        print(f"\n{'#'*70}\n")

    return validation_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run complete validation suite')
    parser.add_argument('--season', type=int, help='Single season to validate')
    parser.add_argument('--start', type=int, help='Start year for multi-season validation')
    parser.add_argument('--end', type=int, help='End year for multi-season validation')
    parser.add_argument('--top-n', type=int, default=5, help='Number of top teams to validate (default: 5)')
    parser.add_argument('--iterations', type=int, default=10000, help='Simulations per team (default: 10,000)')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')

    args = parser.parse_args()

    if not args.season and not (args.start and args.end):
        print("Error: Must specify either --season or both --start and --end")
        return 1

    verbose = not args.quiet

    # Run validation
    if args.season:
        # Single season
        results = run_full_validation_suite(
            season=args.season,
            top_n=args.top_n,
            n_iterations=args.iterations,
            verbose=verbose
        )

        if results and args.export:
            filename = f'validation_suite_{args.season}.csv'
            export_validation_results(results, filename)

    else:
        # Multiple seasons
        all_results = []
        for year in range(args.start, args.end + 1):
            results = run_full_validation_suite(
                season=year,
                top_n=args.top_n,
                n_iterations=args.iterations,
                verbose=verbose
            )
            all_results.extend(results)
            time.sleep(2)  # Delay between seasons

        if all_results and args.export:
            filename = f'validation_suite_{args.start}-{args.end}.csv'
            export_validation_results(all_results, filename)

    return 0


if __name__ == '__main__':
    sys.exit(main())
