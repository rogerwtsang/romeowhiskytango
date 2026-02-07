# ============================================================================
# src/gui/dashboard/lineup_panel.py
# ============================================================================
"""LineupPanel integrates lineup building with simulation controls."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
from src.models.player import Player
from src.gui.widgets.lineup_builder import LineupBuilder
import config


class LineupPanel(ttk.Frame):
    """Panel for lineup configuration and simulation control.

    Integrates LineupBuilder widget with Run button, year selection,
    and inline progress indicator.
    """

    def __init__(
        self,
        parent,
        on_run: Optional[Callable[[], None]] = None,
        on_compare: Optional[Callable[[], None]] = None,
        on_year_change: Optional[Callable[[str, Optional[int], Optional[int], Optional[int]], None]] = None
    ):
        """Initialize LineupPanel.

        Args:
            parent: Parent widget
            on_run: Optional callback for Run Simulation button
            on_compare: Optional callback for Compare Mode button
            on_year_change: Optional callback when year selection changes
                           Args: (mode, year, start_year, end_year)
        """
        super().__init__(parent, padding=10)

        self.on_run = on_run
        self.on_compare = on_compare
        self.on_year_change = on_year_change

        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)  # Main content column (expands)
        self.columnconfigure(1, weight=0)  # Control buttons column (fixed)
        self.rowconfigure(0, weight=0)     # Header row (fixed)
        self.rowconfigure(1, weight=0)     # Year selection row (fixed)
        self.rowconfigure(2, weight=1)     # Lineup builder row (expands)
        self.rowconfigure(3, weight=0)     # Footer/Run controls row (fixed)

        self._create_header()
        self._create_year_selection()
        self._create_content()
        self._create_footer()

    def _create_header(self):
        """Create header with title and optional Compare Mode button."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))

        # Title
        ttk.Label(
            header,
            text="Batting Order",
            font=('TkDefaultFont', 12, 'bold')
        ).pack(side=tk.LEFT)

        # Compare Mode button (if callback provided)
        if self.on_compare:
            ttk.Button(
                header,
                text="Compare Mode",
                command=self.on_compare
            ).pack(side=tk.RIGHT)

    def _create_year_selection(self):
        """Create year selection controls with mode toggle."""
        year_frame = ttk.Frame(self)
        year_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))

        # Year mode selection
        ttk.Label(year_frame, text="Stats:").pack(side=tk.LEFT, padx=(0, 5))

        self.year_mode = tk.StringVar(value="single")
        self.mode_combo = ttk.Combobox(
            year_frame,
            textvariable=self.year_mode,
            values=["Single Year", "Career Totals", "Year Range"],
            state='readonly',
            width=12
        )
        self.mode_combo.current(0)
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.mode_combo.bind('<<ComboboxSelected>>', self._on_mode_change)

        # Year selector frame (for single year or range)
        self.year_controls_frame = ttk.Frame(year_frame)
        self.year_controls_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Single year selector
        years = list(range(2025, 2014, -1))  # 2025 down to 2015
        year_strings = [str(y) for y in years]

        self.year_label = ttk.Label(self.year_controls_frame, text="Year:")
        self.year_combo = ttk.Combobox(
            self.year_controls_frame,
            values=year_strings,
            state='readonly',
            width=6
        )
        self.year_combo.set(str(config.CURRENT_SEASON))
        self.year_combo.bind('<<ComboboxSelected>>', self._on_year_change)

        # Year range selectors (hidden by default)
        self.start_label = ttk.Label(self.year_controls_frame, text="From:")
        self.start_year_combo = ttk.Combobox(
            self.year_controls_frame,
            values=year_strings,
            state='readonly',
            width=6
        )
        self.start_year_combo.set("2022")
        self.start_year_combo.bind('<<ComboboxSelected>>', self._on_year_change)

        self.end_label = ttk.Label(self.year_controls_frame, text="To:")
        self.end_year_combo = ttk.Combobox(
            self.year_controls_frame,
            values=year_strings,
            state='readonly',
            width=6
        )
        self.end_year_combo.set(str(config.CURRENT_SEASON))
        self.end_year_combo.bind('<<ComboboxSelected>>', self._on_year_change)

        # Show single year mode by default
        self._update_year_controls()

    def _update_year_controls(self):
        """Update year controls visibility based on selected mode."""
        # Clear all controls first
        for widget in self.year_controls_frame.winfo_children():
            widget.pack_forget()

        mode = self.mode_combo.get()

        if mode == "Single Year":
            self.year_label.pack(side=tk.LEFT, padx=(0, 5))
            self.year_combo.pack(side=tk.LEFT)
        elif mode == "Year Range":
            self.start_label.pack(side=tk.LEFT, padx=(0, 5))
            self.start_year_combo.pack(side=tk.LEFT, padx=(0, 10))
            self.end_label.pack(side=tk.LEFT, padx=(0, 5))
            self.end_year_combo.pack(side=tk.LEFT)
        # Career Totals mode shows no year controls

    def _on_mode_change(self, event=None):
        """Handle year mode change."""
        self._update_year_controls()
        self._notify_year_change()

    def _on_year_change(self, event=None):
        """Handle year selection change."""
        self._notify_year_change()

    def _notify_year_change(self):
        """Notify callback of year selection change."""
        if not self.on_year_change:
            return

        mode = self.mode_combo.get()
        year = None
        start_year = None
        end_year = None

        if mode == "Single Year":
            year = int(self.year_combo.get())
        elif mode == "Year Range":
            start_year = int(self.start_year_combo.get())
            end_year = int(self.end_year_combo.get())
        # Career Totals mode: all values remain None

        self.on_year_change(mode, year, start_year, end_year)

    def _create_content(self):
        """Create main content area with LineupBuilder and control buttons."""
        # LineupBuilder widget
        self.lineup_builder = LineupBuilder(self)
        self.lineup_builder.grid(row=2, column=0, sticky='nsew', padx=(0, 5))

        # Control buttons
        controls = ttk.Frame(self)
        controls.grid(row=2, column=1, sticky='ns')

        ttk.Button(
            controls,
            text="Move Up",
            command=self.lineup_builder.move_up,
            width=12
        ).pack(pady=2)

        ttk.Button(
            controls,
            text="Move Down",
            command=self.lineup_builder.move_down,
            width=12
        ).pack(pady=2)

        ttk.Button(
            controls,
            text="Remove",
            command=self.lineup_builder.remove_player,
            width=12
        ).pack(pady=2)

        ttk.Separator(controls, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(
            controls,
            text="Clear All",
            command=self.lineup_builder.clear_lineup,
            width=12
        ).pack(pady=2)

    def _create_footer(self):
        """Create footer with Run button and inline progress indicator."""
        footer = ttk.Frame(self)
        footer.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # Run button
        self.run_btn = ttk.Button(
            footer,
            text="Run Simulation",
            command=self._on_run
        )
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(footer, mode='determinate', length=200)

        # Progress label (initially hidden)
        self.progress_label = ttk.Label(footer, text="")

    def _on_run(self):
        """Handle Run button click."""
        if self.on_run:
            self.on_run()

    def update_progress(self, current: int, total: int):
        """Update inline progress indicator.

        Shows progress bar if hidden, updates percentage, and forces UI refresh.

        Args:
            current: Current iteration number
            total: Total number of iterations
        """
        # Show progress widgets if not visible
        if not self.progress.winfo_viewable():
            self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.progress_label.pack(side=tk.LEFT, padx=(10, 0))

        # Calculate and update percentage
        percentage = (current / total) * 100
        self.progress['value'] = percentage
        self.progress_label.config(text=f"{percentage:.0f}%")

        # Force UI refresh (critical for progress display)
        self.update()

    def hide_progress(self):
        """Hide progress indicator."""
        self.progress.pack_forget()
        self.progress_label.pack_forget()

    def get_lineup_data(self) -> List[Optional[Player]]:
        """Get current lineup from LineupBuilder.

        Returns:
            List of 9 Player objects (or None for empty slots)
        """
        return self.lineup_builder.get_lineup()

    def set_lineup_data(self, lineup: List[Optional[Player]]):
        """Set lineup in LineupBuilder.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        self.lineup_builder.set_lineup(lineup)

    def get_year_selection(self) -> Dict[str, Any]:
        """Get current year selection settings.

        Returns:
            Dict with keys: mode, year, start_year, end_year
        """
        mode = self.mode_combo.get()
        result = {
            'mode': mode,
            'year': None,
            'start_year': None,
            'end_year': None
        }

        if mode == "Single Year":
            result['year'] = int(self.year_combo.get())
        elif mode == "Year Range":
            result['start_year'] = int(self.start_year_combo.get())
            result['end_year'] = int(self.end_year_combo.get())

        return result

    def set_year_selection(self, mode: str, year: Optional[int] = None,
                          start_year: Optional[int] = None,
                          end_year: Optional[int] = None):
        """Set year selection mode and values.

        Args:
            mode: "Single Year", "Career Totals", or "Year Range"
            year: Year for Single Year mode
            start_year: Start year for Year Range mode
            end_year: End year for Year Range mode
        """
        # Set mode
        if mode in ["Single Year", "Career Totals", "Year Range"]:
            self.mode_combo.set(mode)
            self._update_year_controls()

        # Set year values
        if year is not None:
            self.year_combo.set(str(year))
        if start_year is not None:
            self.start_year_combo.set(str(start_year))
        if end_year is not None:
            self.end_year_combo.set(str(end_year))
