import time
import pygame
import sys
from random import randrange
from os.path import join
from itertools import product
from typing import Literal


# region game modes
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
NUM_MINES = int(MINE_PERCENT * GRID_SIZE[0] * GRID_SIZE[1])
# endregion

# region display settings
MODE = f"{GRID_SIZE[0]}*{GRID_SIZE[1]},{MINE_PERCENT}"
HEADER_SIZE = 50
SCREEN_SIZE = 750, 750 + HEADER_SIZE
# endregion

# region colors
MINE = "M"
COLOR_PALETTE = {
    1: (36, 124, 208),
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: "purple",
    5: "orange",
    6: "brown",
    7: "dark gray",
    8: "black",
    MINE: "red",
}
LIGHT_FIELD = (150, 195, 61)
DARK_FIELD = (137, 184, 53)
LIGHT_EMPTY = (239, 204, 170)
DARK_EMPTY = (215, 184, 154)
# endregion

# region setup
pygame.init()

CLOCK = pygame.time.Clock()
MAX_FPS = 60

FLAG_IMAGE_PATH = join("assets", "Minesweeper flag.png")
WATCH_IMAGE_PATH = join("assets", "Stopwatch.png")
MINE_IMAGE_PATH = join("assets", "mine.gif")

pygame.display.set_caption("Minesweeper")
ICON = pygame.image.load(MINE_IMAGE_PATH)
pygame.display.set_icon(ICON)

SCREEN = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
# endregion

# region types
Position = tuple[int, int]
Grid = list[list[int | Literal["M"]]]
PositionSet = set[Position]
# endregion


def main():
    while True:
        mine_field, mine_positions = mine_field_set_up()
        revealed: PositionSet = set()
        flagged: PositionSet = set()
        starting_time = pygame.time.get_ticks()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    on_mouse_button_down(event, mine_field, revealed, flagged)
            if len(mine_positions & flagged) == NUM_MINES:  # all mines flagged
                break
            if any(tile in mine_positions for tile in revealed):  # a mine revealed
                show_mines(mine_field, revealed, flagged)
                break
                # pygame.quit()
                # sys.exit()
            draw_mine_field(mine_field, revealed, flagged, starting_time)
            CLOCK.tick(MAX_FPS)
        write_high_score(starting_time)


