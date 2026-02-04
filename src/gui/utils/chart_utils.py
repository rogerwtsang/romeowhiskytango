# ============================================================================
# src/gui/utils/chart_utils.py
# ============================================================================
"""Reusable chart creation utilities for visualization.

Provides helper functions for creating standardized charts with consistent
styling. All functions accept matplotlib Axes objects and avoid global
state modifications.

Example:
    from src.gui.utils.chart_utils import create_histogram_with_kde

    fig, ax = plt.subplots()
    create_histogram_with_kde(ax, data, show_mean=True)
"""

from typing import Optional, Tuple, List
import numpy as np
from numpy.typing import ArrayLike
from matplotlib.axes import Axes
import seaborn as sns


def create_histogram_with_kde(
    ax: Axes,
    data: ArrayLike,
    color: str = 'steelblue',
    show_mean: bool = True,
    show_median: bool = True,
    title: Optional[str] = None,
    xlabel: str = 'Runs per Season',
    ylabel: str = 'Frequency',
    bins: int = 30,
    alpha: float = 0.7,
) -> None:
    """
    Create a histogram with KDE (kernel density estimate) overlay.

    Uses seaborn's histplot with kde=True for smooth distribution
    visualization. Adds optional mean/median vertical lines with labels.

    Args:
        ax: Matplotlib Axes object to plot on
        data: Array-like data for histogram
        color: Bar color (default: 'steelblue')
        show_mean: Whether to show vertical mean line (default: True)
        show_median: Whether to show vertical median line (default: True)
        title: Optional chart title
        xlabel: X-axis label (default: 'Runs per Season')
        ylabel: Y-axis label (default: 'Frequency')
        bins: Number of histogram bins (default: 30)
        alpha: Bar transparency (default: 0.7)

    Note:
        Does NOT call sns.set_theme() to avoid modifying global matplotlib
        state. The ax parameter is passed explicitly to seaborn.
    """
    # Convert to numpy array for consistent handling
    data_arr = np.asarray(data)

    if len(data_arr) == 0:
        ax.text(
            0.5, 0.5,
            'No data to display',
            ha='center',
            va='center',
            transform=ax.transAxes,
            fontsize=12,
            color='gray'
        )
        ax.set_xticks([])
        ax.set_yticks([])
        return

    # Create histogram with KDE overlay
    # Pass ax explicitly to avoid global state changes
    sns.histplot(
        data_arr,
        kde=True,
        ax=ax,
        bins=bins,
        alpha=alpha,
        color=color,
        edgecolor='black',
        linewidth=0.5,
    )

    # Calculate statistics
    mean_val = float(np.mean(data_arr))
    median_val = float(np.median(data_arr))

    # Add mean line
    if show_mean:
        ax.axvline(
            mean_val,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Mean: {mean_val:.1f}'
        )

    # Add median line
    if show_median:
        ax.axvline(
            median_val,
            color='green',
            linestyle=':',
            linewidth=2,
            label=f'Median: {median_val:.1f}'
        )

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    # Clip x-axis to 0 minimum (runs cannot be negative)
    ax.set_xlim(0, None)

    # Add legend if any lines were added
    if show_mean or show_median:
        ax.legend()

    # Add grid for readability
    ax.grid(True, alpha=0.3)


