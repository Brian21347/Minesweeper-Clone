import pygame
from os.path import join
from game import Game


# region setup
STANDARD = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]
KNIGHT = [
    [1, 2],
    [1, -2],
    [2, 1],
    [2, -1],
    [-1, 2],
    [-1, -2],
    [-2, 1],
    [-2, -1],
]
NEIGHBORING = STANDARD  # edit this to change the game mode!
MINE_PERCENT = 0.20
assert MINE_PERCENT < 1, "MINE_PERCENT must be less than 1"
GRID_SIZE = [10, 10]
MODE = f"{GRID_SIZE[0]}*{GRID_SIZE[1]},{MINE_PERCENT}"
HEADER_SIZE = 50
SCREEN_SIZE = 750, 750 + HEADER_SIZE
pygame.init()

CLOCK = pygame.time.Clock()
MAX_FPS = 60

MINE_IMAGE_PATH = join("src", "assets", "mine.gif")
HIGH_SCORES_PATH = join("src", "High Scores.txt")

pygame.display.set_caption("Minesweeper")
ICON = pygame.image.load(MINE_IMAGE_PATH)
pygame.display.set_icon(ICON)

SCREEN = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
# endregion


def main():
    while True:
        game = Game(SCREEN)
        game.run()
        if not game.did_win():
            continue
        write_high_score(game.get_starting_time())


def write_high_score(starting_time: int):
    score = int((pygame.time.get_ticks() - starting_time) / 1000)
    with open(HIGH_SCORES_PATH) as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        line = line.split(";")
        if not len(line):
            continue
        if (
            line[0] == f"{GRID_SIZE[0]}*{GRID_SIZE[1]}"
            and line[1] == str(MINE_PERCENT)
            and line[2] == str(NEIGHBORING)
        ):
            if int(line[3]) > score:
                lines[i] = f"{GRID_SIZE[0]}*{GRID_SIZE[1]};{MINE_PERCENT};{NEIGHBORING};{score}"
            break
    else:
        lines.append(f"{GRID_SIZE[0]}*{GRID_SIZE[1]};{MINE_PERCENT};{NEIGHBORING};{score}")
    with open(HIGH_SCORES_PATH, mode="w") as f:
        string = ""
        for line in lines:
            if line:
                string += line + "\n"
        f.write(string)


if __name__ == "__main__":
    main()
