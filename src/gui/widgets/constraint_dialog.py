"""Dialog for adding/editing lineup constraints."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
from src.models.player import Player


class ConstraintDialog(tk.Toplevel):
    """Dialog for creating lineup constraints."""

    def __init__(self, parent, players: List[Player], constraint: Optional[Dict] = None):
        """
        Initialize constraint dialog.

        Args:
            parent: Parent window
            players: List of available players
            constraint: Existing constraint to edit (None for new constraint)
        """
        super().__init__(parent)

        self.title("Add Lineup Constraint" if constraint is None else "Edit Lineup Constraint")
        self.transient(parent)
        self.grab_set()

        self.players = players
        self.player_names = [p.name for p in players]
        self.result: Optional[Dict[str, Any]] = None
        self.constraint_type = tk.StringVar(value='fixed_position')

        # Create widgets
        self._create_widgets(constraint)

        # Center on parent
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self, constraint: Optional[Dict]):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Constraint type selection
        ttk.Label(main_frame, text="Constraint Type:").grid(row=0, column=0, sticky='w', pady=5)

        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky='w', pady=5)

        ttk.Radiobutton(
            type_frame,
            text="Fixed Position (Player X always bats #N)",
            variable=self.constraint_type,
            value='fixed_position',
            command=self._on_type_change
        ).pack(anchor='w')

        ttk.Radiobutton(
            type_frame,
            text="Batting Order (Player Y always bats after Player X)",
            variable=self.constraint_type,
            value='batting_order',
            command=self._on_type_change
        ).pack(anchor='w')

        ttk.Radiobutton(
            type_frame,
            text="Platoon (Alternate players A and B at position #N)",
            variable=self.constraint_type,
            value='platoon',
            command=self._on_type_change
        ).pack(anchor='w')

        # Container for constraint-specific fields
        self.fields_frame = ttk.LabelFrame(main_frame, text="Constraint Details", padding=10)
        self.fields_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)

        # Set initial type if editing
        if constraint:
            self.constraint_type.set(constraint.get('type', 'fixed_position'))

        # Create initial fields
        self._on_type_change()

        # Set values if editing
        if constraint:
            self._set_constraint_values(constraint)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)

    def _on_type_change(self):
        """Handle constraint type change."""
        # Clear existing fields
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        constraint_type = self.constraint_type.get()

        if constraint_type == 'fixed_position':
            self._create_fixed_position_fields()
        elif constraint_type == 'batting_order':
            self._create_batting_order_fields()
        elif constraint_type == 'platoon':
            self._create_platoon_fields()

    def _create_fixed_position_fields(self):
        """Create fields for fixed position constraint."""
        ttk.Label(self.fields_frame, text="Player:").grid(row=0, column=0, sticky='w', pady=5)
        self.player_combo = ttk.Combobox(self.fields_frame, values=self.player_names, state='readonly', width=25)
        self.player_combo.grid(row=0, column=1, sticky='w', pady=5)
        if self.player_names:
            self.player_combo.current(0)

        ttk.Label(self.fields_frame, text="Position (#1-9):").grid(row=1, column=0, sticky='w', pady=5)
        self.position_spin = ttk.Spinbox(self.fields_frame, from_=1, to=9, width=10)
        self.position_spin.set(1)
        self.position_spin.grid(row=1, column=1, sticky='w', pady=5)

    def _create_batting_order_fields(self):
        """Create fields for batting order constraint."""
        ttk.Label(self.fields_frame, text="Player (bats first):").grid(row=0, column=0, sticky='w', pady=5)
        self.player1_combo = ttk.Combobox(self.fields_frame, values=self.player_names, state='readonly', width=25)
        self.player1_combo.grid(row=0, column=1, sticky='w', pady=5)
        if self.player_names:
            self.player1_combo.current(0)

        ttk.Label(self.fields_frame, text="Player (bats after):").grid(row=1, column=0, sticky='w', pady=5)
        self.player2_combo = ttk.Combobox(self.fields_frame, values=self.player_names, state='readonly', width=25)
        self.player2_combo.grid(row=1, column=1, sticky='w', pady=5)
        if len(self.player_names) > 1:
            self.player2_combo.current(1)

    def _create_platoon_fields(self):
        """Create fields for platoon constraint."""
        ttk.Label(self.fields_frame, text="Player A:").grid(row=0, column=0, sticky='w', pady=5)
        self.player_a_combo = ttk.Combobox(self.fields_frame, values=self.player_names, state='readonly', width=25)
        self.player_a_combo.grid(row=0, column=1, sticky='w', pady=5)
        if self.player_names:
            self.player_a_combo.current(0)

        ttk.Label(self.fields_frame, text="Player B:").grid(row=1, column=0, sticky='w', pady=5)
        self.player_b_combo = ttk.Combobox(self.fields_frame, values=self.player_names, state='readonly', width=25)
        self.player_b_combo.grid(row=1, column=1, sticky='w', pady=5)
        if len(self.player_names) > 1:
            self.player_b_combo.current(1)

        ttk.Label(self.fields_frame, text="Position (#1-9):").grid(row=2, column=0, sticky='w', pady=5)
        self.position_spin = ttk.Spinbox(self.fields_frame, from_=1, to=9, width=10)
        self.position_spin.set(1)
        self.position_spin.grid(row=2, column=1, sticky='w', pady=5)

    def _set_constraint_values(self, constraint: Dict):
        """Set field values from existing constraint."""
        constraint_type = constraint.get('type')

        if constraint_type == 'fixed_position':
            player = constraint.get('player')
            position = constraint.get('position')
            if player and player in self.player_names:
                self.player_combo.set(player)
            if position:
                self.position_spin.set(position)

        elif constraint_type == 'batting_order':
            player1 = constraint.get('player1')
            player2 = constraint.get('player2')
            if player1 and player1 in self.player_names:
                self.player1_combo.set(player1)
            if player2 and player2 in self.player_names:
                self.player2_combo.set(player2)

        elif constraint_type == 'platoon':
            player_a = constraint.get('player_a')
            player_b = constraint.get('player_b')
            position = constraint.get('position')
            if player_a and player_a in self.player_names:
                self.player_a_combo.set(player_a)
            if player_b and player_b in self.player_names:
                self.player_b_combo.set(player_b)
            if position:
                self.position_spin.set(position)

    def _on_ok(self):
        """Handle OK button."""
        constraint_type = self.constraint_type.get()

        if constraint_type == 'fixed_position':
            self.result = {
                'type': 'fixed_position',
                'player': self.player_combo.get(),
                'position': int(self.position_spin.get())
            }
        elif constraint_type == 'batting_order':
            self.result = {
                'type': 'batting_order',
                'player1': self.player1_combo.get(),
                'player2': self.player2_combo.get()
            }
        elif constraint_type == 'platoon':
            self.result = {
                'type': 'platoon',
                'player_a': self.player_a_combo.get(),
                'player_b': self.player_b_combo.get(),
                'position': int(self.position_spin.get())
            }

        self.destroy()

    def _on_cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.destroy()

    def get_result(self) -> Optional[Dict[str, Any]]:
        """
        Get the constraint result.

        Returns:
            Constraint dict, or None if cancelled
        """
        return self.result
