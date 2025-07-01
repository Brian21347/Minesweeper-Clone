import time
import pygame
from sys import exit
from random import randrange

pygame.init()

# constants for what counts as neighboring
STANDARD = [
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [0, -1],
    [0, 1],
    [1, -1],
    [1, 0],
    [1, 1]
]
KNIGHT = [
    [1, 2],
    [1, -2],
    [2, 1],
    [2, -1],
    [-1, 2],
    [-1, -2],
    [-2, 1],
    [-2, -1]
]
NEIGHBORING = STANDARD  # edit this to change the game mode!

FLAG_IMAGE_PATH = 'Minesweeper flag.png'
MINE_IMAGE_PATH = 'mine.gif'

pygame.display.set_caption('Minesweeper')
icon = pygame.image.load(MINE_IMAGE_PATH)
pygame.display.set_icon(icon)

# color constants
LIGHT_FIELD = (150, 195, 61)  # (170, 215, 81)
DARK_FIELD = (137, 184, 53)  # (162, 209, 73)
LIGHT_EMPTY = (239, 204, 170)  # (229, 194, 159)
DARK_EMPTY = (215, 184, 154)  # (215, 184, 154)


# constants for the percentage of tiles that are mines and the size of the screen
MINE_PERCENT = .15
SIZE = [10, 10]
NUM_MINES = MINE_PERCENT * SIZE[0] * SIZE[1]
MODE = f'{SIZE[0]}*{SIZE[1]},{MINE_PERCENT}'

# size of the header
HEADER_SIZE = 50

# display obj
SCREEN = pygame.display.set_mode((750, 750 + HEADER_SIZE), pygame.RESIZABLE)

# colors for the number a tile contains
COLORS_FOR_NUMS = {
    1: (36, 124, 208),
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: 'purple',
    5: 'orange',
    6: 'brown',
    7: 'dark gray',
    8: 'black',
    'M': 'red'
}


# constant for clock
CLOCK = pygame.time.Clock()


