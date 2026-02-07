# ============================================================================
# src/gui/dashboard/results_panel.py
# ============================================================================
"""Results panel widget for displaying simulation results.

Note: Histogram and Player Contributions charts have been moved to VisualsPanel
(05-05-PLAN). This panel now focuses on summary statistics only.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any
import numpy as np

from src.gui.utils.results_manager import ResultsManager
from src.gui.widgets.collapsible_frame import CollapsibleFrame


class ResultsPanel(ttk.Frame):
    """Panel displaying simulation results summary statistics.

    Provides always-visible summary metrics (mean runs, standard deviation,
    confidence interval, iterations) and a collapsible details section with
    additional statistics.

    Note: Histogram and Player Contributions charts have been moved to VisualsPanel
    (05-05-PLAN) for consolidated visualization.

    Usage:
        panel = ResultsPanel(parent, results_manager=results_mgr)
        panel.display_results(result_data)
    """

    def __init__(
        self,
        parent,
        results_manager: Optional[ResultsManager] = None,
        compact: bool = False,
        **kwargs
    ):
        """
        Initialize results panel.

        Args:
            parent: Parent widget
            results_manager: Optional ResultsManager for results storage
            compact: If True, use horizontal layout for bottom placement
            **kwargs: Additional arguments passed to Frame
        """
        super().__init__(parent, **kwargs)

        self.results_manager = results_manager
        self._current_result: Optional[Dict[str, Any]] = None
        self.compact = compact

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

        # Row 4: Win Probability
        ttk.Label(summary_frame, text="Win Probability:").grid(
            row=4, column=0, sticky='w', padx=5, pady=2
        )
        self.win_prob_label = ttk.Label(
            summary_frame,
            text="--",
            font=('TkDefaultFont', 10, 'bold')
        )
        self.win_prob_label.grid(row=4, column=1, sticky='w', padx=5, pady=2)

        # Row 5: LOB per Game
        ttk.Label(summary_frame, text="LOB per Game:").grid(
            row=5, column=0, sticky='w', padx=5, pady=2
        )
        self.lob_label = ttk.Label(summary_frame, text="--")
        self.lob_label.grid(row=5, column=1, sticky='w', padx=5, pady=2)

        # Row 6: RISP Conversion
        ttk.Label(summary_frame, text="RISP Conversion:").grid(
            row=6, column=0, sticky='w', padx=5, pady=2
        )
        self.risp_label = ttk.Label(summary_frame, text="--")
        self.risp_label.grid(row=6, column=1, sticky='w', padx=5, pady=2)

    def _create_details_section(self):
        """Create collapsible detailed results section.

        Note: Histogram and Player Contributions have moved to VisualsPanel.
        This section now contains only Additional Statistics.
        """
        # CollapsibleFrame for details (initially collapsed)
        self.details_frame = CollapsibleFrame(
            self,
            text="Additional Statistics"
        )
        self.details_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)

        # Collapse it initially to save space
        self.details_frame.toggle()

        # Get content frame for adding widgets
        content = self.details_frame.get_content_frame()

        # Configure content layout
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=0)  # Additional stats

        # Additional statistics section
        stats_frame = ttk.Frame(content, padding=5)
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
                - win_probability (optional): Dict with mean, ci_lower, ci_upper
                - lob_per_game (optional): Dict with mean, std
                - risp_conversion (optional): Dict with rate, or None
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

        # Win probability
        win_prob = result_data.get('win_probability', {})
        if win_prob:
            wp_mean = win_prob.get('mean', 0) * 100  # Convert to percentage
            wp_lower = win_prob.get('ci_lower', 0) * 100
            wp_upper = win_prob.get('ci_upper', 0) * 100
            self.win_prob_label.config(text=f"{wp_mean:.0f}% [{wp_lower:.0f}-{wp_upper:.0f}%]")
        else:
            self.win_prob_label.config(text="--")

        # LOB per game
        lob = result_data.get('lob_per_game', {})
        if lob:
            lob_mean = lob.get('mean', 0)
            lob_std = lob.get('std', 0)
            self.lob_label.config(text=f"{lob_mean:.1f} +/- {lob_std:.1f}")
        else:
            self.lob_label.config(text="--")

        # RISP conversion (placeholder handling)
        risp = result_data.get('risp_conversion')
        if risp:
            rate = risp.get('rate', 0) * 100
            self.risp_label.config(text=f"{rate:.1f}%")
        else:
            self.risp_label.config(text="--")  # Graceful degradation

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

    def clear_results(self):
        """Clear all displayed data."""
        self._current_result = None

        # Reset summary labels
        self.mean_label.config(text="--")
        self.std_label.config(text="--")
        self.ci_label.config(text="--")
        self.iterations_label.config(text="--")

        # Reset new metric labels
        self.win_prob_label.config(text="--")
        self.lob_label.config(text="--")
        self.risp_label.config(text="--")

        # Reset additional stats labels
        self.min_label.config(text="--")
        self.max_label.config(text="--")
        self.median_label.config(text="--")
        self.p25_label.config(text="--")
        self.p75_label.config(text="--")

    def get_current_result(self) -> Optional[Dict[str, Any]]:
        """
        Get currently displayed result data.

        Returns:
            Current result dictionary, or None if no results displayed
        """
        return self._current_result
