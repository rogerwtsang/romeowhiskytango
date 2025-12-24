"""Tab for output configuration."""

import tkinter as tk
from tkinter import ttk
import config


class OutputTab(ttk.Frame):
    """Tab for output configuration."""

    def __init__(self, parent, **kwargs):
        """Initialize output tab."""
        super().__init__(parent, **kwargs)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Statistics to Display Section
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics to Display", padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create checkboxes in two columns
        self.stat_vars = {}

        stats_list = [
            ('total_runs', 'Total Runs (mean, median, std, CI)'),
            ('runs_histogram', 'Runs Distribution Histogram'),
            ('runs_per_game', 'Runs per Game'),
            ('hits', 'Hits per Season'),
            ('walks', 'Walks per Season'),
            ('stolen_bases', 'Stolen Base Stats'),
            ('sac_flies', 'Sacrifice Flies'),
            ('lob', 'Left on Base'),
            ('inning_breakdown', 'Inning-by-Inning Breakdown'),
            ('percentiles', 'Percentile Rankings'),
        ]

        for i, (key, label) in enumerate(stats_list):
            var = tk.BooleanVar(value=True)
            self.stat_vars[key] = var

            col = i // 5
            row = i % 5

            ttk.Checkbutton(stats_frame, text=label, variable=var).grid(
                row=row, column=col, sticky='w', padx=10, pady=3
            )

        # Verbosity Section
        verb_frame = ttk.LabelFrame(main_frame, text="Verbosity Level", padding=15)
        verb_frame.pack(fill=tk.X, pady=(0, 15))

        self.verbosity_var = tk.IntVar(value=1)

        ttk.Radiobutton(verb_frame, text="Silent (no output)", variable=self.verbosity_var, value=0).pack(anchor='w', pady=2)
        ttk.Radiobutton(verb_frame, text="Progress (show progress updates)", variable=self.verbosity_var, value=1).pack(anchor='w', pady=2)
        ttk.Radiobutton(verb_frame, text="Debug (detailed output)", variable=self.verbosity_var, value=2).pack(anchor='w', pady=2)

    def _load_defaults(self):
        """Load default values from config."""
        self.verbosity_var.set(config.VERBOSITY)

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            'verbosity': self.verbosity_var.get(),
            'show_stats': {key: var.get() for key, var in self.stat_vars.items()}
        }

    def get_enabled_stats(self) -> list:
        """Get list of enabled statistics."""
        return [key for key, var in self.stat_vars.items() if var.get()]
