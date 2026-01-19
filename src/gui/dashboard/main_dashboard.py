# ============================================================================
# src/gui/dashboard/main_dashboard.py
# ============================================================================
"""Main dashboard container assembling all panels with resizable layout."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List

from src.gui.dashboard.setup_panel import SetupPanel
from src.gui.dashboard.lineup_panel import LineupPanel
from src.gui.dashboard.results_panel import ResultsPanel
from src.gui.utils.config_manager import ConfigManager
from src.gui.utils.results_manager import ResultsManager
from src.gui.utils.simulation_runner import SimulationRunner
from src.models.player import Player


class MainDashboard(ttk.Frame):
    """Main dashboard container with resizable panels and compare mode.

    Replaces the 9-tab notebook structure with a unified dashboard layout
    featuring:
    - Top: Collapsible Setup panel
    - Bottom-left: Lineup panel(s) (1 or 2 in compare mode)
    - Bottom-right: Results panel

    All panels are resizable using PanedWindow dividers.
    """

    def __init__(
        self,
        parent,
        config_manager: ConfigManager,
        results_manager: ResultsManager,
        sim_runner: SimulationRunner
    ):
        """
        Initialize main dashboard.

        Args:
            parent: Parent widget (usually root window)
            config_manager: Configuration manager instance
            results_manager: Results storage manager instance
            sim_runner: Simulation runner instance
        """
        super().__init__(parent)

        self.config_manager = config_manager
        self.results_manager = results_manager
        self.sim_runner = sim_runner

        # State tracking
        self.lineup_panels: List[LineupPanel] = []
        self.compare_mode = False
        self.roster: List[Player] = []
        self.team_data = None

        self._create_layout()
        self._prompt_session_restore()

    def _create_layout(self):
        """Create main dashboard layout with PanedWindow structure."""
        # Main vertical PanedWindow: Setup at top, content below
        self.main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Top pane: Setup panel (collapsible)
        self.setup_panel = SetupPanel(self.main_paned)
        self.setup_panel.set_data_loaded_callback(self._on_data_loaded)
        self.main_paned.add(self.setup_panel, weight=0)

        # Bottom pane: Content horizontal PanedWindow
        self.content_paned = ttk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL)
        self.main_paned.add(self.content_paned, weight=1)

        # Initial single lineup panel
        lineup_panel = self._create_lineup_panel()
        self.content_paned.add(lineup_panel, weight=1)

        # Results panel
        self.results_panel = ResultsPanel(self.content_paned, results_manager=self.results_manager)
        self.content_paned.add(self.results_panel, weight=1)

    def _create_lineup_panel(self) -> LineupPanel:
        """
        Create a lineup panel with callbacks.

        Returns:
            Configured LineupPanel instance
        """
        # Only first panel gets compare button
        on_compare = self.toggle_compare_mode if len(self.lineup_panels) == 0 else None

        panel = LineupPanel(
            self.content_paned,
            on_run=lambda: self._run_simulation(panel),
            on_compare=on_compare
        )
        self.lineup_panels.append(panel)

        # Load roster data if available
        if self.roster:
            panel.lineup_builder.load_data(self.roster, self.team_data)

        return panel

    def toggle_compare_mode(self):
        """Toggle between single lineup and comparison mode.

        Creates/destroys second lineup panel following proper widget lifecycle
        (forget then destroy) to prevent memory leaks.
        """
        self.compare_mode = not self.compare_mode

        if self.compare_mode:
            # Add second lineup panel
            panel = self._create_lineup_panel()
            # Insert between first lineup and results panel
            self.content_paned.insert(1, panel, weight=1)
        else:
            # Remove second lineup panel
            if len(self.lineup_panels) > 1:
                panel = self.lineup_panels[1]
                # Proper widget destruction (RESEARCH.md Pitfall 1)
                self.content_paned.forget(panel)  # Remove from paned window
                panel.destroy()  # Free memory
                self.lineup_panels.remove(panel)  # Clear tracking reference

    def _run_simulation(self, lineup_panel: LineupPanel):
        """
        Run simulation for a specific lineup panel.

        Args:
            lineup_panel: LineupPanel that triggered the run
        """
        # Get lineup data
        lineup_data = lineup_panel.get_lineup_data()

        # Validate lineup is complete
        if not lineup_data or not all(lineup_data):
            messagebox.showerror(
                "Incomplete Lineup",
                "Please fill all 9 lineup slots before running simulation"
            )
            return

        # Type narrowing: after validation, we know all slots are filled
        lineup: List[Player] = [p for p in lineup_data if p is not None]
        assert len(lineup) == 9, "Lineup must have exactly 9 players"

        # Collect configuration
        config_overrides = self.setup_panel.get_config()

        # Update progress indicator
        def progress_callback(current: int, total: int):
            lineup_panel.update_progress(current, total)

        # Completion callback
        def complete_callback(results: Optional[Dict[str, Any]]):
            self._on_simulation_complete(results, lineup_panel)

        # Start simulation in thread
        self.sim_runner.run_in_thread(
            lineup=lineup,
            config_overrides=config_overrides,
            progress_callback=progress_callback,
            complete_callback=complete_callback
        )

    def _on_simulation_complete(self, results: Optional[Dict[str, Any]], lineup_panel: LineupPanel):
        """
        Handle simulation completion.

        Args:
            results: Results dictionary from simulation, or None if stopped/error
            lineup_panel: LineupPanel that ran the simulation
        """
        # Hide progress indicator
        lineup_panel.hide_progress()

        if results is None:
            # Simulation was stopped
            messagebox.showinfo("Stopped", "Simulation was stopped")
        elif 'error' in results:
            # Error occurred
            messagebox.showerror("Error", f"Simulation failed:\n{results['error']}")
        else:
            # Success - normalize and display results
            normalized_results = self._normalize_results(results)

            # Store in results manager
            team = self.setup_panel.get_team_code()
            season = self.setup_panel.get_config()['season']
            lineup_name = f"{team} {season}"
            self.results_manager.store_result(lineup_name, results)

            # Display in results panel
            self.results_panel.display_results(normalized_results)

    def _normalize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize simulation results to standard format for ResultsPanel.

        Args:
            results: Raw results dictionary from run_simulations()

        Returns:
            Normalized dictionary with standard keys for ResultsPanel
        """
        # Extract summary from results
        summary = results.get('summary', {})
        runs = summary.get('runs', {})

        # Extract raw distribution data
        raw_data = results.get('raw_data', {})
        distribution = raw_data.get('season_runs', [])

        # Build normalized result
        normalized = {
            'mean': runs.get('mean', 0),
            'std': runs.get('std', 0),
            'ci_lower': runs.get('ci_lower', 0),
            'ci_upper': runs.get('ci_upper', 0),
            'iterations': summary.get('n_simulations', 0),
            'distribution': distribution,
            'min': runs.get('min'),
            'max': runs.get('max'),
            'median': runs.get('median'),
            'p25': runs.get('p25'),
            'p75': runs.get('p75'),
        }

        return normalized

    def _on_data_loaded(self, roster: List[Player], team_data):
        """
        Handle data loaded from setup panel.

        Args:
            roster: List of Player objects
            team_data: Raw team data DataFrame
        """
        self.roster = roster
        self.team_data = team_data

        # Load data into all existing lineup panels
        for panel in self.lineup_panels:
            panel.lineup_builder.load_data(roster, team_data)

    def get_dashboard_state(self) -> Dict[str, Any]:
        """
        Get current dashboard state for session management.

        Returns:
            Dictionary containing:
                - setup_collapsed: Whether setup panel is collapsed
                - compare_mode: Whether compare mode is active
                - lineup_panels: List of lineup data from each panel
                - paned_positions: Sash positions for resizable panes
        """
        state = {
            'setup_collapsed': self.setup_panel.assumptions_frame.collapsed,
            'compare_mode': self.compare_mode,
            'lineup_panels': [panel.get_lineup_data() for panel in self.lineup_panels],
            'paned_positions': {
                'main_vertical': self.main_paned.sashpos(0),
                'content_horizontal': self.content_paned.sashpos(0)
            }
        }

        return state

    def save_session(self):
        """Save current dashboard state to session file."""
        state = self.get_dashboard_state()
        self.config_manager.save_session(state)

    def _prompt_session_restore(self):
        """Prompt user to restore last session if one exists."""
        if self.config_manager.session_exists():
            restore = messagebox.askyesno(
                "Restore Session",
                "Restore your last session?",
                parent=self
            )
            if restore:
                self._restore_session()

    def _restore_session(self):
        """Restore dashboard state from saved session."""
        state = self.config_manager.load_session()

        if state is None:
            return

        # Restore setup panel collapse state
        if state.get('setup_collapsed'):
            # Only toggle if currently expanded
            if not self.setup_panel.assumptions_frame.collapsed:
                self.setup_panel.assumptions_frame.toggle()

        # Restore compare mode
        if state.get('compare_mode') and not self.compare_mode:
            self.toggle_compare_mode()

        # Restore lineup data
        lineup_data = state.get('lineup_panels', [])
        for i, data in enumerate(lineup_data):
            if i < len(self.lineup_panels):
                self.lineup_panels[i].set_lineup_data(data)

        # Restore paned positions
        positions = state.get('paned_positions', {})
        if 'main_vertical' in positions:
            self.main_paned.sashpos(0, positions['main_vertical'])
        if 'content_horizontal' in positions:
            self.content_paned.sashpos(0, positions['content_horizontal'])
