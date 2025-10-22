import tkinter as tk
from typing import List, Any


def draw_tile(canvas: tk.Canvas, solver: Any, tile_size: int, r: int, c: int, tile_type: str) -> None:
    x1, y1 = c * tile_size, r * tile_size
    x2, y2 = x1 + tile_size, y1 + tile_size
    fill_color = 'white'
    outline_color = 'gray'
    if tile_type == solver.TARGET or tile_type == solver.PLAYER_ON_TARGET or tile_type == solver.BOX_ON_TARGET:
        canvas.create_rectangle(x1, y1, x2, y2, fill='lightyellow', outline=outline_color)
        canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill='gold', outline='orange')
    else:
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline=outline_color)
    if tile_type == solver.WALL:
        canvas.create_rectangle(x1, y1, x2, y2, fill='brown', outline='black')
    if tile_type == solver.PLAYER or tile_type == solver.PLAYER_ON_TARGET:
        canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill='blue', tags='player')
    if tile_type == solver.BOX or tile_type == solver.BOX_ON_TARGET:
        color = 'saddlebrown' if tile_type == solver.BOX else 'limegreen'
        canvas.create_rectangle(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=color, tags='box')



def draw_board(canvas: tk.Canvas, rows: int, cols: int, current_map: List[List[str]], solver: Any, tile_size: int) -> None:
    canvas.delete("all")
    for r in range(rows):
        for c in range(cols):
            draw_tile(canvas, solver, tile_size, r, c, current_map[r][c])
