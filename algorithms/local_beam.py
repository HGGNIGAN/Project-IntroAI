import heapq
import random
from typing import List, Tuple

from .base import NonogramSolver


class BeamState:
        """
        Object storing a candidate solution and its cached scores.
        """

        def __init__(self, board, row_scores, col_scores, black_count):
                self.board = board
                self.row_scores = row_scores
                self.col_scores = col_scores
                self.black_count = black_count
                # Base heuristic: just the line violations
                self.heuristic_score = sum(row_scores) + sum(col_scores)
                # Final score will be calculated dynamically

        def __lt__(self, other):
                # Tie-breaker for heap
                return self.heuristic_score < other.heuristic_score


class LocalBeamSolver(NonogramSolver):
        name = "Local Beam Search"
        description = "Local Beam Search with Swap-moves and Guided Perturbation."

        # Internal state constants
        WHITE = 0
        BLACK = 1

        # --- Scoring Weights ---
        # Increase the run_length_weight to force correct block sizes
        RUN_COUNT_WEIGHT = 50  # Huge penalty for wrong number of blocks
        RUN_LENGTH_WEIGHT = 2  # Moderate penalty for wrong sizes
        GLOBAL_COUNT_WEIGHT = 100  # Massive penalty for wrong total pixel count

        # --- Search Parameters ---
        beam_width = 40  # Sufficient for 10x10 - 20x20
        max_iterations = 5000
        stagnation_threshold = 30

        # --- Mutation Parameters ---
        perturbation_ratio = 0.05  # Flip 5% of board during soft reset

        def _solve_internal(self) -> List[List[int]]:
                # Pre-calculate global target (Total black cells needed)
                self.target_black_count = sum(sum(row_clues) for row_clues in self.rows)
                self._score_cache = {}

                # Initialize Beams
                current_beams = []
                for _ in range(self.beam_width):
                        board = self._generate_smart_random_board()
                        state = self._create_state(board)
                        current_beams.append(state)

                best_global_score = float("inf")
                best_global_board = None
                iterations_without_improvement = 0

                # Main Loop
                for iteration in range(self.max_iterations):
                        # --- Score Calculation ---
                        # Calculate final score with global penalty
                        for beam in current_beams:
                                count_diff = abs(
                                        beam.black_count - self.target_black_count
                                )
                                # If count is perfect, score is just heuristic. If not, massive penalty.
                                beam.final_score = beam.heuristic_score + (
                                        count_diff * self.GLOBAL_COUNT_WEIGHT
                                )

                        # Sort best first
                        current_beams.sort(key=lambda x: x.final_score)
                        best_beam = current_beams[0]

                        # Success check
                        if best_beam.final_score == 0:
                                print(f"Solution found at iteration {iteration}!")
                                return best_beam.board

                        # Progress check
                        if best_beam.final_score < best_global_score:
                                best_global_score = best_beam.final_score
                                best_global_board = best_beam.board
                                iterations_without_improvement = 0
                        else:
                                iterations_without_improvement += 1

                        # --- Generate Neighbors ---
                        candidates_heap = []

                        # Always keep current beams as candidates (Elitism)
                        for beam in current_beams:
                                heapq.heappush(
                                        candidates_heap,
                                        (beam.final_score, random.random(), beam),
                                )

                        # Generate new moves
                        for beam in current_beams:
                                # Decide Strategy: FLIP vs SWAP
                                # If we are close to the correct black count, SWAP is mandatory to avoid penalties.
                                count_diff = abs(
                                        beam.black_count - self.target_black_count
                                )
                                use_swap = (
                                        count_diff < 5
                                )  # Threshold: if count is off by < 5, try swapping

                                moves = self._generate_moves(beam, use_swap=use_swap)

                                for move in moves:
                                        if use_swap:
                                                # Move is ((r1, c1), (r2, c2))
                                                p1, p2 = move
                                                h_score, r_s, c_s, new_cnt = (
                                                        self._evaluate_swap(
                                                                beam, p1, p2
                                                        )
                                                )
                                        else:
                                                # Move is [(r,c), ...]
                                                h_score, r_s, c_s, new_cnt = (
                                                        self._evaluate_flip(beam, move)
                                                )

                                        # Calculate penalty
                                        new_diff = abs(
                                                new_cnt - self.target_black_count
                                        )
                                        final_score = h_score + (
                                                new_diff * self.GLOBAL_COUNT_WEIGHT
                                        )

                                        # Add potential candidates to heap
                                        heapq.heappush(
                                                candidates_heap,
                                                (
                                                        final_score,
                                                        random.random(),
                                                        (
                                                                beam,
                                                                move,
                                                                r_s,
                                                                c_s,
                                                                new_cnt,
                                                                use_swap,
                                                        ),
                                                ),
                                        )

                        # --- Selection ---
                        next_beams = []
                        seen_hashes = set()

                        # Take top K unique
                        while len(next_beams) < self.beam_width and candidates_heap:
                                score, _, item = heapq.heappop(candidates_heap)

                                if isinstance(item, BeamState):
                                        # Existing beam
                                        b_hash = self._hash_board(item.board)
                                        if b_hash not in seen_hashes:
                                                next_beams.append(item)
                                                seen_hashes.add(b_hash)
                                else:
                                        # New Candidate
                                        parent, move, r_s, c_s, cnt, is_swap = item

                                        if is_swap:
                                                new_board = self._apply_swap(
                                                        parent.board, move[0], move[1]
                                                )
                                        else:
                                                new_board = self._apply_flip(
                                                        parent.board, move
                                                )

                                        b_hash = self._hash_board(new_board)
                                        if b_hash not in seen_hashes:
                                                next_beams.append(
                                                        BeamState(
                                                                new_board, r_s, c_s, cnt
                                                        )
                                                )
                                                seen_hashes.add(b_hash)

                        # --- Stagnation Handling (Soft Reset) ---
                        if iterations_without_improvement >= self.stagnation_threshold:
                                # "Kick" the system: Keep the best one, but perturb the rest based on the best one
                                best_current = current_beams[0]
                                next_beams = [best_current]  # Keep the best

                                # Fill the rest with neighbors of the best solution instead of random noise
                                while len(next_beams) < self.beam_width:
                                        mutated_board = self._perturb_board(
                                                best_current.board
                                        )
                                        next_beams.append(
                                                self._create_state(mutated_board)
                                        )

                                iterations_without_improvement = 0

                        current_beams = next_beams

                print(f"Solution not found. Best score: {best_global_score}")
                return best_global_board  # type: ignore

        # ------------------------------------------------------------------
        # Core Logic
        # ------------------------------------------------------------------

        def _generate_moves(self, state: BeamState, use_swap: bool):
                """
                Generates moves.
                If use_swap is True, find a Black cell in a bad row and moves it to a White cell.
                """
                violated_rows = [r for r, s in enumerate(state.row_scores) if s > 0]
                violated_cols = [c for c, s in enumerate(state.col_scores) if s > 0]

                # If perfect heuristic but score > 0 (sanity), force random
                if not violated_rows and not violated_cols:
                        violated_rows = list(range(self.height))
                        violated_cols = list(range(self.width))

                moves = []

                if use_swap:
                        # Generate SWAP moves (Move Black -> White)
                        # 1. Find a black cell involved in a violation
                        candidates_black = []
                        # Check violated rows for black cells
                        for r in violated_rows:
                                for c in range(self.width):
                                        if state.board[r][c] == self.BLACK:
                                                candidates_black.append((r, c))
                        # Check violated cols for black cells
                        for c in violated_cols:
                                for r in range(self.height):
                                        if state.board[r][c] == self.BLACK:
                                                candidates_black.append((r, c))

                        # 2. Find a white cell involved in a violation
                        candidates_white = []
                        for r in violated_rows:
                                for c in range(self.width):
                                        if state.board[r][c] == self.WHITE:
                                                candidates_white.append((r, c))
                        for c in violated_cols:
                                for r in range(self.height):
                                        if state.board[r][c] == self.WHITE:
                                                candidates_white.append((r, c))

                        # 3. Create pairs
                        candidates_black = list(set(candidates_black))
                        candidates_white = list(set(candidates_white))

                        # Randoml pair
                        if candidates_black and candidates_white:
                                for _ in range(20):  # Generate 20 random swaps
                                        b = random.choice(candidates_black)
                                        w = random.choice(candidates_white)
                                        if b != w:
                                                moves.append((b, w))
                else:
                        # Generate FLIP moves (Standard)
                        # Intersect rows and cols to find "hot spots"
                        candidates = set()
                        for r in violated_rows:
                                for c in violated_cols:
                                        candidates.add((r, c))

                        cand_list = list(candidates)
                        if not cand_list:  # Fallback
                                cand_list = [
                                        (r, c)
                                        for r in violated_rows
                                        for c in range(self.width)
                                ]

                        # Sample single flips
                        sample_size = min(len(cand_list), 20)
                        for cell in random.sample(cand_list, sample_size):
                                moves.append([cell])

                return moves

        def _evaluate_swap(
                self, state: BeamState, p1: Tuple[int, int], p2: Tuple[int, int]
        ):
                """Evaluate swapping cell p1 (Black) with p2 (White)."""
                # Count remains identical, so new_cnt = old_cnt
                # We assume p1 is BLACK and p2 is WHITE for logic simplicity

                r1, c1 = p1
                r2, c2 = p2

                # If they are same color, no change (shouldn't happen by logic above)
                if state.board[r1][c1] == state.board[r2][c2]:
                        return (
                                state.heuristic_score,
                                state.row_scores,
                                state.col_scores,
                                state.black_count,
                        )

                # Temporary flip both to simulate swap
                move = [p1, p2]
                return self._evaluate_flip(state, move)

        def _apply_swap(self, board, p1, p2):
                new_board = [row[:] for row in board]
                # Swap values
                val1 = new_board[p1[0]][p1[1]]
                val2 = new_board[p2[0]][p2[1]]
                new_board[p1[0]][p1[1]] = val2
                new_board[p2[0]][p2[1]] = val1
                return new_board

        def _evaluate_flip(self, state: BeamState, move: List[Tuple[int, int]]):
                """Incremental Evaluation."""
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

        # --- Utilities ---

        def _create_state(self, board):
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

                # Weighted Score
                # High penalty for wrong number of blocks (structure is wrong)
                score = abs(len(clues) - len(runs)) * self.RUN_COUNT_WEIGHT
                # Smaller penalty for wrong lengths (details are wrong)
                for i in range(min(len(clues), len(runs))):
                        score += abs(clues[i] - runs[i]) * self.RUN_LENGTH_WEIGHT

                self._score_cache[cache_key] = score
                return score

        def _generate_smart_random_board(self):
                """Generates a random board that roughly matches the density needed."""
                total_cells = self.width * self.height
                target = getattr(self, "target_black_count", total_cells // 2)
                prob = target / total_cells
                return [
                        [1 if random.random() < prob else 0 for _ in range(self.width)]
                        for _ in range(self.height)
                ]

        def _perturb_board(self, board):
                """Flip a small % of cells to escape local optima."""
                new_board = [row[:] for row in board]
                num_flips = max(
                        1, int((self.width * self.height) * self.perturbation_ratio)
                )
                for _ in range(num_flips):
                        r = random.randint(0, self.height - 1)
                        c = random.randint(0, self.width - 1)
                        new_board[r][c] = 1 - new_board[r][c]
                return new_board

        def _hash_board(self, board):
                return tuple(tuple(row) for row in board)
