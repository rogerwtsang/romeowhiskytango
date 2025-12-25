#!/usr/bin/env python3
"""
Prepare validation datasets from consistent teams for simulation testing.

Usage:
    python scripts/prepare_validation_data.py --team LAD --season 2024
    python scripts/prepare_validation_data.py --team STL --season 2023 --min-pa 50
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pandas as pd
from src.data.scraper import get_team_batting_stats, prepare_player_stats
from src.data.processor import prepare_roster
from pybaseball import team_batting


def prepare_validation_dataset(team: str, season: int, min_pa: int = 100, verbose: bool = True):
    """
    Prepare a validation dataset for a consistent team.

    Args:
        team: Team abbreviation (e.g., 'LAD', 'STL')
        season: Season year
        min_pa: Minimum plate appearances for inclusion
        verbose: Print progress messages

    Returns:
        Dictionary with:
            - team: Team abbreviation
            - season: Season year
            - players: Number of players in dataset
            - actual_runs: Actual runs scored by team (if available)
            - actual_wins: Actual wins (if available)
            - actual_losses: Actual losses (if available)
            - roster: Prepared player DataFrame
            - roster_objects: List of Player objects
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Preparing Validation Dataset: {team} {season}")
        print(f"{'='*70}\n")

    # Get team batting stats
    if verbose:
        print(f"Fetching batting stats for {team} {season}...")

    batting_df = get_team_batting_stats(team, season)

    if verbose:
        print(f"  ✓ Found {len(batting_df)} players")

    # Prepare stats with minimum PA filter
    if verbose:
        print(f"Preparing player stats (min PA: {min_pa})...")

    prepared_df = prepare_player_stats(batting_df, min_pa=min_pa)

    if verbose:
        print(f"  ✓ {len(prepared_df)} players meet criteria")

    # Convert to Player objects
    if verbose:
        print("Converting to Player objects...")

    roster_objects = prepare_roster(prepared_df)

    if verbose:
        print(f"  ✓ Created {len(roster_objects)} Player objects")

    # Try to get actual team results (runs, wins, losses)
    actual_runs = None
    actual_wins = None
    actual_losses = None

    if verbose:
        print(f"\nFetching actual team results...")

    try:
        team_results = team_batting(season)

        # Find the team's row
        team_row = team_results[team_results['Team'] == team]

        if not team_row.empty:
            actual_runs = int(team_row['R'].values[0]) if 'R' in team_row.columns else None
            actual_wins = int(team_row['W'].values[0]) if 'W' in team_row.columns else None
            actual_losses = int(team_row['L'].values[0]) if 'L' in team_row.columns else None

            if verbose:
                if actual_runs:
                    print(f"  ✓ Actual runs scored: {actual_runs}")
                if actual_wins and actual_losses:
                    print(f"  ✓ Actual record: {actual_wins}-{actual_losses} ({actual_wins/(actual_wins+actual_losses)*100:.1f}%)")
        else:
            if verbose:
                print(f"  ⚠ Team not found in team_batting results")

    except Exception as e:
        if verbose:
            print(f"  ⚠ Could not fetch team results: {str(e)}")

    # Save validation dataset
    output_path = Path(f'data/validation/validation_{team}_{season}.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared_df.to_csv(output_path, index=False)

    if verbose:
        print(f"\n✓ Validation data saved to: {output_path}")

    # Create summary
    result = {
        'team': team,
        'season': season,
        'players': len(prepared_df),
        'actual_runs': actual_runs,
        'actual_wins': actual_wins,
        'actual_losses': actual_losses,
        'roster': prepared_df,
        'roster_objects': roster_objects,
        'output_file': str(output_path)
    }

    # Print summary
    if verbose:
        print(f"\n{'='*70}")
        print("VALIDATION DATASET SUMMARY")
        print(f"{'='*70}\n")
        print(f"Team:           {team}")
        print(f"Season:         {season}")
        print(f"Players:        {len(prepared_df)}")
        print(f"Min PA filter:  {min_pa}")

        if actual_runs:
            print(f"\nActual Results:")
            print(f"  Runs:         {actual_runs}")
            if actual_wins and actual_losses:
                print(f"  Record:       {actual_wins}-{actual_losses}")

        print(f"\nTop Players (by PA):")
        top_5 = prepared_df.nlargest(5, 'pa')
        for i, row in enumerate(top_5.itertuples(), 1):
            print(f"  {i}. {row.name:20s} {int(row.pa):3d} PA | {row.ba:.3f}/{row.obp:.3f}/{row.slg:.3f}")

        print(f"\n{'='*70}\n")

    return result


def prepare_multiple_teams(teams_seasons: list, min_pa: int = 100, verbose: bool = True):
    """
    Prepare validation datasets for multiple teams.

    Args:
        teams_seasons: List of (team, season) tuples
        min_pa: Minimum plate appearances
        verbose: Print progress messages

    Returns:
        List of validation dataset dictionaries
    """
    results = []

    for team, season in teams_seasons:
        try:
            result = prepare_validation_dataset(team, season, min_pa, verbose)
            results.append(result)
        except Exception as e:
            print(f"\n✗ Error preparing {team} {season}: {str(e)}\n")

    return results


def export_validation_summary(results: list, filename: str):
    """
    Export a summary of all validation datasets.

    Args:
        results: List of validation dataset dictionaries
        filename: Output filename
    """
    summary_data = []

    for r in results:
        summary_data.append({
            'team': r['team'],
            'season': r['season'],
            'players': r['players'],
            'actual_runs': r['actual_runs'],
            'actual_wins': r['actual_wins'],
            'actual_losses': r['actual_losses'],
            'output_file': r['output_file']
        })

    summary_df = pd.DataFrame(summary_data)

    output_path = Path('data/validation') / filename
    summary_df.to_csv(output_path, index=False)

    print(f"\n✓ Validation summary saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Prepare validation datasets')
    parser.add_argument('--team', type=str, required=True, help='Team abbreviation (e.g., LAD, STL)')
    parser.add_argument('--season', type=int, required=True, help='Season year')
    parser.add_argument('--min-pa', type=int, default=100, help='Minimum plate appearances (default: 100)')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')

    args = parser.parse_args()

    verbose = not args.quiet

    # Prepare dataset
    result = prepare_validation_dataset(
        team=args.team.upper(),
        season=args.season,
        min_pa=args.min_pa,
        verbose=verbose
    )

    return 0


if __name__ == '__main__':
    sys.exit(main())
