"""Tab for validation and filters configuration."""

import tkinter as tk
from tkinter import ttk
import config
from src.gui.widgets import LabeledSlider


class ValidationTab(ttk.Frame):
    """Tab for validation configuration."""

    def __init__(self, parent, **kwargs):
        """Initialize validation tab."""
        super().__init__(parent, **kwargs)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Data Quality Section
        quality_frame = ttk.LabelFrame(main_frame, text="Data Quality Filters", padding=15)
        quality_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(quality_frame, text="Min PA for player inclusion:").grid(row=0, column=0, sticky='w', pady=5)
        self.min_pa_spin = ttk.Spinbox(quality_frame, from_=10, to=600, width=10, command=self._update_exclusion_count)
        self.min_pa_spin.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        self.exclusion_label = ttk.Label(quality_frame, text="", foreground='gray')
        self.exclusion_label.grid(row=0, column=2, sticky='w', pady=5, padx=(10, 0))

        ttk.Label(quality_frame, text="Validation tolerance %:").grid(row=1, column=0, sticky='w', pady=5)

        self.validation_tolerance_slider = LabeledSlider(
            quality_frame,
            label="",
            from_=0.01,
            to=0.20,
            initial=0.05,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.validation_tolerance_slider.grid(row=1, column=1, columnspan=2, sticky='ew', pady=5, padx=(10, 0))

    def _load_defaults(self):
        """Load default values from config."""
        self.min_pa_spin.set(config.MIN_PA_FOR_INCLUSION)
        self.validation_tolerance_slider.set(config.VALIDATION_TOLERANCE_PCT)

    def _update_exclusion_count(self):
        """Update exclusion count label (placeholder for now)."""
        min_pa = int(self.min_pa_spin.get())
        self.exclusion_label.config(text=f"(Minimum threshold: {min_pa} PA)")

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            'MIN_PA_FOR_INCLUSION': int(self.min_pa_spin.get()),
            'VALIDATION_TOLERANCE_PCT': self.validation_tolerance_slider.get(),
        }
