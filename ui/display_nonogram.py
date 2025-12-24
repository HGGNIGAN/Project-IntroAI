import tkinter as tk
from tkinter import ttk

# Configuration
CELL_SIZE = 30  # Size of each square in pixels
CLUE_SIZE = 25  # Size of clue cells in pixels


def create_canvas_from_grid(parent, grid, row_clues=None, col_clues=None):
        """
        Create a frame displaying the nonogram grid with clues.

        Args:
            parent: Parent tkinter widget
            grid: 2D list representing the puzzle solution
            row_clues: Optional dict of row clues {index: [clue_numbers]}
            col_clues: Optional dict of col clues {index: [clue_numbers]}

        Returns:
            tk.Frame: The frame containing the nonogram display
        """
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        # Calculate max clue counts to determine clue area sizes
        max_col_clues = 0
        max_row_clues = 0

        if col_clues:
                for c in range(cols):
                        clue_list = col_clues.get(str(c), [])
                        max_col_clues = max(max_col_clues, len(clue_list))

        if row_clues:
                for r in range(rows):
                        clue_list = row_clues.get(str(r), [])
                        max_row_clues = max(max_row_clues, len(clue_list))

        # Create main frame for grid + clues
        main_frame = ttk.Frame(parent)

        # Top left corner (blank area) - spans multiple rows and columns
        for corner_row in range(max_col_clues):
                for corner_col in range(max_row_clues):
                        corner_cell = tk.Canvas(
                                main_frame,
                                width=CELL_SIZE,
                                height=CELL_SIZE,
                                bg="lightgray",
                        )
                        corner_cell.grid(
                                row=corner_row, column=corner_col, sticky="nsew"
                        )

        # Column clues (top) - stacked vertically, bottom-aligned
        if col_clues:
                for c in range(cols):
                        clue_list = col_clues.get(str(c), [])
                        # Bottom-align: pad from top with empty space
                        offset = max_col_clues - len(clue_list)
                        for idx, clue_num in enumerate(clue_list):
                                clue_canvas = tk.Canvas(
                                        main_frame,
                                        width=CELL_SIZE,
                                        height=CELL_SIZE,
                                        bg="lightgray",
                                )
                                clue_canvas.create_text(
                                        CELL_SIZE // 2,
                                        CELL_SIZE // 2,
                                        text=str(clue_num),
                                        font=("Arial", 9),
                                        fill="black",
                                )
                                clue_canvas.grid(
                                        row=offset + idx,
                                        column=max_row_clues + c,
                                        sticky="nsew",
                                )

        # Row clues (left) - arranged horizontally, right-aligned
        for r in range(rows):
                if row_clues:
                        clue_list = row_clues.get(str(r), [])
                        # Right-align: pad from left with empty space
                        offset = max_row_clues - len(clue_list)
                        for idx, clue_num in enumerate(clue_list):
                                clue_canvas = tk.Canvas(
                                        main_frame,
                                        width=CELL_SIZE,
                                        height=CELL_SIZE,
                                        bg="lightgray",
                                )
                                clue_canvas.create_text(
                                        CELL_SIZE // 2,
                                        CELL_SIZE // 2,
                                        text=str(clue_num),
                                        font=("Arial", 9),
                                        fill="black",
                                )
                                clue_canvas.grid(
                                        row=max_col_clues + r,
                                        column=offset + idx,
                                        sticky="nsew",
                                )

                # Grid cells for this row
                for c in range(cols):
                        value = grid[r][c]

                        # Determine color: 1 = Black, 0 = White
                        color = "black" if value == 1 else "white"

                        # Create cell canvas
                        cell = tk.Canvas(
                                main_frame, width=CELL_SIZE, height=CELL_SIZE, bg=color
                        )
                        cell.create_rectangle(
                                0, 0, CELL_SIZE, CELL_SIZE, fill=color, outline="gray"
                        )
                        cell.grid(
                                row=max_col_clues + r,
                                column=max_row_clues + c,
                                sticky="nsew",
                        )

        return main_frame


def display(grid, row_clues=None, col_clues=None):
        """Legacy function for standalone display."""
        # Setup the Window
        root = tk.Tk()
        root.title("Nonogram Display")

        # Create and pack the frame
        frame = create_canvas_from_grid(root, grid, row_clues, col_clues)
        frame.pack()

        # Run the application
        root.mainloop()
