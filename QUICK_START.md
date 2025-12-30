# Nonogram Solver - Quick Start Guide

## Launch the Application

```bash
python main.py
```

The application will open with two tabs: **Configure Puzzle** and **Solution**.

## Tab 1: Configure Puzzle

### Step 1: Set Dimensions

- Use **Width** spinbox to set number of columns (1-100)
- Use **Height** spinbox to set number of rows (1-100)

### Step 2: Generate Puzzle or Enter Clues

**Option A: Generate Random Puzzle**

1. Click **Generate Random**
2. A random puzzle will be created automatically:
   - All clues are generated from the pattern
   - Grid is printed to terminal
   - Config is updated

**Option B: Import Predefined Puzzles**

1. Select the puzzle inside the selection box next to the random generator button
2. Click **Load Selected**
3. The puzzle will be loaded into the settings section and ready to be solved

**Option C: Enter Clues Manually**

The **Row/Column Clues** section has two tabs:

**Rows Tab:**

- Enter clue numbers for each row
- Format: comma-separated numbers (e.g., `1,2,3`)
- Example: "3" means one block of 3 filled cells

**Columns Tab:**

- Enter clue numbers for each column
- Same format as rows

#### Clue Format Examples

| Input | Meaning |
|-------|---------|
| `5` | One block of 5 filled cells |
| `2,2` | Two blocks of 2 cells each (separated by gap) |
| `1,1,1` | Three single cells |
| (empty) | No filled cells in this row/column |

### Step 3: Solve

1. Click **Solve Puzzle**
2. Application automatically switches to Solution tab

## Tab 2: Solution

Displays:

- **Visual Grid**: White squares (0) and black squares (1)
- **Clue Cells**: Row clues displayed to the left and column clues displayed above the grid
- **Solution Info**:
  - Puzzle size (columns × rows)
  - Number of filled cells

### Grid Display Details

- Cell size: 30×30 pixels
- Black = filled cell (1)
- White = empty cell (0)

## Working with Configuration Files

### File Format (JSON)

```json
{
  "width": 5,
  "height": 5,
  "rows": {
    "0": [1, 2],
    "1": [3],
    "2": [2, 1],
    "3": [4],
    "4": [1]
  },
  "columns": {
    "0": [2],
    "1": [5],
    "2": [3],
    "3": [2],
    "4": [1]
  }
}
```

### Editing Configuration Files

You can edit JSON files directly in a text editor:

1. Save your puzzle configuration
2. Open the `.json` file in any text editor
3. Modify clues as needed
4. Save the file
5. Load it back into the application

## Example Workflow

### Quick Start (Using Generate Random)

1. **Launch**: `python main.py`
2. **Configure**:
   - Set Width: 6, Height: 6
   - Click **Generate Random**
   - Watch terminal output for generated grid and clues
3. **Solve**: Click "Solve Puzzle"
4. **View**: Check Solution tab for the result with clues displayed

### Manual Configuration Workflow

1. **Launch**: `python main.py`
2. **Configure**:
   - Set Width: 5, Height: 5
   - Rows Tab → Enter clues for each row:
     - Row 0: `1,1`
     - Row 1: `2`
     - Row 2: `3`
     - Row 3: `2`
     - Row 4: `1,1`
   - Columns Tab → Enter similar patterns
3. **Solve**: Click "Solve Puzzle"
4. **View**: Check Solution tab for the result

## Troubleshooting

### Invalid input errors

- Make sure clues are comma-separated numbers with no spaces
- Correct: `1,2,3`; Wrong: `1, 2, 3` or `1, 2 , 3`
- Empty fields are valid (means no filled cells)

### Configuration won't load

- The app auto-generates `nonogram_config.json` on first run
- Ensure JSON file is valid format
- Check that file has `.json` extension
- Verify you have read/write permissions on the file
