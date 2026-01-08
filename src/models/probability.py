# ============================================================================
# src/models/probability.py
# ============================================================================
"""Probability calculations for PA outcomes."""

from typing import Dict, Tuple, Optional
import config
from src.models.player import Player


def calculate_hit_distribution(
    player: Player,
    league_avg_dist: Optional[Dict[str, float]] = None,
    min_hits_threshold: int = 100
) -> Dict[str, float]:
    """Calculate hit type distribution using actual counts with Bayesian smoothing.

    Uses player's actual hit counts when available. For players with few hits,
    blends with league average using Bayesian updating.

    Args:
        player: Player object with hit count data
        league_avg_dist: League average distribution (fallback)
        min_hits_threshold: Minimum hits to trust player data without smoothing

    Returns:
        Dictionary with probabilities for each hit type given a hit occurred.
        Keys: '1B', '2B', '3B', 'HR'
    """
    # Use config league average if not provided
    if league_avg_dist is None:
        league_avg_dist = config.LEAGUE_AVG_HIT_DISTRIBUTION

    # Check if player has actual hit counts
    if (player.singles is not None and
        player.doubles is not None and
        player.triples is not None and
        player.hr is not None):

        # Calculate total hits
        total_hits = player.singles + player.doubles + player.triples + player.hr

        if total_hits == 0:
            # No hits - use league average
            return league_avg_dist.copy()

        # Calculate actual distribution
        actual_dist = {
            '1B': player.singles / total_hits,
            '2B': player.doubles / total_hits,
            '3B': player.triples / total_hits,
            'HR': player.hr / total_hits
        }

        # Apply Bayesian smoothing for small samples
        if total_hits < min_hits_threshold:
            # Prior equivalent sample size
            prior_weight = 100
            player_weight = total_hits

            smoothed_dist = {}
            for ht in ['1B', '2B', '3B', 'HR']:
                smoothed_dist[ht] = (
                    (league_avg_dist[ht] * prior_weight +
                     actual_dist[ht] * player_weight)
                    / (prior_weight + player_weight)
                )

            return smoothed_dist

        # Enough data - use actual distribution
        return actual_dist

    # No count data - fall back to ISO-based estimation (Option A)
    iso = player.iso

    iso_low = config.ISO_THRESHOLDS['low']
    iso_med = config.ISO_THRESHOLDS['medium']

    singles_profile = config.HIT_DISTRIBUTIONS['singles_hitter']
    balanced_profile = config.HIT_DISTRIBUTIONS['balanced']
    power_profile = config.HIT_DISTRIBUTIONS['power_hitter']

    if iso < iso_low:
        return singles_profile.copy()

    if iso < iso_med:
        weight = (iso - iso_low) / (iso_med - iso_low)
        return {
            '1B': singles_profile['1B'] * (1 - weight) + balanced_profile['1B'] * weight,
            '2B': singles_profile['2B'] * (1 - weight) + balanced_profile['2B'] * weight,
            '3B': singles_profile['3B'] * (1 - weight) + balanced_profile['3B'] * weight,
            'HR': singles_profile['HR'] * (1 - weight) + balanced_profile['HR'] * weight
        }

    weight = min(1.0, (iso - iso_med) / 0.200)
    return {
        '1B': balanced_profile['1B'] * (1 - weight) + power_profile['1B'] * weight,
        '2B': balanced_profile['2B'] * (1 - weight) + power_profile['2B'] * weight,
        '3B': balanced_profile['3B'] * (1 - weight) + power_profile['3B'] * weight,
        'HR': balanced_profile['HR'] * (1 - weight) + power_profile['HR'] * weight
    }


