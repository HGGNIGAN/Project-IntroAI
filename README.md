# Project-IntroAI

A graphical user interface for configuring and solving nonogram puzzles.

### Project Structure

```tree
Current directory
├── README.md                   # This file
├── QUICK_START.md              # Quick start guide
│
├── main.py                     # Entry point
├── algorithms/                 # Algorithm implementations
│   ├── __init__.py             # Grabs all implemented algorithms
│   ├── __base__.py             # Abstract class for solution implementations
│   └── (implementations)
├── core/                       # Core business logic
├── ui/                         # User interface components
└── samples/                    # Predefined puzzle samples (.json) 
```

### Prerequisites

- Python (CPython) 3.8+ or PyPy for runtime boost (PyPy3 recommended if you prefer PyPy).
- `numpy` is required for running the algorithms

Installation (CPython):

```bash
python -m pip install --upgrade pip
python -m pip install numpy
```

Installation (PyPy):

```bash
pypy -m pip install --upgrade pip
pypy -m pip install numpy
# or if your system uses pypy3:
pypy3 -m pip install numpy
```

Notes:

- On PyPy, `numpy` is available but may be provided by a PyPy-compatible binary wheel (often named `numpy` as well). If installation fails, try installing `micronumpy` or consult PyPy documentation for platform-specific guidance.

### Running the Application

```bash
python main.py
```

This will launch the Nonogram Solver application with a graphical interface.

#### Running with PyPy

```bash
pypy main.py
# or if your system uses pypy3:
pypy3 main.py
```

### Usage Guide

#### Configure a Puzzle

##### Generate Random Puzzle

1. Set your desired dimensions
2. Click **Generate Random**:
   - Creates a random puzzle with that dimension
   - Automatically generates all row and column clues from the pattern

##### Using predefined puzzles

1. Select a predefined configuration inside the box
2. Click **Load Selected**
3. The puzzle will be loaded into the settings section and ready to be solved

##### Configure Manually

1. **Set Dimensions**: Use the spinboxes to set the puzzle width and height (1-100)
2. **Enter Clues**:
   - Switch to the **Rows** tab to enter row clues
   - Switch to the **Columns** tab to enter column clues
   - Enter clues as comma-separated numbers (e.g., `1,2,3`)
   - Leave empty for rows/columns with no filled cells

#### Solve

- Click "Solve Puzzle" to generate a solution
- The application will switch to the Solution tab automatically

#### View Solution

The Solution tab displays:

- **The solution grid**
- **Clue Cells**: Row clues on the left and column clues above the grid
- **Solution Info**: Puzzle size, filled cell count and the algorithm's execution time

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
