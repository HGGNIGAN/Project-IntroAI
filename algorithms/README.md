# Adding a New Nonogram Solver Algorithm

This project auto-discovers solver classes in the `algorithms` package. Follow these steps to add your own solver.

## Implement the base interface

- Inherit from `NonogramSolver` defined in `algorithms/base.py`.
- Implement `_solve_internal(self)` - the base class handles initialization automatically.
- Instance variables automatically available:
  - `self.width` (int) - Puzzle width
  - `self.height` (int) - Puzzle height
  - `self.rows` (list[list[int]]) - Row clues, ordered by row index
  - `self.columns` (list[list[int]]) - Column clues, ordered by column index
  - `self.grid` (list[list[int]]) - 2D grid initialized with zeros (height × width)

### Minimal template

```python
from .base import NonogramSolver

class MySolver(NonogramSolver):
        name = "My Solver"
        description = "One-line description of the approach."

        def _solve_internal(self):
                # Instance variables are ready to use:
                # self.width, self.height, self.rows, self.columns, self.grid
                
                # TODO: implement your algorithm by modifying self.grid
                
                # your logic here
                
                return self.grid
```

## File placement

- Add your solver as a new script inside `algorithms/` (e.g., `my_solver.py`).
- You may add helper scripts if they are reusable across algorithms; keep algorithm-specific logic in your solver file.

## Auto-discovery

- No registration needed. Any non-abstract subclass of `NonogramSolver` is discovered automatically on app start.
- The UI dropdown will list `solver_instance.name`.

## Return format

- Return a 2D list of ints with shape `height x width`.
- Cell values: `0` = white/empty, `1` = black/filled.

## Logging and testing

- Feel free to `print()` for debugging; output appears in the terminal.
- Test by running the app and selecting your solver from the dropdown.

## Gotchas

- Implement `_solve_internal()`, not `solve()` (the base class handles `solve()`).
- Use `self.grid` directly - it's pre-initialized as a `height × width` grid of zeros.
- Helper methods can access `self.width`, `self.rows`, etc. without parameter passing.
- Always return `self.grid` (or a new grid) from `_solve_internal()`.
