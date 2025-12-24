"""Threading wrapper for running simulations without freezing the GUI."""

import threading
import queue
import time
from typing import List, Dict, Any, Callable, Optional
import config
from src.models.player import Player
from src.simulation.batch import run_simulations


class SimulationRunner:
    """Manages simulation execution in a separate thread."""

    def __init__(self):
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def run_in_thread(
        self,
        lineup: List[Player],
        config_overrides: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None,
        complete_callback: Optional[Callable[[Dict], None]] = None
    ):
        """
        Start simulation in a background thread.

        Args:
            lineup: List of 9 Player objects
            config_overrides: Dict of config parameters to override
            progress_callback: Called with (current, total) on progress updates
            complete_callback: Called with results dict when complete
        """
        self.stop_flag.clear()
        self.thread = threading.Thread(
            target=self._run_simulation,
            args=(lineup, config_overrides, progress_callback, complete_callback),
            daemon=True
        )
        self.thread.start()

    def _run_simulation(
        self,
        lineup: List[Player],
        config_overrides: Dict[str, Any],
        progress_callback: Optional[Callable],
        complete_callback: Optional[Callable]
    ):
        """Worker thread that runs the simulation."""
        try:
            # Save original config values
            original_values = {}
            for key, value in config_overrides.items():
                if hasattr(config, key):
                    original_values[key] = getattr(config, key)
                    setattr(config, key, value)

            # Define progress callback wrapper
            def progress_wrapper(current: int, total: int):
                if self.stop_flag.is_set():
                    raise InterruptedError("Simulation stopped by user")
                if progress_callback:
                    progress_callback(current, total)

            try:
                # Run simulation with progress callback
                results = run_simulations(
                    lineup=lineup,
                    n_iterations=config_overrides.get('n_iterations', config.N_SIMULATIONS),
                    n_games=config_overrides.get('n_games', config.N_GAMES_PER_SEASON),
                    random_seed=config_overrides.get('random_seed', config.RANDOM_SEED),
                    verbose=config_overrides.get('verbosity', config.VERBOSITY),
                    progress_callback=progress_wrapper
                )

                # Send results to callback
                if complete_callback and not self.stop_flag.is_set():
                    complete_callback(results)

            except InterruptedError:
                # Simulation was stopped - send None to indicate interruption
                if complete_callback:
                    complete_callback(None)

            finally:
                # Restore original config values
                for key, value in original_values.items():
                    setattr(config, key, value)

        except Exception as e:
            # Send error to callback
            if complete_callback:
                complete_callback({'error': str(e)})

    def stop(self):
        """Stop the running simulation."""
        self.stop_flag.set()

    def is_running(self) -> bool:
        """Check if a simulation is currently running."""
        return self.thread is not None and self.thread.is_alive()
