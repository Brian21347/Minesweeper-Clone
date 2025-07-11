import pygame
from aliases import Position
from surface import Surface
from settings import *
from aliases import *
from util import *


class RevealedSurface(Surface):
    """Manages drawing values of revealed tiles."""

    def __init__(self, mine_field: MineField) -> None:
        self.revealed: PositionSet = set()
        self.mine_field = mine_field

    def update(self, position: Position) -> None:
        self.revealed.add(position)
        val = int(value_at(position))
        make_text(
            self.surface, convert_to_absolute(position), val, get_block_size(), CELL_COLORS[val]
        )

    def draw(self) -> None:
        self.display_surface.blit(
            self.surface, (get_left_margin(), get_top_margin() + HEADER_HEIGHT)
        )

    def resize(self) -> None:
        super().resize()
        for revealed in self.revealed:
            self.update(revealed)