def main():
    while True:
        mine_field, mine_positions = mine_field_set_up()
        revealed: set[tuple[int, int],] = set()
        flagged: set[tuple[int, int],] = set()
        starting_time = pygame.time.get_ticks()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    size = min(
                        SCREEN.get_width() / SIZE[0], (SCREEN.get_height() - HEADER_SIZE) / SIZE[1])
                    if not (0 <= mouse_pos[0] <= size * SIZE[0] and HEADER_SIZE <= mouse_pos[1] <= size * SIZE[
                            1] + HEADER_SIZE):
                        continue
                    pos = (mouse_pos[0] // size,
                           (mouse_pos[1] - HEADER_SIZE) // size)

                    if event.button == 1:  # left click
                        if pos not in revealed and pos not in flagged:
                            just_revealed = reveal_zero_tiles(mine_field, pos)
                            revealed |= just_revealed
                            flagged -= just_revealed
                    elif event.button == 2:  # middle click
                        if pos in revealed:
                            revealed, flagged = quick_reveal(
                                mine_field, pos, revealed, flagged)
                    elif event.button == 3:  # right click
                        if pos in revealed:
                            continue
                        if pos in flagged:
                            flagged.remove(pos)
                        elif len(flagged) != NUM_MINES:
                            flagged.add(pos)
            if len(mine_positions & flagged) == int(NUM_MINES):
                break
            if [tile for tile in revealed if tile in mine_positions]:
                show_mines(mine_field, revealed, flagged)
                exit()
            draw_mine_field(mine_field, revealed, flagged, starting_time)
            CLOCK.tick(12)
        write_high_score(starting_time)


def show_mines(mine_field, revealed, flagged):
    horizontal = SCREEN.get_width() / SIZE[0]
    vertical = (SCREEN.get_height() - HEADER_SIZE) / SIZE[1]
    block_size = min(horizontal, vertical)

    flag_image = pygame.transform.scale(pygame.image.load(
        FLAG_IMAGE_PATH), (block_size, block_size))

    mine_image = pygame.transform.scale(pygame.image.load(
        MINE_IMAGE_PATH), [block_size, block_size])

    for x in range(SIZE[0]):
        for y in range(SIZE[1]):
            rect = pygame.rect.Rect(
                x * block_size, y * block_size + HEADER_SIZE, block_size, block_size)

            if (x, y) in revealed and mine_field[x][y] != 'M':
                pygame.draw.rect(SCREEN, DARK_EMPTY if (x + y) %
                                 2 == 1 else LIGHT_EMPTY, rect)
                make_tile_nums([(x + .5) * block_size, (y + .5) * block_size + HEADER_SIZE], mine_field[x][y],
                               block_size)
                continue

            color = DARK_FIELD if (x + y) % 2 == 1 else LIGHT_FIELD

            pygame.draw.rect(SCREEN, color, rect)

            if (x, y) in flagged and mine_field[x][y] != 'M':
                SCREEN.blit(flag_image, [x * block_size,
                            y * block_size + HEADER_SIZE])

            if mine_field[x][y] == 'M':
                SCREEN.blit(mine_image, [x * block_size,
                            y * block_size + HEADER_SIZE])

    pygame.display.update()
    time.sleep(3)


def write_high_score(starting_time):
    score = int((pygame.time.get_ticks() - starting_time) / 1000)
    with open('High Scores.txt') as f:
        lines = f.read().split('\n')
    for i, line in enumerate(lines):
        line = line.split(';')
        if not len(line):
            continue
        if line[0] == f'{SIZE[0]}*{SIZE[1]}' and line[1] == str(MINE_PERCENT) and line[2] == str(NEIGHBORING):
            if int(line[3]) > score:
                lines[i] = f'{SIZE[0]}*{SIZE[1]};{MINE_PERCENT};{NEIGHBORING};{score}'
            break
    else:
        lines.append(
            f'{SIZE[0]}*{SIZE[1]};{MINE_PERCENT};{NEIGHBORING};{score}')
    with open('High Scores.txt', mode='w') as f:
        string = ''
        for line in lines:
            if line:
                string += line + '\n'
        f.write(string)


def quick_reveal(mine_field, pos, revealed: set[tuple[int, int],], flagged: set[tuple[int, int],]):
    n = val_at_pos(mine_field, pos)
    if n == 'M':
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
                just_revealed = reveal_zero_tiles(
                    mine_field, unrevealed_neighbor)
                revealed |= just_revealed
                flagged -= just_revealed
        revealed |= unrevealed_neighbors
    if n == num_unrevealed:
        for unrevealed in unrevealed_neighbors:
            if len(flagged) != NUM_MINES:
                flagged.add(unrevealed)
    return revealed, flagged


def reveal_zero_tiles(mine_field, pos: tuple[int, int]) -> set[tuple[int, int],]:
    if val_at_pos(mine_field, pos) != 0:
        return {pos}
    revealed = {pos} | set(neighbor for neighbor in neighbors(pos))
    to_check = set(neighbor for neighbor in neighbors(
        pos) if val_at_pos(mine_field, neighbor) == 0)
    while len(to_check) > 0:
        tile = to_check.pop()
        revealed.add(tile)
        for neighbor in neighbors(tile):
            if neighbor in revealed or neighbor in to_check:
                continue
            if val_at_pos(mine_field, neighbor) == 0:
                to_check.add(neighbor)
            elif val_at_pos(mine_field, neighbor) != 'M':
                revealed.add(neighbor)
    return revealed


def draw_mine_field(mine_field, revealed: set[tuple[int, int],], flagged: set[tuple[int, int],], starting_time):
    horizontal = SCREEN.get_width() / SIZE[0]
    vertical = (SCREEN.get_height() - HEADER_SIZE) / SIZE[1]
    block_size = min(horizontal, vertical)

    starting_color = (74, 117, 44)
    SCREEN.fill(starting_color)
    pygame.draw.rect(SCREEN, starting_color, pygame.rect.Rect(
        150, 0, block_size, block_size))

    mouse_pos = pygame.mouse.get_pos()
    to_highlight = set(
        neighbor for neighbor in neighbors(
            (int(mouse_pos[0] // block_size),
             int((mouse_pos[1] - HEADER_SIZE) // block_size))
        )
    )
    to_highlight.add((mouse_pos[0] // block_size,
                     (mouse_pos[1] - HEADER_SIZE) // block_size))

    image = pygame.transform.scale(
        pygame.image.load(FLAG_IMAGE_PATH), (47, 47))
    SCREEN.blit(image, [55, 2])
    make_text([100, 25], int(NUM_MINES - len(flagged)), 50, 'white')
    clock_image = pygame.transform.scale(
        pygame.image.load('Stopwatch.png'), (47, 47))
    SCREEN.blit(clock_image, [186, 2])
    make_text([233, 25], min(
        int((pygame.time.get_ticks() - starting_time) / 1000), 99999), 50, 'white')

    for x in range(SIZE[0]):
        for y in range(SIZE[1]):
            rect = pygame.rect.Rect(
                x * block_size, y * block_size + HEADER_SIZE, block_size, block_size)
            if (x, y) in revealed:
                pygame.draw.rect(SCREEN, DARK_EMPTY if (x + y) %
                                 2 == 1 else LIGHT_EMPTY, rect)
                if mine_field[x][y] == 'M':
                    continue
                make_tile_nums([(x + .5) * block_size, (y + .5) * block_size + HEADER_SIZE], mine_field[x][y],
                               block_size)
                continue
            color = [(min(channel + 30, 255) if (x, y) in to_highlight and (x, y) not in flagged else channel)
                     for channel in (DARK_FIELD if (x + y) % 2 == 1 else LIGHT_FIELD)]
            pygame.draw.rect(SCREEN, color, rect)
            if (x, y) in flagged:
                image = pygame.transform.scale(pygame.image.load(
                    FLAG_IMAGE_PATH), (block_size, block_size))
                SCREEN.blit(image, [x * block_size, y *
                            block_size + HEADER_SIZE])

    pygame.display.update()


def make_tile_nums(pos, num, size):
    if num == 0:
        return
    font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
    text = font.render(str(num), True, COLORS_FOR_NUMS[num])
    SCREEN.blit(text, text.get_rect(center=pos))


def make_text(pos, text, size, color):
    font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
    text = font.render(str(text), True, color)
    SCREEN.blit(text, text.get_rect(midleft=pos))


def mine_field_set_up() -> tuple[list[list[int | str],], set[tuple[int, int],]]:
    mine_locations: set[tuple[int, int],] = set()
    while len(mine_locations) < NUM_MINES:
        mine_locations.add((randrange(0, SIZE[0]), randrange(0, SIZE[1])))
    mine_field: list[list[int | str],] = [
        [0 for _ in range(SIZE[1])] for _ in range(SIZE[0])]

    for mine_location in mine_locations:  # mine_location is list[int, int]
        mine_field[mine_location[0]][mine_location[1]] = 'M'
        for neighbor in neighbors(mine_location):
            if neighbor not in mine_locations:
                mine_field[neighbor[0]][neighbor[1]] += 1

    return mine_field, mine_locations


def neighbors(pos: tuple[int, int]):
    for neighboring_pos in NEIGHBORING:
        possible_pos = pos[0] + neighboring_pos[0], pos[1] + neighboring_pos[1]
        if 0 <= possible_pos[0] < SIZE[0] and 0 <= possible_pos[1] < SIZE[1]:
            yield possible_pos


def val_at_pos(mine_field, pos):
    return mine_field[int(pos[0])][int(pos[1])]


if __name__ == '__main__':
    main()
