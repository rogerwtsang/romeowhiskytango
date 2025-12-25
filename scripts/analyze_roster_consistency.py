#!/usr/bin/env python3
"""
Analyze roster consistency across MLB teams to identify the most stable rosters.

Usage:
    python scripts/analyze_roster_consistency.py --season 2024
    python scripts/analyze_roster_consistency.py --start 2010 --end 2024
    python scripts/analyze_roster_consistency.py --season 2024 --top-n 10
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import pandas as pd
from src.data.scraper import get_team_batting_stats
import time


# All 30 MLB teams
MLB_TEAMS = [
    'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CIN', 'CLE', 'COL', 'CWS', 'DET',
    'HOU', 'KC', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
    'PHI', 'PIT', 'SD', 'SEA', 'SF', 'STL', 'TB', 'TEX', 'TOR', 'WSH'
]


def analyze_roster_consistency(season: int, verbose: bool = True) -> pd.DataFrame:
    """
    Analyze roster consistency for all 30 MLB teams in a given season.

    Args:
        season: Season year to analyze
        verbose: Print progress messages

    Returns:
        DataFrame with columns:
            - team: Team abbreviation
            - season: Season year
            - total_players: Total unique players used
            - qualified_players: Players with >= 100 PA
            - players_300pa: Players with >= 300 PA (regulars)
            - total_pa: Total team plate appearances
            - avg_pa_per_player: Average PA per player
            - consistency_score: total_pa / total_players (higher = more consistent)
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"Analyzing Roster Consistency for {season} Season")
        print(f"{'='*70}\n")

    results = []
    errors = []

    for i, team in enumerate(MLB_TEAMS, 1):
        if verbose:
            print(f"[{i:2d}/30] Fetching {team}...", end=" ", flush=True)

        try:
            # Fetch team batting stats
            df = get_team_batting_stats(team, season)

            # Count players by PA thresholds
            total_players = len(df)
            qualified_players = len(df[df['PA'] >= 100])
            regulars = len(df[df['PA'] >= 300])

            # Calculate team totals
            total_pa = df['PA'].sum()
            avg_pa = df['PA'].mean()
            median_pa = df['PA'].median()
            max_pa = df['PA'].max()

            # Consistency score: higher PA per player = more consistent
            consistency_score = total_pa / total_players if total_players > 0 else 0

            results.append({
                'team': team,
                'season': season,
                'total_players': total_players,
                'qualified_players': qualified_players,
                'players_300pa': regulars,
                'total_pa': int(total_pa),
                'avg_pa_per_player': round(avg_pa, 1),
                'median_pa': int(median_pa),
                'max_pa': int(max_pa),
                'consistency_score': round(consistency_score, 1)
            })

            if verbose:
                print(f"✓ {total_players} players, {qualified_players} qualified")

        except Exception as e:
            error_msg = f"{team}: {str(e)}"
            errors.append(error_msg)
            if verbose:
                print(f"✗ Error: {str(e)}")

        # Small delay to avoid rate limiting
        time.sleep(0.1)

    if verbose:
        print(f"\n{'='*70}")
        print(f"Analysis Complete: {len(results)}/{len(MLB_TEAMS)} teams successful")
        if errors:
            print(f"Errors encountered: {len(errors)}")
            for err in errors:
                print(f"  - {err}")
        print(f"{'='*70}\n")

    # Convert to DataFrame and sort by consistency
    df_results = pd.DataFrame(results)
    if not df_results.empty:
        df_results = df_results.sort_values('total_players')

    return df_results


def analyze_multiple_seasons(start_year: int, end_year: int, verbose: bool = True) -> pd.DataFrame:
    """
    Analyze roster consistency across multiple seasons.

    Args:
        start_year: First season to analyze
        end_year: Last season to analyze (inclusive)
        verbose: Print progress messages

    Returns:
        DataFrame with all seasons combined
    """
    all_results = []

    for year in range(start_year, end_year + 1):
        print(f"\n{'#'*70}")
        print(f"SEASON {year}")
        print(f"{'#'*70}")

        season_results = analyze_roster_consistency(year, verbose=verbose)
        if not season_results.empty:
            all_results.append(season_results)

        # Longer delay between seasons
        time.sleep(1)

    if all_results:
        return pd.concat(all_results, ignore_index=True)
    else:
        return pd.DataFrame()


