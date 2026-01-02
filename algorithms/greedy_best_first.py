import heapq
from itertools import combinations

import numpy as np

from .__base__ import NonogramSolver


class NonogramState:
        _state_counter = 0

        def __init__(self, board, rows_possible, cols_possible):
                self.board = board
                self.rows_possible = rows_possible
                self.cols_possible = cols_possible
                self.m = len(board)
                self.n = len(board[0])
                self.counter = NonogramState._state_counter
                NonogramState._state_counter += 1

        def __lt__(self, other):
                return self.counter < other.counter

        def copy(self):
                # Manual deep copy is significantly faster than copy.deepcopy for NumPy structures
                return NonogramState(
                        [row[:] for row in self.board],
                        [p.copy() for p in self.rows_possible],
                        [p.copy() for p in self.cols_possible],
                )

        def is_goal(self):
                for row in self.board:
                        if 0 in row:
                                return False
                return True

        def get_hash(self):
                # Hash the board state and the size of the possibility space
                return (
                        tuple(tuple(row) for row in self.board),
                        tuple(len(r) for r in self.rows_possible),
                        tuple(len(c) for c in self.cols_possible),
                )


class GreedyBestFirstSolver(NonogramSolver):
        name = "Greedy Best-First Search"
        description = "Uses heuristic-guided search with forward checking (constraint propagation)."

        def _solve_internal(self):
                rows_possible = self._create_possibilities(self.rows, self.width)
                cols_possible = self._create_possibilities(self.columns, self.height)

                # Create initial state
                initial_state = NonogramState(self.grid, rows_possible, cols_possible)
                initial_state = self._apply_constraint_propagation(initial_state)

                if initial_state is None:
                        return None

                open_set = []
                visited = set()
                h0 = self._heuristic(initial_state)
                heapq.heappush(open_set, (h0, initial_state))

                iterations = 0
                max_iterations = 100000

                while open_set and iterations < max_iterations:
                        iterations += 1
                        _, current = heapq.heappop(open_set)

                        if current.is_goal():
                                final_board = [
                                        [0 if cell == -1 else cell for cell in row]
                                        for row in current.board
                                ]
                                return final_board

                        current_hash = current.get_hash()
                        if current_hash in visited:
                                continue
                        visited.add(current_hash)

                        cell_info = self._get_next_cell(current)
                        if cell_info is None:
                                continue

                        i, j, possible_vals = cell_info

                        for val in possible_vals:
                                new_state = current.copy()
                                new_state.board[i][j] = val

                                new_state.rows_possible[i] = self._remove_possibilities(
                                        new_state.rows_possible[i], j, val
                                )
                                new_state.cols_possible[j] = self._remove_possibilities(
                                        new_state.cols_possible[j], i, val
                                )

                                # Propagate constraints
                                new_state = self._apply_constraint_propagation(
                                        new_state
                                )

                                if new_state is not None:
                                        new_hash = new_state.get_hash()
                                        if new_hash not in visited:
                                                h = self._heuristic(new_state)
                                                heapq.heappush(open_set, (h, new_state))

                return None

        def _create_possibilities(self, values, no_of_other):
                possibilities = []
                for v in values:
                        groups = len(v)
                        no_empty = no_of_other - sum(v) - groups + 1
                        ones = [[1] * x for x in v]
                        res = self._create_line_permutations(no_empty, groups, ones)
                        possibilities.append(np.array(res, dtype=np.int8))
                return possibilities

        def _create_line_permutations(self, no_empty, groups, ones):
                res_opts = []
                for p in combinations(range(groups + no_empty), groups):
                        selected = [-1] * (groups + no_empty)
                        ones_ind = 0
                        for val in p:
                                selected[val] = ones_ind
                                ones_ind += 1
                        res_opt = [
                                ones[val] + [-1] if val > -1 else [-1]
                                for val in selected
                        ]
                        res_opt = [item for sublist in res_opt for item in sublist][:-1]
                        res_opts.append(res_opt)
                return res_opts

        def _heuristic(self, state):
                # Count rows/cols with >1 possibility remaining
                undecided_rows = sum(1 for p in state.rows_possible if len(p) > 1)
                undecided_cols = sum(1 for p in state.cols_possible if len(p) > 1)
                return min(undecided_rows, undecided_cols)

        def _get_deterministic_cells(self, possibilities_array):
                if possibilities_array.size == 0:
                        return []

                # If min(col) == max(col), then all values in that column are the same
                mins = possibilities_array.min(axis=0)
                maxs = possibilities_array.max(axis=0)

                # Find indices where the column is uniform
                deterministic_indices = np.where(mins == maxs)[0]

                # Zip the index with the value (we can take from mins or maxs)
                if len(deterministic_indices) > 0:
                        return list(
                                zip(deterministic_indices, mins[deterministic_indices])
                        )
                return []

        def _remove_possibilities(self, possibilities_array, index, val):
                # Boolean masking
                mask = possibilities_array[:, index] == val
                return possibilities_array[mask]

        def _apply_constraint_propagation(self, state):
                changed = True
                while changed:
                        changed = False
                        # Check Rows
                        for i in range(state.m):
                                if len(state.rows_possible[i]) == 0:
                                        return None

                                cells = self._get_deterministic_cells(
                                        state.rows_possible[i]
                                )
                                for j, val in cells:
                                        if state.board[i][j] == 0:
                                                state.board[i][j] = val
                                                state.cols_possible[j] = (
                                                        self._remove_possibilities(
                                                                state.cols_possible[j],
                                                                i,
                                                                val,
                                                        )
                                                )
                                                if len(state.cols_possible[j]) == 0:
                                                        return None
                                                changed = True

                        # Check Columns
                        for j in range(state.n):
                                if len(state.cols_possible[j]) == 0:
                                        return None

                                cells = self._get_deterministic_cells(
                                        state.cols_possible[j]
                                )
                                for i, val in cells:
                                        if state.board[i][j] == 0:
                                                state.board[i][j] = val
                                                state.rows_possible[i] = (
                                                        self._remove_possibilities(
                                                                state.rows_possible[i],
                                                                j,
                                                                val,
                                                        )
                                                )
                                                if len(state.rows_possible[i]) == 0:
                                                        return None
                                                changed = True
                return state

        def _get_next_cell(self, state):
                min_opts = float("inf")
                best_cell = None

                for i in range(state.m):
                        for j in range(state.n):
                                if state.board[i][j] == 0:
                                        row_vals = np.unique(
                                                state.rows_possible[i][:, j]
                                        )
                                        col_vals = np.unique(
                                                state.cols_possible[j][:, i]
                                        )

                                        opts = np.intersect1d(row_vals, col_vals)

                                        if len(opts) == 0:
                                                return None

                                        if len(opts) < min_opts:
                                                min_opts = len(opts)
                                                best_cell = (i, j, opts)
                                                # If we find a cell with only 1 option, it's the best possible move. Return immediately.
                                                if min_opts == 1:
                                                        return best_cell

                return best_cell
