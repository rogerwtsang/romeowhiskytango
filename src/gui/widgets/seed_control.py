# ============================================================================
# src/gui/widgets/seed_control.py
# ============================================================================
"""Seed control widget with lock/unlock toggle for random seed management."""

import random
import tkinter as tk
from tkinter import ttk


class SeedControl(ttk.Frame):
    """Seed control widget with lock/unlock toggle and visual indicator.

    When unlocked (default): Entry is disabled (greyed out), seed randomizes on each
    get_seed() call (i.e., each simulation run).

    When locked: Entry is enabled (editable), seed remains fixed until user changes it.

    Attributes:
        locked: Boolean indicating whether seed is locked (fixed) or unlocked (randomized)
    """

    def __init__(self, parent, **kwargs):
        """
        Initialize seed control widget.

        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        # State: locked (editable, fixed) or unlocked (randomized each run)
        self.locked = False

        # Seed entry
        self.seed_entry = ttk.Entry(self, width=12)
        self.seed_entry.pack(side=tk.LEFT, padx=(0, 5))

        # Lock toggle button
        self.lock_btn = ttk.Button(self, text="Unlocked", width=8, command=self._toggle_lock)
        self.lock_btn.pack(side=tk.LEFT)

        # Generate initial random seed
        self._randomize_seed()

        # Apply initial state (unlocked = disabled entry)
        self._update_entry_state()

    def _toggle_lock(self) -> None:
        """Toggle between locked and unlocked states."""
        self.locked = not self.locked
        self._update_entry_state()
        if not self.locked:
            # Newly unlocked - randomize seed
            self._randomize_seed()

    def _update_entry_state(self) -> None:
        """Update entry widget state and button text based on locked state."""
        if self.locked:
            self.seed_entry.configure(state='normal')
            self.lock_btn.configure(text="Locked")
        else:
            self.seed_entry.configure(state='disabled')
            self.lock_btn.configure(text="Unlocked")

    def _randomize_seed(self) -> None:
        """Generate new random seed and update entry."""
        new_seed = random.randint(0, 2**31 - 1)
        # Temporarily enable entry to update value
        self.seed_entry.configure(state='normal')
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(new_seed))
        # Restore appropriate state
        if not self.locked:
            self.seed_entry.configure(state='disabled')

    def get_seed(self) -> int:
        """Get current seed value, randomizing first if unlocked.

        Returns:
            Current seed value as integer
        """
        if not self.locked:
            self._randomize_seed()
        return int(self.seed_entry.get())

    def is_locked(self) -> bool:
        """Check if seed is locked.

        Returns:
            True if seed is locked (fixed), False if unlocked (randomized)
        """
        return self.locked

    def set_seed(self, value: int) -> None:
        """Set seed value programmatically.

        Args:
            value: Seed value to set
        """
        self.seed_entry.configure(state='normal')
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(value))
        if not self.locked:
            self.seed_entry.configure(state='disabled')

    def set_locked(self, locked: bool) -> None:
        """Set locked state programmatically.

        Args:
            locked: True to lock, False to unlock
        """
        self.locked = locked
        self._update_entry_state()
