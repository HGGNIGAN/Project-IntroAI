from algorithms.local_search import LSSolver


def run_test():
    ruleset = {
        "width": 10,
        "height": 10,
        "rows": [[10], [1,6,1], [4], [2], [1,4], [1,1], [1,1], [3,6], [1,2], [1,4,1]],
        "columns": [[2,1,1], [1,1], [2,1,1,1], [2,1,2], [3,1,1,1], [3,2,1,1], [3,1,1], [3,1,1], [1,1,3], [2,1,1,3]],
    }

    solver = LSSolver()
    solution = solver.solve(ruleset)

    for row in solution:
        print(row)


if __name__ == "__main__":
    run_test()
