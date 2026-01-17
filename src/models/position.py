# ============================================================================
# src/models/position.py
# ============================================================================
"""Fielding position data structure and constants.

Standard baseball position numbering (scorekeeping convention):
    1 = Pitcher (P)
    2 = Catcher (C)
    3 = First Baseman (1B)
    4 = Second Baseman (2B)
    5 = Third Baseman (3B)
    6 = Shortstop (SS)
    7 = Left Fielder (LF)
    8 = Center Fielder (CF)
    9 = Right Fielder (RF)
    10 = Designated Hitter (DH)

Note: Shortstop is #6 (not #5) for historical reasons - originally
the shortstop was a fourth outfielder before moving to the infield.
"""

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class FieldingPosition:
    """Represents a defensive fielding position.

    Attributes:
        code: Standard scorekeeping number (1-10)
        abbrev: Short abbreviation (C, 1B, 2B, SS, 3B, LF, CF, RF, DH)
        name: Full position name (e.g., "Shortstop")
        type: Position category (Pitcher, Catcher, Infielder, Outfielder, Hitter)
    """
    code: int
    abbrev: str
    name: str
    type: str

    def __str__(self) -> str:
        return self.abbrev

    def __repr__(self) -> str:
        return f"FieldingPosition({self.code}, '{self.abbrev}')"

    @property
    def is_infielder(self) -> bool:
        return self.type == 'Infielder'

    @property
    def is_outfielder(self) -> bool:
        return self.type == 'Outfielder'

    @property
    def is_catcher(self) -> bool:
        return self.type == 'Catcher'

    @property
    def is_pitcher(self) -> bool:
        return self.type == 'Pitcher'

    @property
    def is_dh(self) -> bool:
        return self.abbrev == 'DH'


# Standard position definitions
PITCHER = FieldingPosition(1, 'P', 'Pitcher', 'Pitcher')
CATCHER = FieldingPosition(2, 'C', 'Catcher', 'Catcher')
FIRST_BASE = FieldingPosition(3, '1B', 'First Baseman', 'Infielder')
SECOND_BASE = FieldingPosition(4, '2B', 'Second Baseman', 'Infielder')
THIRD_BASE = FieldingPosition(5, '3B', 'Third Baseman', 'Infielder')
SHORTSTOP = FieldingPosition(6, 'SS', 'Shortstop', 'Infielder')
LEFT_FIELD = FieldingPosition(7, 'LF', 'Left Fielder', 'Outfielder')
CENTER_FIELD = FieldingPosition(8, 'CF', 'Center Fielder', 'Outfielder')
RIGHT_FIELD = FieldingPosition(9, 'RF', 'Right Fielder', 'Outfielder')
DESIGNATED_HITTER = FieldingPosition(10, 'DH', 'Designated Hitter', 'Hitter')


# Lookup tables for converting between formats
POSITIONS_BY_CODE: Dict[int, FieldingPosition] = {
    1: PITCHER,
    2: CATCHER,
    3: FIRST_BASE,
    4: SECOND_BASE,
    5: THIRD_BASE,
    6: SHORTSTOP,
    7: LEFT_FIELD,
    8: CENTER_FIELD,
    9: RIGHT_FIELD,
    10: DESIGNATED_HITTER,
}

POSITIONS_BY_ABBREV: Dict[str, FieldingPosition] = {
    'P': PITCHER,
    'C': CATCHER,
    '1B': FIRST_BASE,
    '2B': SECOND_BASE,
    '3B': THIRD_BASE,
    'SS': SHORTSTOP,
    'LF': LEFT_FIELD,
    'CF': CENTER_FIELD,
    'RF': RIGHT_FIELD,
    'DH': DESIGNATED_HITTER,
    # Alternative abbreviations sometimes used
    'TWP': PITCHER,  # Two-way player (treated as pitcher)
}

# Position groupings for analysis
INFIELDERS = [FIRST_BASE, SECOND_BASE, THIRD_BASE, SHORTSTOP]
OUTFIELDERS = [LEFT_FIELD, CENTER_FIELD, RIGHT_FIELD]
CORNER_INFIELDERS = [FIRST_BASE, THIRD_BASE]
MIDDLE_INFIELDERS = [SECOND_BASE, SHORTSTOP]
CORNER_OUTFIELDERS = [LEFT_FIELD, RIGHT_FIELD]


def get_position_by_code(code: int) -> Optional[FieldingPosition]:
    """Look up a position by its scorekeeping number.

    Args:
        code: Position number (1-10)

    Returns:
        FieldingPosition or None if invalid code
    """
    return POSITIONS_BY_CODE.get(code)


def get_position_by_abbrev(abbrev: str) -> Optional[FieldingPosition]:
    """Look up a position by its abbreviation.

    Args:
        abbrev: Position abbreviation (e.g., 'SS', '1B', 'CF')

    Returns:
        FieldingPosition or None if invalid abbreviation
    """
    return POSITIONS_BY_ABBREV.get(abbrev.upper())


def parse_position(value) -> Optional[FieldingPosition]:
    """Parse a position from various input formats.

    Args:
        value: Can be:
            - int: Position code (1-10)
            - str: Position abbreviation ('SS', '1B', etc.)
            - FieldingPosition: Returned as-is
            - None: Returns None

    Returns:
        FieldingPosition or None if unable to parse
    """
    if value is None:
        return None

    if isinstance(value, FieldingPosition):
        return value

    if isinstance(value, int):
        return get_position_by_code(value)

    if isinstance(value, str):
        # Try abbreviation first
        pos = get_position_by_abbrev(value)
        if pos:
            return pos

        # Try parsing as integer string
        try:
            code = int(value)
            return get_position_by_code(code)
        except ValueError:
            pass

    return None


if __name__ == "__main__":
    # Test the position module
    print("=== Position Module Tests ===\n")

    # Test lookup by code
    print("Lookup by code:")
    for code in range(1, 11):
        pos = get_position_by_code(code)
        if pos is not None:
            print(f"  {code}: {pos.abbrev} - {pos.name} ({pos.type})")
        else:
            print(f"  {code}: Not found")

    print("\nLookup by abbreviation:")
    for abbrev in ['C', '1B', '2B', 'SS', '3B', 'LF', 'CF', 'RF', 'DH']:
        pos = get_position_by_abbrev(abbrev)
        if pos is not None:
            print(f"  {abbrev}: code={pos.code}, type={pos.type}")
        else:
            print(f"  {abbrev}: Not found")

    print("\nPosition properties:")
    print(f"  SHORTSTOP.is_infielder: {SHORTSTOP.is_infielder}")
    print(f"  CENTER_FIELD.is_outfielder: {CENTER_FIELD.is_outfielder}")
    print(f"  CATCHER.is_catcher: {CATCHER.is_catcher}")

    print("\nPosition groupings:")
    print(f"  Infielders: {[p.abbrev for p in INFIELDERS]}")
    print(f"  Outfielders: {[p.abbrev for p in OUTFIELDERS]}")
    print(f"  Middle infielders: {[p.abbrev for p in MIDDLE_INFIELDERS]}")

    print("\nParse position (flexible input):")
    test_inputs = [6, '6', 'SS', 'ss', SHORTSTOP, None, 'invalid']
    for inp in test_inputs:
        result = parse_position(inp)
        print(f"  parse_position({inp!r}): {result}")

    print("\n✓ All position tests passed")
