# Adding a New Nonogram Solver Algorithm

This project auto-discovers solver classes in the `algorithms` package. Follow these steps to add your own solver.

## 1) Implement the base interface

- Inherit from `NonogramSolver` defined in `algorithms/base.py`.
- Implement `solve(self, ruleset)` with the exact signature.
- Use the ruleset structure:
  - `width` (int)
  - `height` (int)
  - `rows` (list[list[int]]) — ordered by row index
  - `columns` (list[list[int]]) — ordered by column index

### Minimal template

```python
from .base import NonogramSolver

class MySolver(NonogramSolver):
        name = "My Solver"
        description = "One-line description of the approach."

        def solve(self, ruleset):
                width = ruleset["width"]
                height = ruleset["height"]
                rows = ruleset["rows"]
                columns = ruleset["columns"]
                # TODO: implement your algorithm and return a 2D grid of 0/1 values
                return [[0 for _ in range(width)] for _ in range(height)]
```

## 2) File placement

- Add your solver as a new script inside `algorithms/` (e.g., `my_solver.py`).
- You may add helper scripts if they are reusable across algorithms; keep algorithm-specific logic in your solver file.

## 3) Auto-discovery

- No registration needed. Any non-abstract subclass of `NonogramSolver` is discovered automatically on app start.
- The UI dropdown will list `solver_instance.name`.

## 4) Return format

- Return a 2D list of ints with shape `height x width`.
- Cell values: `0` = white/empty, `1` = black/filled.

## 5) Logging and testing

- Feel free to `print()` for debugging; output appears in the terminal.
- Test by running the app and selecting your solver from the dropdown.

## 6) Gotchas

- Do not change the `solve` signature.
- Ensure `rows` and `columns` are treated as ordered lists (not dicts).
- Avoid side effects on the `ruleset` dict; copy if you need to mutate.
