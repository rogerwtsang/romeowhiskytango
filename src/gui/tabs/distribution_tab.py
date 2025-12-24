"""Tab for hit distribution and stats configuration."""

import tkinter as tk
from tkinter import ttk
import config


class DistributionTab(ttk.Frame):
    """Tab for hit distribution configuration."""

    def __init__(self, parent, **kwargs):
        """Initialize distribution tab."""
        super().__init__(parent, **kwargs)

        self._create_widgets()
        self._load_defaults()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ISO Thresholds Section
        iso_frame = ttk.LabelFrame(main_frame, text="ISO Thresholds", padding=15)
        iso_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(iso_frame, text="Low Power Threshold (ISO <):").grid(row=0, column=0, sticky='w', pady=5)
        self.iso_low_entry = ttk.Entry(iso_frame, width=10)
        self.iso_low_entry.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))

        ttk.Label(iso_frame, text="High Power Threshold (ISO ≥):").grid(row=1, column=0, sticky='w', pady=5)
        self.iso_high_entry = ttk.Entry(iso_frame, width=10)
        self.iso_high_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))

        # Hit Distribution Profiles Section
        dist_frame = ttk.LabelFrame(main_frame, text="Hit Distribution Profiles", padding=15)
        dist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create 3 profile sections
        self.singles_entries = self._create_profile_section(dist_frame, "Singles Hitter (ISO < low)", row=0)
        self.balanced_entries = self._create_profile_section(dist_frame, "Balanced (low ≤ ISO < high)", row=1)
        self.power_entries = self._create_profile_section(dist_frame, "Power Hitter (ISO ≥ high)", row=2)

        # League Average Section
        league_frame = ttk.LabelFrame(main_frame, text="League Average Fallback", padding=15)
        league_frame.pack(fill=tk.X, pady=(0, 15))

        self.league_entries = self._create_profile_section(league_frame, None, row=0)

        # Bayesian Smoothing Section
        bayesian_frame = ttk.LabelFrame(main_frame, text="Bayesian Smoothing", padding=15)
        bayesian_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(bayesian_frame, text="Min hits for actual distribution:").grid(row=0, column=0, sticky='w', pady=5)
        self.min_hits_spin = ttk.Spinbox(bayesian_frame, from_=10, to=500, width=10)
        self.min_hits_spin.grid(row=0, column=1, sticky='w', pady=5, padx=(10, 0))
        ttk.Label(bayesian_frame, text="(Players with fewer hits use smoothed distribution)", foreground='gray').grid(row=0, column=2, sticky='w', pady=5, padx=(10, 0))

        ttk.Label(bayesian_frame, text="Prior weight:").grid(row=1, column=0, sticky='w', pady=5)
        self.prior_weight_spin = ttk.Spinbox(bayesian_frame, from_=10, to=500, width=10)
        self.prior_weight_spin.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        ttk.Label(bayesian_frame, text="(Higher = more smoothing toward league average)", foreground='gray').grid(row=1, column=2, sticky='w', pady=5, padx=(10, 0))

        # Reset button
        ttk.Button(main_frame, text="Reset to Defaults", command=self._load_defaults).pack(pady=10)

    def _create_profile_section(self, parent, title, row):
        """Create a hit distribution profile section."""
        if title:
            frame = ttk.LabelFrame(parent, text=title, padding=10)
        else:
            frame = ttk.Frame(parent, padding=10)

        frame.grid(row=row, column=0, sticky='ew', pady=5)

        entries = {}

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
        for entry in [entries['1B'], entries['2B'], entries['3B'], entries['HR']]:
            entry.bind('<KeyRelease>', lambda e, lbl=total_label, ents=entries: self._update_total(lbl, ents))

        return entries

    def _update_total(self, label, entries):
        """Update total percentage label."""
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

    def _load_defaults(self):
        """Load default values from config."""
        # ISO thresholds
        self.iso_low_entry.delete(0, tk.END)
        self.iso_low_entry.insert(0, str(config.ISO_THRESHOLDS['low']))

        self.iso_high_entry.delete(0, tk.END)
        self.iso_high_entry.insert(0, str(config.ISO_THRESHOLDS['medium']))

        # Hit distributions (convert decimal to percentage)
        self._set_distribution(self.singles_entries, config.HIT_DISTRIBUTIONS['singles_hitter'])
        self._set_distribution(self.balanced_entries, config.HIT_DISTRIBUTIONS['balanced'])
        self._set_distribution(self.power_entries, config.HIT_DISTRIBUTIONS['power_hitter'])
        self._set_distribution(self.league_entries, config.LEAGUE_AVG_HIT_DISTRIBUTION)

        # Bayesian smoothing
        self.min_hits_spin.set(config.MIN_HITS_FOR_ACTUAL_DIST)
        self.prior_weight_spin.set(config.BAYESIAN_PRIOR_WEIGHT)

    def _set_distribution(self, entries, dist_dict):
        """Set distribution values from dict."""
        for hit_type in ['1B', '2B', '3B', 'HR']:
            entries[hit_type].delete(0, tk.END)
            entries[hit_type].insert(0, f"{dist_dict[hit_type] * 100:.1f}")

        self._update_total(entries['total_label'], entries)

    def _get_distribution(self, entries) -> dict:
        """Get distribution dict from entries (as decimals)."""
        return {
            '1B': float(entries['1B'].get()) / 100.0,
            '2B': float(entries['2B'].get()) / 100.0,
            '3B': float(entries['3B'].get()) / 100.0,
            'HR': float(entries['HR'].get()) / 100.0,
        }

    def get_config(self) -> dict:
        """Get current configuration as dict."""
        return {
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
