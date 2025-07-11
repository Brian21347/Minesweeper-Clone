from typing import Literal


Position = tuple[int, int]
PositionSet = set[Position]
FrozenPositionSet = frozenset[Position]
MineField = list[list[int | Literal["M"]]]
SetDict = dict[FrozenPositionSet, int]
