"""
Background worker process for solving puzzles.
This file handles the heavy computation in a separate process.
"""


def solve_process_worker(solver_name, ruleset, rows_dict, cols_dict, result_queue):
        """
        Independent process that runs the solver.
        """
        try:
                # Re-import inside process to avoid pickling issues
                from algorithms import get_solver

                solver = get_solver(solver_name)

                if not solver:
                        raise ValueError(f"Solver '{solver_name}' not found")

                # Heavy computation happens here
                solution = solver.solve(ruleset)

                result = {
                        "status": "success",
                        "solution": solution,
                        "rows_dict": rows_dict,
                        "cols_dict": cols_dict,
                        "algorithm_name": solver_name,
                        "width": ruleset["width"],
                        "height": ruleset["height"],
                }
                result_queue.put(result)
        except Exception as e:
                result_queue.put({"status": "error", "message": str(e)})
