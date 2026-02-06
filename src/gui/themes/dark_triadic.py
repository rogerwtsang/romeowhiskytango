# ============================================================================
# src/gui/themes/dark_triadic.py
# ============================================================================
"""Dark triadic color theme for GUI dashboard.

Implements a darker color scheme with triadic color harmony (teal, orange, purple)
for improved visual appeal and reduced eye strain during extended use.

Color Palette:
    - Background: Dark charcoal (#1a1a1a, #2a2a2a)
    - Primary: Deep teal (#00897b) - data visualization, key metrics
    - Secondary: Burnt orange (#d84315) - warnings, highlights
    - Accent: Royal purple (#6a1b9a) - interactive elements
    - Text: Light gray (#e0e0e0) for readability
    - Subtle borders: Mid-gray (#404040)
"""

import tkinter as tk
from tkinter import ttk


# Color constants
COLORS = {
    # Backgrounds
    'bg_darkest': '#1a1a1a',      # Main background
    'bg_dark': '#2a2a2a',         # Panel backgrounds
    'bg_medium': '#3a3a3a',       # Raised elements (frames, buttons)
    'bg_light': '#4a4a4a',        # Hover states

    # Triadic colors
    'primary': '#00897b',         # Deep teal (primary actions, charts)
    'primary_hover': '#00b09f',   # Lighter teal (hover)
    'secondary': '#d84315',       # Burnt orange (warnings, secondary actions)
    'secondary_hover': '#ff6e40', # Lighter orange
    'accent': '#6a1b9a',          # Royal purple (accents, highlights)
    'accent_hover': '#8e24aa',    # Lighter purple

    # Text colors
    'text_primary': '#e0e0e0',    # Main text
    'text_secondary': '#b0b0b0',  # Secondary text
    'text_disabled': '#707070',   # Disabled text
    'text_inverted': '#ffffff',   # Text on colored backgrounds

    # UI elements
    'border': '#404040',          # Borders, separators
    'border_light': '#505050',    # Lighter borders
    'focus': '#00897b',           # Focus indicator (primary teal)
    'selection': '#00897b',       # Selection color
    'success': '#4caf50',         # Success indicators
    'warning': '#d84315',         # Warning indicators (secondary orange)
    'error': '#f44336',           # Error indicators
}


