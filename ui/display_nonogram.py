import tkinter as tk

# Configuration
CELL_SIZE = 50  # Size of each square in pixels


def create_canvas_from_grid(parent, grid):
        """
        Create a canvas displaying the nonogram grid.

        Args:
            parent: Parent tkinter widget
            grid: 2D list representing the puzzle solution

        Returns:
            tk.Canvas: The canvas containing the nonogram display
        """
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        # Create a Canvas to draw on
        canvas = tk.Canvas(
                parent, width=cols * CELL_SIZE, height=rows * CELL_SIZE, bg="white"
        )

        # Loop through the list and draw rectangles
        for r in range(rows):
                for c in range(cols):
                        value = grid[r][c]

                        # Determine color: 0 = Black, 1 = White
                        color = "black" if value == 1 else "white"

                        # Calculate pixel coordinates
                        x1 = c * CELL_SIZE
                        y1 = r * CELL_SIZE
                        x2 = x1 + CELL_SIZE
                        y2 = y1 + CELL_SIZE

                        # Draw the rectangle
                        canvas.create_rectangle(
                                x1, y1, x2, y2, fill=color, outline="gray"
                        )

        return canvas


def display(grid):
        """Legacy function for standalone display."""
        # Setup the Window
        root = tk.Tk()
        root.title("Nonogram Display")

        # Create and pack the canvas
        canvas = create_canvas_from_grid(root, grid)
        canvas.pack()

        # Run the application
        root.mainloop()
