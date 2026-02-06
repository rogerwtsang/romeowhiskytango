#!/usr/bin/env python3
"""
Monte Carlo Baseball Simulator - GUI Application

Main entry point for the Tkinter-based GUI application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.dashboard import MainDashboard
from src.gui.utils import SimulationRunner, ConfigManager, ResultsManager
from src.gui.themes import apply_dark_triadic_theme


class MonteCarloBaseballGUI:
    """Main GUI application for Monte Carlo Baseball Simulator."""

    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Monte Carlo Baseball Simulator")
        self.root.geometry("1200x800")

        # Initialize managers
        self.sim_runner = SimulationRunner()
        self.config_manager = ConfigManager()
        self.results_manager = ResultsManager(max_results=10)

        # Create UI
        self._create_menu()
        self._create_dashboard()
        self._create_status_bar()

        # Load last configuration
        self._load_last_config()

    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self._save_config)
        file_menu.add_command(label="Load Configuration", command=self._load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _create_dashboard(self):
        """Create main dashboard UI."""
        # Create dashboard
        self.dashboard = MainDashboard(
            self.root,
            config_manager=self.config_manager,
            results_manager=self.results_manager,
            sim_runner=self.sim_runner
        )
        self.dashboard.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def _save_config(self):
        """Save current GUI configuration."""
        # Get dashboard state
        state = self.dashboard.get_dashboard_state()

        if self.config_manager.save_gui_config(state):
            messagebox.showinfo("Success", "Configuration saved successfully")
        else:
            messagebox.showerror("Error", "Failed to save configuration")

    def _load_config(self):
        """Load GUI configuration."""
        config = self.config_manager.load_gui_config()
        if not config:
            messagebox.showinfo("No Config", "No saved configuration found")
            return

        # Note: This would require implementing set_config methods for all tabs
        messagebox.showinfo("Info", "Configuration loading not yet implemented")

    def _load_last_config(self):
        """Load last used configuration on startup."""
        config = self.config_manager.load_gui_config()
        # Could load saved config here, but for now we use defaults

    def _show_about(self):
        """Show about dialog."""
        about_text = """Monte Carlo Baseball Simulator

Version 0.4.0 (Sprint 2 Complete)

A sophisticated Monte Carlo simulation tool for baseball
lineup optimization and season analysis.

New in 0.4.0:
• Compare Tab for side-by-side lineup analysis
• Summary cards with baseline comparison
• Distribution and box plot visualizations
• Effect size analysis (Cohen's d)

Previous:
• Results Manager for storing simulations
• Model validation (1.6% error vs MLB data)

Built with Python and Tkinter."""

        messagebox.showinfo("About", about_text)

    def _on_exit(self):
        """Handle application exit."""
        if self.sim_runner.is_running():
            if messagebox.askyesno("Confirm Exit", "Simulation is running. Exit anyway?"):
                self.sim_runner.stop()
                self.root.quit()
        else:
            self.root.quit()


def main():
    """Main entry point."""
    root = tk.Tk()

    # Apply dark triadic theme
    apply_dark_triadic_theme(root)

    # Create and run application
    app = MonteCarloBaseballGUI(root)

    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app._on_exit)

    root.mainloop()


if __name__ == "__main__":
    main()
