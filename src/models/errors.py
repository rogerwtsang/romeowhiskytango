# ============================================================================
# src/models/errors.py
# ============================================================================
"""Errors and wild pitches logic."""

from typing import Tuple
import numpy as np
from src.models.baserunning import BasesState
import config


def check_error_advances_runner(
    bases: BasesState,
    rng: np.random.RandomState
) -> Tuple[BasesState, int]:
    """Check if error/wild pitch advances runners.

    Occurs during PA, advances runners similar to a wild pitch or passed ball.

    Args:
        bases: Current bases state
        rng: Random number generator

    Returns:
        Tuple of (bases_after, runs_scored)
    """
    if not config.ENABLE_ERRORS_WILD_PITCHES:
        return bases, 0

    # Check if error occurs
    if rng.random() > config.ERROR_RATE_PER_PA:
        return bases, 0

    # Error! Advance all runners one base
    runs_scored = 0
    bases_after = bases.copy()

    # Runner from 3rd scores
    if bases['third'] is not None:
        runs_scored = 1
        bases_after['third'] = bases['second']
    else:
        bases_after['third'] = bases['second']

    bases_after['second'] = bases['first']
    # Batter stays at plate (error occurs during PA)
    bases_after['first'] = None

    return bases_after, runs_scored
