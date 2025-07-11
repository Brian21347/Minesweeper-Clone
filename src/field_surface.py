import pygame
from aliases import Position
from surface import Surface
from settings import *
from util import *
from aliases import *
from util import Position


class FieldSurface(Surface):
    def __init__(self):
        super().__init__()
        self.resize()

    def update(self, position: Position) -> None:
        raise NotImplementedError

    def draw(self) -> None:
        self.display_surface.blit(self.surface, [get_left_margin(), get_top_margin() + HEADER_HEIGHT])

    def resize(self) -> None:
        super().resize()
        block_size = get_block_size()
        for row in range(MINE_FIELD_HEIGHT):
            for col in range(MINE_FIELD_WIDTH):
                rect = pygame.rect.Rect(col * block_size, row * block_size, block_size, block_size)
                color = (
                    ColorPallette.DARK_FIELD if (row + col) % 2 == 1 else ColorPallette.LIGHT_FIELD
                )
                pygame.draw.rect(self.surface, color, rect)
