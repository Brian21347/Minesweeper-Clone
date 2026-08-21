from itertools import product
from math import ceil
from typing import Literal
from collections.abc import Generator
from rebuild.interfaces.position import Pos
from random import shuffle
from colorama import Fore
from rebuild.settings import (
    CENTER_DISPERSAL_RADIUS,
    CORNER_DISPERSAL_RADIUS,
    CORNERS,
    ADJACENCY,
    color_pallette,
)


class MineField:
    MINE = Literal["M"]
    FIELD_VALUE = int | MINE
    __grid: list[list[FIELD_VALUE]]
    __mine_positions: set[Pos]
    __revealed: set[Pos]
    __flagged: set[Pos]

    def __init__(self, size: tuple[int, int], num_mines: int) -> None:
        self.size = size
        Pos.set_bounds(*size)
        self.num_mines = num_mines
        self.__grid = [[0] * size[1] for _ in range(size[0])]
        self.__revealed = set()
        self.__flagged = set()

    def generate(self, revealed_location: Pos) -> None:
        possible_locations = set(
            Pos(r, c) for r, c in product(range(self.size[0]), range(self.size[1]))
        )
        dispersal_radius = (
            CORNER_DISPERSAL_RADIUS if revealed_location in CORNERS else CENTER_DISPERSAL_RADIUS
        )
        max_dist = ceil(dispersal_radius)
        radius_squared = dispersal_radius * dispersal_radius
        unviable_locations = set(
            npos
            for dr, dc in product(range(-max_dist, max_dist), range(-max_dist, max_dist))
            if dr * dr + dc * dc <= radius_squared
            if (npos := revealed_location + Pos(dr, dc)).is_valid()
        )
        possible_locations -= unviable_locations
        possible_locations = list(possible_locations)
        shuffle(possible_locations)
        self.__mine_positions = set(possible_locations[: self.num_mines])
        if len(self.__mine_positions) != self.num_mines:
            raise ValueError(
                f"Mine counts differ. {len(self.__mine_positions)} != {self.num_mines}."
            )
        for pos in self.__mine_positions:
            try:
                self.__grid[pos.r][pos.c] = "M"
            except:
                print(pos)
                raise ValueError
            for neighbor in MineField.neighbors(pos):
                if neighbor in self.__mine_positions:
                    continue
                self.__grid[neighbor.r][neighbor.c] += 1  # type: ignore
        self.mark_reveled(revealed_location)

    def get_value(self, pos: Pos) -> FIELD_VALUE:
        if not pos.is_valid():
            raise ValueError
        return self.__grid[pos.r][pos.c]

    @staticmethod
    def neighbors(pos: Pos) -> Generator[Pos, None, None]:
        for dr, dc in ADJACENCY:
            if (npos := pos + Pos(dr, dc)).is_valid():
                yield npos

    def is_revealed(self, pos: Pos) -> bool:
        return pos in self.__revealed

    def is_flagged(self, pos: Pos) -> bool:
        return pos in self.__flagged

    def mark_reveled(self, pos: Pos) -> None:
        if not pos.is_valid() or pos in self.__revealed:
            return
        self.__revealed.add(pos)
        if self.get_value(pos) == 0:
            for neighbor in self.neighbors(pos):
                self.mark_reveled(neighbor)

    def flag(self, pos: Pos) -> None:
        self.__flagged.add(pos)

    def all_revealed(self) -> Generator[tuple[Pos, FIELD_VALUE], None, None]:
        for pos in self.__revealed:
            yield pos, self.get_value(pos)

    def from_grid(self, grid: list[list[FIELD_VALUE]], start: Pos) -> None:
        self.__grid = grid
        self.size = len(grid), len(grid[0])
        self.__revealed = set()
        self.__flagged = set()
        self.mark_reveled(start)

    def all_flagged(self) -> Generator[Pos, None, None]:
        for pos in self.__flagged:
            yield pos

    def __str__(self) -> str:
        def hex_to_ascii(hex_code: str) -> str:
            hex_code = hex_code.lstrip("#")
            r = int(hex_code[0:2], 16)
            g = int(hex_code[2:4], 16)
            b = int(hex_code[4:6], 16)
            return f"\033[38;2;{r};{g};{b}m"

        def convert(pos: Pos, val: MineField.FIELD_VALUE) -> str:
            if val == "M":
                return Fore.RED + str(val) + Fore.RESET
            if val == 0:
                return " "
            if pos not in self.__revealed:
                return Fore.LIGHTBLACK_EX + str(val) + Fore.RESET
            return hex_to_ascii(color_pallette.cell_colors[val - 1]) + str(val) + Fore.RESET

        out = ""
        for i, row in enumerate(self.__grid):
            for j, val in enumerate(row):
                out += convert(Pos(i, j), val)
            out += "\n"
        return out
