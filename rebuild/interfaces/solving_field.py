from typing import Any, Literal
from collections.abc import Generator
from colorama import Fore
from rebuild.interfaces.minefield import MineField
from rebuild.settings import color_pallette
from rebuild.interfaces.position import Pos


class SolverError(Exception):
    """Raised when the solver reveals or flags something incorrectly."""


class SolvingField:
    REVEALED = Literal["R"]
    UNKNOWN = Literal["."]
    FLAGGED = Literal["F"]
    __grid: list[list[int | REVEALED | UNKNOWN | FLAGGED]]

    def __init__(self, mine_field: MineField) -> None:
        self.__mine_field = mine_field
        self.__grid = [["."] * mine_field.size[1] for _ in range(mine_field.size[0])]
        for pos, val in mine_field.all_revealed():
            if val == "M":
                raise ValueError
            self.__grid[pos.r][pos.c] = val

    def get_value(self, pos: Pos):
        if not pos.is_valid():
            raise ValueError
        return self.__grid[pos.r][pos.c]

    def reveal(self, pos: Pos):
        if self.__mine_field.get_value(pos) == "M":
            raise SolverError
        self.__grid[pos.r][pos.c] = "R"

    def flag(self, pos: Pos):
        if self.__mine_field.get_value(pos) != "M":
            raise SolverError
        self.__grid[pos.r][pos.c] = "R"

    def __str__(self):
        def hex_to_ascii(hex_code: str):
            hex_code = hex_code.lstrip("#")
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            return f"\033[38;2;{r};{g};{b}m"

        def convert(val: int | Literal["F", ".", "R"]) -> str:
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
