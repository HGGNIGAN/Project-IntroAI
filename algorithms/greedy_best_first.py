import heapq
from copy import deepcopy
from itertools import combinations

import numpy as np

from .base import NonogramSolver


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
                return NonogramState(
                        deepcopy(self.board),
                        deepcopy(self.rows_possible),
                        deepcopy(self.cols_possible),
                )

        def is_goal(self):
                for row in self.board:
                        if 0 in row:
                                return False
                return True

        def get_hash(self):
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
                                return current.board

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
                        possibilities.append(res)
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
                undecided_rows = sum(1 for p in state.rows_possible if len(p) > 1)
                undecided_cols = sum(1 for p in state.cols_possible if len(p) > 1)
                return min(undecided_rows, undecided_cols)

        def _get_deterministic_cells(self, possibilities):
                if not possibilities:
                        return []
                result = []
                arr = np.array(possibilities)
                for i, col in enumerate(arr.T):
                        if len(np.unique(col)) == 1:
                                result.append((i, col[0]))
                return result

        def _remove_possibilities(self, possibilities, i, val):
                return [p for p in possibilities if p[i] == val]

        def _apply_constraint_propagation(self, state):
                changed = True
                while changed:
                        changed = False
                        for i in range(state.m):
                                if not state.rows_possible[i]:
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
                                                if not state.cols_possible[j]:
                                                        return None
                                                changed = True
                        for j in range(state.n):
                                if not state.cols_possible[j]:
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
                                                if not state.rows_possible[i]:
                                                        return None
                                                changed = True
                return state

        def _get_next_cell(self, state):
                min_opts = float("inf")
                best_cell = None
                for i in range(state.m):
                        for j in range(state.n):
                                if state.board[i][j] == 0:
                                        row_vals = set(
                                                p[j] for p in state.rows_possible[i]
                                        )
                                        col_vals = set(
                                                p[i] for p in state.cols_possible[j]
                                        )
                                        opts = row_vals & col_vals

                                        if not opts:
                                                return None

                                        if len(opts) < min_opts:
                                                min_opts = len(opts)
                                                best_cell = (i, j, opts)
                return best_cell
