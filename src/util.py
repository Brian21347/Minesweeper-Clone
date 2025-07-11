"""A collection of utility functions."""

import pygame
from settings import *
from aliases import *
from typing import Any


def make_text(blit_surf: pygame.Surface, pos: Position, text: Any, size: int, color: str) -> None:
    """Draws text on the provided surface."""
    font = pygame.font.SysFont(pygame.font.get_default_font(), size)
    surf = font.render(str(text), True, color)
    blit_surf.blit(surf, surf.get_rect(center=pos))


def get_mouse_pos() -> Position:
    """Calculates the position on the minefield the mouse is hovering over."""
    mouse_pos = pygame.mouse.get_pos()
    block_size = get_block_size()
    return (
        (mouse_pos[1] - HEADER_HEIGHT - get_top_margin()) // block_size,
        (mouse_pos[0] - get_left_margin()) // block_size,
    )


def get_block_size() -> int:
    """Calculates the block size of the minefield."""
    return min(
        pygame.display.get_surface().get_width() // MINE_FIELD_WIDTH,
        (pygame.display.get_surface().get_height() - HEADER_HEIGHT) // MINE_FIELD_HEIGHT,
    )


def get_left_margin() -> int:
    """Calculates the margin left of the minefield."""
    width = pygame.display.get_surface().get_width()
    mine_field_width = get_block_size() * MINE_FIELD_WIDTH
    return (width - mine_field_width) // 2


def get_top_margin() -> int:
    """Calculates the margin above the minefield."""
    height = pygame.display.get_surface().get_height()
    mine_field_height = get_block_size() * MINE_FIELD_HEIGHT
    return (height - HEADER_HEIGHT - mine_field_height) // 2


def value_at(position: Position) -> int | str: ...


def bind_value_at(mine_field: MineField):
    global value_at

    def func(position: Position) -> int | str:
        return mine_field[position[0]][position[1]]

    value_at = func


def convert_to_absolute(position: Position) -> Position:
    """Converts a position on the minefield to absolute coordinates on the display surface."""
    block_size = get_block_size()
    return (
        position[1] * block_size + get_left_margin(),
        position[0] * block_size + get_top_margin() + HEADER_HEIGHT,
    )
