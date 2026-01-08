"""Data acquisition using pybaseball and MLB Stats API."""

import pandas as pd
from typing import Optional, List, Dict
import pybaseball as pyb
from pybaseball import batting_stats, team_batting, playerid_lookup, statcast_batter

try:
    import statsapi
    STATSAPI_AVAILABLE = True
except ImportError:
    STATSAPI_AVAILABLE = False


# Enable cache to avoid repeated API calls
pyb.cache.enable()


# MLB Team ID mapping (for statsapi)
MLB_TEAM_IDS = {
    'ARI': 109, 'ATL': 144, 'BAL': 110, 'BOS': 111, 'CHC': 112,
    'CIN': 113, 'CLE': 114, 'COL': 115, 'CWS': 145, 'DET': 116,
    'HOU': 117, 'KC': 118, 'LAA': 108, 'LAD': 119, 'MIA': 146,
    'MIL': 158, 'MIN': 142, 'NYM': 121, 'NYY': 147, 'OAK': 133,
    'PHI': 143, 'PIT': 134, 'SD': 135, 'SEA': 136, 'SF': 137,
    'STL': 138, 'TB': 139, 'TEX': 140, 'TOR': 141, 'WSH': 120,
}


def get_team_batting_stats(team: str, season: int) -> pd.DataFrame:
    """Fetch batting statistics for a team's roster.

    Args:
        team: Team abbreviation (e.g., 'TOR')
        season: Season year

    Returns:
        DataFrame with player batting statistics
    """
    print(f"Fetching {season} batting stats for {team}...")

    # Get all batting stats for the season
    stats = batting_stats(season, qual=1)  # qual=1 gets all players with at least 1 PA

    # Filter for specific team
    team_stats = stats[stats['Team'] == team].copy()

    if team_stats.empty:
        raise ValueError(f"No data found for team {team} in {season}")

    print(f"Found {len(team_stats)} players for {team}")

    return team_stats


def search_player(last_name: str, first_name: Optional[str] = None) -> pd.DataFrame:
    """Search for a player by name.

    Args:
        last_name: Player's last name
        first_name: Player's first name (optional)

    Returns:
        DataFrame with matching players and their IDs
    """
    print(f"Searching for player: {first_name or ''} {last_name}".strip())

    # Use playerid_lookup to find the player
    results = playerid_lookup(last_name, first_name)

    if results.empty:
        raise ValueError(f"No players found matching '{first_name or ''} {last_name}'")

    print(f"Found {len(results)} matching player(s)")
    return results


def get_player_batting_stats(player_name: str, season: int) -> pd.DataFrame:
    """Fetch batting statistics for a specific player by searching all players.

    Args:
        player_name: Player name (will search in Name column)
        season: Season year

    Returns:
        DataFrame with player batting statistics (single row)
    """
    print(f"Fetching {season} batting stats for {player_name}...")

    # Get all batting stats for the season
    stats = batting_stats(season, qual=1)  # qual=1 gets all players with at least 1 PA

    # Search for player (case-insensitive partial match)
    player_stats = stats[stats['Name'].str.contains(player_name, case=False, na=False)].copy()

    if player_stats.empty:
        raise ValueError(f"No data found for player '{player_name}' in {season}")

    print(f"Found {len(player_stats)} matching player(s)")

    return player_stats


def get_league_batting_stats(season: int, min_pa: int = 100) -> pd.DataFrame:
    """Fetch league-wide batting statistics for calculating averages.

    Args:
        season: Season year
        min_pa: Minimum plate appearances for inclusion

    Returns:
        DataFrame with qualified league batting statistics
    """
    print(f"Fetching {season} league-wide batting stats...")

    # Get qualified hitters (default qual is typically 3.1 PA per team game)
    stats = batting_stats(season, qual=min_pa)

    print(f"Found {len(stats)} qualified players")

    return stats


def calculate_league_averages(season: int, min_pa: int = 300) -> dict:
    """Calculate league-average hit distributions.

    Args:
        season: Season year
        min_pa: Minimum PAs for inclusion in averages

    Returns:
        Dictionary with league average statistics
    """
    stats = get_league_batting_stats(season, min_pa)

    # Calculate totals
    total_hits = stats['H'].sum()
    total_doubles = stats['2B'].sum()
    total_triples = stats['3B'].sum()
    total_hr = stats['HR'].sum()

    # Singles = Hits - (2B + 3B + HR)
    total_singles = total_hits - (total_doubles + total_triples + total_hr)

    # Distribution of hit types (conditional on a hit occurring)
    hit_dist = {
        '1B': total_singles / total_hits,
        '2B': total_doubles / total_hits,
        '3B': total_triples / total_hits,
        'HR': total_hr / total_hits
    }

    # Overall slash line averages
    # pybaseball uses 'AVG' instead of 'BA'
    ba_col = 'AVG' if 'AVG' in stats.columns else 'BA'

    slash = {
        'BA': stats[ba_col].mean(),
        'OBP': stats['OBP'].mean(),
        'SLG': stats['SLG'].mean(),
        'ISO': stats['ISO'].mean() if 'ISO' in stats.columns else stats['SLG'].mean() - stats[ba_col].mean()
    }

    return {
        'hit_distribution': hit_dist,
        'slash_line': slash,
        'season': season,
        'n_players': len(stats),
        'total_hits': total_hits
    }


