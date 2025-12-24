"""Player list widget with sortable columns."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from src.models.player import Player


class PlayerList(ttk.Frame):
    """Treeview displaying players with sortable columns."""

    def __init__(self, parent, **kwargs):
        """
        Initialize player list.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.players: List[Player] = []
        self.sort_column = 'pa'
        self.sort_reverse = True

        # Create treeview
        columns = ('name', 'pa', 'ba', 'obp', 'slg', 'iso')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)

        # Define headings
        self.tree.heading('name', text='Name', command=lambda: self.sort_by('name'))
        self.tree.heading('pa', text='PA', command=lambda: self.sort_by('pa'))
        self.tree.heading('ba', text='BA', command=lambda: self.sort_by('ba'))
        self.tree.heading('obp', text='OBP', command=lambda: self.sort_by('obp'))
        self.tree.heading('slg', text='SLG', command=lambda: self.sort_by('slg'))
        self.tree.heading('iso', text='ISO', command=lambda: self.sort_by('iso'))

        # Define column widths
        self.tree.column('name', width=150)
        self.tree.column('pa', width=60, anchor='center')
        self.tree.column('ba', width=60, anchor='center')
        self.tree.column('obp', width=60, anchor='center')
        self.tree.column('slg', width=60, anchor='center')
        self.tree.column('iso', width=60, anchor='center')

        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def load_players(self, players: List[Player]):
        """
        Load players into the list.

        Args:
            players: List of Player objects
        """
        self.players = players
        self.refresh()

    def refresh(self):
        """Refresh the treeview with current players."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sort players
        if self.sort_column == 'name':
            sorted_players = sorted(self.players, key=lambda p: p.name, reverse=self.sort_reverse)
        elif self.sort_column == 'pa':
            sorted_players = sorted(self.players, key=lambda p: p.pa, reverse=self.sort_reverse)
        elif self.sort_column == 'ba':
            sorted_players = sorted(self.players, key=lambda p: p.ba, reverse=self.sort_reverse)
        elif self.sort_column == 'obp':
            sorted_players = sorted(self.players, key=lambda p: p.obp, reverse=self.sort_reverse)
        elif self.sort_column == 'slg':
            sorted_players = sorted(self.players, key=lambda p: p.slg, reverse=self.sort_reverse)
        elif self.sort_column == 'iso':
            sorted_players = sorted(self.players, key=lambda p: p.iso, reverse=self.sort_reverse)
        else:
            sorted_players = self.players

        # Insert players
        for player in sorted_players:
            self.tree.insert('', 'end', values=(
                player.name,
                player.pa,
                f"{player.ba:.3f}",
                f"{player.obp:.3f}",
                f"{player.slg:.3f}",
                f"{player.iso:.3f}"
            ))

    def sort_by(self, column: str):
        """
        Sort by a specific column.

        Args:
            column: Column name to sort by
        """
        if self.sort_column == column:
            # Toggle sort direction
            self.sort_reverse = not self.sort_reverse
        else:
            # New column - default to descending (except name)
            self.sort_column = column
            self.sort_reverse = (column != 'name')

        self.refresh()

    def get_selected(self) -> Optional[Player]:
        """
        Get the currently selected player.

        Returns:
            Selected Player object, or None if no selection
        """
        selection = self.tree.selection()
        if not selection:
            return None

        item = self.tree.item(selection[0])
        name = item['values'][0]

        # Find player by name
        for player in self.players:
            if player.name == name:
                return player

        return None

    def get_selected_index(self) -> Optional[int]:
        """
        Get the index of the selected player in the original players list.

        Returns:
            Index of selected player, or None if no selection
        """
        player = self.get_selected()
        if player is None:
            return None

        try:
            return self.players.index(player)
        except ValueError:
            return None
