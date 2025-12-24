"""Mock solver algorithm for testing purposes."""

from .base import NonogramSolver


class MockSolver(NonogramSolver):
        """A mock solver that generates a simple filled pattern."""

        name = "Mock Solver (All Filled)"
        description = (
                "A simple test solver that fills all cells. Used for testing the UI."
        )

        def _solve_internal(self):
                """
                Generate a simple pattern with all cells filled.

                Returns:
                - list: A 2D list representing the generated pattern.
                """
                print(f"Mock Solver - Width: {self.width}, Height: {self.height}")
                print(f"Mock Solver - Rows: {self.rows}")
                print(f"Mock Solver - Columns: {self.columns}")

                # Fill all cells
                for y in range(self.height):
                        for x in range(self.width):
                                self.grid[y][x] = 1

                return self.grid
