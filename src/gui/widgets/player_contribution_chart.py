# ============================================================================
# src/gui/widgets/player_contribution_chart.py
# ============================================================================
"""Player contribution chart widget for visualizing runs by lineup slot or player.

Displays a horizontal bar chart showing contribution to run production, with
toggle between lineup slot view (positions 1-9) and player name view.

Shows placeholder message when contribution data is not available (data will
be provided by optimizer phase in future).

Example:
    chart = PlayerContributionChart(parent)
    chart.set_data({
        'slot_contributions': {1: 85.0, 2: 82.5, ...},
        'player_contributions': {'Player1': 85.0, ...},
        'player_names': ['Player1', 'Player2', ...]
    })
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, List

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import seaborn as sns


class PlayerContributionChart(ttk.Frame):
    """Chart showing player/slot contributions to run production.

    Displays horizontal bar chart with toggle between:
    - Lineup slot view (positions 1-9)
    - Player name view (individual players)

    Shows placeholder message when contribution data not available
    (data will be provided by optimizer phase in future).

    Attributes:
        _view_mode: Current view mode ('slot' or 'player')
        _data: Current contribution data dictionary or None
    """

    SLOT_LABELS = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']

    def __init__(self, parent, **kwargs):
        """
        Initialize player contribution chart.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self._view_mode: str = 'slot'  # 'slot' or 'player'
        self._data: Optional[Dict[str, Any]] = None

        self._create_widgets()

    def _create_widgets(self):
        """Create chart widgets including toggle buttons and matplotlib canvas."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Toggle buttons (fixed)
        self.rowconfigure(1, weight=1)  # Chart (expands)

        # Toggle buttons frame
        toggle_frame = ttk.Frame(self)
        toggle_frame.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # "By Slot" button
        self.slot_button = ttk.Button(
            toggle_frame,
            text="By Slot",
            command=lambda: self._toggle_view('slot'),
            width=10
        )
        self.slot_button.pack(side=tk.LEFT, padx=(0, 5))

        # "By Player" button
        self.player_button = ttk.Button(
            toggle_frame,
            text="By Player",
            command=lambda: self._toggle_view('player'),
            width=10
        )
        self.player_button.pack(side=tk.LEFT)

        # Update button appearance for initial state
        self._update_button_states()

        # Chart frame with matplotlib figure
        chart_frame = ttk.Frame(self)
        chart_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Create matplotlib figure - SMALLER than histogram per visual hierarchy
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize with placeholder
        self._show_placeholder()

    def set_data(self, contribution_data: Optional[Dict[str, Any]]):
        """
        Set contribution data for the chart.

        Args:
            contribution_data: Dict with:
                - slot_contributions: {1: float, 2: float, ...9: float}
                - player_contributions: {name: float, ...}
                - player_names: [name1, name2, ...name9] (in lineup order)

                OR None to show placeholder
        """
        self._data = contribution_data
        self._update_chart()

    def _toggle_view(self, mode: str):
        """
        Switch between slot and player view.

        Args:
            mode: View mode, either 'slot' or 'player'
        """
        if self._view_mode != mode:
            self._view_mode = mode
            self._update_button_states()
            self._update_chart()

    def _update_button_states(self):
        """Update toggle button appearance based on current view mode."""
        # Use relief to indicate active state
        if self._view_mode == 'slot':
            self.slot_button.state(['pressed'])
            self.player_button.state(['!pressed'])
        else:
            self.slot_button.state(['!pressed'])
            self.player_button.state(['pressed'])

    def _update_chart(self):
        """Redraw chart based on current view mode and data."""
        if self._data is None:
            self._show_placeholder()
            return

        self.ax.clear()

        # Get data based on view mode
        if self._view_mode == 'slot':
            slot_contributions = self._data.get('slot_contributions', {})
            if not slot_contributions:
                self._show_placeholder()
                return

            # Build labels and values in lineup order (1-9)
            labels = []
            values = []
            for i in range(1, 10):
                labels.append(self.SLOT_LABELS[i - 1])
                values.append(slot_contributions.get(i, 0.0))
        else:
            player_contributions = self._data.get('player_contributions', {})
            player_names = self._data.get('player_names', [])

            if not player_contributions or not player_names:
                self._show_placeholder()
                return

            # Use player names in lineup order
            labels = list(player_names[:9])  # Limit to 9 players
            values = [player_contributions.get(name, 0.0) for name in labels]

        # Create color gradient from high to low contribution
        values_arr = np.array(values)
        if values_arr.max() > values_arr.min():
            # Normalize to 0-1 for color mapping
            normalized = (values_arr - values_arr.min()) / (values_arr.max() - values_arr.min())
        else:
            normalized = np.ones_like(values_arr) * 0.5

        # Use Blues palette - higher values get darker colors
        colors = sns.color_palette("Blues_d", n_colors=9)
        # Sort indices by normalized value to assign colors
        sorted_indices = np.argsort(normalized)
        bar_colors = [colors[0]] * len(values)  # Initialize with lightest
        for rank, idx in enumerate(sorted_indices):
            bar_colors[idx] = colors[rank]

        # Create horizontal bar chart
        y_positions = np.arange(len(labels))
        bars = self.ax.barh(y_positions, values, color=bar_colors, edgecolor='black', linewidth=0.5)

        # Set y-axis labels
        self.ax.set_yticks(y_positions)
        self.ax.set_yticklabels(labels)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            width = bar.get_width()
            # Position label inside or outside bar depending on size
            if width > max(values) * 0.1:
                # Inside bar
                self.ax.text(
                    width - max(values) * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    f'{value:.1f}',
                    ha='right',
                    va='center',
                    fontsize=8,
                    color='white',
                    fontweight='bold'
                )
            else:
                # Outside bar
                self.ax.text(
                    width + max(values) * 0.02,
                    bar.get_y() + bar.get_height() / 2,
                    f'{value:.1f}',
                    ha='left',
                    va='center',
                    fontsize=8,
                    color='black'
                )

        # Set labels
        self.ax.set_xlabel('Runs Contributed')
        if self._view_mode == 'slot':
            self.ax.set_title('Contribution by Lineup Slot')
        else:
            self.ax.set_title('Contribution by Player')

        # Clip x-axis to 0 minimum
        self.ax.set_xlim(0, None)

        # Add grid for readability
        self.ax.grid(True, axis='x', alpha=0.3)

        # Invert y-axis so 1st slot is at top
        self.ax.invert_yaxis()

        self.figure.tight_layout()
        self.canvas.draw()

    def _show_placeholder(self):
        """Show placeholder when no data available."""
        self.ax.clear()
        self.ax.text(
            0.5, 0.5,
            'Contribution data\nnot yet available',
            ha='center',
            va='center',
            fontsize=10,
            color='gray',
            transform=self.ax.transAxes
        )
        self.ax.axis('off')
        self.canvas.draw()
