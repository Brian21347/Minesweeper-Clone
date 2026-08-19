from os.path import join
import json
from pydantic import BaseModel

# region: colors
class ColorPallette(BaseModel):
    background: str
    header_color: str
    light_field: str
    dark_field: str
    light_empty: str
    dark_empty: str
    light_field_highlight: str
    dark_field_highlight: str
    light_empty_highlight: str
    dark_empty_highlight: str
    separator_color: str
    cell_colors: list
    revealed: str
    flagged: str
    
with open(join("assets", "color pallettes.json")) as f:
    color_data = json.load(f)

color_pallette = ColorPallette.model_validate(color_data["default"])


# endregion: colors

# region: constants
HEADER_HEIGHT = 50  # in pixels
MINE_FIELD_WIDTH = 24
MINE_FIELD_HEIGHT = 20
MIN_WIDTH, MIN_HEIGHT = 640, 480

MINE_FIELD_SIZE = HEADER_HEIGHT, MINE_FIELD_WIDTH
MINE_PERCENT = 0.24  # must be less than 1
NUM_MINES = int(MINE_PERCENT * MINE_FIELD_WIDTH * MINE_FIELD_HEIGHT)
SCREEN_SIZE = 750, 750 + HEADER_HEIGHT


MINE = "M"
MAX_FPS = 60

FLAG_IMAGE_PATH = join("assets", "Minesweeper flag.png")
WATCH_IMAGE_PATH = join("assets", "Stopwatch.png")
MINE_IMAGE_PATH = join("assets", "mine.gif")

BASE_TEXT_SIZE = 30

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
ADJACENCY = CLASSIC
# endregion: data