def find_most_consistent_teams(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Identify the most consistent teams from the analysis.

    Args:
        df: Results DataFrame from analyze_roster_consistency
        top_n: Number of top teams to return

    Returns:
        DataFrame with top N most consistent teams
    """
    return df.nsmallest(top_n, 'total_players')


def find_overall_most_consistent(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Find teams that are most consistently stable across multiple seasons.

    Args:
        df: Multi-season results DataFrame
        top_n: Number of teams to return

    Returns:
        DataFrame with average consistency metrics per team
    """
    # Group by team and calculate average metrics
    team_summary = df.groupby('team').agg({
        'total_players': 'mean',
        'qualified_players': 'mean',
        'players_300pa': 'mean',
        'consistency_score': 'mean',
        'season': 'count'  # Number of seasons analyzed
    }).round(1)

    team_summary.rename(columns={'season': 'seasons_analyzed'}, inplace=True)
    team_summary = team_summary.sort_values('total_players')

    return team_summary.head(top_n)


def export_consistency_report(df: pd.DataFrame, filename: str):
    """
    Export consistency analysis to CSV.

    Args:
        df: Results DataFrame
        filename: Output filename
    """
    output_path = Path('data/analysis') / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"\n✓ Report saved to: {output_path}")


def print_summary(df: pd.DataFrame, season: int = None):
    """
    Print a summary of the consistency analysis.

    Args:
        df: Results DataFrame
        season: Season year (if single season)
    """
    if df.empty:
        print("No data to summarize")
        return

    print(f"\n{'='*70}")
    print("ROSTER CONSISTENCY SUMMARY")
    if season:
        print(f"Season: {season}")
    print(f"{'='*70}\n")

    # Most consistent teams (fewest players)
    print("🏆 MOST CONSISTENT TEAMS (Fewest Players Used)")
    print("-" * 70)
    top_5 = df.nsmallest(5, 'total_players')
    for i, row in enumerate(top_5.itertuples(), 1):
        print(f"{i}. {row.team:4s} - {row.total_players:2d} players | "
              f"{row.qualified_players} qualified | "
              f"{row.players_300pa} regulars (300+ PA)")

    print(f"\n{'='*70}")

    # Least consistent teams (most players)
    print("⚠️  LEAST CONSISTENT TEAMS (Most Players Used)")
    print("-" * 70)
    bottom_5 = df.nlargest(5, 'total_players')
    for i, row in enumerate(bottom_5.itertuples(), 1):
        print(f"{i}. {row.team:4s} - {row.total_players:2d} players | "
              f"{row.qualified_players} qualified | "
              f"{row.players_300pa} regulars (300+ PA)")

    print(f"\n{'='*70}")

    # Statistics
    print("📊 LEAGUE STATISTICS")
    print("-" * 70)
    print(f"Average players per team:     {df['total_players'].mean():.1f}")
    print(f"Median players per team:      {df['total_players'].median():.1f}")
    print(f"Range:                        {df['total_players'].min()}-{df['total_players'].max()}")
    print(f"Average qualified (100+ PA):  {df['qualified_players'].mean():.1f}")
    print(f"Average regulars (300+ PA):   {df['players_300pa'].mean():.1f}")

    print(f"\n{'='*70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze MLB roster consistency')
    parser.add_argument('--season', type=int, help='Single season to analyze')
    parser.add_argument('--start', type=int, help='Start year for multi-season analysis')
    parser.add_argument('--end', type=int, help='End year for multi-season analysis')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top teams to show (default: 10)')
    parser.add_argument('--export', action='store_true', help='Export results to CSV')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')

    args = parser.parse_args()

    verbose = not args.quiet

    # Validate arguments
    if args.season and (args.start or args.end):
        print("Error: Cannot specify both --season and --start/--end")
        return 1

    if not args.season and not (args.start and args.end):
        print("Error: Must specify either --season or both --start and --end")
        return 1

    # Run analysis
    if args.season:
        # Single season
        df = analyze_roster_consistency(args.season, verbose=verbose)
        print_summary(df, season=args.season)

        if args.export:
            filename = f'roster_consistency_{args.season}.csv'
            export_consistency_report(df, filename)

    else:
        # Multiple seasons
        df = analyze_multiple_seasons(args.start, args.end, verbose=verbose)

        if not df.empty:
            # Print per-season summary
            print_summary(df)

            # Print overall most consistent teams
            print("\n" + "="*70)
            print(f"OVERALL MOST CONSISTENT TEAMS ({args.start}-{args.end})")
            print("="*70 + "\n")

            overall = find_overall_most_consistent(df, top_n=args.top_n)
            for i, (team, row) in enumerate(overall.iterrows(), 1):
                print(f"{i:2d}. {team:4s} - Avg {row['total_players']:.1f} players/season | "
                      f"{row['qualified_players']:.1f} qualified | "
                      f"{int(row['seasons_analyzed'])} seasons analyzed")

            print("\n" + "="*70 + "\n")

            if args.export:
                # Export detailed results
                filename = f'roster_consistency_{args.start}-{args.end}.csv'
                export_consistency_report(df, filename)

                # Export summary
                summary_filename = f'roster_consistency_summary_{args.start}-{args.end}.csv'
                export_consistency_report(overall.reset_index(), summary_filename)

    return 0


if __name__ == '__main__':
    sys.exit(main())
