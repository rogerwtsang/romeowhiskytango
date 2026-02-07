# ============================================================================
# src/gui/dashboard/main_dashboard.py
# ============================================================================
"""Main dashboard container assembling all panels with resizable layout."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any, List

from src.gui.dashboard.setup_panel import SetupPanel
from src.gui.dashboard.simulation_panel import SimulationPanel
from src.gui.dashboard.results_panel import ResultsPanel
from src.gui.utils.config_manager import ConfigManager
from src.gui.utils.results_manager import ResultsManager
from src.gui.utils.simulation_runner import SimulationRunner
from src.models.player import Player


class MainDashboard(ttk.Frame):
    """Main dashboard container with left sidebar layout and compare mode.

    Dashboard layout (per 03-07 mockup):
    - Left sidebar: SetupPanel with Team Config, Sim Params, Assumptions
    - Main content area (right):
      - Top: SimulationPanel with tabbed interface and Run button
      - Bottom: ResultsPanel with summary and detailed statistics

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
        self.simulation_panels: List[SimulationPanel] = []
        self.compare_mode = False
        self.roster: List[Player] = []
        self.team_data = None

        self._create_layout()
        self._prompt_session_restore()

    def _create_layout(self):
        """Create main dashboard layout with left sidebar structure."""
        # Main horizontal PanedWindow: Sidebar left, content right
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # Minimum width for left panel
        self._min_left_width = 250

        # Bind Configure event to enforce minimum width
        self.main_paned.bind('<Configure>', self._enforce_min_left_width)

        # Left sidebar: Setup panel
        self.setup_panel = SetupPanel(self.main_paned)
        self.setup_panel.set_data_loaded_callback(self._on_data_loaded)
        self.main_paned.add(self.setup_panel, weight=0)

        # Right content: Vertical PanedWindow for simulation + results
        self.content_paned = ttk.PanedWindow(self.main_paned, orient=tk.VERTICAL)
        self.main_paned.add(self.content_paned, weight=1)

        # Top: Simulation panel with tabs
        simulation_panel = self._create_simulation_panel()
        self.content_paned.add(simulation_panel, weight=1)

        # Bottom: Results panel (compact mode for horizontal layout)
        self.results_panel = ResultsPanel(
            self.content_paned,
            results_manager=self.results_manager,
            compact=True
        )
        self.content_paned.add(self.results_panel, weight=1)

    def _create_simulation_panel(self) -> SimulationPanel:
        """
        Create a simulation panel with callbacks.

        Returns:
            Configured SimulationPanel instance
        """
        # Only first panel gets compare button
        on_compare = self.toggle_compare_mode if len(self.simulation_panels) == 0 else None

        panel = SimulationPanel(
            self.content_paned,
            on_run=lambda: self._run_simulation(panel),
            on_compare=on_compare
        )
        self.simulation_panels.append(panel)

        # Load roster data if available
        if self.roster:
            panel.load_roster_data(self.roster, self.team_data)

        return panel

    def toggle_compare_mode(self):
        """Toggle between single simulation panel and comparison mode.

        Creates/destroys second simulation panel following proper widget lifecycle
        (forget then destroy) to prevent memory leaks.
        """
        self.compare_mode = not self.compare_mode

        if self.compare_mode:
            # Add second simulation panel
            panel = self._create_simulation_panel()
            # Insert between first panel and results
            # Since content_paned is now vertical, insert at position 1
            self.content_paned.insert(1, panel, weight=1)
        else:
            # Remove second simulation panel
            if len(self.simulation_panels) > 1:
                panel = self.simulation_panels[1]
                # Proper widget destruction (RESEARCH.md Pitfall 1)
                self.content_paned.forget(panel)  # Remove from paned window
                panel.destroy()  # Free memory
                self.simulation_panels.remove(panel)  # Clear tracking reference

    def _run_simulation(self, simulation_panel: SimulationPanel):
        """
        Run simulation for a specific simulation panel.

        Args:
            simulation_panel: SimulationPanel that triggered the run
        """
        # Get lineup data
        lineup_data = simulation_panel.get_lineup_data()

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
            simulation_panel.update_progress(current, total)

        # Completion callback
        def complete_callback(results: Optional[Dict[str, Any]]):
            self._on_simulation_complete(results, simulation_panel)

        # Start simulation in thread
        self.sim_runner.run_in_thread(
            lineup=lineup,
            config_overrides=config_overrides,
            progress_callback=progress_callback,
            complete_callback=complete_callback
        )

    def _on_simulation_complete(self, results: Optional[Dict[str, Any]], simulation_panel: SimulationPanel):
        """
        Handle simulation completion.

        Args:
            results: Results dictionary from simulation, or None if stopped/error
            simulation_panel: SimulationPanel that ran the simulation
        """
        # Hide progress indicator
        simulation_panel.hide_progress()

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

        # Extract CI from ci_95 tuple/list
        ci_95 = runs.get('ci_95', (0, 0))
        ci_lower = ci_95[0] if ci_95 else 0
        ci_upper = ci_95[1] if ci_95 else 0

        # Extract percentiles from nested dict
        percentiles = runs.get('percentiles', {})
        p25 = percentiles.get('25th')
        p75 = percentiles.get('75th')

        # Build normalized result
        normalized = {
            'mean': runs.get('mean', 0),
            'std': runs.get('std', 0),
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'iterations': summary.get('n_simulations', 0),
            'distribution': distribution,
            'min': runs.get('min'),
            'max': runs.get('max'),
            'median': runs.get('median'),
            'p25': p25,
            'p75': p75,
            # New metrics (04-02)
            'win_probability': summary.get('win_probability'),
            'lob_per_game': summary.get('lob_per_game'),
            'risp_conversion': summary.get('risp_conversion'),  # None until tracking added
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

        # Load data into all existing simulation panels
        for panel in self.simulation_panels:
            panel.load_roster_data(roster, team_data)

    def get_dashboard_state(self) -> Dict[str, Any]:
        """
        Get current dashboard state for session management.

        Returns:
            Dictionary containing:
                - setup_collapsed: Whether setup panel assumptions are collapsed
                - compare_mode: Whether compare mode is active
                - simulation_panels: List of lineup data from each panel (player names, JSON-serializable)
                - paned_positions: Sash positions for resizable panes
        """
        # Convert Player objects to names for JSON serialization
        serialized_lineups = []
        for panel in self.simulation_panels:
            lineup = panel.get_lineup_data()
            # Convert List[Optional[Player]] to List[Optional[str]]
            names = [p.name if p is not None else None for p in lineup]
            serialized_lineups.append(names)

        state = {
            'setup_collapsed': self.setup_panel.assumptions_frame.collapsed,
            'compare_mode': self.compare_mode,
            'simulation_panels': serialized_lineups,
            'paned_positions': {
                'main_horizontal': self.main_paned.sashpos(0),  # Sidebar width
                'content_vertical': self.content_paned.sashpos(0)  # Simulation vs results split
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

        # Restore lineup data (convert player names back to Player objects)
        # Support both old 'lineup_panels' and new 'simulation_panels' keys
        lineup_data = state.get('simulation_panels', state.get('lineup_panels', []))
        if self.roster:
            # Build name->Player lookup
            player_lookup = {p.name: p for p in self.roster}
            for i, names in enumerate(lineup_data):
                if i < len(self.simulation_panels) and names:
                    # Convert List[Optional[str]] back to List[Optional[Player]]
                    lineup = [player_lookup.get(name) if name else None for name in names]
                    self.simulation_panels[i].set_lineup_data(lineup)

        # Restore paned positions
        positions = state.get('paned_positions', {})
        if 'main_horizontal' in positions:
            self.main_paned.sashpos(0, positions['main_horizontal'])
        if 'content_vertical' in positions:
            self.content_paned.sashpos(0, positions['content_vertical'])
        # Legacy support for old position keys
        elif 'main_vertical' in positions:
            self.main_paned.sashpos(0, positions['main_vertical'])
        if 'content_horizontal' in positions:
            self.content_paned.sashpos(0, positions['content_horizontal'])

    def _enforce_min_left_width(self, event=None) -> None:
        """Enforce minimum width on left panel.

        Prevents the setup panel from shrinking below 250px.

        Args:
            event: Configure event (optional)
        """
        try:
            current_pos = self.main_paned.sashpos(0)
            if current_pos < self._min_left_width:
                self.main_paned.sashpos(0, self._min_left_width)
        except tk.TclError:
            # Ignore if sash doesn't exist yet (window not fully mapped)
            pass