def prepare_player_stats(df: pd.DataFrame, min_pa: int = 100) -> pd.DataFrame:
    """Clean and prepare player statistics for simulation.

    Args:
        df: Raw DataFrame from pybaseball
        min_pa: Minimum plate appearances for inclusion

    Returns:
        Cleaned DataFrame with necessary columns
    """
    # Filter by minimum PAs
    df_clean = df[df['PA'] >= min_pa].copy()

    # Select and rename key columns
    # NOTE: FanGraphs batting_stats does not include defensive position data.
    # The 'Pos' column in FanGraphs is a positional adjustment value, not the position itself.
    # Position data would need to come from Baseball Reference or manual entry.
    columns_needed = {
        'Name': 'name',
        'PA': 'pa',
        'AVG': 'ba',  # pybaseball uses AVG instead of BA
        'OBP': 'obp',
        'SLG': 'slg',
        'H': 'hits',
        '2B': 'doubles',
        '3B': 'triples',
        'HR': 'hr',
        'SB': 'sb',
        'CS': 'cs',
        'K%': 'k_pct'
    }

    # Check which columns exist
    available_cols = {k: v for k, v in columns_needed.items() if k in df.columns}

    df_clean = df_clean[list(available_cols.keys())].copy()
    df_clean.rename(columns=available_cols, inplace=True)

    # Calculate singles if we have the data
    if all(col in df_clean.columns for col in ['hits', 'doubles', 'triples', 'hr']):
        df_clean['singles'] = df_clean['hits'] - (df_clean['doubles'] + df_clean['triples'] + df_clean['hr'])

    # Calculate ISO if not present
    if 'iso' not in df_clean.columns and 'slg' in df_clean.columns and 'ba' in df_clean.columns:
        df_clean['iso'] = df_clean['slg'] - df_clean['ba']

    # Handle missing values
    df_clean = df_clean.dropna(subset=['ba', 'obp', 'slg'])

    print(f"Prepared stats for {len(df_clean)} players (min PA: {min_pa})")

    return df_clean


def save_data(df: pd.DataFrame, filename: str, data_type: str = 'raw'):
    """Save DataFrame to data directory.

    Args:
        df: DataFrame to save
        filename: Filename (without path)
        data_type: 'raw' or 'processed'
    """
    import os

    path = f"data/{data_type}/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    df.to_csv(path, index=False)
    print(f"Saved data to {path}")


def load_data(filename: str, data_type: str = 'raw') -> pd.DataFrame:
    """Load DataFrame from data directory.

    Args:
        filename: Filename (without path)
        data_type: 'raw' or 'processed'

    Returns:
        Loaded DataFrame
    """
    path = f"data/{data_type}/{filename}"
    df = pd.read_csv(path)
    print(f"Loaded data from {path}")
    return df


def get_team_roster_positions(team: str, season: int) -> Dict[str, Dict]:
    """Fetch fielding position data for a team's roster from MLB Stats API.

    Args:
        team: Team abbreviation (e.g., 'TOR')
        season: Season year

    Returns:
        Dictionary mapping player names to position info:
        {
            'Vladimir Guerrero Jr.': {
                'position_code': 3,
                'position_abbrev': '1B',
                'position_name': 'First Baseman',
                'position_type': 'Infielder',
                'mlb_id': 665489
            },
            ...
        }

    Raises:
        ImportError: If statsapi is not installed
        ValueError: If team code is not recognized
    """
    if not STATSAPI_AVAILABLE:
        raise ImportError(
            "MLB-StatsAPI package not installed. "
            "Install with: pip install MLB-StatsAPI"
        )

    team_upper = team.upper()
    if team_upper not in MLB_TEAM_IDS:
        raise ValueError(f"Unknown team code: {team}. Valid codes: {list(MLB_TEAM_IDS.keys())}")

    team_id = MLB_TEAM_IDS[team_upper]
    print(f"Fetching {season} roster positions for {team} (team_id={team_id})...")

    try:
        roster_data = statsapi.get(
            'team_roster',
            {'teamId': team_id, 'rosterType': 'fullSeason', 'season': season}
        )
    except Exception as e:
        print(f"Warning: Could not fetch roster for {season}, trying active roster...")
        roster_data = statsapi.get(
            'team_roster',
            {'teamId': team_id, 'rosterType': 'active'}
        )

    positions = {}
    for entry in roster_data.get('roster', []):
        person = entry.get('person', {})
        position = entry.get('position', {})

        player_name = person.get('fullName')
        if not player_name:
            continue

        positions[player_name] = {
            'position_code': int(position.get('code', 0)) if position.get('code', '').isdigit() else None,
            'position_abbrev': position.get('abbreviation'),
            'position_name': position.get('name'),
            'position_type': position.get('type'),
            'mlb_id': person.get('id'),
        }

    print(f"Found position data for {len(positions)} players")
    return positions


