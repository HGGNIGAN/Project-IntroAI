import tkinter as tk

# Configuration
CELL_SIZE = 30  # Size of each square in pixels
PADDING = 5  # Padding around the canvas


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

        # Calculate dimensions needed for clues
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

        # Calculate the total canvas size
        clue_area_width = max_row_clues * CELL_SIZE
        clue_area_height = max_col_clues * CELL_SIZE

        grid_width = cols * CELL_SIZE
        grid_height = rows * CELL_SIZE

        total_width = clue_area_width + grid_width
        total_height = clue_area_height + grid_height

        # Create the canvas
        canvas = tk.Canvas(
                parent,
                width=total_width + 2 * PADDING,
                height=total_height + 2 * PADDING,
                bg="white",
                highlightthickness=0,
        )

        # Draw column clues (top area)
        if col_clues:
                for c in range(cols):
                        clue_list = col_clues.get(str(c), [])
                        x_start = PADDING + clue_area_width + (c * CELL_SIZE)

                        offset = max_col_clues - len(clue_list)
                        for idx, clue_num in enumerate(clue_list):
                                y_pos = PADDING + (offset + idx) * CELL_SIZE

                                canvas.create_rectangle(
                                        x_start,
                                        y_pos,
                                        x_start + CELL_SIZE,
                                        y_pos + CELL_SIZE,
                                        fill="lightgray",
                                        outline="gray",
                                )
                                canvas.create_text(
                                        x_start + CELL_SIZE / 2,
                                        y_pos + CELL_SIZE / 2,
                                        text=str(clue_num),
                                        font=("Arial", 9),
                                )

        # Draw row clues (left area)
        if row_clues:
                for r in range(rows):
                        clue_list = row_clues.get(str(r), [])
                        y_start = PADDING + clue_area_height + (r * CELL_SIZE)

                        offset = max_row_clues - len(clue_list)
                        for idx, clue_num in enumerate(clue_list):
                                x_pos = PADDING + (offset + idx) * CELL_SIZE

                                canvas.create_rectangle(
                                        x_pos,
                                        y_start,
                                        x_pos + CELL_SIZE,
                                        y_start + CELL_SIZE,
                                        fill="lightgray",
                                        outline="gray",
                                )
                                canvas.create_text(
                                        x_pos + CELL_SIZE / 2,
                                        y_start + CELL_SIZE / 2,
                                        text=str(clue_num),
                                        font=("Arial", 9),
                                )

        # Draw the grid (main area)
        start_x = PADDING + clue_area_width
        start_y = PADDING + clue_area_height

        for r in range(rows):
                y = start_y + (r * CELL_SIZE)
                for c in range(cols):
                        x = start_x + (c * CELL_SIZE)

                        value = grid[r][c]
                        color = "black" if value == 1 else "white"

                        canvas.create_rectangle(
                                x,
                                y,
                                x + CELL_SIZE,
                                y + CELL_SIZE,
                                fill=color,
                                outline="gray",
                        )

        return canvas


def display(grid, row_clues=None, col_clues=None):
        root = tk.Tk()
        root.title("Nonogram Display")
        frame = create_canvas_from_grid(root, grid, row_clues, col_clues)
        frame.pack()
        root.mainloop()
