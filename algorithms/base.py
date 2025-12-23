"""Base class for nonogram solver algorithms."""

from abc import ABC, abstractmethod


class NonogramSolver(ABC):
        """Abstract base class for nonogram solving algorithms."""

        name: str = "Base Solver"
        description: str = "Base solver class"

        @abstractmethod
        def solve(self, ruleset):
                """
                Solve a nonogram puzzle.

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
                raise NotImplementedError("Subclasses must implement the solve method")

        def __str__(self):
                """Return string representation of the solver."""
                return self.name

        def __repr__(self):
                """Return detailed string representation of the solver."""
                return f"{self.__class__.__name__}(name='{self.name}')"
