# Project-IntroAI

A graphical user interface for configuring and solving nonogram puzzles.

### Project Structure

```
Current directory
├── README.md                   # This file
├── nonogram_config.json        # Example puzzle configuration
├── main.py                     # Entry point
├── algorithms/                 # Algorithm implementations
└── ui/
    ├── __init__.py
    ├── app.py                  # Main application window
    ├── configurator.py         # Puzzle configuration UI
    ├── config_manager.py       # Configuration management (save/load)
    └── display_nonogram.py     # Grid display functionality
    
```

### Running the Application

```bash
python main.py
```

This will launch the Nonogram Solver application with a graphical interface.

### Usage Guide

#### Configure a Puzzle

1. **Set Dimensions**: Use the spinboxes to set the puzzle width and height (1-20)
2. **Enter Clues**:
   - Switch to the **Rows** tab to enter row clues
   - Switch to the **Columns** tab to enter column clues
   - Enter clues as comma-separated numbers (e.g., `1,2,3`)
   - Leave empty for rows/columns with no filled cells

3. **Solve**:
   - Click "Solve Puzzle" to generate a solution
   - The application will switch to the Solution tab automatically

#### View Solution

The Solution tab displays:

- Visual grid representation of the puzzle solution
- Cell size: 50x50 pixels (white = 0, black = 1)
- Solution info panel showing puzzle dimensions and filled cell count

### Configuration File Format

Puzzle configurations are stored as JSON files, and are saved/loaded automatically. Example:

```json
{
  "width": 5,
  "height": 5,
  "rows": {
    "0": [1, 1],
    "1": [2],
    "2": [3],
    "3": [2],
    "4": [1, 1]
  },
  "columns": {
    "0": [2],
    "1": [4],
    "2": [1, 1],
    "3": [4],
    "4": [2]
  }
}
```

**Fields:**

- `width`: Number of columns in the puzzle
- `height`: Number of rows in the puzzle
- `rows`: Object mapping row indices to clue arrays
- `columns`: Object mapping column indices to clue arrays

### Configuration Input Format

When entering clues in the UI:

- Separate multiple clues with commas: `1,2,3`
- Each number represents a consecutive block of filled cells
- Leave empty if a row/column has no clues

Example:

- `1,2,3` = blocks of 1, 2, and 3 filled cells separated by at least one empty cell
- `5` = a single block of 5 filled cells
- Empty = no filled cells in this row/column

### Developer Notes

- Read the algorithm guide at [algorithms/README.md](algorithms/README.md) before adding or modifying solvers.
- Implement solvers as classes inheriting from `NonogramSolver` with the signature `solve(self, ruleset)`.
- Ruleset shape passed into solvers: `width`, `height`, `rows` (list of lists), `columns` (list of lists).
- Solvers must return a 2D list shaped `height x width` with cell values: `0` = white/empty, `1` = black/filled.
