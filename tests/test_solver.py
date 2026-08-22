from pathlib import Path

import pytest

from rebuild.interfaces.solver import Solver


def load_data():
    test_data: list[list[str]] = []
    solver_test_dir = Path("tests/solver tests")
    for name in sorted(path.stem for path in solver_test_dir.glob("*.in")):
        in_path = solver_test_dir / f"{name}.in"
        out_path = solver_test_dir / f"{name}.out"
        if in_path.exists() and out_path.exists():
            test_data.append([in_path.read_text(), out_path.read_text()])
    return test_data


@pytest.mark.parametrize("test_input, solution", load_data())
def test_solver(test_input, solution):
    solver = Solver(test_input, solution)
    solver.solve()
    print(solver)
    assert solver.verify()
