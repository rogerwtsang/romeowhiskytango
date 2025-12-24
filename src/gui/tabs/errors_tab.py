"""Tab for errors and randomness configuration."""

import tkinter as tk
from tkinter import ttk
import config
from src.gui.widgets import LabeledSlider


class ErrorsTab(ttk.Frame):
    """Tab for errors configuration."""

    def __init__(self, parent, **kwargs):
        """Initialize errors tab."""
        super().__init__(parent, **kwargs)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Errors Section
        errors_frame = ttk.LabelFrame(main_frame, text="Defensive Errors & Wild Pitches", padding=15)
        errors_frame.pack(fill=tk.X, pady=(0, 15))

        self.enable_errors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            errors_frame,
            text="Enable Errors & Wild Pitches",
            variable=self.enable_errors_var,
            command=self._on_errors_toggle
        ).pack(anchor='w', pady=5)

        self.error_slider_frame = ttk.Frame(errors_frame)
        self.error_slider_frame.pack(fill=tk.X, pady=5)

        self.error_rate_slider = LabeledSlider(
            self.error_slider_frame,
            label="Error Rate per PA:",
            from_=0.0,
            to=0.05,
            initial=0.015,
            resolution=0.001,
            format_str="{:.1%}"
        )
        self.error_rate_slider.pack(fill=tk.X, pady=5)

        # Add explanatory label that updates with the rate
        self.error_explanation = ttk.Label(
            self.error_slider_frame,
            text="",
            foreground='gray'
        )
        self.error_explanation.pack(anchor='w', pady=5)

        # Configure slider to update explanation
        self.error_rate_slider.configure_command(self._update_error_explanation)
        self._update_error_explanation(self.error_rate_slider.get())

    def _load_defaults(self):
        """Load default values from config."""
        self.enable_errors_var.set(config.ENABLE_ERRORS_WILD_PITCHES)
        self.error_rate_slider.set(config.ERROR_RATE_PER_PA)

        self._on_errors_toggle()

    def _on_errors_toggle(self):
        """Handle errors toggle."""
        enabled = self.enable_errors_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.error_slider_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _update_error_explanation(self, value):
        """Update the error rate explanation."""
        if value > 0:
            avg_pas = 1.0 / value
            self.error_explanation.config(text=f"≈ 1 error per {avg_pas:.0f} plate appearances")
        else:
            self.error_explanation.config(text="No errors")

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            'ENABLE_ERRORS_WILD_PITCHES': self.enable_errors_var.get(),
            'ERROR_RATE_PER_PA': self.error_rate_slider.get(),
        }
