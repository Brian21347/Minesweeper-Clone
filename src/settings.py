from os.path import join


# region: colors
class ColorPallette:
    BACKGROUND = "#20978D"
    HEADER_COLOR = "#4A752C"
    LIGHT_FIELD = "#AAD751"
    DARK_FIELD = "#A2D149"
    LIGHT_EMPTY = "#E5C29F"
    DARK_EMPTY = "#D7B899"
    LIGHT_FIELD_HIGHLIGHT = "#BFE17D"
    DARK_FIELD_HIGHLIGHT = "#B9DD77"
    LIGHT_EMPTY_HIGHLIGHT = "#ECD1B7"
    DARK_EMPTY_HIGHLIGHT = "#E1CAB3"
    SEPARATOR_COLOR = "#87AF3A"


CELL_COLORS = {
    1: "#1976D2",
    2: "#388E3C",
    3: "#D32F2F",
    4: "#7B1FA2",
    5: "#FF8F00",
    6: "#0097A7",
    7: "#5C4D35",
    8: "#B7B09D",
    "R": "dark green",
    "F": "dark red",
}
# endregion: colors

# region: constants
HEADER_HEIGHT = 50  # in pixels
MINE_FIELD_WIDTH = 24
MINE_FIELD_HEIGHT = 20
MIN_WIDTH, MIN_HEIGHT = 640, 480 

# MINE_FIELD_SIZE = HEADER_HEIGHT, MINE_FIELD_WIDTH
MINE_PERCENT = 0.24  # must be less than 1
NUM_MINES = int(MINE_PERCENT * MINE_FIELD_WIDTH * MINE_FIELD_HEIGHT)
SCREEN_SIZE = 750, 750 + HEADER_HEIGHT

# MODE = f"{MINE_FIELD_HEIGHT}*{MINE_FIELD_WIDTH},{MINE_PERCENT}"

MINE = "M"
MAX_FPS = 60

FLAG_IMAGE_PATH = join("src", "assets", "Minesweeper flag.png")
WATCH_IMAGE_PATH = join("src", "assets", "Stopwatch.png")
MINE_IMAGE_PATH = join("src", "assets", "mine.gif")

TEXT_SIZE = 30

SHOW_SOLVER_CONCLUSION = False
EXPERT_MODE = True

CENTER_DISPERSAL_RADIUS = 1.5
CORNER_DISPERSAL_RADIUS = 2.5
# endregion: constants

# region: data
CORNERS = [
    # topleft
    *[(0, 0), (0, 1), (1, 0), (1, 1)],
    *[
        (MINE_FIELD_HEIGHT - 1, 0),
        (MINE_FIELD_HEIGHT - 1, 1),
        (MINE_FIELD_HEIGHT - 2, 0),
        (MINE_FIELD_HEIGHT - 2, 1),
    ],  # topright
    *[
        (0, MINE_FIELD_WIDTH - 1),
        (1, MINE_FIELD_WIDTH - 1),
        (0, MINE_FIELD_WIDTH - 2),
        (1, MINE_FIELD_WIDTH - 2),
    ],  # bottomleft
    *[
        (MINE_FIELD_HEIGHT - 1, MINE_FIELD_WIDTH - 1),
        (MINE_FIELD_HEIGHT - 1, MINE_FIELD_WIDTH - 2),
        (MINE_FIELD_HEIGHT - 2, MINE_FIELD_WIDTH - 1),
        (MINE_FIELD_HEIGHT - 2, MINE_FIELD_WIDTH - 2),
    ],  # topright
]

CLASSIC = [
    [-1, -1],
    [-1, 0],
    [-1, 1],
    [0, -1],
    [0, 1],
    [1, -1],
    [1, 0],
    [1, 1],
]
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
MODE = CLASSIC
# endregion: data
