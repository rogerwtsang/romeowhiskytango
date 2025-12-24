"""Tab for team and simulation setup."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import config
from src.data.scraper import get_team_batting_stats, prepare_player_stats, load_data
from src.data.processor import prepare_roster


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


class SetupTab(ttk.Frame):
    """Tab for team and simulation setup."""

    def __init__(self, parent, **kwargs):
        """Initialize setup tab."""
        super().__init__(parent, **kwargs)

        self.roster = []
        self.team_data = None
        self.data_loaded_callback: Optional[Callable] = None

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Team Configuration Section
        team_frame = ttk.LabelFrame(main_frame, text="Team Configuration", padding=15)
        team_frame.pack(fill=tk.X, pady=(0, 15))

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
        sim_frame = ttk.LabelFrame(main_frame, text="Simulation Parameters", padding=15)
        sim_frame.pack(fill=tk.X, pady=(0, 15))

        # Number of simulations
        ttk.Label(sim_frame, text="Number of Simulations:").grid(row=0, column=0, sticky='w', pady=5)
        sim_inner = ttk.Frame(sim_frame)
        sim_inner.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        self.n_sims_scale = tk.Scale(
            sim_inner,
            from_=100,
            to=100000,
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

    def _load_defaults(self):
        """Load default values from config."""
        # Set default team (find TOR in list)
        for i, (code, name) in enumerate(MLB_TEAMS):
            if code == config.TARGET_TEAM:
                self.team_combo.current(i)
                break
        else:
            self.team_combo.current(0)

        # Set other defaults
        self.season_spin.set(config.CURRENT_SEASON)
        self.n_sims_scale.set(config.N_SIMULATIONS)
        self.n_sims_entry.insert(0, str(config.N_SIMULATIONS))
        self.n_games_spin.set(config.N_GAMES_PER_SEASON)
        self.n_innings_spin.set(9)
        self.seed_entry.insert(0, str(config.RANDOM_SEED))

    def _on_sims_change(self, value):
        """Handle simulations slider change."""
        int_val = int(float(value))
        self.n_sims_entry.delete(0, tk.END)
        self.n_sims_entry.insert(0, str(int_val))

    def _on_sims_entry_change(self):
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

    def _on_seed_toggle(self):
        """Handle seed checkbox toggle."""
        if self.use_seed_var.get():
            self.seed_entry.config(state='normal')
        else:
            self.seed_entry.config(state='disabled')

    def _load_team_data(self):
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
        """Get selected team code."""
        selection = self.team_combo.get()
        return selection.split(' - ')[0]

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
            'team': self.get_team_code(),
            'season': int(self.season_spin.get()),
            'n_iterations': int(self.n_sims_scale.get()),
            'n_games': int(self.n_games_spin.get()),
            'n_innings': int(self.n_innings_spin.get()),
            'random_seed': int(self.seed_entry.get()) if self.use_seed_var.get() else None,
        }

    def set_data_loaded_callback(self, callback: Callable):
        """Set callback to be called when data is loaded."""
        self.data_loaded_callback = callback
