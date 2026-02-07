# ============================================================================
# src/gui/widgets/lineup_treeview.py
# ============================================================================
"""Spreadsheet-like lineup display widget with drag-and-drop reordering."""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Dict, Any
from src.models.player import Player


class LineupTreeview(ttk.Frame):
    """Treeview-based lineup display with spreadsheet columns and drag-and-drop.

    Displays lineup in columns: #, Pos, Player, Typ, AVG, OBP, SLG, K%
    Supports drag-and-drop with INSERT behavior (not swap).
    """

    def __init__(self, parent, **kwargs):
        """Initialize LineupTreeview.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        # Internal lineup storage
        self._lineup: List[Optional[Player]] = [None] * 9

        # Configure grid weights
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Create treeview with columns
        columns = ('slot', 'position', 'name', 'typical_slot', 'avg', 'obp', 'slg', 'k_pct')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=9)

        # Configure column headings
        self.tree.heading('slot', text='#')
        self.tree.heading('position', text='Pos')
        self.tree.heading('name', text='Player')
        self.tree.heading('typical_slot', text='Typ')
        self.tree.heading('avg', text='AVG')
        self.tree.heading('obp', text='OBP')
        self.tree.heading('slg', text='SLG')
        self.tree.heading('k_pct', text='K%')

        # Configure column widths
        self.tree.column('slot', width=30, anchor='center', stretch=False)
        self.tree.column('position', width=50, anchor='center', stretch=False)
        self.tree.column('name', width=150, anchor='w', stretch=True)
        self.tree.column('typical_slot', width=40, anchor='center', stretch=False)
        self.tree.column('avg', width=60, anchor='center', stretch=False)
        self.tree.column('obp', width=60, anchor='center', stretch=False)
        self.tree.column('slg', width=60, anchor='center', stretch=False)
        self.tree.column('k_pct', width=60, anchor='center', stretch=False)

        # Grid the treeview
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Drag-and-drop state
        self._drag_start_index: Optional[int] = None
        self._drag_item: Optional[str] = None
        self._original_selection: Optional[tuple] = None

        # Bind drag-and-drop events
        self.tree.bind('<Button-1>', self._on_press)
        self.tree.bind('<B1-Motion>', self._on_motion)
        self.tree.bind('<ButtonRelease-1>', self._on_release)

        # Configure tag for empty slots (gray text)
        self.tree.tag_configure('empty', foreground='gray')

        # Initial display
        self._refresh()

    def _on_press(self, event):
        """Handle mouse press - start drag operation."""
        # Get the item under the cursor
        item = self.tree.identify_row(event.y)
        if item:
            # Store the item being dragged
            self._drag_item = item
            # Get the current index (slot number - 1)
            values = self.tree.item(item, 'values')
            if values:
                self._drag_start_index = int(values[0]) - 1
            # Store original selection
            self._original_selection = self.tree.selection()

    def _on_motion(self, event):
        """Handle mouse motion during drag."""
        if self._drag_item is None:
            return
        # Visual feedback could be added here (e.g., cursor change)
        # For now, the selection follows the mouse naturally

    def _on_release(self, event):
        """Handle mouse release - complete drag with INSERT behavior."""
        if self._drag_item is None or self._drag_start_index is None:
            self._reset_drag_state()
            return

        # Get the target item
        target_item = self.tree.identify_row(event.y)
        if not target_item or target_item == self._drag_item:
            self._reset_drag_state()
            return

        # Get target index
        target_values = self.tree.item(target_item, 'values')
        if not target_values:
            self._reset_drag_state()
            return

        target_index = int(target_values[0]) - 1
        source_index = self._drag_start_index

        if source_index != target_index:
            # INSERT behavior: remove from source, insert at target
            player = self._lineup[source_index]
            self._lineup.pop(source_index)
            self._lineup.insert(target_index, player)
            self._refresh()

        self._reset_drag_state()

    def _reset_drag_state(self):
        """Reset drag-and-drop state."""
        self._drag_start_index = None
        self._drag_item = None
        self._original_selection = None

    def _calculate_typical_slot(self, player: Player) -> int:
        """Calculate typical batting order position from games started data.

        Args:
            player: Player object

        Returns:
            Most common batting order slot (1-9), or 0 if no data
        """
        # Check if player has games_by_slot data (may not exist on all Player objects)
        games_by_slot = getattr(player, 'games_by_slot', None)
        if not games_by_slot:
            return 0
        return max(games_by_slot.keys(), key=lambda k: games_by_slot.get(k, 0))

    def _format_stat(self, value: Optional[float], is_k_pct: bool = False) -> str:
        """Format a stat value for display.

        Args:
            value: Stat value or None
            is_k_pct: True if formatting K% (percentage format)

        Returns:
            Formatted string
        """
        if value is None:
            return '--'
        if is_k_pct:
            return f"{value * 100:.1f}%"
        return f"{value:.3f}"

    def _refresh(self):
        """Refresh the treeview display."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add lineup items
        for i, player in enumerate(self._lineup):
            slot = i + 1
            if player is None:
                # Empty slot
                values = (
                    slot,
                    '',
                    '(empty)',
                    '--',
                    '--',
                    '--',
                    '--',
                    '--'
                )
                self.tree.insert('', 'end', values=values, tags=('empty',))
            else:
                # Filled slot
                pos = player.position.abbrev if player.position else ''
                typical = self._calculate_typical_slot(player)
                typical_str = str(typical) if typical > 0 else '--'
                values = (
                    slot,
                    pos,
                    player.name,
                    typical_str,
                    self._format_stat(player.ba),
                    self._format_stat(player.obp),
                    self._format_stat(player.slg),
                    self._format_stat(player.k_pct, is_k_pct=True)
                )
                self.tree.insert('', 'end', values=values)

    def set_lineup(self, lineup: List[Optional[Player]]):
        """Set the lineup.

        Args:
            lineup: List of 9 Player objects (or None for empty slots)
        """
        if len(lineup) != 9:
            raise ValueError("Lineup must have exactly 9 slots")
        self._lineup = lineup.copy()
        self._refresh()

    def get_lineup(self) -> List[Optional[Player]]:
        """Get current lineup.

        Returns:
            List of 9 Player objects (or None for empty slots)
        """
        return self._lineup.copy()

    def add_player(self, player: Player, slot: Optional[int] = None) -> bool:
        """Add a player to the lineup.

        Args:
            player: Player object to add
            slot: Specific slot (0-8), or None to add to first empty slot

        Returns:
            True if player was added, False otherwise
        """
        # Check if player already in lineup
        if player in self._lineup:
            return False

        if slot is not None:
            # Add to specific slot
            if 0 <= slot < 9:
                self._lineup[slot] = player
                self._refresh()
                return True
            return False
        else:
            # Find first empty slot
            try:
                idx = self._lineup.index(None)
                self._lineup[idx] = player
                self._refresh()
                return True
            except ValueError:
                # Lineup is full
                return False

    def remove_selected(self):
        """Remove the selected player from lineup."""
        selection = self.tree.selection()
        if not selection:
            return

        # Get the selected item
        item = selection[0]
        values = self.tree.item(item, 'values')
        if values:
            idx = int(values[0]) - 1
            self._lineup[idx] = None
            self._refresh()

    def clear_lineup(self):
        """Clear all players from lineup."""
        self._lineup = [None] * 9
        self._refresh()

    def get_selected_index(self) -> Optional[int]:
        """Get the index of the currently selected slot.

        Returns:
            Slot index (0-8) or None if nothing selected
        """
        selection = self.tree.selection()
        if not selection:
            return None
        item = selection[0]
        values = self.tree.item(item, 'values')
        if values:
            return int(values[0]) - 1
        return None

    def move_up(self):
        """Move selected player up in batting order (swap with previous)."""
        idx = self.get_selected_index()
        if idx is None or idx == 0:
            return

        # Swap with previous
        self._lineup[idx], self._lineup[idx - 1] = self._lineup[idx - 1], self._lineup[idx]
        self._refresh()

        # Reselect the moved item
        children = self.tree.get_children()
        if idx - 1 < len(children):
            self.tree.selection_set(children[idx - 1])

    def move_down(self):
        """Move selected player down in batting order (swap with next)."""
        idx = self.get_selected_index()
        if idx is None or idx == 8:
            return

        # Swap with next
        self._lineup[idx], self._lineup[idx + 1] = self._lineup[idx + 1], self._lineup[idx]
        self._refresh()

        # Reselect the moved item
        children = self.tree.get_children()
        if idx + 1 < len(children):
            self.tree.selection_set(children[idx + 1])
