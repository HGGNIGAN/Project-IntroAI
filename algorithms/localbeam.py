import copy
import itertools
import random
from .base import NonogramSolver
from typing import List, Optional


class LocalBeamSolver(NonogramSolver):
    """
    Advanced solver implementing Local Beam Search

    This solver uses a 'Local Beam Search' algorithm:
    1. Initializes multiple candidate solutions (beams).
    2. Iteratively expands and evaluates candidates using logical deductions.
    3. Retains the best candidates for further exploration.
    4. Continues until a solution is found or a maximum number of iterations is reached'
    """

    name = "Local Beam Search"
    description = (
        "Local Beam Search solver."
    )

    # Internal state constants
    UNKNOWN = -1
    WHITE = 0
    BLACK = 1
    RUN_COUNT_WEIGHT = 2
    RUN_LENGTH_WEIGHT = 1

    beam_width = 50
    max_iterations = 500
    neighbor_max_flip = 8
    neighbor_combination_cap = 100
    stagnation_threshold = 10  # Number of iterations without improvement before correction
    stagnation_reset_ratio = 0.3  # Fraction of beams to reset on stagnation

    beams = []

    def _solve_internal(self) -> List[List[int]]:
        """
        Main driver for the solving process.
        """
        
        self.beam_width = 2*len(self.rows)*len(self.columns)
        # 1. Initialize initial beam_width (k) random grids
        self.beams = []
        for _ in range(self.beam_width):
            board = self._generate_random_board()
            self.beams.append(board)

        # Track stagnation
        best_score = float('inf')
        iterations_without_improvement = 0

        # 2. Iteratively improve beams
        for iteration in range(self.max_iterations):
            all_neighbors = []
            for beam in self.beams:
                neighbors = self._generate_neighbors(beam)
                all_neighbors.extend(neighbors)

            # Evaluate all neighbors using beam indices
            previous_beams = self.beams
            self.beams.extend(all_neighbors)
            scored_neighbors = []
            for i in range(len(self.beams)):
                score = self._violation_heuristic(i)
                scored_neighbors.append((score, self.beams[i]))

            # Select the best beam_width neighbors
            scored_neighbors.sort(key=lambda x: x[0])
            self.beams = [neighbor for score, neighbor in scored_neighbors[:self.beam_width]]

            # Check for solution and stagnation
            current_best_score = scored_neighbors[0][0]
            if current_best_score < best_score:
                best_score = current_best_score
                iterations_without_improvement = 0
            else:
                iterations_without_improvement += 1

            for i in range(len(self.beams)):
                score = self._violation_heuristic(i)
                if score == 0:
                    print ("Solution found!")
                    print(self.beams[i])
                    return self.beams[i]

            # Apply stagnation correction
            if iterations_without_improvement >= self.stagnation_threshold:
                num_to_reset = max(1, int(self.beam_width * self.stagnation_reset_ratio))
                for i in range(num_to_reset):
                    self.beams[-(i+1)] = self._generate_random_board()
                iterations_without_improvement = 0
        
        # If no solution found, return the best candidate
        best_idx = min(range(len(self.beams)), key=lambda i: self._violation_heuristic(i))
        best_beam = self.beams[best_idx]
        print ("Solution not found!")
        print(best_beam, "with score", self._violation_heuristic(best_idx))
        return best_beam
    
    def _violation_heuristic(self, beam_idx: int) -> int:
        total_score = 0
        # Evaluate row violations
        for r in range(self.height):
            total_score += self._row_violation_heuristic(beam_idx, r)
        # Evaluate column violations
        for c in range(self.width):
            total_score += self._col_violation_heuristic(beam_idx, c)
        return total_score
    
    def _count_runs(self, line: List[int]) -> List[int]:
        runs = []
        count = 0
        for cell in line:
            if cell == self.BLACK:
                count += 1
            else:
                if count:
                    runs.append(count)
                    count = 0
        if count:
            runs.append(count)
        return runs
    
    def _row_violation_heuristic(self, beam_idx: int, line_idx) -> int:
        score = 0
        line = self.beams[beam_idx][line_idx]
        clues = self.rows[line_idx]
        
        # 1. Add penalty for the difference in the number of runs between actual line and clues
        actual_runs = self._count_runs(line)
        score += abs(len(clues) - len(actual_runs)) * self.RUN_COUNT_WEIGHT

        # 2. Add penalty for the difference in lengths of each run
        for i in range(min(len(clues), len(actual_runs))):
            score += abs(clues[i] - actual_runs[i]) * self.RUN_LENGTH_WEIGHT
        return score
    
    def _col_violation_heuristic(self, beam_idx: int, line_idx) -> int:
        score = 0
        # Extract the column at index `line_idx` from the board
        line = [self.beams[beam_idx][r][line_idx] for r in range(self.height)]
        clues = self.columns[line_idx]
        
        # 1. Add penalty for the difference in the number of runs between actual line and clues
        actual_runs = self._count_runs(line)
        score += abs(len(clues) - len(actual_runs)) * self.RUN_COUNT_WEIGHT

        # 2. Add penalty for the difference in lengths of each run
        for i in range(min(len(clues), len(actual_runs))):
            score += abs(clues[i] - actual_runs[i]) * self.RUN_LENGTH_WEIGHT
        return score

    def _get_violated_rows(self, beam_idx: int) -> List[int]:
        """Returns list of row indices that have violations."""
        violated_rows = []
        for r in range(self.height):
            if self._row_violation_heuristic(beam_idx, r) > 0:
                violated_rows.append(r)
        return violated_rows

    def _get_violated_cols(self, beam_idx: int) -> List[int]:
        """Returns list of column indices that have violations."""
        violated_cols = []
        for c in range(self.width):
            if self._col_violation_heuristic(beam_idx, c) > 0:
                violated_cols.append(c)
        return violated_cols

    def _generate_neighbors(self, board):
        """
        Generates neighboring states from the current state.
        Only flips cells at intersections of violated rows and columns.
        Returns a list of neighboring states.
        """
        # Temporarily add board to beams to use violation methods
        temp_idx = len(self.beams)
        self.beams.append(board)
        
        violated_rows = self._get_violated_rows(temp_idx)
        violated_cols = self._get_violated_cols(temp_idx)
        
        # Remove temporary board
        self.beams.pop()
        
        # Build candidate cells at intersections
        candidate_cells = {(r, c) for r in violated_rows for c in violated_cols}

        neighbors = []

        # If no candidates, fall back to flipping individual cells across the grid
        if not candidate_cells:
            height = len(board)
            width = len(board[0]) if height > 0 else 0
            for r in range(height):
                for c in range(width):
                    new_board = [row[:] for row in board]
                    new_board[r][c] = self.WHITE if board[r][c] == self.BLACK else self.BLACK
                    neighbors.append(new_board)
            return neighbors

        # Generate neighbors by flipping combinations of candidate cells
        cells_list = list(candidate_cells)
        random.shuffle(cells_list)
        total_added = 0
        max_k = min(self.neighbor_max_flip, len(cells_list))
        for k in range(1, max_k + 1):
            for combo in itertools.combinations(cells_list, k):
                new_board = [row[:] for row in board]
                for r, c in combo:
                    new_board[r][c] = self.WHITE if board[r][c] == self.BLACK else self.BLACK
                neighbors.append(new_board)
                total_added += 1
                if total_added >= self.neighbor_combination_cap:
                    break
            if total_added >= self.neighbor_combination_cap:
                break
        
        return neighbors
    
    def _generate_random_board(self):
        return [
            [random.choice([self.WHITE, self.BLACK]) for _ in range(self.width)]
            for _ in range(self.height)
        ]