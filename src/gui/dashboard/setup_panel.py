# ============================================================================
# src/gui/dashboard/setup_panel.py
# ============================================================================
"""Setup panel consolidating team configuration and simulation assumptions."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import config
from src.data.scraper import get_team_batting_stats, prepare_player_stats, load_data
from src.data.processor import prepare_roster
from src.gui.widgets.collapsible_frame import CollapsibleFrame
from src.gui.widgets.labeled_slider import LabeledSlider


# MLB team codes with full names
MLB_TEAMS = [
    ('ARI', 'Arizona Diamondbacks'),
    ('ATL', 'Atlanta Braves'),
    ('BAL', 'Baltimore Orioles'),
    ('BOS', 'Boston Red Sox'),
    ('CHC', 'Chicago Cubs'),
    ('CHW', 'Chicago White Sox'),
    ('CIN', 'Cincinnati Reds'),
    ('CLE', 'Cleveland Guardians'),
    ('COL', 'Colorado Rockies'),
    ('DET', 'Detroit Tigers'),
    ('HOU', 'Houston Astros'),
    ('KCR', 'Kansas City Royals'),
    ('LAA', 'Los Angeles Angels'),
    ('LAD', 'Los Angeles Dodgers'),
    ('MIA', 'Miami Marlins'),
    ('MIL', 'Milwaukee Brewers'),
    ('MIN', 'Minnesota Twins'),
    ('NYM', 'New York Mets'),
    ('NYY', 'New York Yankees'),
    ('OAK', 'Oakland Athletics'),
    ('PHI', 'Philadelphia Phillies'),
    ('PIT', 'Pittsburgh Pirates'),
    ('SDP', 'San Diego Padres'),
    ('SEA', 'Seattle Mariners'),
    ('SFG', 'San Francisco Giants'),
    ('STL', 'St. Louis Cardinals'),
    ('TBR', 'Tampa Bay Rays'),
    ('TEX', 'Texas Rangers'),
    ('TOR', 'Toronto Blue Jays'),
    ('WSN', 'Washington Nationals'),
]


class SetupPanel(ttk.Frame):
    """Consolidated setup panel with team configuration and assumptions subsection.

    Combines team/season configuration with collapsible assumptions section containing
    baserunning, errors, and distribution settings. Reduces navigation overhead by
    grouping all configuration in a single panel.

    Layout:
        - Team/Season configuration at top
        - Collapsible Assumptions subsection below
        - Assumptions contains: Baserunning, Errors & Wild Pitches, Hit Distribution
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize setup panel.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.roster = []
        self.team_data = None
        self.data_loaded_callback: Optional[Callable] = None

        # Configure grid for responsive layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Team config section
        self.rowconfigure(1, weight=0)  # Sim params section
        self.rowconfigure(2, weight=1)  # Assumptions section (expandable)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self) -> None:
        """Create panel widgets."""
        # Team Configuration Section
        team_frame = ttk.LabelFrame(self, text="Team Configuration", padding=10)
        team_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))

        # Team selector
        ttk.Label(team_frame, text="Team:").grid(row=0, column=0, sticky='w', pady=5)
        team_display = [f"{code} - {name}" for code, name in MLB_TEAMS]
        self.team_combo = ttk.Combobox(team_frame, values=team_display, state='readonly', width=30)
        self.team_combo.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        # Season selector
        ttk.Label(team_frame, text="Season:").grid(row=1, column=0, sticky='w', pady=5)
        self.season_spin = ttk.Spinbox(team_frame, from_=2015, to=2025, width=10)
        self.season_spin.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))

        # Load data button
        self.load_btn = ttk.Button(team_frame, text="Load Team Data", command=self._load_team_data)
        self.load_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Data status label
        self.status_label = ttk.Label(team_frame, text="No data loaded", foreground='gray')
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Simulation Parameters Section
        sim_frame = ttk.LabelFrame(self, text="Simulation Parameters", padding=10)
        sim_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # Number of simulations
        ttk.Label(sim_frame, text="Number of Simulations:").grid(row=0, column=0, sticky='w', pady=5)
        sim_inner = ttk.Frame(sim_frame)
        sim_inner.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        self.n_sims_scale = tk.Scale(
            sim_inner,
            from_=100,
            to=10000,
            orient='horizontal',
            length=300,
            command=self._on_sims_change
        )
        self.n_sims_scale.pack(side=tk.LEFT)

        self.n_sims_entry = ttk.Entry(sim_inner, width=10)
        self.n_sims_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.n_sims_entry.bind('<Return>', lambda e: self._on_sims_entry_change())
        self.n_sims_entry.bind('<FocusOut>', lambda e: self._on_sims_entry_change())

        # Games per season
        ttk.Label(sim_frame, text="Games per Season:").grid(row=1, column=0, sticky='w', pady=5)
        self.n_games_spin = ttk.Spinbox(sim_frame, from_=1, to=162, width=10)
        self.n_games_spin.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))

        # Innings per game
        ttk.Label(sim_frame, text="Innings per Game:").grid(row=2, column=0, sticky='w', pady=5)
        self.n_innings_spin = ttk.Spinbox(sim_frame, from_=1, to=20, width=10)
        self.n_innings_spin.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))

        # Random seed
        ttk.Label(sim_frame, text="Random Seed:").grid(row=3, column=0, sticky='w', pady=5)
        seed_frame = ttk.Frame(sim_frame)
        seed_frame.grid(row=3, column=1, sticky='w', pady=5, padx=(10, 0))

        self.use_seed_var = tk.BooleanVar(value=True)
        self.use_seed_check = ttk.Checkbutton(
            seed_frame,
            text="Use seed",
            variable=self.use_seed_var,
            command=self._on_seed_toggle
        )
        self.use_seed_check.pack(side=tk.LEFT)

        self.seed_entry = ttk.Entry(seed_frame, width=10)
        self.seed_entry.pack(side=tk.LEFT, padx=(10, 0))

        # Assumptions Section (Collapsible with Scrollbar)
        self.assumptions_frame = CollapsibleFrame(self, text="Assumptions")
        self.assumptions_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=(5, 10))

        assumptions_content = self.assumptions_frame.get_content_frame()
        assumptions_content.columnconfigure(0, weight=1)
        assumptions_content.rowconfigure(0, weight=1)

        # Create Canvas with scrollbar for overflow content
        self.assumptions_canvas = tk.Canvas(
            assumptions_content,
            highlightthickness=0,
            bg='#2a2a2a'  # Match dark theme
        )
        self.assumptions_scrollbar = ttk.Scrollbar(
            assumptions_content,
            orient='vertical',
            command=self.assumptions_canvas.yview
        )
        self.assumptions_canvas.configure(yscrollcommand=self.assumptions_scrollbar.set)

        # Grid canvas and scrollbar
        self.assumptions_canvas.grid(row=0, column=0, sticky='nsew')
        self.assumptions_scrollbar.grid(row=0, column=1, sticky='ns')

        # Create frame inside canvas for actual content
        self.assumptions_inner_frame = ttk.Frame(self.assumptions_canvas)
        self.assumptions_canvas_window = self.assumptions_canvas.create_window(
            0, 0,
            window=self.assumptions_inner_frame,
            anchor='nw'
        )

        # Configure scrollable region
        self.assumptions_inner_frame.bind(
            '<Configure>',
            lambda e: self.assumptions_canvas.configure(scrollregion=self.assumptions_canvas.bbox('all'))
        )

        # Bind mousewheel for scrolling
        self.assumptions_canvas.bind('<Enter>', self._bind_mousewheel)
        self.assumptions_canvas.bind('<Leave>', self._unbind_mousewheel)

        self.assumptions_inner_frame.columnconfigure(0, weight=1)

        self._create_assumptions_section(self.assumptions_inner_frame)

    def _create_assumptions_section(self, parent: ttk.Frame) -> None:
        """Create assumptions subsection with baserunning, errors, and distribution settings.

        Args:
            parent: Parent frame (assumptions content frame)
        """
        # Baserunning Section
        baserunning_frame = ttk.LabelFrame(parent, text="Baserunning", padding=10)
        baserunning_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        baserunning_frame.columnconfigure(0, weight=1)

        # Stolen Bases
        self.enable_sb_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            baserunning_frame,
            text="Enable Stolen Bases",
            variable=self.enable_sb_var,
            command=self._on_sb_toggle
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.sb_scale_frame = ttk.Frame(baserunning_frame)
        self.sb_scale_frame.grid(row=1, column=0, sticky='ew', pady=5)
        self.sb_scale_frame.columnconfigure(0, weight=1)

        self.sb_attempt_slider = LabeledSlider(
            self.sb_scale_frame,
            label="SB Attempt Frequency:",
            from_=0.0,
            to=3.0,
            initial=1.0,
            resolution=0.1,
            format_str="{:.1f}"
        )
        self.sb_attempt_slider.grid(row=0, column=0, sticky='ew', pady=5)

        ttk.Label(
            self.sb_scale_frame,
            text="(0.0 = Never, 1.0 = Normal, 3.0 = Very Aggressive)",
            foreground='gray'
        ).grid(row=1, column=0, sticky='w')

        # Probabilistic baserunning
        self.enable_prob_br_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            baserunning_frame,
            text="Enable Probabilistic Baserunning",
            variable=self.enable_prob_br_var,
            command=self._on_prob_br_toggle
        ).grid(row=2, column=0, sticky='w', pady=(10, 5))

        self.br_sliders_frame = ttk.Frame(baserunning_frame)
        self.br_sliders_frame.grid(row=3, column=0, sticky='ew', pady=5)
        self.br_sliders_frame.columnconfigure(0, weight=1)

        ttk.Label(self.br_sliders_frame, text="Baserunning Aggression:").grid(row=0, column=0, sticky='w', pady=(0, 5))

        self.single_1st_to_3rd_slider = LabeledSlider(
            self.br_sliders_frame,
            label="1st → 3rd on Single:",
            from_=0.0,
            to=1.0,
            initial=0.28,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.single_1st_to_3rd_slider.grid(row=1, column=0, sticky='ew', pady=2)

        self.double_1st_scores_slider = LabeledSlider(
            self.br_sliders_frame,
            label="1st → Home on Double:",
            from_=0.0,
            to=1.0,
            initial=0.60,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.double_1st_scores_slider.grid(row=2, column=0, sticky='ew', pady=2)

        self.double_2nd_scores_slider = LabeledSlider(
            self.br_sliders_frame,
            label="2nd → Home on Double:",
            from_=0.0,
            to=1.0,
            initial=0.98,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.double_2nd_scores_slider.grid(row=3, column=0, sticky='ew', pady=2)

        # Sacrifice Flies
        self.enable_sf_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            baserunning_frame,
            text="Enable Sacrifice Flies",
            variable=self.enable_sf_var,
            command=self._on_sf_toggle
        ).grid(row=4, column=0, sticky='w', pady=(10, 5))

        self.sf_slider_frame = ttk.Frame(baserunning_frame)
        self.sf_slider_frame.grid(row=5, column=0, sticky='ew', pady=5)
        self.sf_slider_frame.columnconfigure(0, weight=1)

        self.flyout_pct_slider = LabeledSlider(
            self.sf_slider_frame,
            label="Flyout Percentage:",
            from_=0.0,
            to=1.0,
            initial=0.35,
            resolution=0.01,
            format_str="{:.0%}"
        )
        self.flyout_pct_slider.grid(row=0, column=0, sticky='ew', pady=5)

        ttk.Label(
            self.sf_slider_frame,
            text="(% of outs that are fly balls vs. ground outs/strikeouts)",
            foreground='gray'
        ).grid(row=1, column=0, sticky='w')

        # Errors & Wild Pitches Section
        errors_frame = ttk.LabelFrame(parent, text="Errors & Wild Pitches", padding=10)
        errors_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        errors_frame.columnconfigure(0, weight=1)

        self.enable_errors_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            errors_frame,
            text="Enable Errors & Wild Pitches",
            variable=self.enable_errors_var,
            command=self._on_errors_toggle
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.error_slider_frame = ttk.Frame(errors_frame)
        self.error_slider_frame.grid(row=1, column=0, sticky='ew', pady=5)
        self.error_slider_frame.columnconfigure(0, weight=1)

        self.error_rate_slider = LabeledSlider(
            self.error_slider_frame,
            label="Error Rate per PA:",
            from_=0.0,
            to=0.05,
            initial=0.015,
            resolution=0.001,
            format_str="{:.1%}"
        )
        self.error_rate_slider.grid(row=0, column=0, sticky='ew', pady=5)

        # Error explanation label
        self.error_explanation = ttk.Label(
            self.error_slider_frame,
            text="",
            foreground='gray'
        )
        self.error_explanation.grid(row=1, column=0, sticky='w', pady=5)

        # Configure slider to update explanation
        self.error_rate_slider.configure_command(self._update_error_explanation)
        self._update_error_explanation(self.error_rate_slider.get())

        # Hit Distribution Section
        distribution_frame = ttk.LabelFrame(parent, text="Hit Distribution", padding=10)
        distribution_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        distribution_frame.columnconfigure(0, weight=1)

        # ISO Thresholds
        iso_inner = ttk.LabelFrame(distribution_frame, text="ISO Thresholds", padding=10)
        iso_inner.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        ttk.Label(iso_inner, text="Low Power Threshold (ISO <):").grid(row=0, column=0, sticky='w', pady=5)
        self.iso_low_entry = ttk.Entry(iso_inner, width=10)
        self.iso_low_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        ttk.Label(iso_inner, text="High Power Threshold (ISO ≥):").grid(row=1, column=0, sticky='w', pady=5)
        self.iso_high_entry = ttk.Entry(iso_inner, width=10)
        self.iso_high_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))

        # Hit Distribution Profiles
        profiles_inner = ttk.LabelFrame(distribution_frame, text="Hit Distribution Profiles", padding=10)
        profiles_inner.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        profiles_inner.columnconfigure(0, weight=1)

        self.singles_entries = self._create_profile_section(profiles_inner, "Singles Hitter (ISO < low)", row=0)
        self.balanced_entries = self._create_profile_section(profiles_inner, "Balanced (low ≤ ISO < high)", row=1)
        self.power_entries = self._create_profile_section(profiles_inner, "Power Hitter (ISO ≥ high)", row=2)

        # League Average
        league_inner = ttk.LabelFrame(distribution_frame, text="League Average Fallback", padding=10)
        league_inner.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        league_inner.columnconfigure(0, weight=1)

        self.league_entries = self._create_profile_section(league_inner, None, row=0)

        # Bayesian Smoothing
        bayesian_inner = ttk.LabelFrame(distribution_frame, text="Bayesian Smoothing", padding=10)
        bayesian_inner.grid(row=3, column=0, sticky='ew')

        ttk.Label(bayesian_inner, text="Min hits for actual distribution:").grid(row=0, column=0, sticky='w', pady=5)
        self.min_hits_spin = ttk.Spinbox(bayesian_inner, from_=10, to=500, width=10)
        self.min_hits_spin.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        ttk.Label(
            bayesian_inner,
            text="(Players with fewer hits use smoothed distribution)",
            foreground='gray'
        ).grid(row=0, column=2, sticky='w', pady=5, padx=(10, 0))

        ttk.Label(bayesian_inner, text="Prior weight:").grid(row=1, column=0, sticky='w', pady=5)
        self.prior_weight_spin = ttk.Spinbox(bayesian_inner, from_=10, to=500, width=10)
        self.prior_weight_spin.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        ttk.Label(
            bayesian_inner,
            text="(Higher = more smoothing toward league average)",
            foreground='gray'
        ).grid(row=1, column=2, sticky='w', pady=5, padx=(10, 0))

    def _create_profile_section(self, parent: tk.Widget, title: Optional[str], row: int) -> dict:
        """Create a hit distribution profile section.

        Args:
            parent: Parent frame (ttk.Frame or ttk.LabelFrame)
            title: Section title (None for no title)
            row: Grid row position

        Returns:
            Dictionary of entry widgets and total label
        """
        frame: tk.Widget
        if title:
            frame = ttk.LabelFrame(parent, text=title, padding=10)
        else:
            frame = ttk.Frame(parent, padding=10)

        frame.grid(row=row, column=0, sticky='ew', pady=5)

        entries: dict = {}

        # Create entry fields for 1B, 2B, 3B, HR
        for i, hit_type in enumerate(['1B', '2B', '3B', 'HR']):
            ttk.Label(frame, text=f"{hit_type}:").grid(row=0, column=i*2, sticky='w', padx=(0, 5))
            entry = ttk.Entry(frame, width=8)
            entry.grid(row=0, column=i*2+1, sticky='w', padx=(0, 10))
            entries[hit_type] = entry

        # Total label
        ttk.Label(frame, text="Total:").grid(row=0, column=8, sticky='w', padx=(10, 5))
        total_label = ttk.Label(frame, text="100%", foreground='gray')
        total_label.grid(row=0, column=9, sticky='w')
        entries['total_label'] = total_label

        # Bind validation to update total
        def on_keyrelease(event: tk.Event, lbl: ttk.Label = total_label, ents: dict = entries) -> None:
            self._update_total(lbl, ents)

        for hit_type in ['1B', '2B', '3B', 'HR']:
            entries[hit_type].bind('<KeyRelease>', on_keyrelease)

        return entries

    def _update_total(self, label: ttk.Label, entries: dict) -> None:
        """Update total percentage label.

        Args:
            label: Total label widget
            entries: Dictionary of entry widgets
        """
        try:
            total = (
                float(entries['1B'].get() or 0) +
                float(entries['2B'].get() or 0) +
                float(entries['3B'].get() or 0) +
                float(entries['HR'].get() or 0)
            )
            color = 'green' if abs(total - 100) < 0.01 else 'red'
            label.config(text=f"{total:.1f}%", foreground=color)
        except ValueError:
            label.config(text="???", foreground='red')

    def _load_defaults(self) -> None:
        """Load default values from config."""
        # Team configuration
        for i, (code, name) in enumerate(MLB_TEAMS):
            if code == config.TARGET_TEAM:
                self.team_combo.current(i)
                break
        else:
            self.team_combo.current(0)

        # Simulation parameters
        self.season_spin.set(config.CURRENT_SEASON)
        self.n_sims_scale.set(config.N_SIMULATIONS)
        self.n_sims_entry.insert(0, str(config.N_SIMULATIONS))
        self.n_games_spin.set(config.N_GAMES_PER_SEASON)
        self.n_innings_spin.set(9)
        self.seed_entry.insert(0, str(config.RANDOM_SEED))

        # Baserunning
        self.enable_sb_var.set(config.ENABLE_STOLEN_BASES)
        self.sb_attempt_slider.set(config.SB_ATTEMPT_SCALE)
        self.enable_prob_br_var.set(config.ENABLE_PROBABILISTIC_BASERUNNING)
        self.single_1st_to_3rd_slider.set(config.BASERUNNING_AGGRESSION['single_1st_to_3rd'])
        self.double_1st_scores_slider.set(config.BASERUNNING_AGGRESSION['double_1st_scores'])
        self.double_2nd_scores_slider.set(config.BASERUNNING_AGGRESSION['double_2nd_scores'])
        self.enable_sf_var.set(config.ENABLE_SACRIFICE_FLIES)
        self.flyout_pct_slider.set(config.FLYOUT_PERCENTAGE)

        # Errors
        self.enable_errors_var.set(config.ENABLE_ERRORS_WILD_PITCHES)
        self.error_rate_slider.set(config.ERROR_RATE_PER_PA)

        # Distribution
        self.iso_low_entry.insert(0, str(config.ISO_THRESHOLDS['low']))
        self.iso_high_entry.insert(0, str(config.ISO_THRESHOLDS['medium']))
        self._set_distribution(self.singles_entries, config.HIT_DISTRIBUTIONS['singles_hitter'])
        self._set_distribution(self.balanced_entries, config.HIT_DISTRIBUTIONS['balanced'])
        self._set_distribution(self.power_entries, config.HIT_DISTRIBUTIONS['power_hitter'])
        self._set_distribution(self.league_entries, config.LEAGUE_AVG_HIT_DISTRIBUTION)
        self.min_hits_spin.set(config.MIN_HITS_FOR_ACTUAL_DIST)
        self.prior_weight_spin.set(config.BAYESIAN_PRIOR_WEIGHT)

        # Update toggle states
        self._on_sb_toggle()
        self._on_prob_br_toggle()
        self._on_sf_toggle()
        self._on_errors_toggle()

    def _set_distribution(self, entries: dict, dist_dict: dict) -> None:
        """Set distribution values from dict.

        Args:
            entries: Dictionary of entry widgets
            dist_dict: Distribution dictionary with decimal values
        """
        for hit_type in ['1B', '2B', '3B', 'HR']:
            entries[hit_type].delete(0, tk.END)
            entries[hit_type].insert(0, f"{dist_dict[hit_type] * 100:.1f}")

        self._update_total(entries['total_label'], entries)

    def _get_distribution(self, entries: dict) -> dict:
        """Get distribution dict from entries (as decimals).

        Args:
            entries: Dictionary of entry widgets

        Returns:
            Distribution dictionary with decimal values
        """
        return {
            '1B': float(entries['1B'].get()) / 100.0,
            '2B': float(entries['2B'].get()) / 100.0,
            '3B': float(entries['3B'].get()) / 100.0,
            'HR': float(entries['HR'].get()) / 100.0,
        }

    def _on_sims_change(self, value: str) -> None:
        """Handle simulations slider change.

        Args:
            value: Slider value as string
        """
        int_val = int(float(value))
        self.n_sims_entry.delete(0, tk.END)
        self.n_sims_entry.insert(0, str(int_val))

    def _on_sims_entry_change(self) -> None:
        """Handle simulations entry change."""
        try:
            value = int(self.n_sims_entry.get())
            value = max(100, min(100000, value))
            self.n_sims_scale.set(value)
            self.n_sims_entry.delete(0, tk.END)
            self.n_sims_entry.insert(0, str(value))
        except ValueError:
            self.n_sims_entry.delete(0, tk.END)
            self.n_sims_entry.insert(0, str(int(self.n_sims_scale.get())))

    def _on_seed_toggle(self) -> None:
        """Handle seed checkbox toggle."""
        if self.use_seed_var.get():
            self.seed_entry.config(state='normal')
        else:
            self.seed_entry.config(state='disabled')

    def _on_sb_toggle(self) -> None:
        """Handle stolen bases toggle."""
        enabled = self.enable_sb_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.sb_scale_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _on_prob_br_toggle(self) -> None:
        """Handle probabilistic baserunning toggle."""
        enabled = self.enable_prob_br_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.br_sliders_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _on_sf_toggle(self) -> None:
        """Handle sacrifice flies toggle."""
        enabled = self.enable_sf_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.sf_slider_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _on_errors_toggle(self) -> None:
        """Handle errors toggle."""
        enabled = self.enable_errors_var.get()
        state = 'normal' if enabled else 'disabled'

        for widget in self.error_slider_frame.winfo_children():
            try:
                widget.configure(state=state)
            except:
                pass

    def _update_error_explanation(self, value: float) -> None:
        """Update the error rate explanation.

        Args:
            value: Current error rate value
        """
        if value > 0:
            avg_pas = 1.0 / value
            self.error_explanation.config(text=f"≈ 1 error per {avg_pas:.0f} plate appearances")
        else:
            self.error_explanation.config(text="No errors")

    def _load_team_data(self) -> None:
        """Load team data from API or cache."""
        team_code = self.get_team_code()
        season = int(self.season_spin.get())

        self.load_btn.config(state='disabled')
        self.status_label.config(text="Loading data...", foreground='blue')
        self.update()

        try:
            # Try loading from cache first
            cache_filename = f"{team_code.lower()}_{season}_prepared.csv"
            try:
                import pandas as pd
                df = load_data(cache_filename, 'processed')
                self.status_label.config(text=f"Loaded from cache: {len(df)} players", foreground='green')
            except:
                # Fetch from API
                df = get_team_batting_stats(team_code, season)
                df = prepare_player_stats(df, min_pa=50)  # Lower threshold for GUI
                self.status_label.config(text=f"Fetched from API: {len(df)} players", foreground='green')

            # Convert to roster
            self.roster = prepare_roster(df)
            self.team_data = df

            # Notify callback
            if self.data_loaded_callback:
                self.data_loaded_callback(self.roster, df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load team data:\n{str(e)}")
            self.status_label.config(text="Error loading data", foreground='red')

        finally:
            self.load_btn.config(state='normal')

    def get_team_code(self) -> str:
        """Get selected team code.

        Returns:
            Three-letter team code
        """
        selection = self.team_combo.get()
        return selection.split(' - ')[0]

    def get_config(self) -> dict:
        """Get current configuration as dict.

        Returns:
            Dictionary containing all configuration values
        """
        return {
            'team': self.get_team_code(),
            'season': int(self.season_spin.get()),
            'n_iterations': int(self.n_sims_scale.get()),
            'n_games': int(self.n_games_spin.get()),
            'n_innings': int(self.n_innings_spin.get()),
            'random_seed': int(self.seed_entry.get()) if self.use_seed_var.get() else None,
            'ENABLE_STOLEN_BASES': self.enable_sb_var.get(),
            'SB_ATTEMPT_SCALE': self.sb_attempt_slider.get(),
            'ENABLE_PROBABILISTIC_BASERUNNING': self.enable_prob_br_var.get(),
            'BASERUNNING_AGGRESSION': {
                'single_1st_to_3rd': self.single_1st_to_3rd_slider.get(),
                'double_1st_scores': self.double_1st_scores_slider.get(),
                'double_2nd_scores': self.double_2nd_scores_slider.get(),
            },
            'ENABLE_SACRIFICE_FLIES': self.enable_sf_var.get(),
            'FLYOUT_PERCENTAGE': self.flyout_pct_slider.get(),
            'ENABLE_ERRORS_WILD_PITCHES': self.enable_errors_var.get(),
            'ERROR_RATE_PER_PA': self.error_rate_slider.get(),
            'ISO_THRESHOLDS': {
                'low': float(self.iso_low_entry.get()),
                'medium': float(self.iso_high_entry.get()),
            },
            'HIT_DISTRIBUTIONS': {
                'singles_hitter': self._get_distribution(self.singles_entries),
                'balanced': self._get_distribution(self.balanced_entries),
                'power_hitter': self._get_distribution(self.power_entries),
            },
            'LEAGUE_AVG_HIT_DISTRIBUTION': self._get_distribution(self.league_entries),
            'MIN_HITS_FOR_ACTUAL_DIST': int(self.min_hits_spin.get()),
            'BAYESIAN_PRIOR_WEIGHT': int(self.prior_weight_spin.get()),
        }

    def set_data_loaded_callback(self, callback: Callable) -> None:
        """Set callback to be called when data is loaded.

        Args:
            callback: Callback function accepting (roster, team_data)
        """
        self.data_loaded_callback = callback

    def _bind_mousewheel(self, event):
        """Bind mousewheel to canvas scrolling."""
        self.assumptions_canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.assumptions_canvas.bind_all('<Button-4>', self._on_mousewheel)  # Linux scroll up
        self.assumptions_canvas.bind_all('<Button-5>', self._on_mousewheel)  # Linux scroll down

    def _unbind_mousewheel(self, event):
        """Unbind mousewheel from canvas."""
        self.assumptions_canvas.unbind_all('<MouseWheel>')
        self.assumptions_canvas.unbind_all('<Button-4>')
        self.assumptions_canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self.assumptions_canvas.yview_scroll(-1, 'units')
        elif event.num == 5:  # Linux scroll down
            self.assumptions_canvas.yview_scroll(1, 'units')
        else:  # Windows/Mac
            self.assumptions_canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
