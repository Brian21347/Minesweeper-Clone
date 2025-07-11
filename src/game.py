# from screen import Screen
import time
import pygame
import sys
from random import randrange
from os.path import join
from itertools import product
from typing import Literal
from solver import Solver, bind_verifier, PlayerPosition, print_position, print_marked, UNKNOWN
from colorama import Fore


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
MINE_PERCENT = 0.24
assert MINE_PERCENT < 1, "MINE_PERCENT must be less than 1"
GRID_SIZE = 20, 24  # (number of rows, number of columns)
CORNERS = [
    # topleft
    *[(0, 0), (0, 1), (1, 0), (1, 1)],
    *[
        (GRID_SIZE[0] - 1, 0),
        (GRID_SIZE[0] - 1, 1),
        (GRID_SIZE[0] - 2, 0),
        (GRID_SIZE[0] - 2, 1),
    ],  # topright
    *[
        (0, GRID_SIZE[1] - 1),
        (1, GRID_SIZE[1] - 1),
        (0, GRID_SIZE[1] - 2),
        (1, GRID_SIZE[1] - 2),
    ],  # bottomleft
    *[
        (GRID_SIZE[0] - 1, GRID_SIZE[1] - 1),
        (GRID_SIZE[0] - 1, GRID_SIZE[1] - 2),
        (GRID_SIZE[0] - 2, GRID_SIZE[1] - 1),
        (GRID_SIZE[0] - 2, GRID_SIZE[1] - 2),
    ],  # topright
]
CENTER_DISPERSAL_RADIUS = 1.5
CORNER_DISPERSAL_RADIUS = 2.5
NUM_MINES = int(MINE_PERCENT * GRID_SIZE[0] * GRID_SIZE[1])
# endregion

# region display settings
MODE = f"{GRID_SIZE[0]}*{GRID_SIZE[1]},{MINE_PERCENT}"
HEADER_SIZE = 50
# endregion

# region colors
MINE = "M"
COLOR_PALETTE = {
    1: "#1976D2",
    2: (56, 142, 60),
    3: (211, 47, 47),
    4: "purple",
    5: "orange",
    6: "brown",
    7: "dark gray",
    8: "black",
    MINE: "red",
    "R": "dark green",
    "F": "dark red",
}
LIGHT_FIELD = (150, 195, 61)
DARK_FIELD = (137, 184, 53)
LIGHT_EMPTY = (239, 204, 170)
DARK_EMPTY = (215, 184, 154)
# endregion

# region setup
CLOCK = pygame.time.Clock()
MAX_FPS = 60

FLAG_IMAGE_PATH = join("src", "assets", "Minesweeper flag.png")
WATCH_IMAGE_PATH = join("src", "assets", "Stopwatch.png")
MINE_IMAGE_PATH = join("src", "assets", "mine.gif")
# endregion

# region types
Position = tuple[int, int]
Grid = list[list[int | Literal["M"]]]
PositionSet = set[Position]
# endregion

