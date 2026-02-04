# ============================================================================
# src/gui/widgets/optimization_preview.py
# ============================================================================
"""Optimization preview widgets for viewing and comparing lineup candidates."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.player import Player


class LineupRankingList(ttk.Frame):
    """
    Ranked list of lineup candidates ordered by expected runs.

    Displays top N lineups from optimizer with:
    - Rank number
    - Expected runs (mean)
    - Confidence interval
    - Expandable stat breakdown
    - Copy-to-panel button
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_copy: Optional[Callable[[List["Player"]], None]] = None,
        max_display: int = 10,
        **kwargs: Any,
    ):
        """
        Initialize the lineup ranking list.

        Args:
            parent: Parent widget
            on_copy: Callback when user clicks "Copy" (receives lineup list)
            max_display: Maximum candidates to show (default 10)
        """
        super().__init__(parent, **kwargs)
        self.on_copy = on_copy
        self.max_display = max_display
        self._candidates: List[Dict[str, Any]] = []
        self._row_frames: List[ttk.Frame] = []
        self._detail_frames: List[ttk.Frame] = []
        self._detail_visible: List[bool] = []
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create the widget layout."""
        # Header row
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(header, text="Rank", width=6, font=("TkDefaultFont", 9, "bold")).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Label(
            header, text="Expected Runs", width=14, font=("TkDefaultFont", 9, "bold")
        ).pack(side=tk.LEFT, padx=5)
        ttk.Label(header, text="95% CI", width=14, font=("TkDefaultFont", 9, "bold")).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Label(header, text="Actions", width=16, font=("TkDefaultFont", 9, "bold")).pack(
            side=tk.LEFT, padx=5
        )

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)

        # Scrollable container for candidate rows
        self._canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)

        self._scroll_frame = ttk.Frame(self._canvas)
        self._scroll_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )

        self._canvas.create_window((0, 0), window=self._scroll_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mousewheel for scrolling
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        # Empty state message
        self._empty_label = ttk.Label(
            self._scroll_frame,
            text="No candidates available",
            foreground="gray",
            font=("TkDefaultFont", 10, "italic"),
        )

    def set_candidates(self, candidates: List[Dict[str, Any]]) -> None:
        """
        Set lineup candidates to display.

        Args:
            candidates: List of dicts, each with:
                - lineup: List[Player]
                - expected_runs: float
                - ci_lower: float
                - ci_upper: float
                - stats: Dict (optional detailed stats)
        """
        # Clear existing rows
        for frame in self._row_frames:
            frame.destroy()
        for frame in self._detail_frames:
            frame.destroy()
        self._row_frames.clear()
        self._detail_frames.clear()
        self._detail_visible.clear()
        self._candidates = candidates[: self.max_display] if candidates else []

        # Hide empty label if we have candidates
        if self._candidates:
            self._empty_label.pack_forget()
        else:
            self._empty_label.pack(pady=20)
            return

        # Create rows for each candidate
        for rank, candidate in enumerate(self._candidates, start=1):
            row_frame, detail_frame = self._create_candidate_row(rank, candidate)
            self._row_frames.append(row_frame)
            self._detail_frames.append(detail_frame)
            self._detail_visible.append(False)

    def _create_candidate_row(
        self, rank: int, candidate: Dict[str, Any]
    ) -> tuple[ttk.Frame, ttk.Frame]:
        """
        Create a row for a single candidate.

        Args:
            rank: The candidate's rank (1-based)
            candidate: Candidate data dict

        Returns:
            Tuple of (summary_frame, detail_frame)
        """
        # Summary row
        row = ttk.Frame(self._scroll_frame)
        row.pack(fill=tk.X, padx=5, pady=2)

        expected_runs = candidate.get("expected_runs", 0)
        ci_lower = candidate.get("ci_lower", 0)
        ci_upper = candidate.get("ci_upper", 0)
        lineup = candidate.get("lineup", [])

        # Rank
        ttk.Label(row, text=f"#{rank}", width=6).pack(side=tk.LEFT, padx=(0, 5))

        # Expected runs
        ttk.Label(row, text=f"{expected_runs:.1f}", width=14).pack(side=tk.LEFT, padx=5)

        # CI
        ci_text = f"[{ci_lower:.0f}-{ci_upper:.0f}]"
        ttk.Label(row, text=ci_text, width=14).pack(side=tk.LEFT, padx=5)

        # Actions frame
        actions = ttk.Frame(row)
        actions.pack(side=tk.LEFT, padx=5)

        # Copy button - use helper to create callback with captured lineup
        def make_copy_callback(lineup_ref: List["Player"]) -> Callable[[], None]:
            return lambda: self._handle_copy(lineup_ref)

        copy_btn = ttk.Button(
            actions,
            text="Copy",
            width=6,
            command=make_copy_callback(lineup),
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Details toggle button - use helper to create callback with captured index
        idx = rank - 1  # Convert to 0-based index

        def make_toggle_callback(index: int) -> Callable[[], None]:
            return lambda: self._toggle_details(index)

        detail_btn = ttk.Button(
            actions,
            text="Details",
            width=7,
            command=make_toggle_callback(idx),
        )
        detail_btn.pack(side=tk.LEFT)

        # Detail frame (initially hidden)
        detail = ttk.Frame(self._scroll_frame, relief=tk.GROOVE, borderwidth=1)

        self._populate_detail_frame(detail, candidate)

        return row, detail

    def _populate_detail_frame(
        self, detail: ttk.Frame, candidate: Dict[str, Any]
    ) -> None:
        """
        Populate the detail frame with lineup and stats.

        Args:
            detail: The detail frame to populate
            candidate: Candidate data dict
        """
        lineup = candidate.get("lineup", [])
        stats = candidate.get("stats", {})

        # Lineup listing
        lineup_label = ttk.Label(detail, text="Lineup:", font=("TkDefaultFont", 9, "bold"))
        lineup_label.pack(anchor=tk.W, padx=10, pady=(5, 2))

        for slot, player in enumerate(lineup, start=1):
            player_name = getattr(player, "name", str(player))
            player_ba = getattr(player, "ba", 0)
            player_obp = getattr(player, "obp", 0)
            player_slg = getattr(player, "slg", 0)
            text = f"  {slot}. {player_name} ({player_ba:.3f}/{player_obp:.3f}/{player_slg:.3f})"
            ttk.Label(detail, text=text, font=("TkFixedFont", 9)).pack(
                anchor=tk.W, padx=10
            )

        # Additional stats if available
        if stats:
            ttk.Separator(detail, orient=tk.HORIZONTAL).pack(
                fill=tk.X, padx=10, pady=5
            )
            stats_label = ttk.Label(
                detail, text="Statistics:", font=("TkDefaultFont", 9, "bold")
            )
            stats_label.pack(anchor=tk.W, padx=10, pady=(0, 2))

            for key, value in stats.items():
                if isinstance(value, float):
                    text = f"  {key}: {value:.2f}"
                else:
                    text = f"  {key}: {value}"
                ttk.Label(detail, text=text, font=("TkFixedFont", 9)).pack(
                    anchor=tk.W, padx=10
                )

        # Add padding at bottom
        ttk.Frame(detail, height=5).pack()

    def _toggle_details(self, idx: int) -> None:
        """
        Toggle detail visibility for a candidate.

        Args:
            idx: Index of the candidate (0-based)
        """
        if idx >= len(self._detail_frames):
            return

        detail_frame = self._detail_frames[idx]
        row_frame = self._row_frames[idx]

        if self._detail_visible[idx]:
            # Hide details
            detail_frame.pack_forget()
            self._detail_visible[idx] = False
        else:
            # Show details (pack after the row)
            detail_frame.pack(fill=tk.X, padx=10, pady=(0, 5), after=row_frame)
            self._detail_visible[idx] = True

    def _handle_copy(self, lineup: List["Player"]) -> None:
        """
        Handle copy button click.

        Args:
            lineup: The lineup to copy
        """
        if self.on_copy:
            self.on_copy(lineup)


class LineupDiffView(ttk.Frame):
    """
    Shows text diff between two lineups.

    Format: "3<->4, 4<->3" for slot swaps
    or full listing for complex changes.
    """

    def __init__(self, parent: tk.Widget, **kwargs: Any):
        """
        Initialize the lineup diff view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent, **kwargs)
        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create the widget layout."""
        # Header frame with label and clear button
        header = ttk.Frame(self)
        header.pack(fill=tk.X, padx=5, pady=2)

        ttk.Label(header, text="Lineup Comparison", font=("TkDefaultFont", 10, "bold")).pack(
            side=tk.LEFT
        )

        clear_btn = ttk.Button(header, text="Clear", width=6, command=self.clear)
        clear_btn.pack(side=tk.RIGHT)

        # Text widget for diff display
        self._text = tk.Text(
            self,
            height=8,
            width=50,
            wrap=tk.WORD,
            font=("TkFixedFont", 9),
            state=tk.DISABLED,
            background="#f5f5f5",
        )
        self._text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure text tags for styling
        self._text.tag_configure("header", font=("TkDefaultFont", 9, "bold"))
        self._text.tag_configure("swap", foreground="#0066cc")
        self._text.tag_configure("added", foreground="#008800")
        self._text.tag_configure("removed", foreground="#cc0000")
        self._text.tag_configure("summary", font=("TkDefaultFont", 9, "italic"))

    def show_diff(
        self,
        lineup_a: List["Player"],
        lineup_b: List["Player"],
        label_a: str = "Current",
        label_b: str = "Proposed",
    ) -> None:
        """
        Display diff between two lineups.

        Shows:
        - Slot swaps in compact format (e.g., "3<->4")
        - Players added/removed
        - Summary of changes

        Args:
            lineup_a: First lineup (e.g., current)
            lineup_b: Second lineup (e.g., proposed)
            label_a: Label for first lineup
            label_b: Label for second lineup
        """
        diff_text = self._compute_diff(lineup_a, lineup_b, label_a, label_b)

        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, diff_text)
        self._text.config(state=tk.DISABLED)

    def _compute_diff(
        self,
        lineup_a: List["Player"],
        lineup_b: List["Player"],
        label_a: str,
        label_b: str,
    ) -> str:
        """
        Compute human-readable diff string.

        Args:
            lineup_a: First lineup
            lineup_b: Second lineup
            label_a: Label for first lineup
            label_b: Label for second lineup

        Returns:
            Formatted diff string
        """
        lines: List[str] = []

        # Get player names for comparison
        names_a = [getattr(p, "name", str(p)) for p in lineup_a]
        names_b = [getattr(p, "name", str(p)) for p in lineup_b]

        # Check for identical lineups
        if names_a == names_b:
            return "Lineups are identical."

        lines.append(f"{label_a} vs {label_b}")
        lines.append("=" * 40)
        lines.append("")

        # Find slot changes
        changes: List[str] = []
        swaps: List[tuple[int, int]] = []  # Track detected swaps
        processed_swaps: set[tuple[int, int]] = set()

        # Build position maps
        pos_a = {name: idx for idx, name in enumerate(names_a)}
        pos_b = {name: idx for idx, name in enumerate(names_b)}

        # Find players in different slots
        for slot, name_a in enumerate(names_a):
            if slot < len(names_b):
                name_b = names_b[slot]
                if name_a != name_b:
                    # Check if this is a simple swap
                    if name_a in pos_b and name_b in pos_a:
                        slot_of_a_in_b = pos_b[name_a]
                        slot_of_b_in_a = pos_a[name_b]
                        if slot_of_a_in_b == slot_of_b_in_a:
                            # It's a swap - create explicit tuple for type safety
                            min_slot = min(slot, slot_of_a_in_b)
                            max_slot = max(slot, slot_of_a_in_b)
                            swap_key: tuple[int, int] = (min_slot, max_slot)
                            if swap_key not in processed_swaps:
                                swaps.append((slot + 1, slot_of_a_in_b + 1))
                                processed_swaps.add(swap_key)
                        else:
                            changes.append(
                                f"Slot {slot + 1}: {name_a} -> {name_b}"
                            )
                    else:
                        changes.append(f"Slot {slot + 1}: {name_a} -> {name_b}")

        # Report swaps compactly
        if swaps:
            swap_strs = [f"{a}<->{b}" for a, b in swaps]
            lines.append(f"Swaps: {', '.join(swap_strs)}")
            lines.append("")

        # Report other changes
        if changes:
            lines.append("Slot Changes:")
            for change in changes:
                lines.append(f"  {change}")
            lines.append("")

        # Players only in A (removed)
        only_in_a = set(names_a) - set(names_b)
        if only_in_a:
            lines.append(f"Removed from {label_b}:")
            for name in only_in_a:
                lines.append(f"  - {name}")
            lines.append("")

        # Players only in B (added)
        only_in_b = set(names_b) - set(names_a)
        if only_in_b:
            lines.append(f"Added in {label_b}:")
            for name in only_in_b:
                lines.append(f"  + {name}")
            lines.append("")

        # Summary
        total_changes = len(swaps) + len(changes) + len(only_in_a) + len(only_in_b)
        lines.append(f"Total: {total_changes} change(s)")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear the diff display."""
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.config(state=tk.DISABLED)
