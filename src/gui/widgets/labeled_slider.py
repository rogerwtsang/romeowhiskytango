"""Labeled slider widget with entry field for precise input."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class LabeledSlider(ttk.Frame):
    """Slider with label and entry field for value display/input."""

    def __init__(
        self,
        parent,
        label: str,
        from_: float,
        to: float,
        initial: float,
        resolution: float = 1.0,
        format_str: str = "{:.0f}",
        command: Optional[Callable] = None,
        **kwargs
    ):
        """
        Initialize labeled slider.

        Args:
            parent: Parent widget
            label: Label text
            from_: Minimum value
            to: Maximum value
            initial: Initial value
            resolution: Step size
            format_str: Format string for displaying value (e.g., "{:.2f}" for 2 decimals)
            command: Callback function called when value changes
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.from_ = from_
        self.to = to
        self.resolution = resolution
        self.format_str = format_str
        self.command = command

        # Create variable
        self.var = tk.DoubleVar(value=initial)

        # Create label
        self.label = ttk.Label(self, text=label)
        self.label.grid(row=0, column=0, sticky='w', padx=(0, 10))

        # Create slider
        self.slider = ttk.Scale(
            self,
            from_=from_,
            to=to,
            variable=self.var,
            orient='horizontal',
            command=self._on_slider_change
        )
        self.slider.grid(row=0, column=1, sticky='ew', padx=5)

        # Create entry field
        self.entry_var = tk.StringVar(value=self.format_str.format(initial))
        self.entry = ttk.Entry(self, textvariable=self.entry_var, width=10)
        self.entry.grid(row=0, column=2, padx=(5, 0))
        self.entry.bind('<Return>', self._on_entry_change)
        self.entry.bind('<FocusOut>', self._on_entry_change)

        # Configure column weights
        self.columnconfigure(1, weight=1)

    def _on_slider_change(self, value):
        """Handle slider value change."""
        float_val = float(value)
        # Round to resolution
        float_val = round(float_val / self.resolution) * self.resolution
        # Clamp to range
        float_val = max(self.from_, min(self.to, float_val))

        self.var.set(float_val)
        self.entry_var.set(self.format_str.format(float_val))

        if self.command:
            self.command(float_val)

    def _on_entry_change(self, event=None):
        """Handle entry field value change."""
        try:
            value = float(self.entry_var.get())
            # Clamp to range
            value = max(self.from_, min(self.to, value))
            # Round to resolution
            value = round(value / self.resolution) * self.resolution

            self.var.set(value)
            self.entry_var.set(self.format_str.format(value))

            if self.command:
                self.command(value)
        except ValueError:
            # Invalid input - reset to current value
            self.entry_var.set(self.format_str.format(self.var.get()))

    def get(self) -> float:
        """Get current value."""
        return self.var.get()

    def set(self, value: float):
        """Set value."""
        value = max(self.from_, min(self.to, value))
        self.var.set(value)
        self.entry_var.set(self.format_str.format(value))

    def configure_command(self, command: Callable):
        """Set command callback."""
        self.command = command
