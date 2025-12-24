# Project-IntroAI

A graphical user interface for configuring and solving nonogram puzzles.

### Project Structure

```
Current directory
├── README.md                   # This file
├── QUICK_START.md              # Quick start guide
│
├── main.py                     # Entry point
├── algorithms/                 # Algorithm implementations
├── core/                       # Core business logic
│   ├── config_manager.py       # Configuration management (save/load)
│   └── puzzle_generator.py     # Random puzzle generation
└── ui/                         # User interface components
    ├── app.py                  # Main application window
    ├── configurator.py         # Puzzle configuration UI
    └── display_nonogram.py     # Grid display functionality
    
```

### Running the Application

```bash
python main.py
```

This will launch the Nonogram Solver application with a graphical interface.

### Usage Guide

#### Configure a Puzzle

##### Configure Manually

1. **Set Dimensions**: Use the spinboxes to set the puzzle width and height (1-20)
2. **Enter Clues**:
   - Switch to the **Rows** tab to enter row clues
   - Switch to the **Columns** tab to enter column clues
   - Enter clues as comma-separated numbers (e.g., `1,2,3`)
   - Leave empty for rows/columns with no filled cells

##### Generate Random Puzzle

Instead of manually entering clues:

1. Set your desired **Dimensions**
2. Click **Generate Random**:
   - Creates a random puzzle with that dimension
   - Automatically generates all row and column clues from the pattern

#### Solve

- Click "Solve Puzzle" to generate a solution
- The application will switch to the Solution tab automatically

#### View Solution

The Solution tab displays:

- **Visual Grid**: White squares (0) and black squares (1)
- **Clue Cells**: Row clues on the left and column clues above the grid
- **Solution Info**: Puzzle size and filled cell count

### Configuration File Format

Puzzle configurations are stored in a JSON file (`nonogram_config.json`, automatically-generated), and are saved/loaded automatically. Example:

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

- **Directory Organization**:
  - **core/** contains business logic (`ConfigManager`, `PuzzleGenerator`)
  - **ui/** contains only UI components (TKinter-based interface)
  - **algorithms/** contains puzzle solver implementations
  
- **Adding Solvers**: Read [algorithms/README.md](algorithms/README.md) before adding or modifying solvers
  - Implement solvers as classes inheriting from `NonogramSolver`
  - Solver signature: `solve(self, ruleset)` returning 2D list
  - Ruleset contains: `width`, `height`, `rows` (list of lists), `columns` (list of lists)
  - Return format: 2D list shaped `height x width` with `0` (empty) or `1` (filled)
