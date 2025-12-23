# Nonogram Solver - Quick Start Guide

## Launch the Application

```bash
python main.py
```

The application will open with two tabs: **Configure Puzzle** and **Solution**.

## Tab 1: Configure Puzzle

### Step 1: Set Dimensions

- Use **Width** spinbox to set number of columns (1-20)
- Use **Height** spinbox to set number of rows (1-20)

### Step 2: Enter Clues

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

### Step 3: Save/Load (Optional)

**To Save:**

1. Click **Save Configuration**
2. Choose a filename (e.g., `my_puzzle.json`)
3. Click Save

**To Load:**

1. Click **Load Configuration**
2. Select a previously saved JSON file
3. Puzzle data will populate automatically

### Step 4: Solve

1. Click **Solve Puzzle**
2. Application automatically switches to Solution tab

## Tab 2: Solution

Displays:

- **Visual Grid**: White squares (0) and black squares (1)
- **Solution Info**:
  - Puzzle size (columns × rows)
  - Number of filled cells

### Grid Display Details

- Each cell: 50×50 pixels
- Black = filled cell (1)
- White = empty cell (0)
- Gray borders = cell boundaries

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

1. **Launch**: `python main.py`
2. **Configure**:
   - Set Width: 5, Height: 5
   - Row 0 clues: `1,1`
   - Row 1 clues: `2`
   - Row 2 clues: `3`
   - Row 3 clues: `2`
   - Row 4 clues: `1,1`
   - (Set similar patterns for columns)
3. **Solve**: Click "Solve Puzzle"
4. **View**: Check Solution tab for the result

## Troubleshooting

### "Invalid input in Row X"

- Make sure clues are comma-separated numbers
- No spaces before/after numbers
- Correct example: `1,2,3`; Wrong example: `1, 2, 3`

### Configuration won't load

- Ensure JSON file is valid
- Check that file has `.json` extension
- Verify you have read permissions on the file