def on_mouse_button_down(
    event: pygame.event.Event,
    mine_field: Grid,
    revealed: PositionSet,
    flagged: PositionSet,
):
    mouse_pos = pygame.mouse.get_pos()
    size = min(
        SCREEN.get_width() / GRID_SIZE[0],
        (SCREEN.get_height() - HEADER_SIZE) / GRID_SIZE[1],
    )
    if not (
        0 <= mouse_pos[0] <= size * GRID_SIZE[0]
        and HEADER_SIZE <= mouse_pos[1] <= size * GRID_SIZE[1] + HEADER_SIZE
    ):
        return
    pos = (int(mouse_pos[0] // size), int((mouse_pos[1] - HEADER_SIZE) // size))

    if event.button == pygame.BUTTON_LEFT:
        if pos in revealed or pos in flagged:
            return
        just_revealed = reveal_zero_tiles(mine_field, pos)
        revealed |= just_revealed
        flagged -= just_revealed
    elif event.button == pygame.BUTTON_MIDDLE:
        if pos not in revealed:
            return
        revealed, flagged = quick_reveal(mine_field, pos, revealed, flagged)
    elif event.button == pygame.BUTTON_RIGHT:
        if pos in revealed:
            return
        if pos in flagged:
            flagged.remove(pos)
        elif len(flagged) != NUM_MINES:
            flagged.add(pos)


def show_mines(mine_field: Grid, revealed: PositionSet, flagged: PositionSet):
    horizontal = SCREEN.get_width() / GRID_SIZE[0]
    vertical = (SCREEN.get_height() - HEADER_SIZE) / GRID_SIZE[1]
    block_size = min(horizontal, vertical)

    flag_image = pygame.transform.scale(
        pygame.image.load(FLAG_IMAGE_PATH), (block_size, block_size)
    )

    mine_image = pygame.transform.scale(
        pygame.image.load(MINE_IMAGE_PATH), [block_size, block_size]
    )

    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.rect.Rect(
                x * block_size, y * block_size + HEADER_SIZE, block_size, block_size
            )

            if (x, y) in revealed and mine_field[x][y] != MINE:
                color = DARK_EMPTY if (x + y) % 2 == 1 else LIGHT_EMPTY
                pygame.draw.rect(SCREEN, color, rect)
                pos = [
                    (x + 0.5) * block_size,
                    (y + 0.5) * block_size + HEADER_SIZE,
                ]
                draw_tile_nums(pos, mine_field[x][y], block_size)
                continue

            color = DARK_FIELD if (x + y) % 2 == 1 else LIGHT_FIELD

            pygame.draw.rect(SCREEN, color, rect)

            if (x, y) in flagged and mine_field[x][y] != MINE:
                SCREEN.blit(flag_image, [x * block_size, y * block_size + HEADER_SIZE])

            if mine_field[x][y] == MINE:
                SCREEN.blit(mine_image, [x * block_size, y * block_size + HEADER_SIZE])

    pygame.display.update()
    time.sleep(3)


def write_high_score(starting_time: int):
    score = int((pygame.time.get_ticks() - starting_time) / 1000)
    with open("High Scores.txt") as f:
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
    with open("High Scores.txt", mode="w") as f:
        string = ""
        for line in lines:
            if line:
                string += line + "\n"
        f.write(string)


def quick_reveal(
    mine_field: Grid, pos: Position, revealed: PositionSet, flagged: PositionSet
) -> tuple[PositionSet, PositionSet]:
    n = val_at_pos(mine_field, pos)
    if n == MINE:
        return revealed, flagged
    num_unrevealed = 0
    unrevealed_neighbors = set()
    for neighbor in neighbors(pos):
        if neighbor in flagged:
            n -= 1
        elif neighbor not in revealed:
            num_unrevealed += 1
            unrevealed_neighbors.add(neighbor)
    if n == 0:
        for unrevealed_neighbor in unrevealed_neighbors:
            if val_at_pos(mine_field, unrevealed_neighbor) == 0:
                just_revealed = reveal_zero_tiles(mine_field, unrevealed_neighbor)
                revealed |= just_revealed
                flagged -= just_revealed
        revealed |= unrevealed_neighbors
    if n == num_unrevealed:
        for unrevealed in unrevealed_neighbors:
            if len(flagged) != NUM_MINES:
                flagged.add(unrevealed)
    return revealed, flagged


def reveal_zero_tiles(mine_field, pos: Position) -> set[Position,]:
    if val_at_pos(mine_field, pos) != 0:
        return {pos}
    revealed = {pos} | set(neighbor for neighbor in neighbors(pos))
    to_check = set(neighbor for neighbor in neighbors(pos) if val_at_pos(mine_field, neighbor) == 0)
    while len(to_check) > 0:
        tile = to_check.pop()
        revealed.add(tile)
        for neighbor in neighbors(tile):
            if neighbor in revealed or neighbor in to_check:
                continue
            if val_at_pos(mine_field, neighbor) == 0:
                to_check.add(neighbor)
            elif val_at_pos(mine_field, neighbor) != MINE:
                revealed.add(neighbor)
    return revealed


def draw_mine_field(mine_field, revealed: set[Position,], flagged: set[Position,], starting_time):
    horizontal = SCREEN.get_width() / GRID_SIZE[0]
    vertical = (SCREEN.get_height() - HEADER_SIZE) / GRID_SIZE[1]
    block_size = int(min(horizontal, vertical))

    starting_color = (74, 117, 44)
    SCREEN.fill(starting_color)
    pygame.draw.rect(SCREEN, starting_color, pygame.rect.Rect(150, 0, block_size, block_size))

    mouse_pos = pygame.mouse.get_pos()
    converted_mouse_pos = (
        int(mouse_pos[0] // block_size),
        int((mouse_pos[1] - HEADER_SIZE) // block_size),
    )
    to_highlight = set(neighbors(converted_mouse_pos))
    to_highlight.add(converted_mouse_pos)

    image = pygame.transform.scale(pygame.image.load(FLAG_IMAGE_PATH), (47, 47))
    SCREEN.blit(image, [55, 2])
    make_text([100, 25], NUM_MINES - len(flagged), 50, "white")
    clock_image = pygame.transform.scale(pygame.image.load(WATCH_IMAGE_PATH), (47, 47))
    SCREEN.blit(clock_image, [186, 2])
    time = min(int((pygame.time.get_ticks() - starting_time) / 1000), 99999)
    make_text([233, 25], time, 50, "white")

    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.rect.Rect(
                x * block_size, y * block_size + HEADER_SIZE, block_size, block_size
            )
            if (x, y) in revealed:
                pygame.draw.rect(SCREEN, DARK_EMPTY if (x + y) % 2 == 1 else LIGHT_EMPTY, rect)
                if mine_field[x][y] == MINE:
                    continue
                pos = [(x + 0.5) * block_size, (y + 0.5) * block_size + HEADER_SIZE]
                draw_tile_nums(pos, mine_field[x][y], block_size)
                continue
            base_color = DARK_FIELD if (x + y) % 2 == 1 else LIGHT_FIELD
            color = []
            for channel in base_color:
                if (x, y) not in to_highlight or (x, y) in flagged:
                    color.append(channel)
                    continue
                color.append(min(channel + 30, 255))
            pygame.draw.rect(SCREEN, color, rect)
            if (x, y) in flagged:
                image = pygame.transform.scale(
                    pygame.image.load(FLAG_IMAGE_PATH), (block_size, block_size)
                )
                SCREEN.blit(image, [x * block_size, y * block_size + HEADER_SIZE])

    pygame.display.update()


def draw_tile_nums(pos, num, size):
    if num == 0:
        return
    font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
    text = font.render(str(num), True, COLOR_PALETTE[num])
    SCREEN.blit(text, text.get_rect(center=pos))


def make_text(pos, text, size, color):
    font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
    text = font.render(str(text), True, color)
    SCREEN.blit(text, text.get_rect(midleft=pos))


def mine_field_set_up() -> tuple[Grid, PositionSet]:
    possible_locations = list(product(range(GRID_SIZE[0]), range(GRID_SIZE[1])))
    mine_locations = {
        possible_locations.pop(randrange(len(possible_locations))) for _ in range(NUM_MINES)
    }

    mine_field: Grid = [[0] * GRID_SIZE[1] for _ in range(GRID_SIZE[0])]

    for mine_location in mine_locations:
        mine_field[mine_location[0]][mine_location[1]] = MINE
        for neighbor in neighbors(mine_location):
            if neighbor in mine_locations:
                continue
            assert mine_field[neighbor[0]][neighbor[1]] != "M", "Mine not marked in mine_locations"
            mine_field[neighbor[0]][neighbor[1]] += 1  # type: ignore

    return mine_field, mine_locations


def neighbors(pos: Position):
    x, y = pos
    for dx, dy in NEIGHBORING:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE[0] and 0 <= ny < GRID_SIZE[1]:
            yield (nx, ny)


def val_at_pos(mine_field: Grid, pos):
    return mine_field[int(pos[0])][int(pos[1])]


if __name__ == "__main__":
    main()
