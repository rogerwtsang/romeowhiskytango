# ============================================================================
# src/gui/dashboard/results_panel.py
# ============================================================================
"""Results panel widget for displaying simulation results."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from src.gui.utils.results_manager import ResultsManager
from src.gui.utils.chart_utils import create_histogram_with_kde
from src.gui.widgets.collapsible_frame import CollapsibleFrame
from src.gui.widgets import PlayerContributionChart


class ResultsPanel(ttk.Frame):
    """Panel displaying simulation results with summary and detailed charts.

    Provides always-visible summary metrics (mean runs, standard deviation,
    confidence interval, iterations) and a collapsible details section with
    histogram and additional statistics.

    Usage:
        panel = ResultsPanel(parent, results_manager=results_mgr)
        panel.display_results(result_data)
    """

    def __init__(self, parent, results_manager: Optional[ResultsManager] = None, **kwargs):
        """
        Initialize results panel.

        Args:
            parent: Parent widget
            results_manager: Optional ResultsManager for results storage
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.results_manager = results_manager
        self._current_result: Optional[Dict[str, Any]] = None

        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Header (fixed)
        self.rowconfigure(1, weight=0)  # Summary section (fixed)
        self.rowconfigure(2, weight=1)  # Details section (expands)

        self._create_widgets()

    def _create_widgets(self):
        """Create panel widgets."""
        # Header (row 0)
        header = ttk.Label(
            self,
            text="Simulation Results",
            font=('TkDefaultFont', 14, 'bold')
        )
        header.grid(row=0, column=0, sticky='w', padx=10, pady=(10, 5))

        # Summary section (row 1)
        self._create_summary_section()

        # Details section (row 2)
        self._create_details_section()

    def _create_summary_section(self):
        """Create always-visible summary metrics section."""
        summary_frame = ttk.LabelFrame(self, text="Summary", padding=10)
        summary_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # Configure grid for 2-column layout
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)

        # Create labels for metrics (initially empty)
        # Row 0: Mean and Std Dev
        ttk.Label(summary_frame, text="Mean Runs/Season:").grid(
            row=0, column=0, sticky='w', padx=5, pady=2
        )
        self.mean_label = ttk.Label(
            summary_frame,
            text="--",
            font=('TkDefaultFont', 10, 'bold')
        )
        self.mean_label.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        ttk.Label(summary_frame, text="Standard Deviation:").grid(
            row=1, column=0, sticky='w', padx=5, pady=2
        )
        self.std_label = ttk.Label(summary_frame, text="--")
        self.std_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Row 2: Confidence Interval
        ttk.Label(summary_frame, text="95% Confidence Interval:").grid(
            row=2, column=0, sticky='w', padx=5, pady=2
        )
        self.ci_label = ttk.Label(summary_frame, text="--")
        self.ci_label.grid(row=2, column=1, sticky='w', padx=5, pady=2)

        # Row 3: Iterations
        ttk.Label(summary_frame, text="Number of Iterations:").grid(
            row=3, column=0, sticky='w', padx=5, pady=2
        )
        self.iterations_label = ttk.Label(summary_frame, text="--")
        self.iterations_label.grid(row=3, column=1, sticky='w', padx=5, pady=2)

    def _create_details_section(self):
        """Create collapsible detailed results section."""
        # CollapsibleFrame for details (initially collapsed)
        self.details_frame = CollapsibleFrame(
            self,
            text="Detailed Results & Charts"
        )
        self.details_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)

        # Collapse it initially to save space
        self.details_frame.toggle()

        # Get content frame for adding widgets
        content = self.details_frame.get_content_frame()

        # Configure content layout
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=0)  # Additional stats
        content.rowconfigure(1, weight=1)  # Histogram
        content.rowconfigure(2, weight=1)  # Contribution chart

        # Additional statistics section
        stats_frame = ttk.LabelFrame(content, text="Additional Statistics", padding=5)
        stats_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Configure 3-column layout for stats
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        # Min, Max, Median labels
        ttk.Label(stats_frame, text="Min:").grid(row=0, column=0, sticky='w', padx=5)
        self.min_label = ttk.Label(stats_frame, text="--")
        self.min_label.grid(row=1, column=0, sticky='w', padx=5)

        ttk.Label(stats_frame, text="Max:").grid(row=0, column=1, sticky='w', padx=5)
        self.max_label = ttk.Label(stats_frame, text="--")
        self.max_label.grid(row=1, column=1, sticky='w', padx=5)

        ttk.Label(stats_frame, text="Median:").grid(row=0, column=2, sticky='w', padx=5)
        self.median_label = ttk.Label(stats_frame, text="--")
        self.median_label.grid(row=1, column=2, sticky='w', padx=5)

        # Percentiles (25th, 75th)
        ttk.Label(stats_frame, text="25th Percentile:").grid(row=2, column=0, sticky='w', padx=5)
        self.p25_label = ttk.Label(stats_frame, text="--")
        self.p25_label.grid(row=3, column=0, sticky='w', padx=5)

        ttk.Label(stats_frame, text="75th Percentile:").grid(row=2, column=1, sticky='w', padx=5)
        self.p75_label = ttk.Label(stats_frame, text="--")
        self.p75_label.grid(row=3, column=1, sticky='w', padx=5)

        # Matplotlib histogram section
        histogram_frame = ttk.LabelFrame(content, text="Distribution Histogram", padding=5)
        histogram_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=histogram_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Initialize with empty plot
        self._clear_histogram()

        # Player contributions section
        contributions_frame = ttk.LabelFrame(content, text="Player Contributions", padding=5)
        contributions_frame.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        # Create contribution chart widget (figsize=(5,3) is secondary to histogram)
        self.contribution_chart = PlayerContributionChart(contributions_frame)
        self.contribution_chart.pack(fill=tk.BOTH, expand=True)

    def display_results(self, result_data: Dict[str, Any]):
        """
        Update summary and details with new results.

        Args:
            result_data: Results dictionary with keys:
                - mean: Mean runs per season
                - std: Standard deviation
                - ci_lower: Lower bound of 95% CI
                - ci_upper: Upper bound of 95% CI
                - iterations: Number of iterations
                - distribution: List/array of all season runs values
                - min (optional): Minimum value
                - max (optional): Maximum value
                - median (optional): Median value
                - p25 (optional): 25th percentile
                - p75 (optional): 75th percentile
        """
        self._current_result = result_data

        # Update summary labels
        mean = result_data.get('mean', 0)
        std = result_data.get('std', 0)
        ci_lower = result_data.get('ci_lower', 0)
        ci_upper = result_data.get('ci_upper', 0)
        iterations = result_data.get('iterations', 0)

        self.mean_label.config(text=f"{mean:.1f}")
        self.std_label.config(text=f"{std:.1f}")
        self.ci_label.config(text=f"[{ci_lower:.1f}, {ci_upper:.1f}]")
        self.iterations_label.config(text=f"{iterations:,}")

        # Update additional statistics
        distribution = result_data.get('distribution', [])
        if distribution:
            # Calculate if not provided
            min_val = result_data.get('min', min(distribution))
            max_val = result_data.get('max', max(distribution))
            median_val = result_data.get('median', np.median(distribution))
            p25_val = result_data.get('p25', np.percentile(distribution, 25))
            p75_val = result_data.get('p75', np.percentile(distribution, 75))

            self.min_label.config(text=f"{min_val:.1f}")
            self.max_label.config(text=f"{max_val:.1f}")
            self.median_label.config(text=f"{median_val:.1f}")
            self.p25_label.config(text=f"{p25_val:.1f}")
            self.p75_label.config(text=f"{p75_val:.1f}")

            # Update histogram
            self._create_histogram(distribution, mean, median_val)
        else:
            self._clear_histogram()

        # Update contribution chart
        # Extract contribution data if available (will be None until optimizer phase)
        contribution_data = result_data.get('contributions', None)
        self.contribution_chart.set_data(contribution_data)

    def clear_results(self):
        """Clear all displayed data."""
        self._current_result = None

        # Reset summary labels
        self.mean_label.config(text="--")
        self.std_label.config(text="--")
        self.ci_label.config(text="--")
        self.iterations_label.config(text="--")

        # Reset additional stats labels
        self.min_label.config(text="--")
        self.max_label.config(text="--")
        self.median_label.config(text="--")
        self.p25_label.config(text="--")
        self.p75_label.config(text="--")

        # Clear histogram
        self._clear_histogram()

        # Clear contribution chart (shows placeholder)
        self.contribution_chart.set_data(None)

    def get_current_result(self) -> Optional[Dict[str, Any]]:
        """
        Get currently displayed result data.

        Returns:
            Current result dictionary, or None if no results displayed
        """
        return self._current_result

    def _create_histogram(self, distribution, mean: float, median: float):
        """
        Create runs distribution histogram with KDE overlay.

        Args:
            distribution: List/array of season runs values
            mean: Mean value for vertical line (unused, calculated by chart_utils)
            median: Median value for vertical line (unused, calculated by chart_utils)
        """
        self.ax.clear()

        if not distribution:
            self._clear_histogram()
            return

        # Use chart_utils for histogram with KDE overlay
        # Mean and median are calculated internally by create_histogram_with_kde
        create_histogram_with_kde(
            self.ax,
            distribution,
            show_mean=True,
            show_median=True,
            title='Distribution of Simulated Runs per Season'
        )

        self.figure.tight_layout()
        self.canvas.draw()

    def _clear_histogram(self):
        """Clear histogram and show placeholder text."""
        self.ax.clear()
        self.ax.text(
            0.5, 0.5,
            'No data to display',
            ha='center',
            va='center',
            transform=self.ax.transAxes,
            fontsize=12,
            color='gray'
        )
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()
