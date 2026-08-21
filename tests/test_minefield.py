import random

import pytest

from rebuild.interfaces.minefield import MineField
from rebuild.interfaces.position import Pos


@pytest.fixture(autouse=True)
def set_seed():
    random.seed(0)


def test_minefield():
    field = MineField((10, 10), 25)
    field.generate(Pos(0, 0))
    assert list(field.all_revealed()) == [
        (Pos(0, 0), 0),
        (Pos(0, 1), 0),
        (Pos(0, 2), 0),
        (Pos(0, 3), 0),
        (Pos(0, 4), 1),
        (Pos(1, 0), 0),
        (Pos(1, 1), 1),
        (Pos(1, 2), 1),
        (Pos(1, 3), 1),
        (Pos(1, 4), 1),
        (Pos(2, 0), 0),
        (Pos(2, 1), 1),
        (Pos(3, 0), 0),
        (Pos(3, 1), 1),
        (Pos(4, 0), 0),
        (Pos(4, 1), 1),
        (Pos(5, 0), 1),
        (Pos(5, 1), 3),
    ]
