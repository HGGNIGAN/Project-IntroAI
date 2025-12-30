from algorithms.base import NonogramSolver
import random
import math

class LSSolver(NonogramSolver):
    name = "Local Search Solver"
    description = "Local search solver based on simulated annealing with random restarts"

    def __init__(
        self,
        max_steps=20000,
        max_restarts=100,
        temperature=3.0,
        cooling=0.999,
        repair_interval=60,
        reheat_interval=2500,
    ):
        self.max_steps = max_steps
        self.max_restarts = max_restarts
        self.temperature = temperature
        self.cooling = cooling
        self.repair_interval = repair_interval
        self.reheat_interval = reheat_interval

    def _solve_internal(self):
        self.row_patterns = [
            self._generate_patterns(self.width, clues)
            for clues in self.rows
        ]
        self.column_targets = [sum(clues) for clues in self.columns]
        self.total_required = sum(self.column_targets)
        for _ in range(self.max_restarts):
            state = self._biased_initial_state()
            cost = self._column_cost(state)
            if cost == 0:
                return state
            T = self.temperature
            for step in range(self.max_steps):
                if step % self.reheat_interval == 0:
                    T = self.temperature
                if step % self.repair_interval == 0:
                    col = self._most_violated_column(state)
                    self._repair_column(state, col)

                bad_rows = self._conflicting_rows(state)
                row = random.choice(bad_rows) if bad_rows else random.randrange(self.height)
                old_row = state[row]
                state[row] = random.choice(self.row_patterns[row])
                new_cost = self._column_cost(state)
                delta = new_cost - cost

                if delta <= 0 or random.random() < math.exp(-delta / max(T, 1e-6)):
                    cost = new_cost
                else:
                    state[row] = old_row
                if cost == 0:
                    return state
                T *= self.cooling
        raise RuntimeError("Local search failed to find a solution")

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
            patterns = sorted(
                self.row_patterns[r],
                key=lambda p: sum(
                    abs(col_counts[c] + p[c] - self.column_targets[c])
                    for c in range(self.width)
                )
            )
            chosen = random.choice(patterns[: max(5, len(patterns) // 10)])
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
                cost += sum(blocks[len(clues):]) * 2
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
            cost = abs(sum(column) - sum(clues)) + abs(len(self._extract_blocks(column)) - len(clues))
            if cost > worst_cost:
                worst_cost = cost
                worst_col = c
        return worst_col

    def _repair_column(self, state, col):
        r = random.randrange(self.height)
        best_row = state[r]
        best_cost = self._column_cost(state)
        for pattern in self.row_patterns[r]:
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
