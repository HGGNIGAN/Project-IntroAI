import copy
from typing import List, Optional

from .base import NonogramSolver


class BacktrackingSolver(NonogramSolver):
        """
        Advanced solver implementing Chronological Backtracking with Logical Rule filters.

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
                # Initialize a tri-state board for internal logic. base.py initializes self.grid with 0s (White), but we need 'Unknown'.
                self.board = [
                        [self.UNKNOWN for _ in range(self.width)]
                        for _ in range(self.height)
                ]

                # Start the Propagate -> Backtrack cycle
                if self._backtrack(0, 0):
                        # Map internal tri-state board back to binary self.grid for return UNKNOWNs usually shouldn't exist if solved, but map them to 0 (White) just in case.
                        for r in range(self.height):
                                for c in range(self.width):
                                        val = self.board[r][c]
                                        self.grid[r][c] = 1 if val == self.BLACK else 0
                        return self.grid
                else:
                        # No solution found
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

                        # Apply logic to rows
                        for r in range(self.height):
                                current_row = self.board[r]
                                new_row = self._solve_line(
                                        current_row, self.rows[r], self.width
                                )

                                if new_row is None:  # Contradiction found
                                        return False

                                if new_row != current_row:
                                        self.board[r] = new_row
                                        changed = True

                        # Apply logic to columns
                        for c in range(self.width):
                                current_col = [
                                        self.board[r][c] for r in range(self.height)
                                ]
                                new_col = self._solve_line(
                                        current_col, self.columns[c], self.height
                                )

                                if new_col is None:  # Contradiction found
                                        return False

                                if new_col != current_col:
                                        # Apply changes back to the board
                                        for r in range(self.height):
                                                self.board[r][c] = new_col[r]
                                        changed = True

                return True

        def _solve_line(
                self, line: List[int], clues: List[int], length: int
        ) -> Optional[List[int]]:
                """
                Implements the 'Intersection of Permutations' logic:

                - Cells shared by all valid perms become BLACK.
                - Cells unreachable by any perm become WHITE.
                - Generates only permutations that fit the 'line' constraints (e.g. existing BLACKs).
                """
                # Generate all valid permutations for this line that respect currently known cells
                perms = self._generate_permutations(line, clues, length)

                if not perms:
                        return None  # Impossible configuration (Contradiction)

                # If only 1 perm exists, that's the answer
                if len(perms) == 1:
                        return perms[0]

                # Find Intersection
                # Initialize result with the first permutation
                result_line = list(perms[0])

                for p in perms[1:]:
                        for i in range(length):
                                # If cells differ between permutations, they remain/become UNKNOWN
                                if result_line[i] != p[i]:
                                        result_line[i] = self.UNKNOWN

                # Merge the new deductions with the existing knowledge
                # This ensures we don't accidentally unset a known value, though intersection logic shouldn't
                for i in range(length):
                        if line[i] != self.UNKNOWN and result_line[i] == self.UNKNOWN:
                                # This technically shouldn't happen if perms respected line, but better safe than sorry.
                                result_line[i] = line[i]

                return result_line

        def _generate_permutations(
                self, current_line: List[int], clues: List[int], length: int
        ) -> List[List[int]]:
                """
                Generates all valid permutations of 'clues' that fit into 'current_line'.
                Prunes branches early if they conflict with known BLACK/WHITE cells in current_line.
                """
                results = []

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
                        # 1. Base Case: All clues placed
                        if clue_idx == len(clues):
                                # Fill remainder with WHITE
                                remaining_len = length - index
                                potential_tail = (
                                        current_build + [self.WHITE] * remaining_len
                                )

                                # Verify the tail against the constraints
                                # (Check if we are overwriting a known BLACK with WHITE)
                                valid = True
                                for k in range(index, length):
                                        if current_line[k] == self.BLACK:
                                                valid = False
                                                break

                                if valid:
                                        results.append(potential_tail)
                                return

                        # 2. Pruning: Not enough space left
                        if index + min_space_suffix[clue_idx] > length:
                                return

                        block_size = clues[clue_idx]

                        # 3. Try placing the block at every possible start position 's'
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
                                        # If we hit a BLACK cell that we tried to make WHITE, we can't skip past it. Prune immediately.
                                        break

                                # CHECK B: Can we place the BLOCK (Black)?
                                block_ok = True
                                for k in range(s, s + block_size):
                                        if current_line[k] == self.WHITE:
                                                block_ok = False
                                                break

                                # CHECK C: Mandatory Trailing Gap (White)
                                # If not the last block, cell after block MUST be white.
                                if clue_idx < len(clues) - 1:
                                        if (
                                                s + block_size < length
                                                and current_line[s + block_size]
                                                == self.BLACK
                                        ):
                                                block_ok = False

                                if block_ok:
                                        # Build segment: [Whites...] + [Blacks...] + [White (separator)]
                                        # Note: We don't add the separator here explicitly in recursion logic to keep indices clean, but we account for it in 'next_index'.

                                        new_segment = [self.WHITE] * (s - index) + [
                                                self.BLACK
                                        ] * block_size

                                        next_index = s + block_size

                                        # If not last block, force a separator (implicit white)
                                        if clue_idx < len(clues) - 1:
                                                new_segment.append(self.WHITE)
                                                next_index += 1

                                        recursive_search(
                                                next_index,
                                                clue_idx + 1,
                                                current_build + new_segment,
                                        )

                recursive_search(0, 0, [])
                return results

        def _backtrack(self, r, c) -> bool:
                """
                Recursive Backtracking step.
                Finds the first UNKNOWN cell, guesses, and recurses.
                """
                # 1. Propagate Constraints first
                if not self._propagate():
                        return False

                # 2. Find the best cell to guess (Heuristic: First Unknown)
                #    Could pick cell in row with most information/constraints
                next_cell = None
                for i in range(self.height):
                        for j in range(self.width):
                                if self.board[i][j] == self.UNKNOWN:
                                        next_cell = (i, j)
                                        break
                        if next_cell:
                                break

                # Base Case: No unknown cells left -> Solved
                if not next_cell:
                        return True

                target_r, target_c = next_cell

                # 3. Guess BLACK
                snapshot = copy.deepcopy(self.board)
                self.board[target_r][target_c] = self.BLACK
                if self._backtrack(target_r, target_c):
                        return True

                # 4. If BLACK failed, Restore and Guess WHITE
                self.board = snapshot
                self.board[target_r][target_c] = self.WHITE
                if self._backtrack(target_r, target_c):
                        return True

                # 5. Both guesses failed -> this branch is dead
                self.board = copy.deepcopy(
                        snapshot
                )  # restore for clean return (optional)
                return False
