"""Base class for nonogram solver algorithms."""

from abc import ABC, abstractmethod


class NonogramSolver(ABC):
        """Abstract base class for nonogram solving algorithms."""

        name: str = "Base Solver"
        description: str = "Base solver class"

        def solve(self, ruleset):
                """
                Solve a nonogram puzzle.

                Automatically initializes instance variables and calls _solve_internal().

                Parameters:
                - ruleset (dict): A dictionary containing the puzzle configuration.
                                 Expected format: {
                                     'width': int,
                                     'height': int,
                                     'rows': [[clues for row 0], [clues for row 1], ...],
                                     'columns': [[clues for col 0], [clues for col 1], ...]
                                 }

                Returns:
                - list: A 2D list representing the solved puzzle grid.
                        Each cell is 0 (empty) or 1 (filled).
                """
                # Initialize instance variables for use in subclass methods
                self.width = ruleset["width"]
                self.height = ruleset["height"]
                self.rows = ruleset["rows"]
                self.columns = ruleset["columns"]
                self.grid = [[0] * self.width for _ in range(self.height)]

                # Call subclass implementation
                return self._solve_internal()

        @abstractmethod
        def _solve_internal(self):
                """
                Internal solving method to be implemented by subclasses.

                Instance variables available:
                - self.width: Puzzle width
                - self.height: Puzzle height
                - self.rows: List of row clues
                - self.columns: List of column clues
                - self.grid: 2D list initialized with zeros (modify this to create solution)

                Returns:
                - list: A 2D list representing the solved puzzle grid.
                        Each cell is 0 (empty) or 1 (filled).
                """
                raise NotImplementedError(
                        "Subclasses must implement the _solve_internal method"
                )

        def __str__(self):
                """Return string representation of the solver."""
                return self.name

        def __repr__(self):
                """Return detailed string representation of the solver."""
                return f"{self.__class__.__name__}(name='{self.name}')"
