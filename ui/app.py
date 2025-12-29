"""Main UI application for puzzle configuration and solution display."""

import multiprocessing
import queue
import tkinter as tk
from tkinter import messagebox, ttk

from .configurator import ConfiguratorUI
from .display_nonogram import create_canvas_from_grid


def solve_process_worker(solver_name, ruleset, rows_dict, cols_dict, result_queue):
        """
        Independent process that runs the solver.
        """
        try:
                # Re-import inside process to avoid pickling issues
                from algorithms import get_solver

                solver = get_solver(solver_name)

                if not solver:
                        raise ValueError(f"Solver '{solver_name}' not found")

                # Heavy computation happens here
                solution = solver.solve(ruleset)

                result = {
                        "status": "success",
                        "solution": solution,
                        "rows_dict": rows_dict,
                        "cols_dict": cols_dict,
                        "algorithm_name": solver_name,
                        "width": ruleset["width"],
                        "height": ruleset["height"],
                }
                result_queue.put(result)
        except Exception as e:
                result_queue.put({"status": "error", "message": str(e)})


class NonogramSolverApp:
        """Main application window."""

        def __init__(self, root):
                self.root = root
                self.root.minsize(440, 500)
                self.root.title("Nonogram Solver")
                self.root.geometry("800x600")

                self.cached_solution = None
                self.cached_row_clues = None
                self.cached_col_clues = None

                # Multiprocessing tools
                self.solve_queue = multiprocessing.Queue()
                self.current_process = None
                self.is_solving = False

                self.notebook = ttk.Notebook(self.root)
                self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

                self.config_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.config_frame, text="Configure Puzzle")

                self.configurator = ConfiguratorUI(
                        self.config_frame, callback=self.on_solve
                )
                self.configurator.set_cache_invalidator(self.invalidate_solution_cache)

                # Get the main container (child of config_frame)
                main_container = self.configurator.parent.winfo_children()[0]

                # Get the button frame (last child of main_container)
                # This is the frame that actually holds the other buttons
                button_frame = main_container.winfo_children()[-1]

                self.stop_button = ttk.Button(
                        button_frame,
                        text="Stop Solving",
                        command=self.stop_solving,
                        state="disabled",
                )
                self.stop_button.pack(side="left", padx=5, pady=8)

                self.solution_frame = ttk.Frame(self.notebook)
                self.notebook.add(self.solution_frame, text="Solution")

                # Grid layout for solution_frame
                self.solution_frame.grid_rowconfigure(0, weight=1)  # Content expands
                self.solution_frame.grid_rowconfigure(1, weight=0)  # Status stays fixed
                self.solution_frame.grid_columnconfigure(0, weight=1)

                # Solution canvas container with scrollbars
                self.canvas_frame = ttk.Frame(self.solution_frame)
                self.canvas_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
                # Grid for canvas_frame
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
                if self.is_solving:
                        return

                try:
                        width = config["width"]
                        height = config["height"]
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

                        self.is_solving = True
                        self.status_label.config(
                                text=f"Solving... ({algorithm_name})", foreground="blue"
                        )
                        self.root.config(cursor="watch")
                        self.stop_button.config(state="normal")  # Enable Stop button

                        # Start Process
                        self.current_process = multiprocessing.Process(
                                target=solve_process_worker,
                                args=(
                                        algorithm_name,
                                        ruleset,
                                        rows_dict,
                                        cols_dict,
                                        self.solve_queue,
                                ),
                        )
                        self.current_process.daemon = True
                        self.current_process.start()

                        self.root.after(100, self._check_solve_queue)

                except Exception as e:
                        self.cleanup_solve_state()
                        messagebox.showerror(
                                "Error", f"Error preparing puzzle: {str(e)}"
                        )

        def stop_solving(self):
                """Manually kill the solving process."""
                if (
                        self.is_solving
                        and self.current_process
                        and self.current_process.is_alive()
                ):
                        # FORCE KILL THE PROCESS
                        self.current_process.terminate()
                        self.current_process.join()

                        self.cleanup_solve_state()
                        self.status_label.config(
                                text="Solving stopped by user.", foreground="orange"
                        )
                        messagebox.showinfo("Stopped", "Solver process terminated.")

        def _check_solve_queue(self):
                try:
                        result = self.solve_queue.get_nowait()

                        self.cleanup_solve_state()

                        if result["status"] == "success":
                                self._handle_solve_success(result)
                        else:
                                self._handle_solve_error(result["message"])

                except queue.Empty:
                        if self.is_solving:
                                self.root.after(100, self._check_solve_queue)

        def cleanup_solve_state(self):
                """Resets UI and process variables."""
                self.is_solving = False
                self.current_process = None
                self.root.config(cursor="")
                self.stop_button.config(state="disabled")

        def _handle_solve_success(self, result):
                grid = result["solution"]
                rows_dict = result["rows_dict"]
                cols_dict = result["cols_dict"]
                algo_name = result["algorithm_name"]

                self.cached_solution = grid
                self.cached_row_clues = rows_dict
                self.cached_col_clues = cols_dict

                self.display_solution(grid, rows_dict, cols_dict)
                self.notebook.select(1)

                self.status_label.config(
                        text=f"Solved {result['width']}x{result['height']} using {algo_name}",
                        foreground="green",
                )

        def _handle_solve_error(self, error_message):
                messagebox.showerror(
                        "Solve Error", f"Error solving puzzle: {error_message}"
                )
                self.status_label.config(
                        text=f"Error: {error_message}", foreground="red"
                )

        def invalidate_solution_cache(self):
                """Clear cached solution when configuration changes."""
                self.cached_solution = None
                self.cached_row_clues = None
                self.cached_col_clues = None
                # Remove previously-displayed solution
                for widget in self.canvas_frame.winfo_children():
                        widget.destroy()

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
                                return
                        grid = self.cached_solution
                        row_clues = self.cached_row_clues
                        col_clues = self.cached_col_clues

                # Clear previous widgets from canvas_frame
                for widget in self.canvas_frame.winfo_children():
                        widget.destroy()

                # Frame holding scrollable content and info panel
                content_frame = ttk.Frame(self.canvas_frame)
                content_frame.grid(row=0, column=0, sticky="nsew")
                # Configure grid for content_frame
                content_frame.grid_rowconfigure(0, weight=1)
                content_frame.grid_columnconfigure(0, weight=1)
                content_frame.grid_columnconfigure(1, weight=0)

                # Scrollable container for the grid display
                v_scrollbar = ttk.Scrollbar(content_frame, orient="vertical")
                v_scrollbar.grid(row=0, column=1, sticky="ns")
                h_scrollbar = ttk.Scrollbar(content_frame, orient="horizontal")
                h_scrollbar.grid(row=1, column=0, sticky="ew")

                # Canvas for scrolling
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

                # Frame holding the grid display; must be a direct child of canvas
                grid_container = tk.Frame(canvas)
                # Grid display frame
                grid_display = create_canvas_from_grid(
                        grid_container, grid, row_clues, col_clues
                )
                grid_display.pack(fill="both", expand=False)

                # Canvas window with the grid container
                canvas_window = canvas.create_window(
                        0, 0, window=grid_container, anchor="nw"
                )

                def update_scroll_region(event=None):
                        canvas.configure(scrollregion=canvas.bbox("all"))
                        canvas.itemconfig(
                                canvas_window,
                                width=max(
                                        canvas.winfo_width(),
                                        grid_container.winfo_reqwidth(),
                                ),
                        )

                grid_container.bind("<Configure>", update_scroll_region)
                canvas.bind("<Configure>", update_scroll_region)

                # Handle mouse wheel scrolling
                def _on_mousewheel(event):
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

                def _on_shift_mousewheel(event):
                        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

                canvas.bind("<MouseWheel>", _on_mousewheel)
                canvas.bind("<Shift-MouseWheel>", _on_shift_mousewheel)

                # Info panel
                info_frame = ttk.LabelFrame(
                        content_frame, text="Solution Info", padding="10"
                )
                info_frame.grid(row=0, column=2, sticky="n", padx=5, pady=5)
                rows = len(grid)
                cols = len(grid[0]) if rows > 0 else 0
                filled = sum(sum(row) for row in grid)
                ttk.Label(info_frame, text=f"Size: {cols}x{rows}").pack(
                        anchor="w", pady=5
                )
                ttk.Label(info_frame, text=f"Filled: {filled}/{rows * cols}").pack(
                        anchor="w", pady=5
                )


def main():
        multiprocessing.freeze_support()
        root = tk.Tk()
        app = NonogramSolverApp(root)
        root.mainloop()


if __name__ == "__main__":
        main()
