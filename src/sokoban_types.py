from __future__ import annotations

from typing import Protocol, List
import tkinter as tk


class SokobanGUIProtocol(Protocol):
    initial_map: List[str]
    current_map: List[List[str]]
    rows: int
    cols: int
    class SokobanSolverProtocol(Protocol):
        WALL: str
        FLOOR: str
        TARGET: str
        BOX: str
        PLAYER: str
        BOX_ON_TARGET: str
        PLAYER_ON_TARGET: str

        def solve(self) -> list: ...

    solver: SokobanSolverProtocol
    canvas: tk.Canvas
    tile_size: int
    master: tk.Tk
    status_label: tk.Label

    def reset_game(self) -> None: ...

    def _draw_board(self) -> None: ...
