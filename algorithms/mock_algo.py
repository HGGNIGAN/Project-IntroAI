"""Mock solver algorithm for testing purposes."""

from .base import NonogramSolver


class MockSolver(NonogramSolver):
        """A mock solver that generates a simple filled pattern."""

        name = "Mock Solver (All Filled)"
        description = (
                "A simple test solver that fills all cells. Used for testing the UI."
        )

        def solve(self, ruleset):
                """
                Generate a simple pattern with all cells filled.

                Parameters:
                - ruleset (dict): A dictionary defining the puzzle configuration.

                Returns:
                - list: A 2D list representing the generated pattern.
                """
                print(f"Mock Solver - Ruleset: {ruleset}")

                width = ruleset["width"]
                height = ruleset["height"]

                pattern = []
                for y in range(height):
                        row = []
                        for x in range(width):
                                row.append(1)
                        pattern.append(row)
                return pattern
