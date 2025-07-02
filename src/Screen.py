import pygame
from abc import ABC, abstractmethod


class Screen(ABC):
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.screen = screen
    
    @abstractmethod
    def run(self):
        pass
