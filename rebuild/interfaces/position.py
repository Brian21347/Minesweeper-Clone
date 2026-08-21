from collections.abc import Sequence


class Pos:
    width: int = -1
    height: int = -1

    @classmethod
    def set_bounds(cls, width, height):
        cls.width = width
        cls.height = height

    def __init__(self, row: int, column: int) -> None:
        self.r = row
        self.c = column

    def is_valid(self) -> bool:
        return 0 <= self.r < Pos.width and 0 <= self.c < Pos.height

    def __add__(self, other: Pos):
        return Pos(self.r + other.r, self.c + other.c)

    def __sub__(self, other: Pos):
        return Pos(self.r - other.r, self.c - other.c)

    def __eq__(self, other: object):
        if isinstance(other, Sequence):
            if len(other) != 2:
                return False
            return other[0] == self.r and other[1] == self.c
        if isinstance(other, Pos):
            return self.r == other.r and self.c == other.c
        return False

    def __str__(self) -> str:
        return f"({self.r}, {self.c})"

    def __hash__(self) -> int:
        return hash((self.r, self.c))
