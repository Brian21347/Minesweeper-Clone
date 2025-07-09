from itertools import combinations
from typing import Literal, Callable, Iterable, overload
from time import perf_counter
from colorama import Fore, Back
from copy import deepcopy

PlayerPosition = list[list[int | Literal[".", "F", "R"]]]
MineField = list[list[int | Literal["M"]]]
Position = tuple[int, int]
PositionSet = set[Position]
SetDict = dict[frozenset[Position], int]

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
MINE = "M"
UNKNOWN = "."
FLAG = "F"
REVEALED = "R"


def verifier(
    position: PlayerPosition,
    mine_field: MineField,
    to_reveal: Iterable[Position],
    to_flag: Iterable[Position],
):
    """
    Checks that moves made by the solver are correct. Assumes all past moves are correct.
    """
    assert all(MINE not in row for row in position), "A mine was revealed in the position"
    assert all(
        UNKNOWN not in row for row in mine_field
    ), "The mine field does not have all information"
    assert all(FLAG not in row for row in mine_field), "The mine field has a flag in it"
    for r, c in to_reveal:
        if mine_field[r][c] == MINE:
            print_position(position)
            raise ValueError("Solver tried revealing a mine")
        position[r][c] = mine_field[r][c]  # type: ignore
    for r, c in to_flag:
        if mine_field[r][c] != MINE:
            print_position(position)
            raise ValueError("Solver flagging a non mine")
        position[r][c] = FLAG


def bind_verifier(mine_field: MineField):
    def func(position: PlayerPosition, to_reveal: Iterable[Position], to_flag: Iterable[Position]):
        verifier(position, mine_field, to_reveal, to_flag)

    return func


