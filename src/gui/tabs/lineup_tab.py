"""Tab for lineup management with constraints."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import List, Optional
import pandas as pd
from src.models.player import Player
from src.gui.widgets import PlayerList, LineupBuilder, ConstraintDialog
from src.gui.utils import ConstraintValidator, ConfigManager


class LineupTab(ttk.Frame):
    """Tab for lineup management."""

    def __init__(self, parent, **kwargs):
        """Initialize lineup tab."""
        super().__init__(parent, **kwargs)

        self.roster: List[Player] = []
        self.roster_df: Optional[pd.DataFrame] = None
        self.constraints: List[dict] = []
        self.config_manager = ConfigManager()

        self._create_widgets()

    def _create_widgets(self):
        """Create tab widgets."""
        # Main container
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top section: Player list and lineup builder
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Left: Available players
        left_frame = ttk.LabelFrame(top_frame, text="Available Players", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Min PA filter
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(filter_frame, text="Min PA:").pack(side=tk.LEFT, padx=(0, 5))
        self.min_pa_var = tk.IntVar(value=100)
        self.min_pa_spin = ttk.Spinbox(filter_frame, from_=0, to=600, width=8, textvariable=self.min_pa_var)
        self.min_pa_spin.pack(side=tk.LEFT)
        ttk.Button(filter_frame, text="Apply Filter", command=self._apply_filter).pack(side=tk.LEFT, padx=(5, 0))

        # Player list
        self.player_list = PlayerList(left_frame)
        self.player_list.pack(fill=tk.BOTH, expand=True)

        # Middle: Add button
        mid_frame = ttk.Frame(top_frame)
        mid_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(mid_frame, text="Add →", command=self._add_to_lineup, width=10).pack(pady=5)

        # Right: Lineup builder
        right_frame = ttk.LabelFrame(top_frame, text="Batting Order (9 slots)", padding=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.lineup_builder = LineupBuilder(right_frame)
        self.lineup_builder.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Auto-order controls
        auto_frame = ttk.Frame(right_frame)
        auto_frame.pack(fill=tk.X)

        ttk.Label(auto_frame, text="Auto-order by:").pack(side=tk.LEFT, padx=(0, 5))
        self.order_stat_var = tk.StringVar(value='ops')
        stat_combo = ttk.Combobox(
            auto_frame,
            textvariable=self.order_stat_var,
            values=['ops', 'obp', 'slg', 'ba', 'iso'],
            state='readonly',
            width=8
        )
        stat_combo.pack(side=tk.LEFT)
        ttk.Button(auto_frame, text="Apply", command=self._auto_order).pack(side=tk.LEFT, padx=(5, 0))

        # Bottom section: Save/Load lineup
        save_frame = ttk.Frame(right_frame)
        save_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(save_frame, text="Save Lineup", command=self._save_lineup, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(save_frame, text="Load Lineup", command=self._load_lineup, width=12).pack(side=tk.LEFT)

        # Constraints section
        constraints_frame = ttk.LabelFrame(main_frame, text="Lineup Rules & Constraints", padding=10)
        constraints_frame.pack(fill=tk.BOTH, expand=True)

        # Constraints list
        list_frame = ttk.Frame(constraints_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.constraints_listbox = tk.Listbox(list_frame, height=4)
        self.constraints_listbox.pack(fill=tk.BOTH, expand=True)

        # Constraints buttons
        btn_frame = ttk.Frame(constraints_frame)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Button(btn_frame, text="Add Rule", command=self._add_constraint, width=12).pack(pady=2)
        ttk.Button(btn_frame, text="Edit Rule", command=self._edit_constraint, width=12).pack(pady=2)
        ttk.Button(btn_frame, text="Remove Rule", command=self._remove_constraint, width=12).pack(pady=2)
        ttk.Button(btn_frame, text="Clear All", command=self._clear_constraints, width=12).pack(pady=2)

    def load_data(self, roster: List[Player], roster_df: pd.DataFrame):
        """
        Load player data.

        Args:
            roster: List of Player objects
            roster_df: DataFrame of player stats
        """
        self.roster = roster
        self.roster_df = roster_df
        self._apply_filter()

    def _apply_filter(self):
        """Apply PA filter to player list."""
        if not self.roster:
            return

        min_pa = self.min_pa_var.get()
        filtered = [p for p in self.roster if p.pa >= min_pa]
        self.player_list.load_players(filtered)

    def _add_to_lineup(self):
        """Add selected player to lineup."""
        player = self.player_list.get_selected()
        if player is None:
            messagebox.showwarning("No Selection", "Please select a player to add")
            return

        if not self.lineup_builder.add_player(player):
            messagebox.showwarning("Cannot Add", "Player is already in lineup or lineup is full")

    def _auto_order(self):
        """Auto-order lineup by selected statistic."""
        if not self.roster:
            messagebox.showwarning("No Data", "Please load team data first")
            return

        stat = self.order_stat_var.get()

        # Get top 9 players by stat
        if stat == 'ops':
            sorted_players = sorted(self.roster, key=lambda p: p.obp + p.slg, reverse=True)
        elif stat == 'obp':
            sorted_players = sorted(self.roster, key=lambda p: p.obp, reverse=True)
        elif stat == 'slg':
            sorted_players = sorted(self.roster, key=lambda p: p.slg, reverse=True)
        elif stat == 'ba':
            sorted_players = sorted(self.roster, key=lambda p: p.ba, reverse=True)
        elif stat == 'iso':
            sorted_players = sorted(self.roster, key=lambda p: p.iso, reverse=True)
        else:
            sorted_players = self.roster

        # Take top 9
        top_9 = sorted_players[:9]

        # Apply constraints
        if self.constraints:
            # Create temporary lineup with player names
            temp_lineup = [p.name for p in top_9]
            roster_names = [p.name for p in self.roster]
            validated = ConstraintValidator.apply_constraints(self.constraints, temp_lineup, roster_names)

            # Convert back to Player objects
            lineup = []
            for name in validated:
                if name is None:
                    lineup.append(None)
                else:
                    # Find player by name
                    player = next((p for p in self.roster if p.name == name), None)
                    lineup.append(player)

            # Fill empty slots with remaining players
            used = {p.name for p in lineup if p is not None}
            remaining = [p for p in sorted_players if p.name not in used]
            for i in range(9):
                if lineup[i] is None and remaining:
                    lineup[i] = remaining.pop(0)
        else:
            lineup = top_9

        self.lineup_builder.set_lineup(lineup)

    def _save_lineup(self):
        """Save current lineup as preset."""
        lineup = self.lineup_builder.get_lineup()
        if not lineup or not all(lineup):
            messagebox.showwarning("Incomplete Lineup", "Please fill all 9 lineup slots before saving")
            return

        name = simpledialog.askstring("Save Lineup", "Enter lineup name:")
        if not name:
            return

        # Save lineup data
        lineup_data = {
            'lineup': [p.name if p else None for p in lineup],
            'constraints': self.constraints
        }

        if self.config_manager.save_lineup(name, lineup_data):
            messagebox.showinfo("Success", f"Lineup '{name}' saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save lineup")

    def _load_lineup(self):
        """Load a saved lineup preset."""
        lineups = self.config_manager.list_lineups()
        if not lineups:
            messagebox.showinfo("No Lineups", "No saved lineups found")
            return

        # Create selection dialog
        dialog = tk.Toplevel(self)
        dialog.title("Load Lineup")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Select lineup:").pack(padx=10, pady=5)

        listbox = tk.Listbox(dialog, height=10)
        listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        for lineup_name in lineups:
            listbox.insert(tk.END, lineup_name)

        def on_ok():
            selection = listbox.curselection()
            if not selection:
                return

            name = listbox.get(selection[0])
            data = self.config_manager.load_lineup(name)

            if data:
                # Load constraints
                self.constraints = data.get('constraints', [])
                self._refresh_constraints_list()

                # Load lineup
                player_names = data.get('lineup', [])
                lineup = []
                for name in player_names:
                    if name is None:
                        lineup.append(None)
                    else:
                        player = next((p for p in self.roster if p.name == name), None)
                        lineup.append(player)

                self.lineup_builder.set_lineup(lineup)
                self.lineup_builder.apply_constraints(self.constraints)

                messagebox.showinfo("Success", "Lineup loaded successfully")

            dialog.destroy()

        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack(pady=5)

    def _add_constraint(self):
        """Add a new constraint."""
        if not self.roster:
            messagebox.showwarning("No Data", "Please load team data first")
            return

        dialog = ConstraintDialog(self, self.roster)
        self.wait_window(dialog)

        result = dialog.get_result()
        if result:
            self.constraints.append(result)
            self._refresh_constraints_list()
            self.lineup_builder.apply_constraints(self.constraints)

    def _edit_constraint(self):
        """Edit selected constraint."""
        selection = self.constraints_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a constraint to edit")
            return

        idx = selection[0]
        constraint = self.constraints[idx]

        dialog = ConstraintDialog(self, self.roster, constraint)
        self.wait_window(dialog)

        result = dialog.get_result()
        if result:
            self.constraints[idx] = result
            self._refresh_constraints_list()
            self.lineup_builder.apply_constraints(self.constraints)

    def _remove_constraint(self):
        """Remove selected constraint."""
        selection = self.constraints_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a constraint to remove")
            return

        idx = selection[0]
        self.constraints.pop(idx)
        self._refresh_constraints_list()
        self.lineup_builder.apply_constraints(self.constraints)

    def _clear_constraints(self):
        """Clear all constraints."""
        if self.constraints and messagebox.askyesno("Confirm", "Remove all constraints?"):
            self.constraints.clear()
            self._refresh_constraints_list()
            self.lineup_builder.apply_constraints(self.constraints)

    def _refresh_constraints_list(self):
        """Refresh constraints listbox."""
        self.constraints_listbox.delete(0, tk.END)
        for constraint in self.constraints:
            desc = ConstraintValidator.get_constraint_description(constraint)
            self.constraints_listbox.insert(tk.END, desc)

    def get_lineup(self) -> List[Optional[Player]]:
        """Get current lineup."""
        return self.lineup_builder.get_lineup()

    def validate_lineup(self) -> tuple:
        """
        Validate current lineup against constraints.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        lineup = self.lineup_builder.get_lineup()
        if not all(lineup):
            return False, ["Lineup must have all 9 positions filled"]

        lineup_names = [p.name for p in lineup]
        roster_names = [p.name for p in self.roster]

        return ConstraintValidator.validate_all_constraints(self.constraints, lineup_names, roster_names)
