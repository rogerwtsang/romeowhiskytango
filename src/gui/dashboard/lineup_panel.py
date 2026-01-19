# ============================================================================
# src/gui/dashboard/lineup_panel.py
# ============================================================================
"""LineupPanel integrates lineup building with simulation controls."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
from src.models.player import Player
from src.gui.widgets.lineup_builder import LineupBuilder


class LineupPanel(ttk.Frame):
    """Panel for lineup configuration and simulation control.

    Integrates LineupBuilder widget with Run button and inline progress indicator,
    allowing users to build lineups and run simulations from a single contextual panel.
    """

    def __init__(
        self,
        parent,
        on_run: Optional[Callable[[], None]] = None,
        on_compare: Optional[Callable[[], None]] = None
    ):
        """Initialize LineupPanel.

        Args:
            parent: Parent widget
            on_run: Optional callback for Run Simulation button
            on_compare: Optional callback for Compare Mode button
        """
        super().__init__(parent, padding=10)

        self.on_run = on_run
        self.on_compare = on_compare

        # Configure grid weights for responsive layout
        self.columnconfigure(0, weight=1)  # Main content column (expands)
        self.columnconfigure(1, weight=0)  # Control buttons column (fixed)
        self.rowconfigure(0, weight=0)     # Header row (fixed)
        self.rowconfigure(1, weight=1)     # Lineup builder row (expands)
        self.rowconfigure(2, weight=0)     # Footer/Run controls row (fixed)

        self._create_header()
        self._create_content()
        self._create_footer()

    def _create_header(self):
        """Create header with title and optional Compare Mode button."""
        header = ttk.Frame(self)
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 10))

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

    def _create_content(self):
        """Create main content area with LineupBuilder and control buttons."""
        # LineupBuilder widget
        self.lineup_builder = LineupBuilder(self)
        self.lineup_builder.grid(row=1, column=0, sticky='nsew', padx=(0, 5))

        # Control buttons
        controls = ttk.Frame(self)
        controls.grid(row=1, column=1, sticky='ns')

        ttk.Button(
            controls,
            text="▲ Move Up",
            command=self.lineup_builder.move_up,
            width=12
        ).pack(pady=2)

        ttk.Button(
            controls,
            text="▼ Move Down",
            command=self.lineup_builder.move_down,
            width=12
        ).pack(pady=2)

        ttk.Button(
            controls,
            text="✖ Remove",
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
        footer.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # Run button
        self.run_btn = ttk.Button(
            footer,
            text="▶ Run Simulation",
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
