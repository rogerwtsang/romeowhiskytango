"""Validates lineup against constraints and applies constraint rules."""

from typing import List, Dict, Any, Tuple, Optional


class ConstraintValidator:
    """Validates and applies lineup constraints."""

    @staticmethod
    def validate_constraint(constraint: Dict[str, Any], lineup: List[str], roster: List[str]) -> Tuple[bool, str]:
        """
        Validate a single constraint against current lineup.

        Args:
            constraint: Constraint dict with 'type' and constraint-specific fields
            lineup: List of player names in batting order (9 players, None for empty slots)
            roster: List of all available player names

        Returns:
            Tuple of (is_valid, error_message)
        """
        constraint_type = constraint.get('type')

        if constraint_type == 'fixed_position':
            player = constraint.get('player')
            position = constraint.get('position')  # 1-based index

            if player not in roster:
                return False, f"Player '{player}' not in roster"

            if position < 1 or position > 9:
                return False, f"Position must be 1-9, got {position}"

            # Check if player is in lineup at specified position
            lineup_idx = position - 1  # Convert to 0-based
            if len(lineup) > lineup_idx:
                if lineup[lineup_idx] != player:
                    return False, f"'{player}' must bat in position {position}"

            return True, ""

        elif constraint_type == 'batting_order':
            player1 = constraint.get('player1')  # Bats first
            player2 = constraint.get('player2')  # Bats after player1

            if player1 not in roster or player2 not in roster:
                return False, f"Players not in roster"

            if player1 not in lineup or player2 not in lineup:
                return True, ""  # Constraint doesn't apply if players not in lineup

            # Find positions
            idx1 = lineup.index(player1)
            idx2 = lineup.index(player2)

            if idx1 >= idx2:
                return False, f"'{player2}' must bat after '{player1}'"

            return True, ""

        elif constraint_type == 'platoon':
            player_a = constraint.get('player_a')
            player_b = constraint.get('player_b')
            position = constraint.get('position')  # 1-based

            if player_a not in roster or player_b not in roster:
                return False, f"Players not in roster"

            if position < 1 or position > 9:
                return False, f"Position must be 1-9"

            lineup_idx = position - 1
            if len(lineup) > lineup_idx and lineup[lineup_idx] is not None:
                if lineup[lineup_idx] not in [player_a, player_b]:
                    return False, f"Position {position} must be either '{player_a}' or '{player_b}'"

            # Check that both players are not in lineup simultaneously
            if player_a in lineup and player_b in lineup:
                return False, f"Cannot have both '{player_a}' and '{player_b}' in lineup (platoon)"

            return True, ""

        return False, f"Unknown constraint type: {constraint_type}"

    @staticmethod
    def validate_all_constraints(constraints: List[Dict], lineup: List[str], roster: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate all constraints against lineup.

        Args:
            constraints: List of constraint dicts
            lineup: List of player names in batting order
            roster: List of all available player names

        Returns:
            Tuple of (all_valid, list_of_error_messages)
        """
        errors = []
        all_valid = True

        for constraint in constraints:
            is_valid, error_msg = ConstraintValidator.validate_constraint(constraint, lineup, roster)
            if not is_valid:
                all_valid = False
                errors.append(error_msg)

        return all_valid, errors

    @staticmethod
    def apply_constraints(constraints: List[Dict], lineup: List[Optional[str]], roster: List[str]) -> List[Optional[str]]:
        """
        Apply constraints to a lineup (for auto-ordering).

        Args:
            constraints: List of constraint dicts
            lineup: Initial lineup (may have None for empty slots)
            roster: List of all available player names

        Returns:
            Modified lineup with constraints applied (best effort)
        """
        result = lineup.copy()

        # Apply fixed_position constraints first
        for constraint in constraints:
            if constraint.get('type') == 'fixed_position':
                player = constraint.get('player')
                position = constraint.get('position') - 1  # Convert to 0-based

                if player in roster and 0 <= position < 9:
                    # Remove player from current position if present
                    if player in result:
                        result[result.index(player)] = None

                    # Place player at fixed position
                    result[position] = player

        # Apply platoon constraints (exclude one player from roster if both present)
        for constraint in constraints:
            if constraint.get('type') == 'platoon':
                player_a = constraint.get('player_a')
                player_b = constraint.get('player_b')

                if player_a in result and player_b in result:
                    # Keep the first one, remove the second
                    if result.index(player_a) < result.index(player_b):
                        result[result.index(player_b)] = None
                    else:
                        result[result.index(player_a)] = None

        return result

    @staticmethod
    def get_constraint_description(constraint: Dict[str, Any]) -> str:
        """
        Get human-readable description of a constraint.

        Args:
            constraint: Constraint dict

        Returns:
            Description string
        """
        constraint_type = constraint.get('type')

        if constraint_type == 'fixed_position':
            player = constraint.get('player')
            position = constraint.get('position')
            return f"{player} always bats #{position}"

        elif constraint_type == 'batting_order':
            player1 = constraint.get('player1')
            player2 = constraint.get('player2')
            return f"{player2} always bats after {player1}"

        elif constraint_type == 'platoon':
            player_a = constraint.get('player_a')
            player_b = constraint.get('player_b')
            position = constraint.get('position')
            return f"Platoon {player_a} / {player_b} at position #{position}"

        return f"Unknown constraint: {constraint_type}"