def decompose_slash_line(
    ba: float,
    obp: float,
    slg: float,
    player: Optional[Player] = None,
    k_pct: Optional[float] = None
) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Convert slash line statistics to PA outcome probabilities.

    Args:
        ba: Batting average
        obp: On-base percentage
        slg: Slugging percentage
        player: Optional Player object (for actual hit counts)
        k_pct: Optional strikeout rate (as decimal, e.g., 0.220 = 22%)

    Returns:
        Tuple of (pa_probs, hit_dist)
    """
    # Calculate ISO
    iso = slg - ba

    # Get hit type distribution
    if player is not None:
        hit_dist = calculate_hit_distribution(player)
    else:
        # Create temporary player object for ISO-based calculation
        temp_player = Player("temp", ba, obp, slg, iso, 0)
        hit_dist = calculate_hit_distribution(temp_player)

    # Basic PA outcome probabilities
    p_walk = obp - ba
    p_hit = ba
    p_total_outs = 1.0 - obp

    # Split outs into strikeouts and balls-in-play outs
    if k_pct is not None:
        p_strikeout = k_pct
        p_out = p_total_outs - k_pct
        # Ensure p_out doesn't go negative (can happen with extreme K%)
        if p_out < 0:
            p_out = 0.0
            p_strikeout = p_total_outs
    else:
        # Use default league average if no k_pct provided
        p_strikeout = config.DEFAULT_K_PCT
        p_out = p_total_outs - p_strikeout
        if p_out < 0:
            p_out = 0.0
            p_strikeout = p_total_outs

    # Distribute hits into specific types
    pa_probs = {
        'OUT': p_out,
        'STRIKEOUT': p_strikeout,
        'WALK': p_walk,
        'SINGLE': p_hit * hit_dist['1B'],
        'DOUBLE': p_hit * hit_dist['2B'],
        'TRIPLE': p_hit * hit_dist['3B'],
        'HR': p_hit * hit_dist['HR']
    }

    # Validate
    validate_probabilities(pa_probs)
    validate_probabilities(hit_dist)

    return pa_probs, hit_dist


def validate_probabilities(probs: Dict[str, float], tolerance: float = 1e-6) -> bool:
    """Validate that probabilities sum to 1.0 and are non-negative.

    Args:
        probs: Dictionary of probabilities
        tolerance: Acceptable deviation from 1.0

    Returns:
        True if valid, raises ValueError otherwise
    """
    # Check for negative probabilities
    for key, prob in probs.items():
        if prob < 0:
            raise ValueError(f"Negative probability for {key}: {prob}")

    # Check sum
    total = sum(probs.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"Probabilities sum to {total:.6f}, expected 1.0 (tolerance: {tolerance})")

    return True


def calculate_expected_bases_per_hit(hit_dist: Dict[str, float]) -> float:
    """Calculate expected total bases per hit given a hit distribution.

    Useful for validating that hit distribution matches observed SLG/BA ratio.

    Args:
        hit_dist: Dictionary with keys '1B', '2B', '3B', 'HR'

    Returns:
        Expected bases per hit
    """
    return (
        1 * hit_dist['1B'] +
        2 * hit_dist['2B'] +
        3 * hit_dist['3B'] +
        4 * hit_dist['HR']
    )


def compare_to_observed(ba: float, slg: float, hit_dist: Dict[str, float]) -> Dict[str, float]:
    """Compare calculated hit distribution to observed SLG/BA ratio.

    Args:
        ba: Observed batting average
        slg: Observed slugging percentage
        hit_dist: Calculated hit distribution

    Returns:
        Dictionary with comparison metrics
    """
    observed_bases_per_hit = slg / ba if ba > 0 else 0
    expected_bases_per_hit = calculate_expected_bases_per_hit(hit_dist)

    error = expected_bases_per_hit - observed_bases_per_hit
    error_pct = (error / observed_bases_per_hit * 100) if observed_bases_per_hit > 0 else 0

    return {
        'observed_bases_per_hit': observed_bases_per_hit,
        'expected_bases_per_hit': expected_bases_per_hit,
        'absolute_error': error,
        'error_pct': error_pct
    }


if __name__ == "__main__":
    # Add project root to path for standalone testing
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    import config

    # Test the probability calculations
    print("=== Testing Probability Calculations ===\n")

    # Test case 1: Singles hitter
    print("Test 1: Singles Hitter (BA: .280, OBP: .340, SLG: .360)")
    ba, obp, slg = 0.280, 0.340, 0.360
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 2: Balanced hitter
    print("\n" + "="*60 + "\n")
    print("Test 2: Balanced Hitter (BA: .270, OBP: .340, SLG: .450)")
    ba, obp, slg = 0.270, 0.340, 0.450
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 3: Power hitter
    print("\n" + "="*60 + "\n")
    print("Test 3: Power Hitter (BA: .250, OBP: .330, SLG: .520)")
    ba, obp, slg = 0.250, 0.330, 0.520
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    # Test case 4: 2025 Blue Jays team average
    print("\n" + "="*60 + "\n")
    print("Test 4: 2025 Blue Jays Team Average (BA: .261, OBP: .331, SLG: .424)")
    ba, obp, slg = 0.261, 0.331, 0.424
    pa_probs, hit_dist = decompose_slash_line(ba, obp, slg)

    print(f"ISO: {slg - ba:.3f}")
    print("\nPA Outcome Probabilities:")
    for outcome, prob in pa_probs.items():
        print(f"  {outcome}: {prob:.4f} ({prob*100:.2f}%)")

    print("\nHit Distribution (given a hit):")
    for hit_type, prob in hit_dist.items():
        print(f"  {hit_type}: {prob:.4f} ({prob*100:.2f}%)")

    comparison = compare_to_observed(ba, slg, hit_dist)
    print(f"\nBases/hit - Observed: {comparison['observed_bases_per_hit']:.3f}, Expected: {comparison['expected_bases_per_hit']:.3f}")
    print(f"Error: {comparison['error_pct']:.2f}%")

    print("\n" + "="*60)
    print("✓ All tests passed - probabilities valid")