def apply_dark_triadic_theme(root: tk.Tk) -> None:
    """
    Apply dark triadic theme to tkinter application.

    Configures ttk styles for all common widgets (Frame, Label, Button, etc.)
    using the dark triadic color palette.

    Args:
        root: Root Tk window
    """
    style = ttk.Style(root)

    # Set theme base (may vary by platform)
    try:
        style.theme_use('clam')  # Works well for custom colors
    except:
        pass  # Fall back to default theme

    # Configure main window background
    root.configure(bg=COLORS['bg_darkest'])

    # Frame styles
    style.configure(
        'TFrame',
        background=COLORS['bg_dark'],
        bordercolor=COLORS['border'],
        borderwidth=0
    )

    # LabelFrame styles
    style.configure(
        'TLabelframe',
        background=COLORS['bg_dark'],
        bordercolor=COLORS['border'],
        borderwidth=1,
        relief='solid'
    )
    style.configure(
        'TLabelframe.Label',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_primary'],
        font=('TkDefaultFont', 10, 'bold')
    )

    # Label styles
    style.configure(
        'TLabel',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_primary']
    )

    # Button styles
    style.configure(
        'TButton',
        background=COLORS['bg_medium'],
        foreground=COLORS['text_primary'],
        bordercolor=COLORS['border_light'],
        borderwidth=1,
        focuscolor=COLORS['focus'],
        lightcolor=COLORS['bg_medium'],
        darkcolor=COLORS['bg_dark']
    )
    style.map(
        'TButton',
        background=[('active', COLORS['bg_light']), ('disabled', COLORS['bg_dark'])],
        foreground=[('disabled', COLORS['text_disabled'])]
    )

    # Primary action button (for Run Simulation, etc.)
    style.configure(
        'Primary.TButton',
        background=COLORS['primary'],
        foreground=COLORS['text_inverted'],
        borderwidth=0
    )
    style.map(
        'Primary.TButton',
        background=[('active', COLORS['primary_hover']), ('disabled', COLORS['bg_dark'])],
        foreground=[('disabled', COLORS['text_disabled'])]
    )

    # Entry styles
    style.configure(
        'TEntry',
        fieldbackground=COLORS['bg_medium'],
        foreground=COLORS['text_primary'],
        bordercolor=COLORS['border'],
        insertcolor=COLORS['text_primary'],
        selectbackground=COLORS['selection'],
        selectforeground=COLORS['text_inverted']
    )
    style.map(
        'TEntry',
        fieldbackground=[('readonly', COLORS['bg_dark']), ('disabled', COLORS['bg_dark'])],
        foreground=[('disabled', COLORS['text_disabled'])]
    )

    # Combobox styles
    style.configure(
        'TCombobox',
        fieldbackground=COLORS['bg_medium'],
        background=COLORS['bg_medium'],
        foreground=COLORS['text_primary'],
        bordercolor=COLORS['border'],
        arrowcolor=COLORS['text_primary'],
        selectbackground=COLORS['selection'],
        selectforeground=COLORS['text_inverted']
    )
    style.map(
        'TCombobox',
        fieldbackground=[('readonly', COLORS['bg_medium']), ('disabled', COLORS['bg_dark'])],
        foreground=[('disabled', COLORS['text_disabled'])]
    )

    # Checkbutton styles
    style.configure(
        'TCheckbutton',
        background=COLORS['bg_dark'],
        foreground=COLORS['text_primary'],
        indicatorcolor=COLORS['bg_medium'],
        bordercolor=COLORS['border']
    )
    style.map(
        'TCheckbutton',
        background=[('active', COLORS['bg_dark'])],
        foreground=[('disabled', COLORS['text_disabled'])]
    )

    # Progressbar styles
    style.configure(
        'TProgressbar',
        background=COLORS['primary'],
        troughcolor=COLORS['bg_medium'],
        bordercolor=COLORS['border'],
        lightcolor=COLORS['primary'],
        darkcolor=COLORS['primary']
    )

    # Notebook (tab) styles
    style.configure(
        'TNotebook',
        background=COLORS['bg_dark'],
        bordercolor=COLORS['border']
    )
    style.configure(
        'TNotebook.Tab',
        background=COLORS['bg_medium'],
        foreground=COLORS['text_secondary'],
        bordercolor=COLORS['border'],
        padding=[10, 5]
    )
    style.map(
        'TNotebook.Tab',
        background=[('selected', COLORS['bg_dark']), ('active', COLORS['bg_light'])],
        foreground=[('selected', COLORS['primary']), ('active', COLORS['text_primary'])]
    )

    # PanedWindow styles
    style.configure(
        'TPanedwindow',
        background=COLORS['bg_dark']
    )

    # Separator styles
    style.configure(
        'TSeparator',
        background=COLORS['border']
    )

    # Scrollbar styles
    style.configure(
        'Vertical.TScrollbar',
        background=COLORS['bg_medium'],
        troughcolor=COLORS['bg_dark'],
        bordercolor=COLORS['border'],
        arrowcolor=COLORS['text_secondary']
    )
    style.map(
        'Vertical.TScrollbar',
        background=[('active', COLORS['bg_light'])]
    )

    style.configure(
        'Horizontal.TScrollbar',
        background=COLORS['bg_medium'],
        troughcolor=COLORS['bg_dark'],
        bordercolor=COLORS['border'],
        arrowcolor=COLORS['text_secondary']
    )
    style.map(
        'Horizontal.TScrollbar',
        background=[('active', COLORS['bg_light'])]
    )
