# ============================================================================
# src/gui/widgets/visuals_panel.py
# ============================================================================
"""Visuals panel widget containing comprehensive chart suite."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from src.gui.utils.chart_utils import (
    create_histogram_with_kde,
    create_radar_chart,
    create_run_expectancy_chart,
    create_multi_overlay,
)
from src.gui.utils.results_manager import ResultsManager
from src.gui.widgets import PlayerContributionChart
from src.models.player import Player


class VisualsPanel(ttk.Frame):
    """Panel containing all visualization charts for simulation results.

    Provides a scrollable area with multiple chart sections:
    - Distribution Histogram (with KDE overlay)
    - Player Contributions
    - Run Expectancy by Slot
    - Distribution Overlay (compare 2-4 lineups)
    - Player Stat Radar (compare player profiles)

    Usage:
        panel = VisualsPanel(parent, results_manager=results_mgr)
        panel.set_result_data(result_data)  # Update charts with new results
        panel.set_roster(roster)  # Enable player radar chart
    """

    def __init__(
        self,
        parent,
        results_manager: Optional[ResultsManager] = None,
        **kwargs
    ):
        """
        Initialize visuals panel.

        Args:
            parent: Parent widget
            results_manager: Optional ResultsManager for accessing stored results
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.results_manager = results_manager
        self._current_result: Optional[Dict[str, Any]] = None
        self._roster: List[Player] = []

        # Configure grid for scrollable content
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        """Create panel widgets with scrollable layout."""
        # Create canvas with scrollbar for scrollable content
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure scroll region
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )

        # Create window for scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')

        # Configure scrollable frame
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Mousewheel scrolling (bind/unbind on enter/leave to avoid conflicts)
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

        # Create chart sections
        self._create_histogram_section()
        self._create_contributions_section()
        self._create_run_expectancy_section()
        self._create_overlay_section()
        self._create_radar_section()

    def _bind_mousewheel(self, event=None):
        """Bind mousewheel to canvas for scrolling."""
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel)

    def _unbind_mousewheel(self, event=None):
        """Unbind mousewheel to avoid conflicts with other scrollable areas."""
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, 'units')

    def _create_histogram_section(self):
        """Create distribution histogram section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Distribution Histogram",
            padding=10
        )
        frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Matplotlib figure
        self.histogram_figure = Figure(figsize=(8, 4), dpi=100)
        self.histogram_ax = self.histogram_figure.add_subplot(111)
        self.histogram_canvas = FigureCanvasTkAgg(self.histogram_figure, master=frame)
        self.histogram_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty state
        self._clear_histogram()

    def _create_contributions_section(self):
        """Create player contributions chart section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Player Contributions",
            padding=10
        )
        frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # PlayerContributionChart widget
        self.contribution_chart = PlayerContributionChart(frame)
        self.contribution_chart.pack(fill=tk.BOTH, expand=True)

    def _create_run_expectancy_section(self):
        """Create run expectancy by slot chart section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Run Expectancy by Slot",
            padding=10
        )
        frame.grid(row=2, column=0, sticky='ew', padx=10, pady=5)

        # Matplotlib figure
        self.run_exp_figure = Figure(figsize=(8, 4), dpi=100)
        self.run_exp_ax = self.run_exp_figure.add_subplot(111)
        self.run_exp_canvas = FigureCanvasTkAgg(self.run_exp_figure, master=frame)
        self.run_exp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty state
        self._clear_run_expectancy()

    def _create_overlay_section(self):
        """Create distribution overlay section for comparing lineups."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Distribution Overlay (Compare Lineups)",
            padding=10
        )
        frame.grid(row=3, column=0, sticky='ew', padx=10, pady=5)

        # Controls frame
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=(0, 10))

        # Listbox for selecting results (multi-select)
        ttk.Label(controls, text="Select 2-4 results to compare:").pack(side=tk.LEFT, padx=(0, 10))

        self.overlay_listbox = tk.Listbox(
            controls,
            selectmode=tk.MULTIPLE,
            height=4,
            width=40
        )
        self.overlay_listbox.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        self.refresh_overlay_btn = ttk.Button(
            controls,
            text="Refresh List",
            command=self._refresh_overlay_list
        )
        self.refresh_overlay_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Compare button
        self.compare_btn = ttk.Button(
            controls,
            text="Compare",
            command=self._create_overlay_chart
        )
        self.compare_btn.pack(side=tk.LEFT)

        # Matplotlib figure
        self.overlay_figure = Figure(figsize=(8, 4), dpi=100)
        self.overlay_ax = self.overlay_figure.add_subplot(111)
        self.overlay_canvas = FigureCanvasTkAgg(self.overlay_figure, master=frame)
        self.overlay_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty state
        self._clear_overlay()

        # Store result IDs for listbox lookup
        self._overlay_result_ids: List[str] = []

    def _create_radar_section(self):
        """Create player stat radar chart section."""
        frame = ttk.LabelFrame(
            self.scrollable_frame,
            text="Player Stat Radar",
            padding=10
        )
        frame.grid(row=4, column=0, sticky='ew', padx=10, pady=5)

        # Controls frame
        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=(0, 10))

        # Player listbox (multi-select)
        ttk.Label(controls, text="Select 1-4 players:").pack(side=tk.LEFT, padx=(0, 10))

        self.radar_listbox = tk.Listbox(
            controls,
            selectmode=tk.MULTIPLE,
            height=4,
            width=25
        )
        self.radar_listbox.pack(side=tk.LEFT, padx=(0, 10))

        # Percentile toggle
        self.radar_percentile_var = tk.BooleanVar(value=False)
        self.radar_percentile_check = ttk.Checkbutton(
            controls,
            text="Percentile Ranks",
            variable=self.radar_percentile_var,
            command=self._update_radar_chart
        )
        self.radar_percentile_check.pack(side=tk.LEFT, padx=(0, 10))

        # Update button
        self.update_radar_btn = ttk.Button(
            controls,
            text="Update Chart",
            command=self._update_radar_chart
        )
        self.update_radar_btn.pack(side=tk.LEFT)

        # Matplotlib figure (polar projection)
        self.radar_figure = Figure(figsize=(8, 6), dpi=100)
        self.radar_ax = self.radar_figure.add_subplot(111, projection='polar')
        self.radar_canvas = FigureCanvasTkAgg(self.radar_figure, master=frame)
        self.radar_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initial empty state
        self._clear_radar()

    def set_result_data(self, result_data: Dict[str, Any]):
        """
        Update histogram and contributions charts with new simulation results.

        Args:
            result_data: Normalized results dictionary with keys:
                - distribution: List/array of season runs values
                - contributions: Optional player contribution data
                - slot_runs: Optional dict mapping slot to avg runs
        """
        self._current_result = result_data

        # Update histogram
        distribution = result_data.get('distribution', [])
        if distribution:
            self._create_histogram(distribution)
        else:
            self._clear_histogram()

        # Update contributions
        contribution_data = result_data.get('contributions', None)
        self.contribution_chart.set_data(contribution_data)

        # Update run expectancy (if data available)
        slot_runs = result_data.get('slot_runs', None)
        if slot_runs:
            self._create_run_expectancy(slot_runs)
        else:
            self._clear_run_expectancy()

    def set_roster(self, roster: List[Player]):
        """
        Set roster for player radar chart selection.

        Args:
            roster: List of Player objects
        """
        self._roster = roster

        # Update radar listbox
        self.radar_listbox.delete(0, tk.END)
        for player in roster:
            self.radar_listbox.insert(tk.END, player.name)

    def _create_histogram(self, distribution):
        """Create histogram with KDE overlay."""
        self.histogram_ax.clear()

        create_histogram_with_kde(
            self.histogram_ax,
            distribution,
            show_mean=True,
            show_median=True,
            title='Distribution of Simulated Runs per Season'
        )

        self.histogram_figure.tight_layout()
        self.histogram_canvas.draw()

    def _clear_histogram(self):
        """Clear histogram and show placeholder."""
        self.histogram_ax.clear()
        self.histogram_ax.text(
            0.5, 0.5,
            'Run a simulation to view distribution',
            ha='center',
            va='center',
            transform=self.histogram_ax.transAxes,
            fontsize=12,
            color='gray'
        )
        self.histogram_ax.set_xticks([])
        self.histogram_ax.set_yticks([])
        self.histogram_canvas.draw()

    def _create_run_expectancy(self, slot_data: Dict[int, float]):
        """Create run expectancy bar chart."""
        self.run_exp_ax.clear()

        create_run_expectancy_chart(
            self.run_exp_ax,
            slot_data,
            title='Average Runs by Batting Order Position'
        )

        self.run_exp_figure.tight_layout()
        self.run_exp_canvas.draw()

    def _clear_run_expectancy(self):
        """Clear run expectancy chart and show placeholder."""
        self.run_exp_ax.clear()
        self.run_exp_ax.text(
            0.5, 0.5,
            'Slot-level run tracking not yet available',
            ha='center',
            va='center',
            transform=self.run_exp_ax.transAxes,
            fontsize=12,
            color='gray'
        )
        self.run_exp_ax.set_xticks([])
        self.run_exp_ax.set_yticks([])
        self.run_exp_canvas.draw()

    def _refresh_overlay_list(self):
        """Refresh the list of available results for overlay comparison."""
        if not self.results_manager:
            return

        # Clear and repopulate listbox
        self.overlay_listbox.delete(0, tk.END)
        self._overlay_result_ids.clear()

        results = self.results_manager.list_results()
        for result in results:
            self._overlay_result_ids.append(result['id'])
            self.overlay_listbox.insert(
                tk.END,
                f"{result['lineup_name']} ({result['mean_runs']:.0f} runs)"
            )

    def _create_overlay_chart(self):
        """Create distribution overlay chart from selected results."""
        if not self.results_manager:
            return

        # Get selected indices
        selected = self.overlay_listbox.curselection()

        if len(selected) < 2:
            self._show_overlay_error('Select at least 2 results to compare')
            return

        if len(selected) > 4:
            self._show_overlay_error('Select at most 4 results to compare')
            return

        # Get result IDs for selected items
        selected_ids = [self._overlay_result_ids[i] for i in selected]

        # Build data dictionary
        data_dict = {}
        for result_id in selected_ids:
            entry = self.results_manager.get_result_entry(result_id)
            if entry:
                results = entry['results']
                raw_data = results.get('raw_data', {})
                season_runs = raw_data.get('season_runs', [])
                if season_runs:
                    data_dict[entry['lineup_name']] = season_runs

        if len(data_dict) < 2:
            self._show_overlay_error('Selected results have no distribution data')
            return

        # Create overlay chart
        self.overlay_ax.clear()
        create_multi_overlay(
            self.overlay_ax,
            data_dict,
            title='Distribution Comparison'
        )
        self.overlay_figure.tight_layout()
        self.overlay_canvas.draw()

    def _show_overlay_error(self, message: str):
        """Show error message in overlay chart area."""
        self.overlay_ax.clear()
        self.overlay_ax.text(
            0.5, 0.5,
            message,
            ha='center',
            va='center',
            transform=self.overlay_ax.transAxes,
            fontsize=12,
            color='red'
        )
        self.overlay_ax.set_xticks([])
        self.overlay_ax.set_yticks([])
        self.overlay_canvas.draw()

    def _clear_overlay(self):
        """Clear overlay chart and show placeholder."""
        self.overlay_ax.clear()
        self.overlay_ax.text(
            0.5, 0.5,
            'Select results and click Compare',
            ha='center',
            va='center',
            transform=self.overlay_ax.transAxes,
            fontsize=12,
            color='gray'
        )
        self.overlay_ax.set_xticks([])
        self.overlay_ax.set_yticks([])
        self.overlay_canvas.draw()

    def _update_radar_chart(self):
        """Update radar chart based on selected players."""
        if not self._roster:
            self._clear_radar()
            return

        # Get selected indices
        selected = self.radar_listbox.curselection()

        if len(selected) == 0:
            self._clear_radar()
            return

        if len(selected) > 4:
            self._show_radar_error('Select at most 4 players')
            return

        # Get selected players
        selected_players = [self._roster[i] for i in selected]

        # Define stats to show
        categories = ['OBP', 'SLG', 'K%', 'ISO', 'BABIP']

        # Calculate values for each player
        use_percentile = self.radar_percentile_var.get()

        if use_percentile:
            # Calculate percentile ranks across roster
            values_dict = self._calculate_percentile_values(selected_players, categories)
        else:
            # Use normalized raw values
            values_dict = self._calculate_normalized_values(selected_players, categories)

        # Create radar chart
        self.radar_ax.clear()
        create_radar_chart(
            self.radar_ax,
            categories,
            values_dict,
            title='Player Comparison' + (' (Percentile Ranks)' if use_percentile else '')
        )
        self.radar_figure.tight_layout()
        self.radar_canvas.draw()

    def _calculate_normalized_values(
        self,
        players: List[Player],
        categories: List[str]
    ) -> Dict[str, List[float]]:
        """
        Calculate normalized (0-1) stat values for players.

        Normalization is min-max based on league typical ranges.
        """
        values_dict = {}

        # Typical stat ranges for normalization
        ranges = {
            'OBP': (0.250, 0.450),  # min, max typical values
            'SLG': (0.300, 0.600),
            'K%': (0.05, 0.35),     # Lower is better, but we show raw position
            'ISO': (0.050, 0.300),
            'BABIP': (0.250, 0.350),
        }

        for player in players:
            values = []
            for cat in categories:
                if cat == 'OBP':
                    raw = player.obp
                elif cat == 'SLG':
                    raw = player.slg
                elif cat == 'K%':
                    # K% might be stored as k_pct or similar
                    raw = getattr(player, 'k_pct', 0.22)  # Default if not available
                elif cat == 'ISO':
                    raw = player.slg - player.avg  # ISO = SLG - AVG
                elif cat == 'BABIP':
                    raw = getattr(player, 'babip', 0.300)  # Default if not available
                else:
                    raw = 0.0

                # Normalize to 0-1 range
                min_val, max_val = ranges.get(cat, (0, 1))
                normalized = (raw - min_val) / (max_val - min_val) if max_val > min_val else 0.5
                normalized = max(0.0, min(1.0, normalized))  # Clamp to 0-1
                values.append(normalized)

            values_dict[player.name] = values

        return values_dict

    def _calculate_percentile_values(
        self,
        players: List[Player],
        categories: List[str]
    ) -> Dict[str, List[float]]:
        """
        Calculate percentile rank (0-1) stat values across roster.

        Percentile is relative to all players in roster.
        """
        if not self._roster:
            return self._calculate_normalized_values(players, categories)

        values_dict = {}

        # Calculate all roster values for each stat
        roster_stats: Dict[str, List[float]] = {cat: [] for cat in categories}

        for p in self._roster:
            for cat in categories:
                if cat == 'OBP':
                    roster_stats[cat].append(p.obp)
                elif cat == 'SLG':
                    roster_stats[cat].append(p.slg)
                elif cat == 'K%':
                    roster_stats[cat].append(getattr(p, 'k_pct', 0.22))
                elif cat == 'ISO':
                    roster_stats[cat].append(p.slg - p.avg)
                elif cat == 'BABIP':
                    roster_stats[cat].append(getattr(p, 'babip', 0.300))

        # Calculate percentile for selected players
        for player in players:
            values = []
            for cat in categories:
                if cat == 'OBP':
                    raw = player.obp
                elif cat == 'SLG':
                    raw = player.slg
                elif cat == 'K%':
                    raw = getattr(player, 'k_pct', 0.22)
                elif cat == 'ISO':
                    raw = player.slg - player.avg
                elif cat == 'BABIP':
                    raw = getattr(player, 'babip', 0.300)
                else:
                    raw = 0.0

                # Calculate percentile rank
                all_vals = roster_stats[cat]
                if all_vals:
                    # Count how many values are below this one
                    below = sum(1 for v in all_vals if v < raw)
                    percentile = below / len(all_vals)
                else:
                    percentile = 0.5

                values.append(percentile)

            values_dict[player.name] = values

        return values_dict

    def _show_radar_error(self, message: str):
        """Show error message in radar chart area."""
        self.radar_ax.clear()
        self.radar_ax.text(
            0.5, 0.5,
            message,
            ha='center',
            va='center',
            transform=self.radar_ax.transAxes,
            fontsize=12,
            color='red'
        )
        self.radar_ax.set_xticks([])
        self.radar_ax.set_yticks([])
        self.radar_canvas.draw()

    def _clear_radar(self):
        """Clear radar chart and show placeholder."""
        self.radar_ax.clear()
        self.radar_ax.text(
            0.5, 0.5,
            'Load roster and select players',
            ha='center',
            va='center',
            transform=self.radar_ax.transAxes,
            fontsize=12,
            color='gray'
        )
        self.radar_ax.set_xticks([])
        self.radar_ax.set_yticks([])
        self.radar_canvas.draw()

    def clear_all(self):
        """Clear all charts to initial state."""
        self._current_result = None
        self._clear_histogram()
        self.contribution_chart.set_data(None)
        self._clear_run_expectancy()
        self._clear_overlay()
        self._clear_radar()
