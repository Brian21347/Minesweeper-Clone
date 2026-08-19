from collections.abc import Sequence


class Pos:
    width: int = -1
    height: int = -1

    @classmethod
    def set_bounds(cls, width, height):
        cls.width = width
        cls.height = height

    def __init__(self, row: int, column: int) -> None:
        self.row = row
        self.col = column

    def is_valid(self) -> bool:
        return 0 <= self.row < Pos.width and 0 <= self.col < Pos.height

    def __add__(self, other: Pos):
        return Pos(self.row + other.row, self.col + other.col)

    def __sub__(self, other: Pos):
        return Pos(self.row - other.row, self.col - other.col)

    def __eq__(self, other: object):
        if isinstance(other, Sequence):
            if len(other) != 2:
                return False
            return other[0] == self.row and other[1] == self.col
        if isinstance(other, Pos):
            return self.row == other.row and self.col == other.col
        return False

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"

    def __hash__(self) -> int:
        return hash((self.row, self.col))
