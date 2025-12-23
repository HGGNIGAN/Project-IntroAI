"""Algorithm discovery and registration for nonogram solvers."""

import importlib
import inspect
import pkgutil
from pathlib import Path
from .base import NonogramSolver


def discover_solvers():
        """
        Automatically discover all solver classes in the algorithms package.

        Returns:
            dict: Dictionary mapping solver names to solver classes.
        """
        solvers = {}
        algorithms_dir = Path(__file__).parent

        # Iterate through all Python files in the algorithms directory
        for module_info in pkgutil.iter_modules([str(algorithms_dir)]):
                module_name = module_info.name

                # Skip base module and private modules
                if module_name in ("base", "__init__") or module_name.startswith("_"):
                        continue

                try:
                        # Import the module
                        module = importlib.import_module(
                                f".{module_name}", package="algorithms"
                        )

                        # Find all classes that inherit from NonogramSolver
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                                if (
                                        issubclass(obj, NonogramSolver)
                                        and obj is not NonogramSolver
                                        and not inspect.isabstract(obj)
                                ):
                                        # Instantiate the solver
                                        solver_instance = obj()
                                        solvers[solver_instance.name] = solver_instance

                except Exception as e:
                        print(f"Warning: Could not load solver from {module_name}: {e}")

        return solvers


# Discover and register all available solvers
available_solvers = discover_solvers()


def get_solver(name):
        """
        Get a solver instance by name.

        Args:
            name (str): Name of the solver.

        Returns:
            NonogramSolver: Solver instance, or None if not found.
        """
        return available_solvers.get(name)


def list_solvers():
        """
        Get list of available solver names.

        Returns:
            list: List of solver names.
        """
        return list(available_solvers.keys())


def get_solver_info(name):
        """
        Get information about a specific solver.

        Args:
            name (str): Name of the solver.

        Returns:
            dict: Dictionary with solver information (name, description).
        """
        solver = available_solvers.get(name)
        if solver:
                return {"name": solver.name, "description": solver.description}
        return None
