import pygame, sys
from settings import *
from mine_field import MineField
from typing import NoReturn


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(
            SCREEN_SIZE, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        pygame.display.set_caption("Minesweeper")
        icon = pygame.image.load(MINE_IMAGE_PATH)
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.mine_field = MineField()
    
    def run(self) -> NoReturn:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    self.mine_field.handle_key_down(event)
                if event.type == pygame.VIDEORESIZE:
                    width, height = event.size
                    width = max(width, MIN_WIDTH)
                    height = max(height, MIN_HEIGHT)
                    self.screen = pygame.display.set_mode([width, height], pygame.RESIZABLE)
                    self.mine_field.resize()
            self.draw()
            self.clock.tick(MAX_FPS)

    def draw(self) -> None:
        self.screen.fill(ColorPallette.BACKGROUND)
        self.mine_field.draw()
        pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
