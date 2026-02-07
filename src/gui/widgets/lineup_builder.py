"""Lineup builder widget with 9 batting order slots."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any
from src.models.player import Player
from src.gui.widgets.lineup_treeview import LineupTreeview


class LineupBuilder(ttk.Frame):
    """Widget for building and managing 9-player lineup.

    Uses LineupTreeview for the batting order display with spreadsheet columns
    and drag-and-drop reordering.
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize lineup builder.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.constraints: List[Dict[str, Any]] = []
        self.locked_positions: set = set()  # Positions with constraints
        self.roster: List[Player] = []
        self.team_data = None

        # Configure grid weights for two-panel layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Roster panel (left)
        self.columnconfigure(1, weight=0)  # Separator
        self.columnconfigure(2, weight=2)  # Lineup panel (right) - wider for treeview

        # Create left panel: Available Players
        self._create_roster_panel()

        # Create separator
        separator = ttk.Separator(self, orient='vertical')
        separator.grid(row=0, column=1, sticky='ns', padx=10)

        # Create right panel: Batting Order with Treeview
        self._create_lineup_panel()

        # Initial refresh
        self.refresh()

    def _create_roster_panel(self):
        """Create the roster (available players) panel on the left."""
        roster_frame = ttk.Frame(self)
        roster_frame.grid(row=0, column=0, sticky='nsew')

        # Configure grid weights
        roster_frame.rowconfigure(0, weight=0)  # Label
        roster_frame.rowconfigure(1, weight=1)  # Listbox
        roster_frame.rowconfigure(2, weight=0)  # Instruction
        roster_frame.columnconfigure(0, weight=1)

        # Label
        ttk.Label(
            roster_frame,
            text="Available Players",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))

        # Frame for listbox and scrollbar
        list_frame = ttk.Frame(roster_frame)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Create roster listbox
        self.roster_listbox = tk.Listbox(list_frame, font=('TkDefaultFont', 10))
        self.roster_listbox.grid(row=0, column=0, sticky='nsew')

        # Create scrollbar
        roster_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.roster_listbox.yview)
        self.roster_listbox.configure(yscrollcommand=roster_scrollbar.set)
        roster_scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind double-click to add player
        self.roster_listbox.bind('<Double-Button-1>', self._on_roster_double_click)

        # Instruction label
        ttk.Label(
            roster_frame,
            text="Double-click to add to lineup",
            foreground='gray',
            font=('TkDefaultFont', 9)
        ).grid(row=2, column=0, sticky='w', pady=(5, 0))

    def _create_lineup_panel(self):
        """Create the lineup (batting order) panel on the right using LineupTreeview."""
        lineup_frame = ttk.Frame(self)
        lineup_frame.grid(row=0, column=2, sticky='nsew')

        # Configure grid weights
        lineup_frame.rowconfigure(0, weight=0)  # Label
        lineup_frame.rowconfigure(1, weight=1)  # Treeview
        lineup_frame.columnconfigure(0, weight=1)

        # Label
        ttk.Label(
            lineup_frame,
            text="Batting Order",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))

        # Use LineupTreeview for the batting order display
        self.lineup_treeview = LineupTreeview(lineup_frame)
        self.lineup_treeview.grid(row=1, column=0, sticky='nsew')

    def _on_roster_double_click(self, event):
        """Handle double-click on roster player to add to lineup."""
        selection = self.roster_listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if 0 <= idx < len(self.roster):
            player = self.roster[idx]
            # Add to first empty slot
            if self.add_player(player):
                self.refresh()

    def refresh(self):
        """Refresh both the roster and lineup displays."""
        # Get current lineup from treeview
        lineup = self.lineup_treeview.get_lineup()

        # Refresh roster listbox
        self.roster_listbox.delete(0, tk.END)
        for player in self.roster:
            # Show if player is already in lineup
            in_lineup = player in lineup
            prefix = "[IN LINEUP] " if in_lineup else ""
            pos_abbrev = player.position.abbrev if player.position else ""
            pos_display = f"[{pos_abbrev}] " if pos_abbrev else ""
            text = f"{prefix}{pos_display}{player.name} ({player.ba:.3f}/{player.obp:.3f}/{player.slg:.3f})"
            self.roster_listbox.insert(tk.END, text)

            # Gray out players already in lineup
            if in_lineup:
                idx = self.roster_listbox.size() - 1
                self.roster_listbox.itemconfig(idx, foreground='gray')

    def add_player(self, player: Player, position: Optional[int] = None) -> bool:
        """
        Add a player to the lineup.

        Args:
            player: Player object to add
            position: Specific position (0-8), or None to add to first empty slot

        Returns:
            True if player was added, False otherwise
        """
        result = self.lineup_treeview.add_player(player, position)
        if result:
            self.refresh()
        return result

    def remove_player(self):
        """Remove the selected player from lineup."""
        idx = self.lineup_treeview.get_selected_index()
        if idx is not None and idx in self.locked_positions:
            return
        self.lineup_treeview.remove_selected()
        self.refresh()

    def move_up(self):
        """Move selected player up in batting order."""
        idx = self.lineup_treeview.get_selected_index()
        if idx is not None:
            if idx in self.locked_positions or (idx - 1) in self.locked_positions:
                return
        self.lineup_treeview.move_up()
        self.refresh()

    def move_down(self):
        """Move selected player down in batting order."""
        idx = self.lineup_treeview.get_selected_index()
        if idx is not None:
            if idx in self.locked_positions or (idx + 1) in self.locked_positions:
                return
        self.lineup_treeview.move_down()
        self.refresh()

    def clear_lineup(self):
        """Clear the entire lineup (except locked positions)."""
        if not self.locked_positions:
            self.lineup_treeview.clear_lineup()
        else:
            # Selectively clear non-locked positions
            lineup = self.lineup_treeview.get_lineup()
            for i in range(9):
                if i not in self.locked_positions:
                    lineup[i] = None
            self.lineup_treeview.set_lineup(lineup)
        self.refresh()

    def get_lineup(self) -> List[Optional[Player]]:
        """Get current lineup."""
        return self.lineup_treeview.get_lineup()

    def set_lineup(self, lineup: List[Optional[Player]]):
        """
        Set the lineup.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        self.lineup_treeview.set_lineup(lineup)
        self.refresh()

    def apply_constraints(self, constraints: List[Dict[str, Any]]):
        """
        Apply constraints to the lineup.

        Args:
            constraints: List of constraint dicts
        """
        self.constraints = constraints
        self.locked_positions.clear()

        # Mark positions that have fixed_position constraints
        for constraint in constraints:
            if constraint.get('type') == 'fixed_position':
                position = constraint.get('position')
                if position and 1 <= position <= 9:
                    self.locked_positions.add(position - 1)

        self.refresh()

    def is_full(self) -> bool:
        """Check if lineup has all 9 players."""
        lineup = self.lineup_treeview.get_lineup()
        return all(player is not None for player in lineup)

    def is_valid(self) -> bool:
        """Check if lineup is valid (all 9 slots filled)."""
        return self.is_full()

    def load_data(self, roster: List[Player], team_data) -> None:
        """
        Load roster and team data for lineup building.

        Stores roster and team data references and refreshes the roster display.

        Args:
            roster: List of Player objects available for lineup building
            team_data: Raw team data DataFrame from pybaseball
        """
        self.roster = roster
        self.team_data = team_data
        self.refresh()

    # Legacy property for backward compatibility
    @property
    def lineup(self) -> List[Optional[Player]]:
        """Get current lineup (legacy property for backward compatibility)."""
        return self.lineup_treeview.get_lineup()

    @lineup.setter
    def lineup(self, value: List[Optional[Player]]):
        """Set lineup (legacy property for backward compatibility)."""
        self.lineup_treeview.set_lineup(value)
