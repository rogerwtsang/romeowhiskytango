# ============================================================================
# src/gui/widgets/collapsible_frame.py
# ============================================================================
"""Collapsible frame widget with toggle button for expanding/collapsing content."""

import tkinter as tk
from tkinter import ttk


class CollapsibleFrame(ttk.Frame):
    """Frame with collapsible content section.

    Provides a header with toggle button and content area that can be shown/hidden.
    Uses pack_forget() to hide content and pack() to show it. Toggle button shows
    visual indicator (▼ when expanded, ▶ when collapsed).

    Usage:
        frame = CollapsibleFrame(parent, text="Setup")
        content = frame.get_content_frame()
        # Add widgets to content frame
        ttk.Label(content, text="Content").pack()
    """

    def __init__(self, parent, text: str = "", **kwargs):
        """
        Initialize collapsible frame.

        Args:
            parent: Parent widget
            text: Section title displayed in header
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.collapsed = False
        self._text = text

        # Header with toggle button
        self.header = ttk.Frame(self, relief=tk.RAISED, borderwidth=1)
        self.header.pack(fill=tk.X, pady=(0, 2))

        self.toggle_btn = ttk.Button(
            self.header,
            text=f"▼ {text}",
            command=self.toggle,
            width=20
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5, pady=2)

        # Content frame
        self.content = ttk.Frame(self, padding=10, relief=tk.SUNKEN, borderwidth=1)
        self.content.pack(fill=tk.BOTH, expand=True)

    def toggle(self) -> None:
        """Toggle content visibility.

        When collapsed, hides content using pack_forget() and changes arrow to ▶.
        When expanded, shows content using pack() and changes arrow to ▼.
        """
        if self.collapsed:
            # Expand
            self.content.pack(fill=tk.BOTH, expand=True)
            # Use direct button config to avoid StringVar memory leak (RESEARCH.md Pitfall 2)
            self.toggle_btn.config(text=f"▼ {self._text}")
        else:
            # Collapse
            self.content.pack_forget()
            self.toggle_btn.config(text=f"▶ {self._text}")

        self.collapsed = not self.collapsed

    def get_content_frame(self) -> ttk.Frame:
        """Get the content frame for adding widgets.

        Returns:
            Content frame where child widgets should be added
        """
        return self.content
