"""Random nonogram puzzle generator."""

import random


class PuzzleGenerator:
        """Generate random nonogram puzzles and their clues."""

        @staticmethod
        def generate_random_puzzle(width, height, config_manager):
                """
                Generate a random puzzle and update the config manager with clues.

                Args:
                    width: Puzzle width
                    height: Puzzle height
                    config_manager: ConfigManager instance to update with generated clues

                Returns:
                    list: The generated random grid (2D array of 0s and 1s)
                """
                # Create random 2D array (0 or 1)
                random_grid = [
                        [random.randint(0, 1) for _ in range(width)]
                        for _ in range(height)
                ]

                # Print to terminal
                print("\n" + "=" * 50)
                print("Generated Random Puzzle")
                print("=" * 50)
                print(f"Dimensions: {width}x{height}\n")
                print("Grid (1 = filled, 0 = empty):")
                for row in random_grid:
                        print("  " + " ".join(str(cell) for cell in row))
                print()

                # Generate row clues
                row_clues = {}
                for r, row in enumerate(random_grid):
                        clues = PuzzleGenerator._generate_clues_from_line(row)
                        row_clues[str(r)] = clues
                        print(f"Row {r}: {clues}")

                print()

                # Generate column clues
                col_clues = {}
                for c in range(width):
                        column = [random_grid[r][c] for r in range(height)]
                        clues = PuzzleGenerator._generate_clues_from_line(column)
                        col_clues[str(c)] = clues
                        print(f"Col {c}: {clues}")

                print("=" * 50 + "\n")

                # Update config with generated clues
                for r, clues in row_clues.items():
                        config_manager.set_row_clue(int(r), clues)
                for c, clues in col_clues.items():
                        config_manager.set_column_clue(int(c), clues)

                # Save config
                config_manager.save_config()

                return random_grid

        @staticmethod
        def _generate_clues_from_line(line):
                """
                Generate clue numbers from a line of 1s and 0s.

                Args:
                    line: List of 0s and 1s

                Returns:
                    list: Clue numbers representing consecutive filled cells
                """
                clues = []
                count = 0
                for cell in line:
                        if cell == 1:
                                count += 1
                        elif count > 0:
                                clues.append(count)
                                count = 0
                if count > 0:
                        clues.append(count)
                return clues