SHOW_SOLVER_CONCLUSION = False
EXPERT_MODE = True


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.mine_field: Grid = []
        self.mine_positions: PositionSet = set()
        self.won = False
        self.first_click = True
        self.revealed: PositionSet = set()
        self.flagged: PositionSet = set()
        self.guess_flags: PositionSet = set()
        self.starting_time = pygame.time.get_ticks()
        self.solver = None
        # screen_size = self.screen.get_size()
        # self.field_surf = pygame.surface.Surface(screen_size)
        # self.uncovered_surf = pygame.surface.Surface(screen_size)
        # self.flag_surf = pygame.surface.Surface(screen_size)

    def get_block_size(self):
        return int(
            min(
                self.screen.get_width() / GRID_SIZE[1],
                (self.screen.get_height() - HEADER_SIZE) / GRID_SIZE[0],
            )
        )

    def run(self):
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
                    if EXPERT_MODE and self.is_guess(event):
                        self.make_loss_position(event)
                        self.lose()
                        return
                    self.on_mouse_button_down(event)
            if len(self.revealed) == GRID_SIZE[0] * GRID_SIZE[1] - NUM_MINES:  # all non-mines revealed
                self.won = True
                return
            if any(tile in self.mine_positions for tile in self.revealed):  # a mine was revealed
                self.lose()
                return
            self.draw()
            CLOCK.tick(MAX_FPS)

    def lose(self):
        self.show_mines()
        pygame.event.clear()
        self.won = False

    def on_mouse_button_down(
        self,
        event: pygame.event.Event,
    ):
        mouse_pos = self.get_mouse_pos()
        if not 0 <= mouse_pos[0] < GRID_SIZE[1] and 0 <= mouse_pos[1] < GRID_SIZE[0]:
            return

        if event.button == pygame.BUTTON_LEFT:
            if mouse_pos in self.revealed or mouse_pos in self.flagged:
                return 
            if self.first_click:
                self.mine_field_set_up(mouse_pos)
                self.first_click = False
            else:
                self.reveal_tile(mouse_pos)
        elif event.button == pygame.BUTTON_MIDDLE:
            if mouse_pos not in self.revealed:
                return
            self.quick_reveal(mouse_pos)
        elif event.button == pygame.BUTTON_RIGHT:
            if mouse_pos in self.revealed:
                return
            if mouse_pos in self.flagged:
                self.flagged.remove(mouse_pos)
                if mouse_pos in self.guess_flags:
                    self.guess_flags.remove(mouse_pos)
            elif len(self.flagged) != NUM_MINES:
                self.flagged.add(mouse_pos)
    
    def is_guess(self, event: pygame.event.Event):
        revealed, flagged = [], []
        if self.solver is None:
            return None
        self.solver.update(NUM_MINES - len(self.flagged), self.get_player_position())
        revealed, flagged = self.solver.solve(True)

        mouse_pos = self.get_mouse_pos()
        if not 0 <= mouse_pos[0] < GRID_SIZE[1] and 0 <= mouse_pos[1] < GRID_SIZE[0]:
            return False
        if event.button == pygame.BUTTON_LEFT:
            if mouse_pos in self.revealed or mouse_pos in self.flagged:
                return False
            if mouse_pos not in revealed:
                return True
        elif event.button == pygame.BUTTON_MIDDLE:
            if mouse_pos not in self.revealed:
                return False
            for neighbor in self.neighbors(mouse_pos):
                if neighbor in self.guess_flags:
                    return True
        elif event.button == pygame.BUTTON_RIGHT:
            if mouse_pos in self.revealed:
                return False
            if mouse_pos in self.flagged:
                return False
            if len(self.flagged) == NUM_MINES:
                return False
            if mouse_pos in flagged:
                return False
            self.guess_flags.add(mouse_pos)
            return True
        return False

    def make_loss_position(self, event):
        assert self.solver
        mouse_pos = self.get_mouse_pos()
        if mouse_pos in self.mine_positions:
            return
        self.solver.update_position(self.get_player_position())
        revealed, flagged = self.solver.solve(tentative=True)
        unrevealed_neighbors = set(
            (nr, nc)
            for r, c in self.solver.bordering
            for nr, nc in self.neighbors((r, c))
            if self.solver.position[nr][nc] == "."
        )
        uncertain = unrevealed_neighbors - revealed - flagged
        if mouse_pos not in uncertain:
            can_remove = self.mine_positions - self.flagged - flagged
            self.mine_positions.remove(can_remove.pop())
            self.mine_positions.add(mouse_pos)
            return
        to_remove = set()
        for mine_pos in self.mine_positions:
            if mine_pos in uncertain:
                to_remove.add(mine_pos)
        for mine in to_remove:
            self.mine_positions.remove(mine)

        self.flagged.add(mouse_pos)
        self.mine_positions.add(mouse_pos)
        self.solver.update_position(self.get_player_position())
        self.flagged.remove(mouse_pos)
        _, n_flagged = self.solver.solve(tentative=True)
        self.mine_positions.add(mouse_pos)
        self.mine_positions.update(n_flagged - flagged)

    def get_player_position(self):
        """
        Return a version of the minefield that the player would be seeing
        0-8: Neighboring tile values
        .  : Unknown
        F  : Flagged
        """
        self.flagged
        self.revealed
        field: PlayerPosition = []
        for x, row in enumerate(self.mine_field):
            field.append([])
            for y, val in enumerate(row):
                pos = (x, y)
                if pos in self.flagged:
                    field[-1].append("F")
                    continue
                if pos in self.revealed:
                    field[-1].append(int(val))
                    continue
                field[-1].append(".")
        return field
    
    def save_to_file(self):
        """
        Saves the initially revealed position to a file
        """
        field = self.get_player_position()
        with open("Tests.txt", "a") as f:
            print(NUM_MINES, file=f)
            for row in field:
                print("".join(map(str, row)), file=f)
            print("=====", file=f)
            for row in self.mine_field:
                print("".join(map(str, row)), file=f)
            print("==========", file=f)

    def show_mines(self):
        block_size = self.get_block_size()

        flag_image = pygame.transform.scale(
            pygame.image.load(FLAG_IMAGE_PATH), (block_size, block_size)
        )

        mine_image = pygame.transform.scale(
            pygame.image.load(MINE_IMAGE_PATH), [block_size, block_size]
        )

        for r in range(GRID_SIZE[0]):
            for c in range(GRID_SIZE[1]):
                rect = pygame.rect.Rect(
                    c * block_size, r * block_size + HEADER_SIZE, block_size, block_size
                )

                if (r, c) in self.revealed and (r, c) not in self.mine_positions:
                    color = DARK_EMPTY if (r + c) % 2 == 1 else LIGHT_EMPTY
                    pygame.draw.rect(self.screen, color, rect)
                    pos = [
                        (c + 0.5) * block_size,
                        (r + 0.5) * block_size + HEADER_SIZE,
                    ]
                    self.draw_tile_nums(pos, self.mine_field[r][c], block_size)
                    continue

                color = DARK_FIELD if (r + c) % 2 == 1 else LIGHT_FIELD

                pygame.draw.rect(self.screen, color, rect)

                if (r, c) in self.flagged and (r, c) not in self.mine_positions:
                    self.screen.blit(flag_image, [c * block_size, r * block_size + HEADER_SIZE])

                if (r, c) in self.mine_positions:
                    self.screen.blit(mine_image, [c * block_size, r * block_size + HEADER_SIZE])

        pygame.display.update()
        time.sleep(2)

    def quick_reveal(self, pos):
        n = self.val_at_pos(pos)
        if n == MINE:
            return
        num_unrevealed = 0
        unrevealed_neighbors = set()
        for neighbor in self.neighbors(pos):
            if neighbor in self.flagged:
                n -= 1
            elif neighbor not in self.revealed:
                num_unrevealed += 1
                unrevealed_neighbors.add(neighbor)
        if n == 0:
            for unrevealed_neighbor in unrevealed_neighbors:
                self.reveal_tile(unrevealed_neighbor)
        if n == num_unrevealed:
            for unrevealed in unrevealed_neighbors:
                self.flagged.add(unrevealed)

    def reveal_tile(self, pos: Position):
        if self.val_at_pos(pos) != 0:
            self.revealed |= {pos}
            return
        just_revealed = {pos} | set(neighbor for neighbor in self.neighbors(pos))
        to_check = set(
            neighbor for neighbor in self.neighbors(pos) if self.val_at_pos(neighbor) == 0
        )
        while len(to_check) > 0:
            tile = to_check.pop()
            just_revealed.add(tile)
            for neighbor in self.neighbors(tile):
                if neighbor in just_revealed or neighbor in to_check:
                    continue
                if self.val_at_pos(neighbor) == 0:
                    to_check.add(neighbor)
                else:
                    assert (
                        self.val_at_pos(neighbor) != MINE
                    ), "Revealed a mine through reveal_zero_tile"
                    just_revealed.add(neighbor)
        self.revealed |= just_revealed
        assert self.flagged & just_revealed == set(), "No revealed mines should have been flagged"

    def draw(self):
        block_size = self.get_block_size()

        starting_color = (74, 117, 44)
        self.screen.fill(starting_color)

        mouse_pos = self.get_mouse_pos()
        to_highlight = {mouse_pos}
        if mouse_pos in self.revealed:
            to_highlight |= set(self.neighbors(mouse_pos))

        image = pygame.transform.scale(pygame.image.load(FLAG_IMAGE_PATH), (47, 47))
        self.screen.blit(image, [55, 2])
        self.make_text([100, 25], NUM_MINES - len(self.flagged), 50, "white")
        clock_image = pygame.transform.scale(pygame.image.load(WATCH_IMAGE_PATH), (47, 47))
        self.screen.blit(clock_image, [186, 2])
        time = min(int((pygame.time.get_ticks() - self.starting_time) / 1000), 99999)
        self.make_text([233, 25], time, 50, "white")


        revealed, flagged = [], []
        if SHOW_SOLVER_CONCLUSION and self.solver is not None:
            self.solver.update(NUM_MINES - len(self.flagged) + len(self.guess_flags), self.get_player_position())
            revealed, flagged = self.solver.solve(tentative=True)

        for r in range(GRID_SIZE[0]):
            for c in range(GRID_SIZE[1]):
                rect = pygame.rect.Rect(
                    c * block_size, r * block_size + HEADER_SIZE, block_size, block_size
                )
                if (r, c) in self.revealed:
                    pygame.draw.rect(
                        self.screen, DARK_EMPTY if (r + c) % 2 == 1 else LIGHT_EMPTY, rect
                    )
                    if self.mine_field[r][c] == MINE:
                        continue
                    pos = [(c + 0.5) * block_size, (r + 0.5) * block_size + HEADER_SIZE]
                    self.draw_tile_nums(pos, self.mine_field[r][c], block_size)
                    continue
                base_color = DARK_FIELD if (r + c) % 2 == 1 else LIGHT_FIELD
                color = []
                for channel in base_color:
                    if (r, c) not in to_highlight or (r, c) in self.flagged:
                        color.append(channel)
                        continue
                    color.append(min(channel + 30, 255))
                pygame.draw.rect(self.screen, color, rect)
                if (r, c) in self.flagged:
                    image = pygame.transform.scale(
                        pygame.image.load(FLAG_IMAGE_PATH), (block_size, block_size)
                    )
                    self.screen.blit(image, [c * block_size, r * block_size + HEADER_SIZE])
                if SHOW_SOLVER_CONCLUSION:
                    if (r, c) in revealed:
                        pos = [(c + 0.5) * block_size, (r + 0.5) * block_size + HEADER_SIZE]
                        self.draw_tile_nums(pos, "R", block_size)
                    if (r, c) in flagged:
                        pos = [(c + 0.5) * block_size, (r + 0.5) * block_size + HEADER_SIZE]
                        self.draw_tile_nums(pos, "F", block_size)

        pygame.display.update()

    def draw_tile_nums(self, pos, num, size):
        if num == 0:
            return
        font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
        text = font.render(str(num), True, COLOR_PALETTE[num])
        self.screen.blit(text, text.get_rect(center=pos))

    def make_text(self, pos, text, size, color):
        font = pygame.font.SysFont(pygame.font.get_default_font(), int(size))
        text = font.render(str(text), True, color)
        self.screen.blit(text, text.get_rect(midleft=pos))

    def mine_field_set_up(self, mouse_pos: Position):
        possible_locations = list(
            (r, c) for r, c in product(range(GRID_SIZE[0]), range(GRID_SIZE[1]))
        )

        mr, mc = mouse_pos
        radius = CORNER_DISPERSAL_RADIUS if mouse_pos in CORNERS else CENTER_DISPERSAL_RADIUS
        i = 0
        while i < len(possible_locations):
            r, c = possible_locations[i]
            if abs(mr - r) ** 2 + abs(mc - c) ** 2 <= radius**2:
                possible_locations.pop(i)
                continue
            i += 1

        self.mine_positions = {
            possible_locations.pop(randrange(len(possible_locations))) for _ in range(NUM_MINES)
        }

        self.mine_field: Grid = [[0] * GRID_SIZE[1] for _ in range(GRID_SIZE[0])]

        for r, c in self.mine_positions:
            self.mine_field[r][c] = MINE
            for nr, nc in self.neighbors((r, c)):
                if (nr, nc) in self.mine_positions:
                    continue
                assert self.mine_field[nr][nc] != "M", "Mine not marked in mine_locations"
                self.mine_field[nr][nc] += 1  # type: ignore
        self.reveal_tile(mouse_pos)
        self.solver = Solver(NUM_MINES, self.get_player_position(), bind_verifier(self.mine_field))

    def neighbors(self, pos: Position):
        r, c = pos
        for dr, dc in NEIGHBORING:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE[0] and 0 <= nc < GRID_SIZE[1]:
                yield (nr, nc)

    def val_at_pos(self, pos: Position):
        return self.mine_field[pos[0]][pos[1]]

    def get_starting_time(self):
        return self.starting_time

    def did_win(self):
        return self.won
    
    def get_mouse_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        block_size = self.get_block_size()
        return (int((mouse_pos[1] - HEADER_SIZE) // block_size), int(mouse_pos[0] // block_size))
