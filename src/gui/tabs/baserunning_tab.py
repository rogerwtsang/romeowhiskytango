"""Tab for baserunning and game situations configuration."""

import tkinter as tk
from tkinter import ttk
import config
from src.gui.widgets import LabeledSlider


class BaserunningTab(ttk.Frame):
    """Tab for baserunning configuration."""

    def __init__(self, parent, **kwargs):
        """Initialize baserunning tab."""
        super().__init__(parent, **kwargs)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Stolen Bases Section
        sb_frame = ttk.LabelFrame(main_frame, text="Stolen Bases", padding=15)
        sb_frame.pack(fill=tk.X, pady=(0, 15))

        self.enable_sb_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sb_frame,
            text="Enable Stolen Bases",
            variable=self.enable_sb_var,
            command=self._on_sb_toggle
        ).pack(anchor='w', pady=5)

        self.sb_scale_frame = ttk.Frame(sb_frame)
        self.sb_scale_frame.pack(fill=tk.X, pady=5)

        self.sb_attempt_slider = LabeledSlider(
            self.sb_scale_frame,
            label="SB Attempt Frequency:",
            from_=0.0,
            to=3.0,
            initial=1.0,
            resolution=0.1,
            format_str="{:.1f}"
        )
        self.sb_attempt_slider.pack(fill=tk.X, pady=5)

        ttk.Label(self.sb_scale_frame, text="(0.0 = Never, 1.0 = Normal, 3.0 = Very Aggressive)", foreground='gray').pack(anchor='w')

        ttk.Label(sb_frame, text="Min SB attempts for player-specific rate:").pack(anchor='w', pady=(10, 0))
        self.min_sb_spin = ttk.Spinbox(sb_frame, from_=1, to=50, width=10)
        self.min_sb_spin.pack(anchor='w', pady=5)

        # Baserunning Section
        br_frame = ttk.LabelFrame(main_frame, text="Baserunning Advancement", padding=15)
        br_frame.pack(fill=tk.X, pady=(0, 15))

        self.enable_prob_br_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            br_frame,
            text="Enable Probabilistic Baserunning",
            variable=self.enable_prob_br_var,
            command=self._on_prob_br_toggle
        ).pack(anchor='w', pady=5)

        self.conservative_br_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            br_frame,
            text="Conservative Mode (disables extra-base advancement)",
            variable=self.conservative_br_var
        ).pack(anchor='w', pady=5)

        self.br_sliders_frame = ttk.Frame(br_frame)
        self.br_sliders_frame.pack(fill=tk.X, pady=10)

        ttk.Label(self.br_sliders_frame, text="Baserunning Aggression:").pack(anchor='w', pady=(0, 5))

        self.single_1st_to_3rd_slider = LabeledSlider(
            self.br_sliders_frame,
            label="1st → 3rd on Single:",
            from_=0.0,
            to=1.0,
            initial=0.28,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.single_1st_to_3rd_slider.pack(fill=tk.X, pady=2)

        self.double_1st_scores_slider = LabeledSlider(
            self.br_sliders_frame,
            label="1st → Home on Double:",
            from_=0.0,
            to=1.0,
            initial=0.60,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.double_1st_scores_slider.pack(fill=tk.X, pady=2)

        self.double_2nd_scores_slider = LabeledSlider(
            self.br_sliders_frame,
            label="2nd → Home on Double:",
            from_=0.0,
            to=1.0,
            initial=0.98,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.double_2nd_scores_slider.pack(fill=tk.X, pady=2)

        # Preset buttons
        preset_frame = ttk.Frame(self.br_sliders_frame)
        preset_frame.pack(fill=tk.X, pady=10)

        ttk.Label(preset_frame, text="Presets:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(preset_frame, text="Conservative", command=lambda: self._apply_preset('conservative')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Average", command=lambda: self._apply_preset('average')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Aggressive", command=lambda: self._apply_preset('aggressive')).pack(side=tk.LEFT, padx=2)

        # Sacrifice Flies Section
        sf_frame = ttk.LabelFrame(main_frame, text="Sacrifice Flies", padding=15)
        sf_frame.pack(fill=tk.X, pady=(0, 15))

        self.enable_sf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            sf_frame,
            text="Enable Sacrifice Flies",
            variable=self.enable_sf_var,
            command=self._on_sf_toggle
        ).pack(anchor='w', pady=5)

        self.sf_slider_frame = ttk.Frame(sf_frame)
        self.sf_slider_frame.pack(fill=tk.X, pady=5)

        self.flyout_pct_slider = LabeledSlider(
            self.sf_slider_frame,
            label="Flyout Percentage:",
            from_=0.0,
            to=1.0,
            initial=0.35,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.flyout_pct_slider.pack(fill=tk.X, pady=5)

        ttk.Label(self.sf_slider_frame, text="(% of outs that are fly balls vs. ground outs/strikeouts)", foreground='gray').pack(anchor='w')

    def _load_defaults(self):
        """Load default values from config."""
        self.enable_sb_var.set(config.ENABLE_STOLEN_BASES)
        self.sb_attempt_slider.set(config.SB_ATTEMPT_SCALE)
        self.min_sb_spin.set(config.MIN_SB_ATTEMPTS_FOR_RATE)

        self.enable_prob_br_var.set(config.ENABLE_PROBABILISTIC_BASERUNNING)
        self.conservative_br_var.set(config.CONSERVATIVE_BASERUNNING)
        self.single_1st_to_3rd_slider.set(config.BASERUNNING_AGGRESSION['single_1st_to_3rd'])
        self.double_1st_scores_slider.set(config.BASERUNNING_AGGRESSION['double_1st_scores'])
        self.double_2nd_scores_slider.set(config.BASERUNNING_AGGRESSION['double_2nd_scores'])

        self.enable_sf_var.set(config.ENABLE_SACRIFICE_FLIES)
        self.flyout_pct_slider.set(config.FLYOUT_PERCENTAGE)

        self._on_sb_toggle()
        self._on_prob_br_toggle()
        self._on_sf_toggle()

    def _on_sb_toggle(self):
        """Handle stolen bases toggle."""
        enabled = self.enable_sb_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.sb_scale_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass  # Some widgets don't support state config

    def _on_prob_br_toggle(self):
        """Handle probabilistic baserunning toggle."""
        enabled = self.enable_prob_br_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.br_sliders_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _on_sf_toggle(self):
        """Handle sacrifice flies toggle."""
        enabled = self.enable_sf_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.sf_slider_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _apply_preset(self, preset: str):
        """Apply baserunning preset."""
        if preset == 'conservative':
            self.single_1st_to_3rd_slider.set(0.15)
            self.double_1st_scores_slider.set(0.40)
            self.double_2nd_scores_slider.set(0.95)
        elif preset == 'average':
            self.single_1st_to_3rd_slider.set(0.28)
            self.double_1st_scores_slider.set(0.60)
            self.double_2nd_scores_slider.set(0.98)
        elif preset == 'aggressive':
            self.single_1st_to_3rd_slider.set(0.40)
            self.double_1st_scores_slider.set(0.75)
            self.double_2nd_scores_slider.set(1.00)

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            'ENABLE_STOLEN_BASES': self.enable_sb_var.get(),
            'SB_ATTEMPT_SCALE': self.sb_attempt_slider.get(),
            'MIN_SB_ATTEMPTS_FOR_RATE': int(self.min_sb_spin.get()),
            'ENABLE_PROBABILISTIC_BASERUNNING': self.enable_prob_br_var.get(),
            'CONSERVATIVE_BASERUNNING': self.conservative_br_var.get(),
            'BASERUNNING_AGGRESSION': {
                'single_1st_to_3rd': self.single_1st_to_3rd_slider.get(),
                'double_1st_scores': self.double_1st_scores_slider.get(),
                'double_2nd_scores': self.double_2nd_scores_slider.get(),
            },
            'ENABLE_SACRIFICE_FLIES': self.enable_sf_var.get(),
            'FLYOUT_PERCENTAGE': self.flyout_pct_slider.get(),
        }
