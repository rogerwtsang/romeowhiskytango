# ============================================================================
# src/gui/models/team_roster.py
# ============================================================================
"""Team, Roster, and Lineup data models for organized lineup management."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from src.models.player import Player


@dataclass
class Lineup:
    """A specific 9-player batting order.

    Represents a named lineup configuration that can be saved and loaded.
    Multiple lineups can exist per roster for comparison purposes.

    Attributes:
        name: Descriptive name (e.g., "Standard", "Lefty Stack")
        players: 9-slot list of players, None for empty slots
        created_at: ISO timestamp when lineup was created
    """

    name: str  # e.g., "Standard", "Lefty Stack"
    players: List[Optional[Player]] = field(default_factory=lambda: [None] * 9)
    created_at: str = ""  # ISO timestamp

    def is_complete(self) -> bool:
        """Check if all 9 lineup slots are filled.

        Returns:
            True if lineup has a player in every slot
        """
        return all(p is not None for p in self.players)

    def to_dict(self) -> Dict[str, Any]:
        """Convert lineup to dictionary for serialization.

        Returns:
            Dictionary with name, player names, and timestamp
        """
        return {
            "name": self.name,
            "players": [p.name if p else None for p in self.players],
            "created_at": self.created_at,
        }


@dataclass
class Roster:
    """Subset of team players eligible for batting order.

    A roster represents a filtered set of players from a team that can be
    used to build lineups. Multiple rosters can exist per team
    (e.g., "Active Roster", "Playoff Eligible").

    Attributes:
        name: Descriptive roster name
        players: List of Player objects in roster
        lineups: List of saved Lineup configurations
    """

    name: str  # e.g., "Active Roster", "Playoff Eligible"
    players: List[Player] = field(default_factory=list)
    lineups: List[Lineup] = field(default_factory=list)

    def add_lineup(self, lineup: Lineup) -> None:
        """Add a lineup to this roster.

        Args:
            lineup: Lineup to add
        """
        self.lineups.append(lineup)

    def get_lineup(self, name: str) -> Optional[Lineup]:
        """Get lineup by name.

        Args:
            name: Lineup name to search for

        Returns:
            Lineup if found, None otherwise
        """
        for lineup in self.lineups:
            if lineup.name == name:
                return lineup
        return None

    def remove_lineup(self, name: str) -> bool:
        """Remove lineup by name.

        Args:
            name: Lineup name to remove

        Returns:
            True if lineup was found and removed
        """
        for i, lineup in enumerate(self.lineups):
            if lineup.name == name:
                self.lineups.pop(i)
                return True
        return False


@dataclass
class Team:
    """Collection of loaded players with stats.

    A Team represents all players loaded from a data source (e.g., FanGraphs)
    for a specific team and season. Teams can have multiple rosters and
    user-defined nicknames.

    Attributes:
        code: Three-letter team code (e.g., "TOR")
        full_name: Full team name (e.g., "Toronto Blue Jays")
        season: Season year (e.g., 2024)
        nickname: User-defined nickname for this team
        players: All loaded players
        rosters: List of roster subsets
    """

    code: str  # e.g., "TOR"
    full_name: str  # e.g., "Toronto Blue Jays"
    season: int  # e.g., 2024
    nickname: str = ""  # User-defined nickname
    players: List[Player] = field(default_factory=list)
    rosters: List[Roster] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        """Get display name for this team.

        Returns nickname if set, otherwise "{season} {full_name}".

        Returns:
            Display name string
        """
        if self.nickname:
            return self.nickname
        return f"{self.season} {self.full_name}"

    def add_roster(self, roster: Roster) -> None:
        """Add a roster to this team.

        Args:
            roster: Roster to add
        """
        self.rosters.append(roster)

    def get_default_roster(self) -> Roster:
        """Get default roster, creating if necessary.

        Returns first roster if any exist, otherwise creates a "Full Roster"
        containing all team players.

        Returns:
            Default Roster instance
        """
        if self.rosters:
            return self.rosters[0]
        default = Roster(name="Full Roster", players=self.players.copy())
        self.add_roster(default)
        return default

    def get_roster(self, name: str) -> Optional[Roster]:
        """Get roster by name.

        Args:
            name: Roster name to search for

        Returns:
            Roster if found, None otherwise
        """
        for roster in self.rosters:
            if roster.name == name:
                return roster
        return None
