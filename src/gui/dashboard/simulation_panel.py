# ============================================================================
# src/gui/dashboard/simulation_panel.py
# ============================================================================
"""SimulationPanel with tabbed interface for Lineup and Visuals views."""

import tkinter as tk
from tkinter import ttk, simpledialog
from typing import Optional, Callable, List
from src.models.player import Player
from src.gui.dashboard.lineup_panel import LineupPanel


class SimulationPanel(ttk.Frame):
    """Tabbed simulation panel with header, tab selectors, and run button.

    Provides a unified interface for simulation configuration and execution:
    - Header with "Simulation" title
    - Tab selectors: [Lineup] and [Visuals]
    - Run Simulation button in header (always accessible)
    - Tab content area below

    Layout matches mockup design with easily accessible Run button.
    """

    def __init__(
        self,
        parent,
        on_run: Optional[Callable[[], None]] = None,
        on_compare: Optional[Callable[[], None]] = None,
        on_save_lineup: Optional[Callable[[str], None]] = None,
        on_load_lineup: Optional[Callable[[str], None]] = None,
        on_delete_lineup: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize SimulationPanel.

        Args:
            parent: Parent widget
            on_run: Callback for Run Simulation button
            on_compare: Callback for Compare Mode button (passed to LineupPanel)
            on_save_lineup: Callback for Save Lineup button, receives lineup name
            on_load_lineup: Callback for Load Lineup button, receives lineup name
            on_delete_lineup: Callback for Delete Lineup, receives lineup name
        """
        super().__init__(parent, padding=10)

        self.on_run = on_run
        self.on_compare = on_compare
        self.on_save_lineup = on_save_lineup
        self.on_load_lineup = on_load_lineup
        self.on_delete_lineup = on_delete_lineup

        # State
        self.current_tab = 'lineup'  # 'lineup' or 'visuals'
        self.lineup_panel: Optional[LineupPanel] = None
        self._lineup_names: List[str] = []

        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Header row
        self.rowconfigure(1, weight=1)  # Content row (expands)

        self._create_header()
        self._create_content()

    def _create_header(self):
        """Create header with title, tab selectors, lineup controls, and Run button."""
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        # Configure header layout: title on left, controls on right
        header_frame.columnconfigure(0, weight=0)  # Title
        header_frame.columnconfigure(1, weight=0)  # Lineup controls
        header_frame.columnconfigure(2, weight=1)  # Spacer
        header_frame.columnconfigure(3, weight=0)  # Tab selectors
        header_frame.columnconfigure(4, weight=0)  # Run button

        # Title (with team name placeholder)
        self.title_label = ttk.Label(
            header_frame,
            text="Simulation",
            font=('TkDefaultFont', 14, 'bold')
        )
        self.title_label.grid(row=0, column=0, sticky='w', padx=(0, 20))

        # Lineup controls frame
        lineup_controls = ttk.Frame(header_frame)
        lineup_controls.grid(row=0, column=1, sticky='w', padx=(0, 20))

        # Lineup dropdown
        ttk.Label(lineup_controls, text="Lineup:").pack(side=tk.LEFT, padx=(0, 5))
        self.lineup_combo = ttk.Combobox(
            lineup_controls,
            values=[],
            state='readonly',
            width=15
        )
        self.lineup_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.lineup_combo.bind('<<ComboboxSelected>>', self._on_lineup_selected)

        # Load button
        self.load_lineup_btn = ttk.Button(
            lineup_controls,
            text="Load",
            command=self._on_load_lineup,
            width=6
        )
        self.load_lineup_btn.pack(side=tk.LEFT, padx=2)

        # Save button
        self.save_lineup_btn = ttk.Button(
            lineup_controls,
            text="Save",
            command=self._on_save_lineup,
            width=6
        )
        self.save_lineup_btn.pack(side=tk.LEFT, padx=2)

        # Delete button
        self.delete_lineup_btn = ttk.Button(
            lineup_controls,
            text="Del",
            command=self._on_delete_lineup,
            width=4
        )
        self.delete_lineup_btn.pack(side=tk.LEFT, padx=2)

        # Tab selector frame
        tab_selector_frame = ttk.Frame(header_frame)
        tab_selector_frame.grid(row=0, column=3, sticky='e', padx=(0, 10))

        # Lineup tab button
        self.lineup_tab_btn = ttk.Button(
            tab_selector_frame,
            text="Lineup",
            command=lambda: self._switch_tab('lineup'),
            width=10
        )
        self.lineup_tab_btn.pack(side=tk.LEFT, padx=2)

        # Visuals tab button
        self.visuals_tab_btn = ttk.Button(
            tab_selector_frame,
            text="Visuals",
            command=lambda: self._switch_tab('visuals'),
            width=10
        )
        self.visuals_tab_btn.pack(side=tk.LEFT, padx=2)

        # Run Simulation button (primary action style)
        self.run_btn = ttk.Button(
            header_frame,
            text="Run Simulation",
            command=self._on_run,
            style='Primary.TButton'
        )
        self.run_btn.grid(row=0, column=4, sticky='e')

        # Update tab button states
        self._update_tab_buttons()

    def _create_content(self):
        """Create content area with tab panels."""
        # Content container frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky='nsew')

        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Create Lineup tab
        self.lineup_panel = LineupPanel(
            self.content_frame,
            on_run=self.on_run,
            on_compare=self.on_compare
        )
        self.lineup_panel.grid(row=0, column=0, sticky='nsew')

        # Create Visuals tab (placeholder for future implementation)
        self.visuals_panel = ttk.Frame(self.content_frame)
        self.visuals_panel.grid(row=0, column=0, sticky='nsew')

        # Placeholder content for Visuals tab
        ttk.Label(
            self.visuals_panel,
            text="Visuals Tab - Coming Soon",
            font=('TkDefaultFont', 12, 'italic'),
            foreground='gray'
        ).pack(expand=True)

        # Initially show lineup tab
        self._show_tab('lineup')

    def _switch_tab(self, tab_name: str):
        """
        Switch to specified tab.

        Args:
            tab_name: Either 'lineup' or 'visuals'
        """
        if tab_name != self.current_tab:
            self.current_tab = tab_name
            self._show_tab(tab_name)
            self._update_tab_buttons()

    def _show_tab(self, tab_name: str):
        """
        Show specified tab content.

        Args:
            tab_name: Either 'lineup' or 'visuals'
        """
        if tab_name == 'lineup':
            self.lineup_panel.lift()
        elif tab_name == 'visuals':
            self.visuals_panel.lift()

    def _update_tab_buttons(self):
        """Update tab button states to reflect current tab."""
        # Update button styles to show active/inactive
        if self.current_tab == 'lineup':
            self.lineup_tab_btn.state(['pressed'])
            self.visuals_tab_btn.state(['!pressed'])
        else:
            self.lineup_tab_btn.state(['!pressed'])
            self.visuals_tab_btn.state(['pressed'])

    def _on_run(self):
        """Handle Run Simulation button click."""
        if self.on_run:
            self.on_run()

    def _on_lineup_selected(self, event=None):
        """Handle lineup selection from dropdown."""
        # Selection triggers load automatically
        pass

    def _on_load_lineup(self):
        """Handle Load Lineup button click."""
        lineup_name = self.lineup_combo.get()
        if lineup_name and self.on_load_lineup:
            self.on_load_lineup(lineup_name)

    def _on_save_lineup(self):
        """Handle Save Lineup button click."""
        # Prompt for lineup name
        lineup_name = simpledialog.askstring(
            "Save Lineup",
            "Enter lineup name:",
            parent=self
        )
        if lineup_name and self.on_save_lineup:
            self.on_save_lineup(lineup_name)
            # Refresh dropdown
            if lineup_name not in self._lineup_names:
                self._lineup_names.append(lineup_name)
                self.lineup_combo['values'] = self._lineup_names
            self.lineup_combo.set(lineup_name)

    def _on_delete_lineup(self):
        """Handle Delete Lineup button click."""
        lineup_name = self.lineup_combo.get()
        if lineup_name and self.on_delete_lineup:
            self.on_delete_lineup(lineup_name)
            # Refresh dropdown
            if lineup_name in self._lineup_names:
                self._lineup_names.remove(lineup_name)
                self.lineup_combo['values'] = self._lineup_names
            self.lineup_combo.set('')

    def set_lineup_names(self, names: List[str]):
        """Set available lineup names in dropdown.

        Args:
            names: List of lineup names
        """
        self._lineup_names = list(names)
        self.lineup_combo['values'] = self._lineup_names
        if self._lineup_names:
            self.lineup_combo.set(self._lineup_names[0])

    def set_team_display_name(self, display_name: str):
        """Set team display name in title.

        Args:
            display_name: Team display name (nickname or full name)
        """
        self.title_label.config(text=f"Simulation - {display_name}")

    def get_lineup_data(self) -> List[Optional[Player]]:
        """
        Get current lineup from active LineupPanel.

        Returns:
            List of 9 Player objects (or None for empty slots)
        """
        if self.lineup_panel:
            return self.lineup_panel.get_lineup_data()
        return [None] * 9

    def set_lineup_data(self, lineup: List[Optional[Player]]):
        """
        Set lineup in LineupPanel.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        if self.lineup_panel:
            self.lineup_panel.set_lineup_data(lineup)

    def update_progress(self, current: int, total: int):
        """
        Update progress indicator in active LineupPanel.

        Args:
            current: Current iteration
            total: Total iterations
        """
        if self.lineup_panel:
            self.lineup_panel.update_progress(current, total)

    def hide_progress(self):
        """Hide progress indicator in active LineupPanel."""
        if self.lineup_panel:
            self.lineup_panel.hide_progress()

    def load_roster_data(self, roster: List[Player], team_data):
        """
        Load roster data into LineupPanel.

        Args:
            roster: List of Player objects
            team_data: Raw team DataFrame
        """
        if self.lineup_panel:
            self.lineup_panel.lineup_builder.load_data(roster, team_data)
