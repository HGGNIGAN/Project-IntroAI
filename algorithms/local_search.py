import math
import random

from algorithms.__base__ import NonogramSolver


class LocalSearchSolver(NonogramSolver):
        name = "Local Search"
        description = "Simulated annealing with constraint propagation and min-conflict heuristics"

        def __init__(
                self,
                max_steps=30000,
                max_restarts=20,
                temperature=3.0,
                cooling=0.999,
                repair_interval=60,
                reheat_interval=2500,
                mutation_samples=5,
        ):
                self.max_steps = max_steps
                self.max_restarts = max_restarts
                self.temperature = temperature
                self.cooling = cooling
                self.repair_interval = repair_interval
                self.reheat_interval = reheat_interval
                self.mutation_samples = mutation_samples

        def _solve_internal(self):
                # 1. Generate initial domains
                self.row_patterns = [
                        self._generate_patterns(self.width, clues)
                        for clues in self.rows
                ]
                # Generate column patterns solely for logical pruning
                self.col_patterns = [
                        self._generate_patterns(self.height, clues)
                        for clues in self.columns
                ]

                self.column_targets = [sum(clues) for clues in self.columns]
                self.total_required = sum(self.column_targets)

                # 2. LOGICAL PREPROCESSING: Prune the search space
                self._logical_pruning()

                # Check for immediate impossibility
                if any(not p for p in self.row_patterns):
                        raise RuntimeError(
                                "Puzzle proven impossible during preprocessing."
                        )

                for _ in range(self.max_restarts):
                        state = self._biased_initial_state()
                        cost = self._column_cost(state)

                        if cost == 0:
                                return state

                        T = self.temperature

                        # Track current column sums for fast heuristic updates
                        # (used by guided mutation)
                        current_col_sums = [
                                sum(state[r][c] for r in range(self.height))
                                for c in range(self.width)
                        ]

                        for step in range(self.max_steps):
                                if step % self.reheat_interval == 0:
                                        T = self.temperature

                                # Periodically fix the worst column entirely
                                if step % self.repair_interval == 0:
                                        col = self._most_violated_column(state)
                                        self._repair_column(state, col)
                                        # Recompute sums after heavy repair
                                        current_col_sums = [
                                                sum(
                                                        state[r][c]
                                                        for r in range(self.height)
                                                )
                                                for c in range(self.width)
                                        ]
                                        cost = self._column_cost(state)

                                bad_rows = self._conflicting_rows(state)
                                row = (
                                        random.choice(bad_rows)
                                        if bad_rows
                                        else random.randrange(self.height)
                                )

                                old_pattern = state[row]

                                # 3. GUIDED MUTATION: Pick 'best of k' instead of random
                                new_pattern = self._guided_selection(
                                        row, current_col_sums
                                )

                                state[row] = new_pattern
                                new_cost = self._column_cost(state)
                                delta = new_cost - cost

                                if delta <= 0 or random.random() < math.exp(
                                        -delta / max(T, 1e-6)
                                ):
                                        cost = new_cost
                                        # Update column sums to keep heuristic accurate
                                        for c in range(self.width):
                                                current_col_sums[c] += (
                                                        new_pattern[c] - old_pattern[c]
                                                )
                                else:
                                        state[row] = old_pattern  # Revert

                                if cost == 0:
                                        return state

                                T *= self.cooling

                raise RuntimeError("Local search failed to find a solution")

        def _logical_pruning(self):
                """
                Iteratively intersects patterns to find fixed cells (must be 0 or must be 1).
                Uses these fixed cells to remove invalid patterns from domains.
                """
                fixed_board = [[-1] * self.width for _ in range(self.height)]
                changed = True

                while changed:
                        changed = False

                        # --- ROW PASS ---
                        for r in range(self.height):
                                possible = self.row_patterns[r]
                                if not possible:
                                        continue

                                # Filter based on current fixed board knowledge
                                filtered = []
                                for p in possible:
                                        valid = True
                                        for c in range(self.width):
                                                if (
                                                        fixed_board[r][c] != -1
                                                        and fixed_board[r][c] != p[c]
                                                ):
                                                        valid = False
                                                        break
                                        if valid:
                                                filtered.append(p)

                                if len(filtered) < len(possible):
                                        self.row_patterns[r] = filtered
                                        changed = True
                                        possible = filtered

                                # Deduce new fixed cells from remaining patterns
                                # If all patterns have 1 at pos c, then board[r][c] is 1.
                                if possible:
                                        for c in range(self.width):
                                                if fixed_board[r][c] == -1:
                                                        val = possible[0][c]
                                                        if all(
                                                                pat[c] == val
                                                                for pat in possible
                                                        ):
                                                                fixed_board[r][c] = val
                                                                changed = True

                        # --- COLUMN PASS ---
                        for c in range(self.width):
                                possible = self.col_patterns[c]
                                if not possible:
                                        continue

                                # Filter based on current fixed board knowledge
                                filtered = []
                                for p in possible:
                                        valid = True
                                        for r in range(self.height):
                                                if (
                                                        fixed_board[r][c] != -1
                                                        and fixed_board[r][c] != p[r]
                                                ):
                                                        valid = False
                                                        break
                                        if valid:
                                                filtered.append(p)

                                if len(filtered) < len(possible):
                                        self.col_patterns[c] = filtered
                                        changed = True
                                        possible = filtered

                                # Deduce new fixed cells
                                if possible:
                                        for r in range(self.height):
                                                if fixed_board[r][c] == -1:
                                                        val = possible[0][r]
                                                        if all(
                                                                pat[r] == val
                                                                for pat in possible
                                                        ):
                                                                fixed_board[r][c] = val
                                                                changed = True

        def _guided_selection(self, row_idx, current_col_sums):
                """
                Selects a pattern from the domain that minimizes deviation from column targets.
                Uses a random sample (size k) to avoid scanning huge domains every step.
                """
                candidates = self.row_patterns[row_idx]

                # If domain is small, check all. If large, sample 'mutation_samples'
                if len(candidates) > self.mutation_samples:
                        selection_pool = random.sample(
                                candidates, self.mutation_samples
                        )
                else:
                        selection_pool = candidates

                best_p = selection_pool[0]
                best_score = float("inf")

                # Heuristic: difference in column sums.
                # Avoids the expensive full _column_cost calculation.
                for p in selection_pool:
                        # Score = sum of how far the new column sums would be from targets
                        # We want column_sum == target.
                        score = 0
                        for c in range(self.width):
                                # Predict new sum: current_sum - old_bit + new_bit

                                diff = self.column_targets[c] - current_col_sums[c]
                                # If diff > 0, we need more 1s. If p[c] is 1, good.
                                # If diff < 0, we have too many 1s. If p[c] is 0, good.
                                if p[c] == 1:
                                        score += -diff  # Reward if we need ones (diff positive), punish if we don't
                                else:
                                        score += diff  # Opposite

                        if score < best_score:
                                best_score = score
                                best_p = p

                return best_p

        def _generate_patterns(self, length, clues):
                if not clues:
                        return [[0] * length]
                patterns = []
                MAX_PATTERNS = 5000

                def backtrack(pos, idx, current):
                        if len(patterns) >= MAX_PATTERNS:
                                return
                        if idx == len(clues):
                                patterns.append(current + [0] * (length - pos))
                                return
                        block = clues[idx]
                        for start in range(pos, length - block + 1):
                                new = current + [0] * (start - pos) + [1] * block
                                if start + block < length:
                                        backtrack(start + block + 1, idx + 1, new + [0])
                                else:
                                        backtrack(start + block, idx + 1, new)

                backtrack(0, 0, [])
                return patterns

        def _biased_initial_state(self):
                state = []
                col_counts = [0] * self.width
                for r in range(self.height):
                        # Pick random from filtered list because the list is now "smart"
                        chosen = random.choice(self.row_patterns[r])
                        state.append(chosen)
                        for c in range(self.width):
                                col_counts[c] += chosen[c]
                return state

        def _column_cost(self, state):
                cost = 0
                total_filled = 0
                for c, clues in enumerate(self.columns):
                        column = [state[r][c] for r in range(self.height)]
                        blocks = self._extract_blocks(column)
                        filled = sum(column)
                        total_filled += filled
                        target = sum(clues)
                        cost += abs(filled - target) * 3
                        cost += abs(len(blocks) - len(clues)) * 4
                        for a, b in zip(blocks, clues):
                                cost += max(0, a - b)
                                cost += abs(a - b)
                        if len(blocks) > len(clues):
                                cost += sum(blocks[len(clues) :]) * 2
                        transitions = sum(
                                column[i] != column[i + 1]
                                for i in range(len(column) - 1)
                        )
                        cost += max(0, transitions - 2 * len(clues))
                        if blocks:
                                cost += max(0, blocks[0] - clues[0])
                                cost += max(0, blocks[-1] - clues[-1])
                        required = sum(clues) + max(0, len(clues) - 1)
                        cost += max(0, required - self.height) * 10
                cost += abs(total_filled - self.total_required)
                return cost

        def _conflicting_rows(self, state):
                bad = set()
                for c, clues in enumerate(self.columns):
                        column = [state[r][c] for r in range(self.height)]
                        if self._extract_blocks(column) == clues:
                                continue
                        for r in range(self.height):
                                if state[r][c] == 1:
                                        bad.add(r)
                return list(bad)

        def _most_violated_column(self, state):
                worst_col = 0
                worst_cost = -1
                for c, clues in enumerate(self.columns):
                        column = [state[r][c] for r in range(self.height)]
                        cost = abs(sum(column) - sum(clues)) + abs(
                                len(self._extract_blocks(column)) - len(clues)
                        )
                        if cost > worst_cost:
                                worst_cost = cost
                                worst_col = c
                return worst_col

        def _repair_column(self, state, col):
                r = random.randrange(self.height)
                best_row = state[r]
                best_cost = self._column_cost(state)
                # Check all filtered patterns, or a subset if still large
                domain = self.row_patterns[r]
                if len(domain) > 20:
                        domain = random.sample(domain, 20)

                for pattern in domain:
                        state[r] = pattern
                        cost = self._column_cost(state)
                        if cost < best_cost:
                                best_cost = cost
                                best_row = pattern
                state[r] = best_row

        def _extract_blocks(self, line):
                blocks = []
                count = 0
                for cell in line:
                        if cell == 1:
                                count += 1
                        elif count > 0:
                                blocks.append(count)
                                count = 0
                if count > 0:
                        blocks.append(count)
                return blocks