def merge_batting_with_positions(batting_df: pd.DataFrame, team: str, season: int) -> pd.DataFrame:
    """Merge batting statistics with position data.

    Args:
        batting_df: DataFrame with batting stats (must have 'Name' or 'name' column)
        team: Team abbreviation
        season: Season year

    Returns:
        DataFrame with added position columns:
        - position_code: int (1-10)
        - position_abbrev: str (C, 1B, SS, etc.)
        - position_name: str (Catcher, First Baseman, etc.)
        - position_type: str (Catcher, Infielder, Outfielder, etc.)
    """
    # Get position data
    try:
        positions = get_team_roster_positions(team, season)
    except (ImportError, Exception) as e:
        print(f"Warning: Could not fetch position data: {e}")
        print("Proceeding without position information.")
        batting_df['position_code'] = None
        batting_df['position_abbrev'] = None
        batting_df['position_name'] = None
        batting_df['position_type'] = None
        return batting_df

    # Determine name column
    name_col = 'Name' if 'Name' in batting_df.columns else 'name'

    # Create position columns
    batting_df = batting_df.copy()
    batting_df['position_code'] = None
    batting_df['position_abbrev'] = None
    batting_df['position_name'] = None
    batting_df['position_type'] = None

    # Match players by name
    matched = 0
    for idx, row in batting_df.iterrows():
        player_name = row[name_col]

        # Try exact match first
        if player_name in positions:
            pos_info = positions[player_name]
            batting_df.at[idx, 'position_code'] = pos_info['position_code']
            batting_df.at[idx, 'position_abbrev'] = pos_info['position_abbrev']
            batting_df.at[idx, 'position_name'] = pos_info['position_name']
            batting_df.at[idx, 'position_type'] = pos_info['position_type']
            matched += 1
            continue

        # Try fuzzy match (partial name matching)
        for roster_name, pos_info in positions.items():
            # Check if either name contains the other (handles Jr., accents, etc.)
            if (player_name.lower() in roster_name.lower() or
                roster_name.lower() in player_name.lower()):
                batting_df.at[idx, 'position_code'] = pos_info['position_code']
                batting_df.at[idx, 'position_abbrev'] = pos_info['position_abbrev']
                batting_df.at[idx, 'position_name'] = pos_info['position_name']
                batting_df.at[idx, 'position_type'] = pos_info['position_type']
                matched += 1
                break

    print(f"Matched position data for {matched}/{len(batting_df)} players")
    return batting_df


if __name__ == "__main__":
    # Test the scraper
    import sys

    # Check for 2025 data availability
    try:
        print("\n=== Testing Data Scraper ===\n")

        # Try 2025 first
        tor_stats = get_team_batting_stats('TOR', 2025)
        print(f"\nColumns available: {list(tor_stats.columns)}")
        print(f"\nFirst few rows:\n{tor_stats.head()}")

        # Save raw data
        save_data(tor_stats, 'blue_jays_2025_raw.csv', 'raw')

        # Prepare stats
        prepared = prepare_player_stats(tor_stats)
        save_data(prepared, 'blue_jays_2025_prepared.csv', 'processed')

        print(f"\n=== Sample prepared data ===")
        print(prepared[['name', 'pa', 'ba', 'obp', 'slg', 'iso']].head())

        # Calculate league averages
        print("\n=== Calculating league averages ===")
        league_avg = calculate_league_averages(2025, min_pa=300)
        print(f"\nLeague average hit distribution: {league_avg['hit_distribution']}")
        print(f"League average slash line: {league_avg['slash_line']}")

    except Exception as e:
        print(f"\nError with 2025 data: {e}")
        print("\nTrying 2024 data as fallback...")

        try:
            tor_stats = get_team_batting_stats('TOR', 2024)
            print(f"\nUsing 2024 data: {len(tor_stats)} players found")
            save_data(tor_stats, 'blue_jays_2024_raw.csv', 'raw')

            prepared = prepare_player_stats(tor_stats)
            save_data(prepared, 'blue_jays_2024_prepared.csv', 'processed')

            print(f"\n=== Sample 2024 prepared data ===")
            print(prepared[['name', 'pa', 'ba', 'obp', 'slg', 'iso']].head())

        except Exception as e2:
            print(f"\nError with 2024 data: {e2}")
            sys.exit(1)
