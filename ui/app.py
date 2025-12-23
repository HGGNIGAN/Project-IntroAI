"""Main UI application for puzzle configuration and solution display."""

import tkinter as tk
from tkinter import ttk, messagebox
from .configurator import ConfiguratorUI
from .display_nonogram import create_canvas_from_grid
from algorithms import get_solver


class NonogramSolverApp:
        """Main application window."""

        def __init__(self, root):
                """Initialize the application."""
                self.root = root
                self.root.minsize(440, 500)
                self.root.title("Nonogram Solver")
                self.root.geometry("800x600")

                # Create notebook for tabs
                self.notebook = ttk.Notebook(self.root)
                self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

                # Configurator tab
                self.config_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.config_frame, text="Configure Puzzle")

                self.configurator = ConfiguratorUI(
                        self.config_frame, callback=self.on_solve
                )

                # Solution tab
                self.solution_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.solution_frame, text="Solution")

                # Status label
                self.status_label = ttk.Label(
                        self.solution_frame,
                        text="No solution generated yet. Configure and solve a puzzle.",
                        relief="sunken",
                )
                self.status_label.pack(side="bottom", fill="x", padx=5, pady=5)

                # Solution canvas container
                self.canvas_frame = ttk.Frame(self.solution_frame)
                self.canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)

        def on_solve(self, config, algorithm_name):
                """
                Handle solve action.

                Args:
                    config: Configuration dictionary from configurator
                    algorithm_name: Name of the selected algorithm
                """
                try:
                        width = config["width"]
                        height = config["height"]

                        # Convert stored dict clues into ordered lists for solvers
                        rows_dict = config.get("rows", {})
                        cols_dict = config.get("columns", {})
                        rows = [rows_dict.get(str(i), []) for i in range(height)]
                        columns = [cols_dict.get(str(i), []) for i in range(width)]

                        ruleset = {
                                "width": width,
                                "height": height,
                                "rows": rows,
                                "columns": columns,
                        }

                        # Get the selected solver
                        solver = get_solver(algorithm_name)
                        if not solver:
                                raise ValueError(f"Solver '{algorithm_name}' not found")

                        # Call the selected algorithm
                        solution = solver.solve(ruleset)

                        # Display solution in the solution tab
                        self.display_solution(solution)

                        # Switch to solution tab
                        self.notebook.select(1)
                        self.root.update()  # Force UI update

                        self.status_label.config(
                                text=f"Solution generated for {width}x{height} puzzle using {algorithm_name}",
                                foreground="green",
                        )
                except Exception as e:
                        messagebox.showerror(
                                "Solve Error", f"Error solving puzzle: {str(e)}"
                        )
                        self.status_label.config(
                                text=f"Error: {str(e)}", foreground="red"
                        )

        def display_solution(self, grid):
                """
                Display the solution grid.

                Args:
                    grid: 2D list representing the solution
                """
                # Clear previous canvas
                for widget in self.canvas_frame.winfo_children():
                        widget.destroy()

                # Create canvas
                canvas = create_canvas_from_grid(self.canvas_frame, grid)
                canvas.pack(side="left", fill="both", expand=True)

                # Create info panel
                info_frame = ttk.LabelFrame(
                        self.canvas_frame, text="Solution Info", padding="10"
                )
                info_frame.pack(side="right", fill="y", padx=5)

                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 0

                ttk.Label(info_frame, text=f"Size: {cols}x{rows}").pack(
                        anchor="w", pady=5
                )

                # Count filled cells
                filled = sum(sum(row) for row in grid)
                total = rows * cols
                ttk.Label(info_frame, text=f"Filled: {filled}/{total}").pack(
                        anchor="w", pady=5
                )


def main():
        """Run the main application."""
        root = tk.Tk()
        app = NonogramSolverApp(root)
        root.mainloop()


if __name__ == "__main__":
        main()
