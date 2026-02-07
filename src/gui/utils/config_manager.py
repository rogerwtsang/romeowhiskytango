"""Configuration management for GUI settings."""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """Manages saving and loading GUI configurations."""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config manager.

        Args:
            config_dir: Directory to store config files (default: ~/.montecarlo_baseball/)
        """
        if config_dir is None:
            self.config_dir = Path.home() / '.montecarlo_baseball'
        else:
            self.config_dir = Path(config_dir)

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.gui_config_file = self.config_dir / 'gui_config.json'
        self.lineups_dir = self.config_dir / 'lineups'
        self.lineups_dir.mkdir(exist_ok=True)

    def save_gui_config(self, config: Dict[str, Any]) -> bool:
        """
        Save GUI configuration to file.

        Args:
            config: Dictionary of GUI settings

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.gui_config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving GUI config: {e}")
            return False

    def load_gui_config(self) -> Dict[str, Any]:
        """
        Load GUI configuration from file.

        Returns:
            Dictionary of GUI settings, or empty dict if file doesn't exist
        """
        if not self.gui_config_file.exists():
            return {}

        try:
            with open(self.gui_config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading GUI config: {e}")
            return {}

    def save_lineup(self, name: str, lineup_data: Dict[str, Any]) -> bool:
        """
        Save a lineup preset.

        Args:
            name: Name of the lineup preset
            lineup_data: Dict containing lineup info (indices, constraints, etc.)

        Returns:
            True if successful, False otherwise
        """
        try:
            filename = self.lineups_dir / f"{name}.json"
            with open(filename, 'w') as f:
                json.dump(lineup_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving lineup '{name}': {e}")
            return False

    def load_lineup(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load a lineup preset.

        Args:
            name: Name of the lineup preset

        Returns:
            Dictionary of lineup data, or None if not found
        """
        try:
            filename = self.lineups_dir / f"{name}.json"
            if not filename.exists():
                return None

            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading lineup '{name}': {e}")
            return None

    def list_lineups(self) -> list:
        """
        Get list of available lineup presets.

        Returns:
            List of lineup preset names
        """
        try:
            return [f.stem for f in self.lineups_dir.glob('*.json')]
        except Exception as e:
            print(f"Error listing lineups: {e}")
            return []

    def delete_lineup(self, name: str) -> bool:
        """
        Delete a lineup preset.

        Args:
            name: Name of the lineup preset

        Returns:
            True if successful, False otherwise
        """
        try:
            filename = self.lineups_dir / f"{name}.json"
            if filename.exists():
                filename.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting lineup '{name}': {e}")
            return False

    def save_session(self, dashboard_state: Dict[str, Any]) -> None:
        """
        Save current dashboard session state to file.

        Args:
            dashboard_state: Dictionary containing dashboard state with keys:
                - setup_collapsed (bool): Whether setup panel is collapsed
                - compare_mode (bool): Whether compare mode is active
                - lineup_panels (list): List of lineup data dicts
                - paned_positions (dict): Sash positions for paned windows
        """
        try:
            session_file = self.config_dir / 'last_session.json'
            with open(session_file, 'w') as f:
                json.dump(dashboard_state, f, indent=2)
        except IOError as e:
            print(f"Error saving session state: {e}")

    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load last dashboard session state from file.

        Returns:
            Dictionary containing dashboard state, or None if file doesn't exist
            or is invalid.
        """
        session_file = self.config_dir / 'last_session.json'

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading session state: {e}")
            return None

    def session_exists(self) -> bool:
        """
        Check if a valid session file exists.

        Returns:
            True if last_session.json exists and is valid JSON, False otherwise.
        """
        session_file = self.config_dir / 'last_session.json'

        if not session_file.exists():
            return False

        try:
            with open(session_file, 'r') as f:
                json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    # =========================================================================
    # Team-specific lineup persistence (05-04)
    # =========================================================================

    def _get_team_lineups_file(self, team_code: str, season: int) -> Path:
        """Get path to team-specific lineups file.

        Args:
            team_code: Three-letter team code (e.g., "TOR")
            season: Season year

        Returns:
            Path to lineups JSON file
        """
        return self.lineups_dir / f"{team_code.lower()}_{season}.json"

    def save_team_lineup(
        self,
        team_code: str,
        season: int,
        lineup_name: str,
        player_names: List[Optional[str]],
    ) -> bool:
        """
        Save a lineup for a specific team/season.

        Args:
            team_code: Three-letter team code (e.g., "TOR")
            season: Season year
            lineup_name: Name for this lineup
            player_names: List of player names (9 slots, None for empty)

        Returns:
            True if successful, False otherwise
        """
        try:
            lineups_file = self._get_team_lineups_file(team_code, season)

            # Load existing lineups
            existing: Dict[str, Any] = {}
            if lineups_file.exists():
                with open(lineups_file, "r") as f:
                    existing = json.load(f)

            # Add/update lineup
            existing[lineup_name] = {
                "players": player_names,
                "created_at": datetime.now().isoformat(),
            }

            # Save back
            with open(lineups_file, "w") as f:
                json.dump(existing, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving team lineup: {e}")
            return False

    def load_team_lineups(self, team_code: str, season: int) -> List[Dict[str, Any]]:
        """
        Load all lineups for a specific team/season.

        Args:
            team_code: Three-letter team code
            season: Season year

        Returns:
            List of lineup dictionaries with 'name', 'players', 'created_at'
        """
        try:
            lineups_file = self._get_team_lineups_file(team_code, season)

            if not lineups_file.exists():
                return []

            with open(lineups_file, "r") as f:
                data = json.load(f)

            # Convert dict to list of lineup dicts
            return [
                {"name": name, **lineup_data}
                for name, lineup_data in data.items()
            ]
        except Exception as e:
            print(f"Error loading team lineups: {e}")
            return []

    def delete_team_lineup(self, team_code: str, season: int, lineup_name: str) -> bool:
        """
        Delete a lineup for a specific team/season.

        Args:
            team_code: Three-letter team code
            season: Season year
            lineup_name: Name of lineup to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            lineups_file = self._get_team_lineups_file(team_code, season)

            if not lineups_file.exists():
                return False

            with open(lineups_file, "r") as f:
                data = json.load(f)

            if lineup_name not in data:
                return False

            del data[lineup_name]

            with open(lineups_file, "w") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error deleting team lineup: {e}")
            return False

    def get_team_lineup_names(self, team_code: str, season: int) -> List[str]:
        """
        Get list of lineup names for a team/season.

        Args:
            team_code: Three-letter team code
            season: Season year

        Returns:
            List of lineup names
        """
        lineups = self.load_team_lineups(team_code, season)
        return [lineup["name"] for lineup in lineups]