class Solver:
    def __init__(
        self,
        num_mines: int,
        position: PlayerPosition,
        verifier: Callable[[PlayerPosition, Iterable[Position], Iterable[Position]], None],
    ) -> None:
        self.num_mines = num_mines
        self.position = position
        self.verifier = verifier

        self.num_rows = len(position)
        self.num_columns = len(position[0])

        self.bordering = set(self.find_all_bordering())

    def solve(self):
        revealed, flagged = set(), set()
        while (val := self.solve_step())[0]:
            revealed |= val[1][0]
            flagged |= val[1][1]
        # to_reveal, to_flag = self.brute_force(2)
        # if bool(to_reveal) or bool(to_flag):
        #     print_marked(
        #         self.position,
        #         {
        #             frozenset(to_reveal): Fore.GREEN + "R" + Fore.RESET,
        #             frozenset(to_flag): Fore.GREEN + "F" + Fore.RESET,
        #         },
        #     )
        #     print("Brute force revealed something")
        # return revealed | to_reveal, flagged | to_flag
        return revealed, flagged

    def find_all_bordering(self):
        for row in range(self.num_rows):
            for col in range(self.num_columns):
                if self.is_bordering(row, col):
                    yield (row, col)

    def is_bordering(self, r, c):
        value = self.position[r][c]
        if value == FLAG or value == UNKNOWN:
            return False
        for nr, nc in self.neighbors(r, c):
            if self.position[nr][nc] == UNKNOWN:
                return True
        return False

    def solve_step(self, tentative=False):
        sets = self.get_sets()
        self.check_subsets(sets)
        self.check_squeezes(sets)
        self.check_subsets(sets)
        changed = self.apply_basic_logic(sets, tentative)
        if not tentative:
            self.update_bordering()
        return (bool(changed[0]) or bool(changed[1])), changed

    def brute_force(self, max_depth):
        possible_mine_positions = set()

        def dfs(flagged: PositionSet, depth=0):
            nonlocal possible_mine_positions
            if self.num_mines < len(flagged):
                return
            mark_flagged = set()
            try:
                while (changed := self.solve_step(tentative=True))[0]:
                    mark_flagged |= changed[1][1]
            except ValueError:
                return
            sets = self.get_sets()
            if not sets:  # no empty unknown positions neighboring the initial bordering positions
                if len(flagged | mark_flagged) > self.num_mines:
                    return
                if not self.position_is_valid():
                    return
                possible_mine_positions.add(frozenset(flagged | mark_flagged))
                return
            possible_combos = set()  # get unique mine placements
            while sets:
                group, val = sets.popitem()
                for mine_combo in combinations(group, val):
                    possible_combos.add(frozenset(mine_combo))
            if depth >= max_depth:
                return
            original_position = deepcopy(self.position)
            for mine_combo in possible_combos:
                self.mark_tentatively([], mine_combo)
                dfs(flagged | mine_combo | mark_flagged, depth + 1)
                self.position = deepcopy(original_position)

        orig = deepcopy(self.position)
        dfs(set())
        self.position = orig
        if not possible_mine_positions:
            return set(), set()
        always_mines = frozenset.intersection(*possible_mine_positions)
        unrevealed = frozenset(
            (nr, nc)
            for r, c in self.bordering
            for nr, nc in self.neighbors(r, c)
            if self.position[nr][nc] == UNKNOWN
        )
        never_mines = unrevealed - frozenset.union(*possible_mine_positions)
        try:
            self.verifier(self.position, never_mines, always_mines)
        except ValueError as e:
            print(e)
            print("Mines:", always_mines)
            print("Revealed:", never_mines)
        # print("FINAL:")
        # print_marked(
        #     self.position,
        #     {
        #         always_mines: Fore.GREEN + FLAG + Fore.RESET,
        #         never_mines: Fore.GREEN + REVEALED + Fore.RESET,
        #     },
        # )
        return set(never_mines), set(always_mines)

    def position_is_valid(self):
        """
        Used for checking during brute force if positions is valid.
        """
        for r, c in self.bordering:
            val = int(self.position[r][c])
            completed = True
            for nr, nc in self.neighbors(r, c):
                if self.position[nr][nc] == FLAG:
                    val -= 1
                if self.position[nr][nc] == UNKNOWN:
                    completed = False
                    break
            if val < 0:
                return False
            if completed and val > 0:
                return False
        return True

    def update_bordering(self):
        new_bordering = set()
        seen = self.bordering.copy()
        while self.bordering:
            r, c = self.bordering.pop()
            seen.add((r, c))
            if self.is_bordering(r, c):
                new_bordering.add((r, c))
            for nr, nc in self.neighbors(r, c):
                if (nr, nc) in seen:
                    continue
                if self.is_bordering(nr, nc):
                    new_bordering.add((nr, nc))
        self.bordering = new_bordering

    def apply_basic_logic(self, sets: SetDict, tentative):
        to_reveal = set()
        to_flag = set()
        for s, val in sets.items():
            if len(s) == 0 or val > len(s):
                raise ValueError("Sets/values are malformed")
            if val == 0:
                to_reveal |= s
            elif len(s) == val:
                to_flag |= s
        if tentative:
            self.mark_tentatively(to_reveal, to_flag)
        else:
            self.verifier(self.position, to_reveal, to_flag)
            self.num_mines -= len(to_flag)
        return to_reveal, to_flag

    def mark_tentatively(self, to_reveal: Iterable, to_flag: Iterable):
        for r, c in to_reveal:
            if self.position[r][c] != UNKNOWN:
                raise ValueError
            self.position[r][c] = REVEALED
        for r, c in to_flag:
            if self.position[r][c] != UNKNOWN:
                raise ValueError
            self.position[r][c] = FLAG

    def get_sets(self):
        sets: SetDict = {}
        for row, col in self.bordering:
            val = int(self.position[row][col])
            assert Solver.is_revealed(val), "position in bordering is not revealed"
            group = set()
            for nr, nc in self.neighbors(row, col):
                n_val = self.position[nr][nc]
                if n_val == UNKNOWN:
                    group.add((nr, nc))
                    continue
                if n_val == FLAG:
                    val -= 1
            if val < 0:
                raise ValueError
            if group:
                sets[frozenset(group)] = val
        return sets

    def check_subsets(self, sets: SetDict):
        changed = False
        for (set1, val1), (set2, val2) in combinations(sets.items(), 2):
            if set1.issubset(set2):
                superset = set2
                superset_val = val2
                subset = set1
                subset_val = val1
            elif set2.issubset(set1):
                superset = set1
                superset_val = val1
                subset = set2
                subset_val = val2
            else:
                continue
            changed = True
            new_val = superset_val - subset_val
            new_set = superset - subset
            if superset in sets:
                sets.pop(superset)
            if new_set and new_set not in sets:
                sets[new_set] = new_val
        return changed

    def check_squeezes(self, sets: SetDict):
        """
        Check for "squeezes" that could occur.
        Ex:
        ....
        .12#
        The cell in the top right must be a mine and the leftmost two cells must not be mines.
        """
        seen_groups = {}
        changed = False
        for (set1, val1), (set2, val2) in combinations(sets.items(), 2):
            if val1 == 0 or val2 == 0:
                continue
            # no squeeze can happen if both cells have the same values
            if val1 == val2:
                continue
            intersection = set1 & set2
            # squeezes can only happen when a number of mines in an area is limited by an adjacent cell, thus the shared area between the sets must be more than the minimum number of mines in an area
            if len(intersection) < min(val1, val2) + 1:
                continue
            large_set, small_val, large_val = (
                (set2, val1, val2) if val1 < val2 else (set1, val2, val1)
            )
            large_not_small = large_set - intersection
            # after limiting the number of mines that can be in the intersecting area, there must be mines in the larger, non-intersecting area
            if len(large_not_small) == large_val - small_val:
                if intersection not in sets:
                    sets[intersection] = small_val
                    changed = True
                continue
            if intersection not in seen_groups:
                seen_groups[intersection] = (0, small_val)
            else:
                other_small, other_large = seen_groups[intersection]
                if small_val == other_small and intersection not in sets:
                    changed = True
                    sets[intersection] = small_val

            if large_not_small not in seen_groups:
                seen_groups[large_not_small] = (large_val - small_val, large_val)
            else:
                other_small, other_large = seen_groups[large_not_small]
                if other_small != large_val and other_large != large_val - small_val:
                    continue
                val = large_val if other_small == large_val else other_large
                if large_not_small not in sets:
                    changed = True
                    sets[large_not_small] = val
        return changed

    def neighbors(self, r, c):
        for dr, dc in NEIGHBORING:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(self.position) and 0 <= nc < len(self.position[1]):
                yield (nr, nc)

    @staticmethod
    def is_revealed(val) -> bool:
        return isinstance(val, int) or val == REVEALED

    def update_position(self, position: PlayerPosition):
        self.position = position
        self.num_rows = len(position)
        self.num_columns = len(position[0])
        self.bordering = set(self.find_all_bordering())

    def update_num_mines(self, num_mines: int):
        if num_mines < 0:
            raise ValueError("num_mines must be a non negative integer")
        self.num_mines = num_mines

    def update(self, num_mines: int, position: PlayerPosition):
        self.update_num_mines(num_mines)
        self.update_position(position)