def create_comparison_overlay(
    ax: Axes,
    data1: ArrayLike,
    data2: ArrayLike,
    label1: str,
    label2: str,
    colors: Optional[Tuple[str, str]] = None,
    bins: int = 30,
    alpha: float = 0.5,
    title: Optional[str] = None,
    xlabel: str = 'Runs per Season',
    ylabel: str = 'Frequency',
) -> None:
    """
    Create overlaid histograms for comparing two distributions.

    Uses step histograms for clarity when overlaying. Adds mean lines
    for each distribution with difference annotation.

    Args:
        ax: Matplotlib Axes object to plot on
        data1: First distribution data
        data2: Second distribution data
        label1: Label for first distribution
        label2: Label for second distribution
        colors: Optional tuple of (color1, color2). Default: ('steelblue', 'coral')
        bins: Number of histogram bins (default: 30)
        alpha: Histogram transparency (default: 0.5)
        title: Optional chart title
        xlabel: X-axis label (default: 'Runs per Season')
        ylabel: Y-axis label (default: 'Frequency')
    """
    # Default colors
    if colors is None:
        colors = ('steelblue', 'coral')

    # Convert to numpy arrays
    data1_arr = np.asarray(data1)
    data2_arr = np.asarray(data2)

    if len(data1_arr) == 0 or len(data2_arr) == 0:
        ax.text(
            0.5, 0.5,
            'Insufficient data for comparison',
            ha='center',
            va='center',
            transform=ax.transAxes,
            fontsize=12,
            color='gray'
        )
        ax.set_xticks([])
        ax.set_yticks([])
        return

    # Calculate common bin edges for fair comparison
    all_data = np.concatenate([data1_arr, data2_arr])
    bin_edges = np.histogram_bin_edges(all_data, bins=bins)

    # Create overlaid step histograms
    ax.hist(
        data1_arr,
        bins=bin_edges,
        alpha=alpha,
        color=colors[0],
        edgecolor=colors[0],
        linewidth=1.5,
        histtype='stepfilled',
        label=label1,
    )
    ax.hist(
        data2_arr,
        bins=bin_edges,
        alpha=alpha,
        color=colors[1],
        edgecolor=colors[1],
        linewidth=1.5,
        histtype='stepfilled',
        label=label2,
    )

    # Calculate means
    mean1 = float(np.mean(data1_arr))
    mean2 = float(np.mean(data2_arr))
    diff = mean2 - mean1

    # Add mean lines
    ax.axvline(
        mean1,
        color=colors[0],
        linestyle='--',
        linewidth=2,
        alpha=0.8,
    )
    ax.axvline(
        mean2,
        color=colors[1],
        linestyle='--',
        linewidth=2,
        alpha=0.8,
    )

    # Add difference annotation
    diff_sign = '+' if diff >= 0 else ''
    ax.annotate(
        f'Difference: {diff_sign}{diff:.1f} runs',
        xy=(0.95, 0.95),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=10,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
    )

    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)

    # Clip x-axis to 0 minimum
    ax.set_xlim(0, None)

    # Add legend
    ax.legend()

    # Add grid
    ax.grid(True, alpha=0.3)


def add_effect_size_annotation(
    ax: Axes,
    data1: ArrayLike,
    data2: ArrayLike,
    x_position: float = 0.95,
    y_position: float = 0.85,
) -> float:
    """
    Calculate Cohen's d effect size and add annotation to chart.

    Cohen's d measures the standardized difference between two means.
    Interpretation:
        - |d| < 0.2: negligible
        - |d| < 0.5: small
        - |d| < 0.8: medium
        - |d| >= 0.8: large

    Args:
        ax: Matplotlib Axes object to annotate
        data1: First distribution data (control/baseline)
        data2: Second distribution data (treatment/comparison)
        x_position: X position in axes fraction (default: 0.95, right side)
        y_position: Y position in axes fraction (default: 0.85)

    Returns:
        Cohen's d value (positive means data2 > data1)
    """
    # Convert to numpy arrays
    data1_arr = np.asarray(data1)
    data2_arr = np.asarray(data2)

    if len(data1_arr) < 2 or len(data2_arr) < 2:
        return 0.0

    # Calculate Cohen's d
    # d = (mean2 - mean1) / pooled_std
    mean1 = np.mean(data1_arr)
    mean2 = np.mean(data2_arr)
    std1 = np.std(data1_arr, ddof=1)
    std2 = np.std(data2_arr, ddof=1)
    n1 = len(data1_arr)
    n2 = len(data2_arr)

    # Pooled standard deviation
    pooled_std = np.sqrt(
        ((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2)
    )

    if pooled_std == 0:
        cohens_d = 0.0
    else:
        cohens_d = float((mean2 - mean1) / pooled_std)

    # Interpret magnitude
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        magnitude = 'negligible'
    elif abs_d < 0.5:
        magnitude = 'small'
    elif abs_d < 0.8:
        magnitude = 'medium'
    else:
        magnitude = 'large'

    # Add annotation
    ax.annotate(
        f"Cohen's d: {cohens_d:.3f} ({magnitude})",
        xy=(x_position, y_position),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
    )

    return cohens_d
