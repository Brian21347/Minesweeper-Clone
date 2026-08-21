from rebuild.interfaces.position import Pos
from rebuild.interfaces.solving_field import SolvingField
from rebuild.interfaces.minefield import MineField


class Solver:
    def __init__(self, mine_field: MineField) -> None: 
        self.field = SolvingField(mine_field)
        self.num_mines = mine_field.num_mines
        self.size = mine_field.size

        self.border = set()
        return

    def solve(self): ...
