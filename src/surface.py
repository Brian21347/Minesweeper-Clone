from abc import ABC, abstractmethod
import pygame
from settings import *
from aliases import *
from util import *


class Surface(ABC):
    def __init__(self):
        block_size = get_block_size()
        self.surface = pygame.Surface([MINE_FIELD_WIDTH * block_size, MINE_FIELD_HEIGHT * block_size])
        self.display_surface = pygame.display.get_surface()

    @abstractmethod
    def update(self, position: Position) -> None: ...

    @abstractmethod
    def draw(self) -> None: ...

    def resize(self) -> None:
        block_size = get_block_size()
        self.surface = pygame.Surface([MINE_FIELD_WIDTH * block_size, MINE_FIELD_HEIGHT * block_size])
