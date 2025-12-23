import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .config_manager import ConfigManager
from algorithms import list_solvers, get_solver_info


class ConfiguratorUI:
        """UI for configuring nonogram puzzles."""

        def __init__(self, parent, callback=None):
                """
                Initialize the configurator UI.

                Args:
                    parent: Parent tkinter widget
                    callback: Function to call when solving (receives config)
                """
                self.parent = parent
                self.callback = callback
                self.config_manager = ConfigManager()
                self.row_entries = {}
                self.col_entries = {}
                self._loading = False  # Flag to prevent auto-save during loading
                self.setup_ui()
                self.load_default_config()

        def setup_ui(self):
                """Setup the configurator UI."""
                # Main container using grid layout
                main_container = ttk.Frame(self.parent)
                main_container.pack(fill="both", expand=True, padx=10, pady=10)

                # Configure grid weights - row 0 expands, row 1 (button) stays fixed
                main_container.grid_rowconfigure(0, weight=1)
                main_container.grid_rowconfigure(1, weight=0)
                main_container.grid_columnconfigure(0, weight=1)

                # Content frame (scrollable area)
                content_frame = ttk.LabelFrame(
                        main_container, text="Puzzle Configuration", padding="10"
                )
                content_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

                # Algorithm selection section
                algo_frame = ttk.LabelFrame(
                        content_frame, text="Solver Algorithm", padding="10"
                )
                algo_frame.pack(fill="x", pady=10)

                ttk.Label(algo_frame, text="Algorithm:").grid(
                        row=0, column=0, sticky="w", padx=5, pady=5
                )

                # Get available algorithms
                self.available_algorithms = list_solvers()
                if not self.available_algorithms:
                        self.available_algorithms = ["No algorithms found"]

                self.algorithm_var = tk.StringVar(
                        value=self.available_algorithms[0]
                        if self.available_algorithms
                        else ""
                )
                algo_combo = ttk.Combobox(
                        algo_frame,
                        textvariable=self.algorithm_var,
                        values=self.available_algorithms,
                        state="readonly",
                        width=30,
                )
                algo_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
                algo_combo.bind("<<ComboboxSelected>>", self.on_algorithm_change)

                # Algorithm description
                self.algo_desc_label = ttk.Label(
                        algo_frame, text="", foreground="gray", wraplength=400
                )
                self.algo_desc_label.grid(
                        row=1, column=0, columnspan=2, sticky="w", padx=5, pady=(0, 5)
                )
                self.update_algorithm_description()

                # Dimensions section
                dim_frame = ttk.LabelFrame(
                        content_frame, text="Puzzle Dimensions", padding="10"
                )
                dim_frame.pack(fill="x", pady=10)

                # Width
                ttk.Label(dim_frame, text="Width:").grid(
                        row=0, column=0, sticky="w", padx=5, pady=5
                )
                self.width_var = tk.IntVar(value=5)
                width_spinbox = ttk.Spinbox(
                        dim_frame, from_=1, to=20, textvariable=self.width_var, width=10
                )
                width_spinbox.grid(row=0, column=1, sticky="w", padx=5, pady=5)

                # Height
                ttk.Label(dim_frame, text="Height:").grid(
                        row=1, column=0, sticky="w", padx=5, pady=5
                )
                self.height_var = tk.IntVar(value=5)
                height_spinbox = ttk.Spinbox(
                        dim_frame,
                        from_=1,
                        to=20,
                        textvariable=self.height_var,
                        width=10,
                )
                height_spinbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)

                # Clues section
                clues_frame = ttk.LabelFrame(
                        content_frame, text="Row/Column Clues", padding="10"
                )
                clues_frame.pack(fill="both", expand=True, pady=10)

                # Create notebook for tabs
                self.notebook = ttk.Notebook(clues_frame)
                self.notebook.pack(fill="both", expand=True)

                self.row_frame = ttk.Frame(self.notebook)
                self.col_frame = ttk.Frame(self.notebook)

                self.notebook.add(self.row_frame, text="Rows")
                self.notebook.add(self.col_frame, text="Columns")

                # Initialize clue entries
                self.update_clue_entries()

                # Fixed button frame at the bottom (always visible) - uses grid row 1
                button_frame = ttk.Frame(main_container)
                button_frame.grid(row=1, column=0, sticky="ew")

                ttk.Button(button_frame, text="Solve Puzzle", command=self.solve).pack(
                        side="left", padx=5, pady=8
                )

                # Bind dimension changes to update clue entries and auto-save
                self.width_var.trace("w", lambda *args: self.on_dimension_change())
                self.height_var.trace("w", lambda *args: self.on_dimension_change())

        def load_default_config(self):
                """Load the default config file on startup if it exists."""
                if self.config_manager.load_config():
                        width, height = self.config_manager.get_dimensions()
                        # Temporarily disable auto-save during loading
                        self._loading = True
                        self.width_var.set(width)
                        self.height_var.set(height)
                        self.update_clue_entries()
                        self._loading = False

        def update_clue_entries(self):
                """Update clue entry fields based on current dimensions."""
                width = self.width_var.get()
                height = self.height_var.get()

                # Clear existing widgets
                for widget in self.row_frame.winfo_children():
                        widget.destroy()
                for widget in self.col_frame.winfo_children():
                        widget.destroy()

                # Create scrollable frames
                self.row_entries = {}
                self.col_entries = {}

                # Configure grid layout for row_frame
                self.row_frame.grid_rowconfigure(0, weight=1)
                self.row_frame.grid_columnconfigure(0, weight=1)

                # Row clues with grid layout
                row_canvas = tk.Canvas(self.row_frame, highlightthickness=0)
                row_scrollbar = ttk.Scrollbar(
                        self.row_frame, orient="vertical", command=row_canvas.yview
                )
                row_scrollable_frame = ttk.Frame(row_canvas)

                row_scrollable_frame.bind(
                        "<Configure>",
                        lambda e: row_canvas.configure(
                                scrollregion=row_canvas.bbox("all")
                        ),
                )

                row_canvas.create_window(
                        (0, 0), window=row_scrollable_frame, anchor="nw"
                )
                row_canvas.configure(yscrollcommand=row_scrollbar.set)

                for i in range(height):
                        ttk.Label(row_scrollable_frame, text=f"Row {i}:").grid(
                                row=i, column=0, sticky="w", padx=5, pady=5
                        )
                        entry = ttk.Entry(
                                row_scrollable_frame, width=30, style="NoFocus.TEntry"
                        )
                        entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                        self.row_entries[i] = entry
                        clues = self.config_manager.get_row_clue(i)
                        if clues:
                                entry.insert(0, ",".join(map(str, clues)))
                        # Bind entry changes to auto-save
                        entry.bind(
                                "<KeyRelease>",
                                lambda *args, idx=i: self.on_entry_change(idx),
                        )

                row_canvas.grid(row=0, column=0, sticky="nsew")
                row_scrollbar.grid(row=0, column=1, sticky="ns")
                self._attach_mousewheel_scroll(row_canvas)

                # Configure grid layout for col_frame
                self.col_frame.grid_rowconfigure(0, weight=1)
                self.col_frame.grid_columnconfigure(0, weight=1)

                # Column clues with grid layout
                col_canvas = tk.Canvas(self.col_frame, highlightthickness=0)
                col_scrollbar = ttk.Scrollbar(
                        self.col_frame, orient="vertical", command=col_canvas.yview
                )
                col_scrollable_frame = ttk.Frame(col_canvas)

                col_scrollable_frame.bind(
                        "<Configure>",
                        lambda e: col_canvas.configure(
                                scrollregion=col_canvas.bbox("all")
                        ),
                )

                col_canvas.create_window(
                        (0, 0), window=col_scrollable_frame, anchor="nw"
                )
                col_canvas.configure(yscrollcommand=col_scrollbar.set)

                for i in range(width):
                        ttk.Label(col_scrollable_frame, text=f"Col {i}:").grid(
                                row=i, column=0, sticky="w", padx=5, pady=5
                        )
                        entry = ttk.Entry(
                                col_scrollable_frame, width=30, style="NoFocus.TEntry"
                        )
                        entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                        self.col_entries[i] = entry
                        entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)
                        self.col_entries[i] = entry
                        clues = self.config_manager.get_column_clue(i)
                        if clues:
                                entry.insert(0, ",".join(map(str, clues)))
                        # Bind entry changes to auto-save
                        entry.bind(
                                "<KeyRelease>",
                                lambda *args, idx=i: self.on_entry_change(
                                        idx, is_row=False
                                ),
                        )

                col_canvas.grid(row=0, column=0, sticky="nsew")
                col_scrollbar.grid(row=0, column=1, sticky="ns")
                self._attach_mousewheel_scroll(col_canvas)

        def on_algorithm_change(self, event=None):
                """Handle algorithm selection change."""
                self.update_algorithm_description()

        def update_algorithm_description(self):
                """Update the algorithm description label."""
                selected = self.algorithm_var.get()
                if selected and selected != "No algorithms found":
                        info = get_solver_info(selected)
                        if info:
                                self.algo_desc_label.config(text=info["description"])
                        else:
                                self.algo_desc_label.config(text="")
                else:
                        self.algo_desc_label.config(text="")

        def on_dimension_change(self):
                """Handle dimension changes and auto-save."""
                if self._loading:
                        return  # Skip auto-save during initial load
                width = self.width_var.get()
                height = self.height_var.get()
                self.config_manager.set_dimensions(width, height)
                self.update_clue_entries()
                self.auto_save()

        def on_entry_change(self, index, is_row=True):
                """Handle clue entry changes and auto-save."""
                if self._loading:
                        return  # Skip auto-save during initial load
                self.collect_clues()
                self.auto_save()

        def collect_clues(self):
                """Collect clues from entry fields into config."""
                for i, entry in self.row_entries.items():
                        clue_text = entry.get().strip()
                        if clue_text:
                                try:
                                        clues = [
                                                int(x.strip())
                                                for x in clue_text.split(",")
                                                if x.strip()
                                        ]
                                        self.config_manager.set_row_clue(i, clues)
                                except ValueError:
                                        # Silently skip invalid entries (don't show dialog on every keystroke)
                                        pass
                        else:
                                self.config_manager.set_row_clue(i, [])

                for i, entry in self.col_entries.items():
                        clue_text = entry.get().strip()
                        if clue_text:
                                try:
                                        clues = [
                                                int(x.strip())
                                                for x in clue_text.split(",")
                                                if x.strip()
                                        ]
                                        self.config_manager.set_column_clue(i, clues)
                                except ValueError:
                                        # Silently skip invalid entries (don't show dialog on every keystroke)
                                        pass
                        else:
                                self.config_manager.set_column_clue(i, [])

        def auto_save(self):
                """Automatically save configuration to default file."""
                self.config_manager.save_config()

        def _attach_mousewheel_scroll(self, canvas):
                """Wire the standard wheel/trackpad events to the given Canvas."""

                def _on_mousewheel(event):
                        if event.delta:
                                canvas.yview_scroll(int(-event.delta / 120), "units")
                        elif event.num == 4:
                                canvas.yview_scroll(-1, "units")
                        elif event.num == 5:
                                canvas.yview_scroll(1, "units")

                canvas.bind(
                        "<Enter>",
                        lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel),
                )
                canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
                canvas.bind("<Button-4>", _on_mousewheel)
                canvas.bind("<Button-5>", _on_mousewheel)

        def solve(self):
                """Solve the puzzle with current configuration."""
                self.collect_clues()
                is_valid, message = self.config_manager.validate_config()

                if not is_valid:
                        messagebox.showerror("Invalid Configuration", message)
                        return

                # Check if a valid algorithm is selected
                selected_algo = self.algorithm_var.get()
                if not selected_algo or selected_algo == "No algorithms found":
                        messagebox.showerror(
                                "No Algorithm",
                                "Please select a valid solver algorithm.",
                        )
                        return

                if self.callback:
                        config = self.config_manager.get_config()
                        self.callback(config, selected_algo)
                else:
                        messagebox.showinfo(
                                "Config",
                                f"Configuration:\n{self.config_manager.get_config()}",
                        )