def print_position(position: PlayerPosition):
    def convert(val: int | str) -> str:
        if val == UNKNOWN:
            fore = Fore.LIGHTBLACK_EX
        elif val == FLAG:
            fore = Fore.LIGHTRED_EX
        elif val == REVEALED:
            fore = Fore.CYAN
        elif val == MINE:
            fore = Fore.GREEN
        else:
            return str(val)
        return fore + str(val) + Fore.RESET

    for row in position:
        print("".join(map(convert, row)))
    print()


def print_marked(position: PlayerPosition, marked: dict[frozenset[Position], str]):
    tmp: list = deepcopy(position)
    for group, marker in marked.items():
        for r, c in group:
            tmp[r][c] = marker
    print_position(tmp)


def main():
    def to_int(val: str) -> int | Literal["M", "F", ".", "R"]:
        if val.isdigit():
            return int(val)
        if val not in [MINE, FLAG, UNKNOWN, REVEALED]:
            raise ValueError(f'The value "{val}" is not recognized')
        return val  # type: ignore

    # region strings
    str_position = """
    .....
    ..2..
    122..
    01F2.
    012..
    001..
    """
    str_mine_field = """
    """
    # endregion
    num_mines = 100
    # region parsing
    position: PlayerPosition = []
    for row in str_position.splitlines():
        row = row.strip()
        if not row:
            continue
        position.append(list(map(to_int, row)))  # type: ignore
    mine_field: MineField = []
    for row in str_mine_field.splitlines():
        row = row.strip()
        if not row:
            continue
        mine_field.append(list(map(to_int, row)))  # type: ignore
    # endregion
    solver = Solver(num_mines, position, bind_verifier(mine_field))
    SOLVE = False
    if SOLVE:
        start = perf_counter()
        while solver.solve_step()[0]:
            print_position(solver.position)
            pass
        end = perf_counter()
        print(f"Finished in {end - start:.3f} secs")
        solved = True
        for row1, row2 in zip(position, mine_field):
            if not all(a == b for a, b in zip(row1, row2) if a != FLAG):
                solved = False
                break
        print(f"SOLVED: {solved}")
    else:
        start = perf_counter()
        solver.brute_force(20)
        print_position(solver.position)
        end = perf_counter()
        print(f"Finished in {end - start:.5f} secs")


if __name__ == "__main__":
    main()
