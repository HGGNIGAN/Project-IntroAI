from algorithms.base import NonogramSolver

import random
import math
from copy import deepcopy

class LSSolver(NonogramSolver):
    name = "Local Search Solver"
    description = "Solves Nonogram puzzles using Hill-climbing with random restart."
    def __init__(self):
        super().__init__()

    def _solve_internal(self):
        self.total_ones = sum(sum(row) for row in self.rows)

        max_restart = 50
        max_step = 5000
        initial_temp = 5.0
        cooling_rate = 0.995

        for i in range(max_restart):
            self.grid = self._random_initial_grid()
            temperature = initial_temp
            current_cost = self._evaluate()
            for j in range(max_step):
                if current_cost == 0:
                    return self.grid
                neighbor = self._random_neighbor()
                neighbor_cost = self._evaluate(neighbor)
                cost = neighbor_cost - current_cost
                if cost <=0 or random.random() < math.exp(-cost/temperature):
                    self.grid = neighbor
                    current_cost = neighbor_cost
                temperature *= cooling_rate
        raise RuntimeError("Local search failed to find a solution.")
    
    def _random_initial_grid(self):
        grid = [[0] * self.width for _ in range(self.height)]
        cells = [(r, c) for r in range(self.height) for c in range(self.width)]
        random.shuffle(cells)

        for r,c in cells[:self.total_ones]:
            grid[r][c] = 1
        return grid
    
    def _random_neighbor(self):
        one = [(r, c) for r in range(self.height) for c in range(self.width) if self.grid[r][c] == 1]
        zero = [(r, c) for r in range(self.height) for c in range(self.width) if self.grid[r][c] == 0]
        r1, c1 = random.choice(one)
        r0, c0 = random.choice(zero)

        new_grid = deepcopy(self.grid)
        new_grid[r1][c1] = 0
        new_grid[r0][c0] = 1
        return new_grid
    
    def _evaluate(self, grid=None):
        if grid is None:
            grid = self.grid
        cost = 0

        for r in range(self.height):
            cost += abs(self._line_cost(grid[r], self.rows[r]))

        for c in range(self.width):
            col = [grid[r][c] for r in range(self.height)]
            cost += abs(self._line_cost(col, self.columns[c]))
        return cost
    
    def _line_cost(self, line, clues):
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
        cost = abs(len(blocks) - len(clues))
        for b, c in zip(blocks, clues):
            cost += abs(b - c)
        return cost
    
