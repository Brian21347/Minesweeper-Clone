from itertools import product
from typing import Any, cast, overload

from colorama import Fore

from rebuild.interfaces.aliases import *
from rebuild.interfaces.minefield import MineField
from rebuild.interfaces.position import Pos
from rebuild.settings import color_pallette


class SolverError(Exception):
    """Raised when the solver reveals or flags something incorrectly."""


class SolutionField:
    def __init__(self, grid: list[str] | None) -> None:
        self.__grid = grid

    def get_value(self, pos: Pos):
        if self.__grid is None:
            return None
        grid_val = self.__grid[pos.r][pos.c]
        if grid_val == "F":  # replace flags with mines
            return "M"
        if grid_val == ".":  # Error when trying to flag/reveal an unknown square
            raise SolverError
        return grid_val


class SolvingField:
    """A class for storing the state of a minefield from the perspective of the solver."""

    __grid: list[list[SolvingFieldValue]]

    @overload
    def __init__(self, mine_field: MineField, /) -> None:
        """Used for storing the current state of the minefield in a normal game."""
        ...

    @overload
    def __init__(self, test_input: str, test_solution: str | None, /) -> None:
        """Used for storing a test and solution pair when testing the solver.

        When `test_solution` is set to `None`, there is no validation of the solver's moves.
        """
        ...

    def __init__(self, *args: Any) -> None:
        def convert(s: str) -> SolvingFieldValue:
            if s.isnumeric():
                return int(s)
            if s not in [".", "F", "R"]:
                raise ValueError
            return cast(SolvingFieldValue, s)

        if len(args) == 1:
            mine_field = args[0]
            assert isinstance(mine_field, MineField)
            self.__solution_field = mine_field
            self.__grid = [["."] * mine_field.size[1] for _ in range(mine_field.size[0])]
            for pos, val in mine_field.all_revealed():
                if val == "M":
                    raise ValueError
                self.__grid[pos.r][pos.c] = val
        elif len(args) == 2:
            test_input, solution = map(lambda s: s.strip().split(), args)
            self.__grid = [[convert(s) for s in row] for row in test_input]
            self.__solution_field = SolutionField(solution)
        else:
            raise NotImplementedError
        self.size = len(self.__grid), len(self.__grid[0])
        Pos.set_bounds(*self.size)
        self.revealed = set()
        self.flagged = set()

    def get_value(self, pos: Pos) -> SolvingFieldValue:
        if not pos.is_valid():
            raise ValueError
        return self.__grid[pos.r][pos.c]

    def reveal(self, pos: Pos) -> None:
        if self.__solution_field.get_value(pos) == "M":
            raise SolverError
        self.__grid[pos.r][pos.c] = "R"
        self.revealed.add(pos)

    def flag(self, pos: Pos) -> None:
        if self.__solution_field.get_value(pos) != "M":
            raise SolverError
        self.__grid[pos.r][pos.c] = "F"
        self.flagged.add(pos)

    def verify(self) -> bool:
        if self.__solution_field is None:
            raise ValueError("No verification is possible without a set `solution_field`.")
        for r, c in product(range(self.size[0]), range(self.size[1])):
            pos = Pos(r, c)
            self_val = self.get_value(pos)
            # revealing and flagging are already checked
            # if the value is an integer, then it must have been revealed beforehand
            if self_val == "R" or self_val == "F" or isinstance(self_val, int):
                continue
            # if the value in the solution field is not unknown, then there should have been more
            # actions taken and the solver failed
            if self.__solution_field.get_value(pos) != ".":
                return False
        return True

    def __str__(self) -> str:
        def hex_to_ascii(hex_code: str) -> str:
            hex_code = hex_code.lstrip("#")
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            return f"\033[38;2;{r};{g};{b}m"

        def convert(val: SolvingFieldValue) -> str:
            if val == "F":
                return Fore.RED + str(val) + Fore.RESET
            if val == ".":
                return Fore.LIGHTBLACK_EX + str(val) + Fore.RESET
            if val == "R":
                return Fore.CYAN + str(val) + Fore.RESET
            if val == 0:
                return " "
            return hex_to_ascii(color_pallette.cell_colors[val - 1]) + str(val) + Fore.RESET

        out = ""
        for row in self.__grid:
            for val in row:
                out += convert(val)
            out += "\n"
        return out
