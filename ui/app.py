"""Main UI application for puzzle configuration and solution display."""

import tkinter as tk
from tkinter import messagebox, ttk

from algorithms import get_solver

from .configurator import ConfiguratorUI
from .display_nonogram import create_canvas_from_grid


class NonogramSolverApp:
        """Main application window."""

        def __init__(self, root):
                """Initialize the application."""
                self.root = root
                self.root.minsize(440, 500)
                self.root.title("Nonogram Solver")
                self.root.geometry("800x600")

                # Cache for the current solution
                self.cached_solution = None
                self.cached_row_clues = None
                self.cached_col_clues = None

                # Create notebook for tabs
                self.notebook = ttk.Notebook(self.root)
                self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

                # Configurator tab
                self.config_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.config_frame, text="Configure Puzzle")

                self.configurator = ConfiguratorUI(
                        self.config_frame, callback=self.on_solve
                )
                # Set callback to invalidate solution cache when config changes
                self.configurator.set_cache_invalidator(self.invalidate_solution_cache)
                self.solution_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.solution_frame, text="Solution")

                # Configure grid layout for solution_frame
                self.solution_frame.grid_rowconfigure(0, weight=1)  # Content expands
                self.solution_frame.grid_rowconfigure(1, weight=0)  # Status stays fixed
                self.solution_frame.grid_columnconfigure(0, weight=1)

                # Solution canvas container with scrollbars
                self.canvas_frame = ttk.Frame(self.solution_frame)
                self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

                # Configure grid for canvas_frame
                self.canvas_frame.grid_rowconfigure(0, weight=1)
                self.canvas_frame.grid_columnconfigure(0, weight=1)

                # Status label
                self.status_label = ttk.Label(
                        self.solution_frame,
                        text="No solution generated yet. Configure and solve a puzzle.",
                        relief="sunken",
                )
                self.status_label.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

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

                        # Cache the solution in memory
                        self.cached_solution = solution
                        self.cached_row_clues = rows_dict
                        self.cached_col_clues = cols_dict

                        # Display solution in the solution tab with clues
                        self.display_solution(solution, rows_dict, cols_dict)

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

        def invalidate_solution_cache(self):
                """Clear cached solution when configuration changes."""
                self.cached_solution = None
                self.cached_row_clues = None
                self.cached_col_clues = None
                self.status_label.config(
                        text="Solution outdated. Solve again to update.",
                        foreground="orange",
                )

        def display_solution(self, grid=None, row_clues=None, col_clues=None):
                """
                Display the solution grid with clues.

                Args:
                    grid: 2D list representing the solution (uses cache if None)
                    row_clues: Optional dict of row clues (uses cache if None)
                    col_clues: Optional dict of column clues (uses cache if None)
                """
                # Use cached solution if available and no new grid provided
                if grid is None:
                        if self.cached_solution is None:
                                self.status_label.config(
                                        text="No solution generated yet. Configure and solve a puzzle.",
                                        foreground="gray",
                                )
                                return
                        grid = self.cached_solution
                        row_clues = self.cached_row_clues
                        col_clues = self.cached_col_clues

                # Clear previous widgets from canvas_frame
                for widget in self.canvas_frame.winfo_children():
                        widget.destroy()

                # Create a frame to hold scrollable content and info panel
                content_frame = ttk.Frame(self.canvas_frame)
                content_frame.grid(row=0, column=0, sticky="nsew")

                # Configure grid for content_frame
                content_frame.grid_rowconfigure(0, weight=1)
                content_frame.grid_columnconfigure(0, weight=1)
                content_frame.grid_columnconfigure(1, weight=0)

                # Create scrollable container for the grid display
                # Vertical scrollbar
                v_scrollbar = ttk.Scrollbar(content_frame, orient="vertical")
                v_scrollbar.grid(row=0, column=1, sticky="ns")

                # Horizontal scrollbar
                h_scrollbar = ttk.Scrollbar(content_frame, orient="horizontal")
                h_scrollbar.grid(row=1, column=0, sticky="ew")

                # Create canvas for scrolling
                canvas = tk.Canvas(
                        content_frame,
                        bg="white",
                        yscrollcommand=v_scrollbar.set,
                        xscrollcommand=h_scrollbar.set,
                        highlightthickness=0,
                )
                canvas.grid(row=0, column=0, sticky="nsew")

                # Configure scrollbars to control canvas
                v_scrollbar.config(command=canvas.yview)
                h_scrollbar.config(command=canvas.xview)

                # Create a frame to hold the grid display - this must be a direct child of canvas
                grid_container = tk.Frame(canvas)

                # Create the grid display frame
                grid_display = create_canvas_from_grid(
                        grid_container, grid, row_clues, col_clues
                )
                grid_display.pack(fill="both", expand=False)

                # Create window in canvas with the grid container
                canvas_window = canvas.create_window(
                        0, 0, window=grid_container, anchor="nw"
                )

                # Update scroll region after grid is configured
                def update_scroll_region(event=None):
                        canvas.configure(scrollregion=canvas.bbox("all"))
                        # Make canvas window span full width for horizontal centering if desired
                        canvas.itemconfig(
                                canvas_window,
                                width=max(
                                        canvas.winfo_width(),
                                        grid_container.winfo_reqwidth(),
                                ),
                        )

                grid_container.bind("<Configure>", update_scroll_region)
                canvas.bind("<Configure>", update_scroll_region)

                # Bind mousewheel to canvas
                self._setup_mousewheel_scrolling(canvas)

                # Create info panel (always visible on the right)
                info_frame = ttk.LabelFrame(
                        content_frame, text="Solution Info", padding="10"
                )
                info_frame.grid(row=0, column=2, sticky="n", padx=5, pady=5)

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

        def _setup_mousewheel_scrolling(self, canvas):
                """Setup mousewheel scrolling for the canvas."""

                def _on_mousewheel(event):
                        # Windows mousewheel scrolling
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

                def _on_shift_mousewheel(event):
                        # Shift+mousewheel for horizontal scrolling
                        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

                def _on_linux_scroll_up(event):
                        # Linux scroll up
                        canvas.yview_scroll(-3, "units")

                def _on_linux_scroll_down(event):
                        # Linux scroll down
                        canvas.yview_scroll(3, "units")

                def _on_linux_scroll_left(event):
                        # Linux scroll left
                        canvas.xview_scroll(-3, "units")

                def _on_linux_scroll_right(event):
                        # Linux scroll right
                        canvas.xview_scroll(3, "units")

                # Bind mousewheel events
                canvas.bind("<MouseWheel>", _on_mousewheel)
                canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)

                # Linux scrolling events
                canvas.bind("<Button-4>", _on_linux_scroll_up)
                canvas.bind("<Button-5>", _on_linux_scroll_down)
                canvas.bind("<Shift-Button-4>", _on_linux_scroll_left)
                canvas.bind("<Shift-Button-5>", _on_linux_scroll_right)


def main():
        """Run the main application."""
        root = tk.Tk()
        app = NonogramSolverApp(root)
        root.mainloop()


if __name__ == "__main__":
        main()
