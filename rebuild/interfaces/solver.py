from collections.abc import Iterable
from itertools import combinations, product
from typing import overload

from rebuild.interfaces.minefield import MineField
from rebuild.interfaces.position import Pos
from rebuild.interfaces.solving_field import SolvingField

SetDict = dict[frozenset[Pos], int]

# fmt: off
STANDARD_ADJACENCY = [
    Pos(-1, -1), Pos(-1, 0), Pos(-1, 1),
    Pos(0, -1),              Pos(0, 1),
    Pos(1, -1),  Pos(1, 0),  Pos(1, 1),
]
# fmt: on


class Solver:
    @overload
    def __init__(self, mine_field: MineField, /) -> None: ...

    @overload
    def __init__(self, test_input: str, test_output: str, /): ...

    def __init__(self, *args: MineField | str) -> None:
        if len(args) == 1:
            mine_field = args[0]
            assert isinstance(mine_field, MineField)
            self.field = SolvingField(mine_field)
            self.num_mines = mine_field.num_mines
        elif len(args) == 2:
            test_input, test_output = args[0], args[1]
            assert isinstance(test_input, str) and isinstance(test_output, str)
            num_mines, _, test_input = test_input.partition("\n")
            self.field = SolvingField(test_input, test_output)
            self.num_mines = int(num_mines)
        else:
            raise NotImplementedError
        self.size = self.field.size
        self.bordering: set[Pos] = set(self.find_all_bordering())
        self.unknowns: set[Pos] = set(self.find_all_unknown())

    def verify(self) -> bool:
        return self.field.verify()

    def solve(self) -> None:
        while True:
            changed = self.solve_step()
            if not changed:
                break

    def solve_step(self) -> bool:
        if len(self.unknowns) == 0:
            return False
        print(self.field)
        sets = self.get_sets()
        self.check_subsets(sets)
        self.check_squeezes(sets)
        self.check_subsets(sets)

        if changed := self.apply_basic_logic(sets):
            self.update_bordering()

        return changed

    def get_sets(self) -> SetDict:
        sets: SetDict = {}
        for pos in self.bordering:
            val = self.field.get_value(pos)
            if not isinstance(val, int):
                continue

            group = set()
            for npos in self.neighbors(pos):
                n_val = self.field.get_value(npos)
                if n_val == ".":
                    group.add(npos)
                elif n_val == "F":
                    val -= 1

            if val < 0:
                raise ValueError(f"Negative mine count detected at {pos}")
            if group:
                sets[frozenset(group)] = val
        sets[frozenset(self.unknowns)] = self.num_mines
        return sets

    def check_subsets(self, sets: SetDict) -> bool:
        changed = False
        for (set1, val1), (set2, val2) in combinations(list(sets.items()), 2):
            if set1.issubset(set2):
                superset, superset_val = set2, val2
                subset, subset_val = set1, val1
            elif set2.issubset(set1):
                superset, superset_val = set1, val1
                subset, subset_val = set2, val2
            else:
                continue

            new_val = superset_val - subset_val
            new_set = superset - subset

            if superset in sets:
                sets.pop(superset)
                changed = True
            if new_set and new_set not in sets:
                sets[new_set] = new_val
                changed = True

        return changed

    def check_squeezes(self, sets: SetDict) -> bool:
        seen_groups = {}
        changed = False
        for (set1, val1), (set2, val2) in combinations(list(sets.items()), 2):
            if val1 == 0 or val2 == 0:
                continue
            if val1 == val2:
                continue

            intersection = set1 & set2
            if len(intersection) < min(val1, val2) + 1:
                continue

            large_set, small_val, large_val = (
                (set2, val1, val2) if val1 < val2 else (set1, val2, val1)
            )
            large_not_small = large_set - intersection

            if len(large_not_small) == large_val - small_val:
                if intersection not in sets:
                    sets[intersection] = small_val
                    changed = True
                continue

            if intersection not in seen_groups:
                seen_groups[intersection] = (0, small_val)
            else:
                other_small, _ = seen_groups[intersection]
                if small_val == other_small and intersection not in sets:
                    sets[intersection] = small_val
                    changed = True

            if large_not_small not in seen_groups:
                seen_groups[large_not_small] = (large_val - small_val, large_val)
            else:
                other_small, other_large = seen_groups[large_not_small]
                if other_small != large_val and other_large != large_val - small_val:
                    continue
                val = large_val if other_small == large_val else other_large
                if large_not_small not in sets:
                    sets[large_not_small] = val
                    changed = True

        return changed

    def apply_basic_logic(self, sets: SetDict) -> bool:
        changed = False
        for s, val in sets.items():
            if len(s) == 0 or val > len(s):
                raise ValueError("Sets/values are malformed")
            if val == 0:
                self.reveal_all(s)
                changed = True
            elif len(s) == val:
                self.num_mines -= len(s)
                self.flag_all(s)
                changed = True
        return changed

    def reveal_all(self, s: frozenset[Pos]):
        for pos in s:
            self.field.reveal(pos)
            self.unknowns.remove(pos)

    def flag_all(self, s: frozenset[Pos]):
        for pos in s:
            self.field.flag(pos)
            self.unknowns.remove(pos)

    def neighbors(self, pos: Pos) -> Iterable[Pos]:
        for d_pos in STANDARD_ADJACENCY:
            npos = pos + d_pos
            if npos.is_valid():
                yield npos

    def is_bordering(self, pos: Pos) -> bool:
        value = self.field.get_value(pos)
        if not isinstance(value, int):
            return False
        for npos in self.neighbors(pos):
            if self.field.get_value(npos) == ".":
                return True
        return False

    def find_all_unknown(self) -> Iterable[Pos]:
        for r, c in product(range(self.size[0]), range(self.size[1])):
            pos = Pos(r, c)
            if self.field.get_value(pos) == ".":
                yield pos

    def find_all_bordering(self) -> Iterable[Pos]:
        for r, c in product(range(self.size[0]), range(self.size[1])):
            pos = Pos(r, c)
            if self.is_bordering(pos):
                yield pos

    def update_bordering(self) -> None:
        new_bordering = set()
        seen = self.bordering.copy()

        while self.bordering:
            pos = self.bordering.pop()
            seen.add(pos)
            if self.is_bordering(pos):
                new_bordering.add(pos)
            for npos in self.neighbors(pos):
                if npos in seen:
                    continue
                if self.is_bordering(npos):
                    new_bordering.add(npos)

        self.bordering = new_bordering
