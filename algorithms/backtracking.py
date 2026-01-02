from typing import List, Optional

import numpy as np

from .__base__ import NonogramSolver


class BacktrackingSolver(NonogramSolver):
        """
        Chronological Backtracking with Logical Rule filters.

        This solver uses a 'Propagate & Backtrack' strategy:
        1. Propagation: Repeatedly applies logical deduction (Line Intersection) to all rows and columns until no new information can be found.
           This finds the intersection of all valid permutations.
        2. Backtracking: If logic stalls, it guesses an unknown cell and recurses.
        """

        name = "Backtracking Solver"
        description = (
                "Backtracking solver optimized with Line Intersection logical checks."
        )

        # Internal state constants
        UNKNOWN = -1
        WHITE = 0
        BLACK = 1

        def _solve_internal(self) -> List[List[int]]:
                """
                Main driver for the solving process.
                """
                # Initialize board
                self.board = np.full(
                        (self.height, self.width), self.UNKNOWN, dtype=np.int8
                )

                # Start the Propagate -> Backtrack cycle
                if self._backtrack():
                        # Map internal state to binary result
                        # Convert -1 (UNKNOWN) to 0 (WHITE) and 1 to 1.
                        final_grid = np.where(self.board == self.BLACK, 1, 0)
                        return final_grid.tolist()
                else:
                        return []

        def _propagate(self) -> bool:
                """
                Implements the Logical Rules Filter, which repeatedly applies constraint propagation to deduce cell values.
                The process continues until no new information can be derived (board reaches a stable state).

                Returns:
                    bool: True if the board is in a valid state with no contradictions.
                          False if a contradiction is found (a line has 0 valid permutations).
                """
                changed = True
                while changed:
                        changed = False

                        # --- ROWS ---
                        for r in range(self.height):
                                current_row = self.board[r, :]

                                # Check intersection of possibilities
                                new_row = self._solve_line(current_row, self.rows[r])

                                if new_row is None:
                                        return False  # Contradiction

                                if not np.array_equal(current_row, new_row):
                                        self.board[r, :] = new_row
                                        changed = True

                        # --- COLUMNS ---
                        for c in range(self.width):
                                current_col = self.board[:, c]

                                # Check intersection of possibilities
                                new_col = self._solve_line(current_col, self.columns[c])

                                if new_col is None:
                                        return False  # Contradiction

                                if not np.array_equal(current_col, new_col):
                                        self.board[:, c] = new_col
                                        changed = True

                return True

        def _solve_line(
                self, current_line: np.ndarray, clues: List[int]
        ) -> Optional[np.ndarray]:
                """
                Implements the 'Intersection of Permutations' logic:

                - Cells shared by all valid perms become BLACK.
                - Cells unreachable by any perm become WHITE.
                - Generates only permutations that fit the 'line' constraints (e.g. existing BLACKs).
                """
                length = len(current_line)

                # Generate all valid permutations for this line that respect currently known cells
                perms_list = self._generate_permutations(current_line, clues, length)

                if not perms_list:
                        return None  # Contradiction

                # If only 1 perm exists, that's the answer
                if len(perms_list) == 1:
                        return np.array(perms_list[0], dtype=np.int8)

                # Find Intersection
                perms_matrix = np.array(perms_list, dtype=np.int8)

                # Find columns where ALL rows are BLACK (1)
                # axis=0 means "look down the column across all permutations"
                all_black = np.all(perms_matrix == self.BLACK, axis=0)

                # Find columns where ALL rows are WHITE (0)
                all_white = np.all(perms_matrix == self.WHITE, axis=0)

                # Construct the result line
                result_line = np.full(length, self.UNKNOWN, dtype=np.int8)
                result_line[all_black] = self.BLACK
                result_line[all_white] = self.WHITE

                # Merge the new deductions with the existing knowledge
                # This ensures we don't accidentally unset a known value, though intersection logic shouldn't
                mask_known = current_line != self.UNKNOWN
                result_line[mask_known] = current_line[mask_known]

                return result_line

        def _generate_permutations(
                self, current_line: np.ndarray, clues: List[int], length: int
        ) -> List[List[int]]:
                """
                Generates all valid permutations of 'clues' that fit into 'current_line'.
                Prunes branches early if they conflict with known BLACK/WHITE cells in current_line.
                """
                results = []
                clues_tuple = tuple(clues)  # lighter to pass around

                # Pre-calculate minimum space needed for remaining blocks
                # e.g., clues [2, 1] needs 2 + 1 + 1 = 4 spaces minimum
                min_space_suffix = [0] * (len(clues) + 1)
                for i in range(len(clues) - 1, -1, -1):
                        min_space_suffix[i] = (
                                min_space_suffix[i + 1]
                                + clues[i]
                                + (1 if i < len(clues) - 1 else 0)
                        )

                def recursive_search(index, clue_idx, current_build):
                        # Base Case: All clues placed
                        if clue_idx == len(clues_tuple):
                                remaining_len = length - index

                                # Verify tail against constraints
                                # (Check if we are overwriting a known BLACK with WHITE)
                                valid = True
                                # Check if any remaining cell in current_line is BLACK
                                for k in range(index, length):
                                        if current_line[k] == self.BLACK:
                                                valid = False
                                                break

                                if valid:
                                        # Found a valid full line
                                        results.append(
                                                current_build
                                                + [self.WHITE] * remaining_len
                                        )
                                return

                        # Pruning: Not enough space left
                        if index + min_space_suffix[clue_idx] > length:
                                return

                        block_size = clues_tuple[clue_idx]

                        # Try placing the block at every possible start position 's'
                        # Range: from 'index' up to limit
                        # limit = length - (space needed for THIS block + space for REST) + 1
                        # min_space_suffix includes this block.
                        limit = length - min_space_suffix[clue_idx] + 1

                        for s in range(index, limit):
                                # CHECK A: Can we place GAP (White) before this block?
                                # We need (s - index) white cells.
                                gap_ok = True
                                for k in range(index, s):
                                        if current_line[k] == self.BLACK:
                                                gap_ok = False
                                                break
                                if not gap_ok:
                                        break

                                # CHECK B: Can we place the BLOCK (Black)?
                                block_ok = True
                                for k in range(s, s + block_size):
                                        if current_line[k] == self.WHITE:
                                                block_ok = False
                                                break

                                # CHECK C: Mandatory Trailing Gap (White)
                                # If not the last block, cell after block MUST be white.
                                if clue_idx < len(clues_tuple) - 1:
                                        if (
                                                s + block_size < length
                                                and current_line[s + block_size]
                                                == self.BLACK
                                        ):
                                                block_ok = False

                                if block_ok:
                                        # Build segment: [Whites...] + [Blacks...] + [White (separator)]
                                        # We don't add the separator here explicitly in recursion logic to keep indices clean, but we account for it in 'next_index'.
                                        new_segment = [self.WHITE] * (s - index) + [
                                                self.BLACK
                                        ] * block_size

                                        next_index = s + block_size

                                        # If not last block, force a separator (implicit white)
                                        if clue_idx < len(clues_tuple) - 1:
                                                new_segment.append(self.WHITE)
                                                next_index += 1

                                        recursive_search(
                                                next_index,
                                                clue_idx + 1,
                                                current_build + new_segment,
                                        )

                recursive_search(0, 0, [])
                return results

        def _backtrack(self) -> bool:
                """
                Recursive Backtracking step.
                Finds the first UNKNOWN cell, guesses, and recurses.
                """

                # Propagate constraints first
                if not self._propagate():
                        return False

                # Heuristic: Find first UNKNOWN cell
                # argwhere returns coordinates of all True values
                unknown_coords = np.argwhere(self.board == self.UNKNOWN)

                if unknown_coords.size == 0:
                        return True  # Solved

                # Pick the first one
                target_r, target_c = unknown_coords[0]

                # Guess BLACK
                snapshot = self.board.copy()
                self.board[target_r, target_c] = self.BLACK
                if self._backtrack():
                        return True

                # Restore and Guess WHITE
                self.board = snapshot
                self.board[target_r, target_c] = self.WHITE
                if self._backtrack():
                        return True

                # Fail
                self.board = snapshot  # Clean up before returning up the stack
                return False
