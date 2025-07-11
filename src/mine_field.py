import pygame
from revealed_surface import RevealedSurface
from field_surface import FieldSurface


class MineField:
    def __init__(self) -> None:
        self.board = ...
        self.display_surface = pygame.display.get_surface()
        self.field_surface = FieldSurface()
        self.revealed_surface = None
        self.flag_surface = ...
    
    def handle_key_down(self, event: pygame.event.Event) -> None:
        pass
    
    def draw(self) -> None:
        self.field_surface.draw()
    
    def resize(self) -> None:
        self.field_surface.resize()
