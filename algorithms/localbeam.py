import heapq
import random
from typing import List, Tuple

from .base import NonogramSolver


class BeamState:
        """
        Helper object to store a candidate solution and its cached scores.
        """

        def __init__(self, board, row_scores, col_scores, black_count):
                self.board = board
                self.row_scores = row_scores
                self.col_scores = col_scores
                self.black_count = black_count
                # We calculate total score dynamically in the solver to allow weighting changes
                self.heuristic_score = sum(row_scores) + sum(col_scores)

        # Allow comparison for the heap (lower score is better)
        def __lt__(self, other):
                return self.heuristic_score < other.heuristic_score


class LocalBeamSolver(NonogramSolver):
        """
        Robust Solver implementing Local Beam Search.

        Improvements for Exact Solutions:
        1. Global Count Constraint: Penalizes boards that don't match the total target black cells.
        2. Stochastic Selection: Maintains diversity to escape local optima.
        3. Memoization: Caches line scores for speed.
        """

        name = "Local Beam Search"
        description = (
                "Local Beam Search with global constraints and stochastic selection."
        )

        # Internal state constants
        WHITE = 0
        BLACK = 1

        # Weights
        RUN_COUNT_WEIGHT = 10  # High penalty for wrong number of blocks
        RUN_LENGTH_WEIGHT = 1  # Low penalty for wrong length (easier to fix)
        GLOBAL_COUNT_WEIGHT = 50  # Massive penalty if total black cells are wrong

        # Search Parameters
        beam_width = 50  # Keep this high (50-100) for >10x10 puzzles
        max_iterations = 5000  # Give it time to converge
        neighbor_combination_cap = 20
        stagnation_threshold = 40  # Allow it to struggle longer before resetting
        stagnation_reset_ratio = 0.5

        def _solve_internal(self) -> List[List[int]]:
                """Main driver for the solving process."""

                # Pre-calculate global target (Total Black Cells needed)
                self.target_black_count = sum(sum(row_clues) for row_clues in self.rows)
                self._score_cache = {}

                # Initialize beams
                current_beams = []
                for _ in range(self.beam_width):
                        board = self._generate_random_board()
                        state = self._create_initial_state(board)
                        current_beams.append(state)

                best_global_score = float("inf")
                best_global_board = None
                iterations_without_improvement = 0

                # Iteratively improve
                for iteration in range(self.max_iterations):
                        # --- Scoring & Solution Check ---
                        # Augment the heuristic score with the Global Count Penalty here
                        for beam in current_beams:
                                count_diff = abs(
                                        beam.black_count - self.target_black_count
                                )
                                beam.final_score = beam.heuristic_score + (
                                        count_diff * self.GLOBAL_COUNT_WEIGHT
                                )

                        # Sort by this new final_score
                        current_beams.sort(key=lambda x: x.final_score)
                        best_beam = current_beams[0]

                        if best_beam.final_score == 0:
                                print(f"Solution found at iteration {iteration}!")
                                return best_beam.board

                        # Track global best
                        if best_beam.final_score < best_global_score:
                                best_global_score = best_beam.final_score
                                best_global_board = best_beam.board
                                iterations_without_improvement = 0
                        else:
                                iterations_without_improvement += 1

                        # --- Generate Neighbors ---
                        candidates_heap = []

                        # Keep existing beams (Elitism)
                        for beam in current_beams:
                                heapq.heappush(
                                        candidates_heap,
                                        (beam.final_score, random.random(), beam),
                                )

                        # Generate new moves
                        for beam in current_beams:
                                violated_cells = self._get_violated_cells(beam)

                                # If heuristic fails to find violations but score > 0, pick random cells
                                if not violated_cells and beam.final_score > 0:
                                        violated_cells = [
                                                (r, c)
                                                for r in range(self.height)
                                                for c in range(self.width)
                                        ]

                                moves = self._generate_moves(violated_cells, beam)

                                for move_coords in moves:
                                        # Incremental Evaluate
                                        h_score, r_scores, c_scores, new_count = (
                                                self._evaluate_flip(beam, move_coords)
                                        )

                                        # Calculate Final Score with Global Penalty
                                        count_diff = abs(
                                                new_count - self.target_black_count
                                        )
                                        final_score = h_score + (
                                                count_diff * self.GLOBAL_COUNT_WEIGHT
                                        )

                                        # Add to heap (potential candidate)
                                        heapq.heappush(
                                                candidates_heap,
                                                (
                                                        final_score,
                                                        random.random(),
                                                        (
                                                                beam,
                                                                move_coords,
                                                                r_scores,
                                                                c_scores,
                                                                new_count,
                                                        ),
                                                ),
                                        )

                        # --- Selection (Stochastic Tournament) ---
                        # Instead of taking strictly the top N, we take top N/2 strictly, and the rest probabilistic from the top 3N candidates.

                        # Pop best candidates from heap
                        pool_size = min(len(candidates_heap), self.beam_width * 3)
                        top_pool = heapq.nsmallest(pool_size, candidates_heap)

                        next_beams = []
                        seen_hashes = set()

                        # Elitism: Take top 30% strictly
                        elite_count = int(self.beam_width * 0.3)

                        for i in range(len(top_pool)):
                                if len(next_beams) >= self.beam_width:
                                        break

                                score, _, item = top_pool[i]

                                # If we are past elite count, introduce randomness
                                # 20% chance to skip a candidate to let a worse one in (maintains diversity)
                                if i >= elite_count and random.random() < 0.2:
                                        continue

                                if isinstance(item, BeamState):
                                        b_hash = self._hash_board(item.board)
                                        if b_hash not in seen_hashes:
                                                next_beams.append(item)
                                                seen_hashes.add(b_hash)
                                else:
                                        parent, move, r_s, c_s, count = item
                                        new_board = self._apply_flip(parent.board, move)
                                        b_hash = self._hash_board(new_board)

                                        if b_hash not in seen_hashes:
                                                new_state = BeamState(
                                                        new_board, r_s, c_s, count
                                                )
                                                next_beams.append(new_state)
                                                seen_hashes.add(b_hash)

                        # Fill if empty (rare)
                        while len(next_beams) < self.beam_width:
                                board = self._generate_random_board()
                                next_beams.append(self._create_initial_state(board))

                        current_beams = next_beams

                        # Stagnation Handling
                        if iterations_without_improvement >= self.stagnation_threshold:
                                # Hard Reset: Keep only 1 best beam, randomize the rest
                                # This breaks out of deep local optima plateaus
                                print(
                                        f"Stagnation detected at it {iteration}. Scrambling..."
                                )
                                current_beams = [current_beams[0]]
                                while len(current_beams) < self.beam_width:
                                        board = self._generate_random_board()
                                        current_beams.append(
                                                self._create_initial_state(board)
                                        )
                                iterations_without_improvement = 0

                print(
                        f"Solution not found. Best approximate score: {best_global_score}"
                )
                return best_global_board  # type:ignore

        # Helper Methods

        def _create_initial_state(self, board) -> BeamState:
                r_scores = [
                        self._calculate_line_score(board[r], self.rows[r])
                        for r in range(self.height)
                ]
                c_scores = []
                for c in range(self.width):
                        col_line = [board[r][c] for r in range(self.height)]
                        c_scores.append(
                                self._calculate_line_score(col_line, self.columns[c])
                        )

                # Calculate black count
                black_count = sum(row.count(self.BLACK) for row in board)

                return BeamState(board, r_scores, c_scores, black_count)

        def _calculate_line_score(self, line: List[int], clues: List[int]) -> int:
                line_key = tuple(line)
                clues_key = tuple(clues)
                cache_key = (line_key, clues_key)

                if cache_key in self._score_cache:
                        return self._score_cache[cache_key]

                runs = []
                count = 0
                for cell in line:
                        if cell == self.BLACK:
                                count += 1
                        elif count:
                                runs.append(count)
                                count = 0
                if count:
                        runs.append(count)

                score = abs(len(clues) - len(runs)) * self.RUN_COUNT_WEIGHT
                for i in range(min(len(clues), len(runs))):
                        score += abs(clues[i] - runs[i]) * self.RUN_LENGTH_WEIGHT

                self._score_cache[cache_key] = score
                return score

        def _evaluate_flip(self, state: BeamState, move: List[Tuple[int, int]]):
                """
                Calculates score AND new black count incrementally.
                """
                new_r_scores = list(state.row_scores)
                new_c_scores = list(state.col_scores)
                new_black_count = state.black_count

                affected_rows = set()
                affected_cols = set()

                for r, c in move:
                        affected_rows.add(r)
                        affected_cols.add(c)
                        # Update black count based on flip
                        if state.board[r][c] == self.WHITE:
                                new_black_count += 1  # White -> Black
                        else:
                                new_black_count -= 1  # Black -> White

                for r in affected_rows:
                        line = list(state.board[r])
                        for fr, fc in move:
                                if fr == r:
                                        line[fc] = (
                                                self.WHITE
                                                if line[fc] == self.BLACK
                                                else self.BLACK
                                        )
                        new_r_scores[r] = self._calculate_line_score(line, self.rows[r])

                for c in affected_cols:
                        line = [state.board[row][c] for row in range(self.height)]
                        for fr, fc in move:
                                if fc == c:
                                        line[fr] = (
                                                self.WHITE
                                                if line[fr] == self.BLACK
                                                else self.BLACK
                                        )
                        new_c_scores[c] = self._calculate_line_score(
                                line, self.columns[c]
                        )

                total = sum(new_r_scores) + sum(new_c_scores)
                return total, new_r_scores, new_c_scores, new_black_count

        def _apply_flip(self, board, move):
                new_board = [row[:] for row in board]
                for r, c in move:
                        new_board[r][c] = (
                                self.WHITE
                                if new_board[r][c] == self.BLACK
                                else self.BLACK
                        )
                return new_board

        def _get_violated_cells(self, state: BeamState):
                v_rows = [r for r, s in enumerate(state.row_scores) if s > 0]
                v_cols = [c for c, s in enumerate(state.col_scores) if s > 0]
                return [(r, c) for r in v_rows for c in v_cols]

        def _generate_moves(self, candidate_cells, state: BeamState):
                moves = []
                limit = min(len(candidate_cells), self.neighbor_combination_cap)
                sample = random.sample(candidate_cells, limit)
                for cell in sample:
                        moves.append([cell])

                # If we have too many blacks, prefer flipping Black->White
                # If we have too few, prefer White->Black.
                # This biases the Double-Flips to fix the count.
                if len(candidate_cells) > 1:
                        for _ in range(5):
                                pair = random.sample(candidate_cells, 2)
                                moves.append(pair)
                return moves

        def _generate_random_board(self):
                # Try to respect density roughly
                # This helps the search start closer to the target black count
                total_cells = self.width * self.height
                target = getattr(self, "target_black_count", total_cells // 2)
                prob = max(0.1, min(0.9, target / total_cells))

                return [
                        [
                                self.BLACK if random.random() < prob else self.WHITE
                                for _ in range(self.width)
                        ]
                        for _ in range(self.height)
                ]

        def _hash_board(self, board):
                return tuple(tuple(row) for row in board)
