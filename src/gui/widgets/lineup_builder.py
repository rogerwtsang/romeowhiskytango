"""Lineup builder widget with 9 batting order slots."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any
from src.models.player import Player


class LineupBuilder(ttk.Frame):
    """Widget for building and managing 9-player lineup."""

    def __init__(self, parent, **kwargs):
        """
        Initialize lineup builder.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.lineup: List[Optional[Player]] = [None] * 9
        self.constraints: List[Dict[str, Any]] = []
        self.locked_positions: set = set()  # Positions with constraints
        self.roster: List[Player] = []
        self.team_data = None

        # Configure grid weights for two-panel layout
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Roster panel (left)
        self.columnconfigure(1, weight=0)  # Separator
        self.columnconfigure(2, weight=1)  # Lineup panel (right)

        # Create left panel: Available Players
        self._create_roster_panel()

        # Create separator
        separator = ttk.Separator(self, orient='vertical')
        separator.grid(row=0, column=1, sticky='ns', padx=10)

        # Create right panel: Batting Order
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
        """Create the lineup (batting order) panel on the right."""
        lineup_frame = ttk.Frame(self)
        lineup_frame.grid(row=0, column=2, sticky='nsew')

        # Configure grid weights
        lineup_frame.rowconfigure(0, weight=0)  # Label
        lineup_frame.rowconfigure(1, weight=1)  # Listbox + buttons
        lineup_frame.columnconfigure(0, weight=1)
        lineup_frame.columnconfigure(1, weight=0)  # Buttons

        # Label
        ttk.Label(
            lineup_frame,
            text="Batting Order",
            font=('TkDefaultFont', 10, 'bold')
        ).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))

        # Frame for listbox and scrollbar
        list_frame = ttk.Frame(lineup_frame)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Create lineup listbox
        self.listbox = tk.Listbox(list_frame, height=9, font=('TkDefaultFont', 10))
        self.listbox.grid(row=0, column=0, sticky='nsew')

        # Create scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Create control buttons
        btn_frame = ttk.Frame(lineup_frame)
        btn_frame.grid(row=1, column=1, sticky='ns')

        self.up_btn = ttk.Button(btn_frame, text="▲ Move Up", command=self.move_up, width=12)
        self.up_btn.pack(pady=2)

        self.down_btn = ttk.Button(btn_frame, text="▼ Move Down", command=self.move_down, width=12)
        self.down_btn.pack(pady=2)

        self.remove_btn = ttk.Button(btn_frame, text="✖ Remove", command=self.remove_player, width=12)
        self.remove_btn.pack(pady=2)

        ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)

        self.clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_lineup, width=12)
        self.clear_btn.pack(pady=2)

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
        """Refresh both the roster and lineup listbox displays."""
        # Refresh roster listbox
        self.roster_listbox.delete(0, tk.END)
        for player in self.roster:
            # Show if player is already in lineup
            in_lineup = player in self.lineup
            prefix = "[IN LINEUP] " if in_lineup else ""
            pos_display = f"[{player.position}] " if player.position else ""
            text = f"{prefix}{pos_display}{player.name} ({player.ba:.3f}/{player.obp:.3f}/{player.slg:.3f})"
            self.roster_listbox.insert(tk.END, text)

            # Gray out players already in lineup
            if in_lineup:
                idx = self.roster_listbox.size() - 1
                self.roster_listbox.itemconfig(idx, foreground='gray')

        # Refresh lineup listbox
        self.listbox.delete(0, tk.END)

        for i, player in enumerate(self.lineup):
            if player is None:
                text = f"{i+1}. (empty)"
                self.listbox.insert(tk.END, text)
                self.listbox.itemconfig(i, foreground='gray')
            else:
                lock_icon = "🔒 " if i in self.locked_positions else ""
                pos_display = f"[{player.position}] " if player.position else ""
                text = f"{i+1}. {lock_icon}{pos_display}{player.name} ({player.ba:.3f}/{player.obp:.3f}/{player.slg:.3f})"
                self.listbox.insert(tk.END, text)

                # Highlight locked positions
                if i in self.locked_positions:
                    self.listbox.itemconfig(i, background='#ffffcc')

    def add_player(self, player: Player, position: Optional[int] = None) -> bool:
        """
        Add a player to the lineup.

        Args:
            player: Player object to add
            position: Specific position (0-8), or None to add to first empty slot

        Returns:
            True if player was added, False otherwise
        """
        # Check if player already in lineup
        if player in self.lineup:
            return False

        if position is not None:
            # Add to specific position
            if 0 <= position < 9:
                self.lineup[position] = player
                self.refresh()
                return True
            return False
        else:
            # Find first empty slot
            try:
                idx = self.lineup.index(None)
                self.lineup[idx] = player
                self.refresh()
                return True
            except ValueError:
                # Lineup is full
                return False

    def remove_player(self):
        """Remove the selected player from lineup."""
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]

        # Don't allow removing locked positions
        if idx in self.locked_positions:
            return

        self.lineup[idx] = None
        self.refresh()

    def move_up(self):
        """Move selected player up in batting order."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]

        # Don't allow moving locked positions
        if idx in self.locked_positions or (idx-1) in self.locked_positions:
            return

        # Swap with previous
        self.lineup[idx], self.lineup[idx-1] = self.lineup[idx-1], self.lineup[idx]
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx-1)

    def move_down(self):
        """Move selected player down in batting order."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 8:
            return

        idx = selection[0]

        # Don't allow moving locked positions
        if idx in self.locked_positions or (idx+1) in self.locked_positions:
            return

        # Swap with next
        self.lineup[idx], self.lineup[idx+1] = self.lineup[idx+1], self.lineup[idx]
        self.refresh()
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx+1)

    def clear_lineup(self):
        """Clear the entire lineup (except locked positions)."""
        for i in range(9):
            if i not in self.locked_positions:
                self.lineup[i] = None
        self.refresh()

    def get_lineup(self) -> List[Optional[Player]]:
        """Get current lineup."""
        return self.lineup.copy()

    def set_lineup(self, lineup: List[Optional[Player]]):
        """
        Set the lineup.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        if len(lineup) != 9:
            raise ValueError("Lineup must have exactly 9 slots")

        self.lineup = lineup.copy()
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
        return all(player is not None for player in self.lineup)

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
