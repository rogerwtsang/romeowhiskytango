# ============================================================================
# src/models/player.py
# ============================================================================
"""Player data representation."""

from dataclasses import dataclass
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .position import FieldingPosition


@dataclass
class Player:
    """Represents a baseball player with their statistics and calculated probabilities.

    Attributes:
        name: Player name
        ba: Batting average
        obp: On-base percentage
        slg: Slugging percentage
        iso: Isolated power (SLG - BA)
        pa: Plate appearances
        singles: Number of singles (if available)
        doubles: Number of doubles (if available)
        triples: Number of triples (if available)
        hr: Number of home runs (if available)
        sb: Stolen bases (if available)
        cs: Caught stealing (if available)
        position: Fielding position (FieldingPosition object)
        pa_probs: Calculated probabilities for each PA outcome
        hit_dist: Distribution of hit types given a hit occurred
    """
    name: str
    ba: float
    obp: float
    slg: float
    iso: float
    pa: int

    # Raw counts (optional, for future Bayesian upgrade)
    singles: Optional[int] = None
    doubles: Optional[int] = None
    triples: Optional[int] = None
    hr: Optional[int] = None

    # Stolen base data
    sb: Optional[int] = None
    cs: Optional[int] = None

    # Fielding position (FieldingPosition object, not just a string)
    position: Optional['FieldingPosition'] = None

    # Calculated probabilities
    pa_probs: Optional[Dict[str, float]] = None
    hit_dist: Optional[Dict[str, float]] = None

    def __post_init__(self):
        """Calculate ISO if not provided."""
        if self.iso is None:
            self.iso = self.slg - self.ba

    @property
    def position_abbrev(self) -> Optional[str]:
        """Get position abbreviation (e.g., 'SS', '1B')."""
        return self.position.abbrev if self.position else None

    @property
    def position_code(self) -> Optional[int]:
        """Get position code (1-10)."""
        return self.position.code if self.position else None

    @property
    def position_type(self) -> Optional[str]:
        """Get position type (Catcher, Infielder, Outfielder, etc.)."""
        return self.position.type if self.position else None
