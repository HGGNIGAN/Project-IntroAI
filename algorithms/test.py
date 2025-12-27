from algorithms.local_search import LSSolver


def run_test():
    ruleset = {
        "width": 5,
        "height": 5,
        "rows": [[2], [4], [3], [3], [1]],
        "columns": [[2], [3], [4], [1,1], [2]],
    }

    solver = LSSolver()
    solution = solver.solve(ruleset)

    for row in solution:
        print(row)


if __name__ == "__main__":
    run_test()
