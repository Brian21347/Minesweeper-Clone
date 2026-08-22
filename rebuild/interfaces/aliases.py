from typing import Literal

Mine = Literal["M"]
Revealed = Literal["R"]
Unknown = Literal["."]
Flagged = Literal["F"]


MineFieldValue = int | Mine
SolvingFieldValue = int | Revealed | Unknown | Flagged
