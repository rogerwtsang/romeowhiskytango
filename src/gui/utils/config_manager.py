"""Configuration management for GUI settings."""

import json
import os
from typing import Dict, Any, Optional
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
