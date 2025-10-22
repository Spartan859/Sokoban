from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, filedialog
import random
from typing import List, Tuple, Set, Any
from sokoban_types import SokobanGUIProtocol
from SokobanSolver import SokobanSolver

_last_random_params = {'walls': None, 'boxes': None, 'targets': None}

def save_scene(gui: SokobanGUIProtocol) -> None:
    file_path = filedialog.asksaveasfilename(title="保存场景为", defaultextension=".txt", filetypes=[("Text Files","*.txt"), ("All Files","*.*")])
    if not file_path:
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            for row in gui.initial_map:
                f.write(row + '\n')
        messagebox.showinfo("保存成功", f"场景已保存到 {file_path}")
    except Exception as e:
        messagebox.showerror("保存失败", f"无法保存文件: {e}")


def import_scene(gui: SokobanGUIProtocol) -> None:
    file_path = filedialog.askopenfilename(title="导入场景", filetypes=[("Text Files","*.txt"), ("All Files","*.*")])
    if not file_path:
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip() != '']
        if not lines:
            messagebox.showwarning("导入失败", "文件为空或格式不正确")
            return
        # 更新地图并重置状态
        gui.initial_map = lines
        gui.current_map = [list(row) for row in gui.initial_map]
        gui.rows = len(gui.initial_map)
        gui.cols = len(gui.initial_map[0])
        gui.solver = SokobanSolver(gui.initial_map, debug=getattr(gui, 'debug', False))
        gui.canvas.config(width=gui.cols * gui.tile_size, height=gui.rows * gui.tile_size)
        gui.reset_game()
        gui.status_label.config(text="状态: 等待求解")
        messagebox.showinfo("导入成功", f"已从 {file_path} 导入场景")
    except Exception as e:
        messagebox.showerror("导入失败", f"无法读取文件: {e}")


def prompt_resize_board(gui: SokobanGUIProtocol) -> None:
    dlg = tk.Toplevel(gui.master)
    dlg.title("重设地图大小")
    dlg.transient(gui.master)
    dlg.grab_set()

    tk.Label(dlg, text="行数:").grid(row=0, column=0, padx=6, pady=6)
    rows_var = tk.IntVar(value=max(3, gui.rows))
    rows_entry = tk.Spinbox(dlg, from_=3, to=200, textvariable=rows_var, width=5)
    rows_entry.grid(row=0, column=1, padx=6, pady=6)

    tk.Label(dlg, text="x").grid(row=0, column=2, padx=2)

    tk.Label(dlg, text="列数:").grid(row=0, column=3, padx=6, pady=6)
    cols_var = tk.IntVar(value=max(3, gui.cols))
    cols_entry = tk.Spinbox(dlg, from_=3, to=200, textvariable=cols_var, width=5)
    cols_entry.grid(row=0, column=4, padx=6, pady=6)

    def on_confirm():
        try:
            new_rows = int(rows_var.get())
            new_cols = int(cols_var.get())
        except Exception as e:
            messagebox.showerror("输入错误", f"请输入有效整数: {e}", parent=dlg)
            return
        if new_rows < 3 or new_cols < 3:
            messagebox.showwarning("输入错误", "行数和列数必须至少为 3", parent=dlg)
            return
        # 生成新地图（外围墙，内部地板）
        new_map = []
        for r in range(new_rows):
            if r == 0 or r == new_rows - 1:
                new_map.append('#' * new_cols)
            else:
                new_map.append('#' + ' ' * (new_cols - 2) + '#')
        # 在 (1,1) 放置玩家（如果有空间）
        if new_rows > 2 and new_cols > 2:
            row0 = list(new_map[1])
            row0[1] = gui.solver.PLAYER
            new_map[1] = ''.join(row0)

        # 应用新地图
        gui.initial_map = new_map
        gui.current_map = [list(row) for row in new_map]
        gui.rows = new_rows
        gui.cols = new_cols
        gui.solver = SokobanSolver(gui.initial_map, debug=getattr(gui, 'debug', False))
        gui.canvas.config(width=gui.cols * gui.tile_size, height=gui.rows * gui.tile_size)
        gui.reset_game()
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    btn_frame = tk.Frame(dlg)
    btn_frame.grid(row=1, column=0, columnspan=5, pady=6)
    tk.Button(btn_frame, text="确定", command=on_confirm).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=6)

    rows_entry.focus_set()
    gui.master.wait_window(dlg)


def prompt_random_map(gui: SokobanGUIProtocol) -> None:
    dlg = tk.Toplevel(gui.master)
    dlg.title("随机生成地图")
    dlg.transient(gui.master)
    dlg.grab_set()

    inner_cells = (gui.rows - 2) * (gui.cols - 2)
    tk.Label(dlg, text=f"当前尺寸: {gui.rows} x {gui.cols}，内部可用格数: {inner_cells}").grid(row=0, column=0, columnspan=4, padx=6, pady=6)

    # 记忆参数优先，否则用默认
    global _last_random_params
    default_walls = _last_random_params['walls'] if _last_random_params['walls'] is not None else max(0, inner_cells // 6)
    default_boxes = _last_random_params['boxes'] if _last_random_params['boxes'] is not None else 1
    default_targets = _last_random_params['targets'] if _last_random_params['targets'] is not None else 1

    tk.Label(dlg, text="墙数量:").grid(row=1, column=0, padx=6, pady=6)
    walls_var = tk.IntVar(value=default_walls)
    tk.Spinbox(dlg, from_=0, to=inner_cells, textvariable=walls_var, width=6).grid(row=1, column=1, padx=6, pady=6)

    tk.Label(dlg, text="箱子数量:").grid(row=1, column=2, padx=6, pady=6)
    boxes_var = tk.IntVar(value=default_boxes)
    tk.Spinbox(dlg, from_=0, to=inner_cells, textvariable=boxes_var, width=6).grid(row=1, column=3, padx=6, pady=6)

    tk.Label(dlg, text="目标数量:").grid(row=2, column=0, padx=6, pady=6)
    targets_var = tk.IntVar(value=default_targets)
    tk.Spinbox(dlg, from_=0, to=inner_cells, textvariable=targets_var, width=6).grid(row=2, column=1, padx=6, pady=6)

    def on_confirm():
        try:
            walls = int(walls_var.get())
            boxes = int(boxes_var.get())
            targets = int(targets_var.get())
        except Exception as e:
            messagebox.showerror("输入错误", f"请输入有效整数: {e}", parent=dlg)
            return
        if walls < 0 or boxes < 0 or targets < 0:
            messagebox.showwarning("输入错误", "请确保数量为非负整数", parent=dlg)
            return
        if targets < boxes:
            messagebox.showwarning("输入错误", "目标点数量应 >= 箱子数量以保证可解， 请调整。", parent=dlg)
            return
        required = 1 + boxes + targets
        if required + walls > inner_cells:
            messagebox.showwarning("输入错误", f"指定数量超出可用内部格数 ({inner_cells})，请减少数量", parent=dlg)
            return

        # 记忆本次参数
        global _last_random_params
        _last_random_params['walls'] = walls
        _last_random_params['boxes'] = boxes
        _last_random_params['targets'] = targets

        inner_positions = [(r, c) for r in range(1, gui.rows-1) for c in range(1, gui.cols-1)]
        player_pos = random.choice(inner_positions)
        remaining = set(inner_positions)
        remaining.remove(player_pos)

        boxes_pos = set()
        if boxes > 0:
            rem_list = list(remaining)
            if boxes > len(rem_list):
                messagebox.showwarning("输入错误", f"请求的箱子数量超出可选位置 ({len(rem_list)})", parent=dlg)
                return
            boxes_pos = set(random.sample(rem_list, boxes))
            for p in boxes_pos:
                remaining.remove(p)

        targets_pos = set()
        if targets > 0:
            rem_list = list(remaining)
            if targets > len(rem_list):
                messagebox.showwarning("输入错误", f"请求的目标数量超出可选位置 ({len(rem_list)})", parent=dlg)
                return
            targets_pos = set(random.sample(rem_list, targets))
            for p in targets_pos:
                remaining.remove(p)

        walls_pos = set()
        if walls > 0:
            rem_list = list(remaining)
            if walls > len(rem_list):
                messagebox.showwarning("输入错误", f"请求的墙数量超出可选位置 ({len(rem_list)})", parent=dlg)
                return
            walls_pos = set(random.sample(rem_list, walls))
            for p in walls_pos:
                remaining.remove(p)

        new_map = []
        for r in range(gui.rows):
            if r == 0 or r == gui.rows - 1:
                new_map.append('#' * gui.cols)
            else:
                row = []
                for c in range(gui.cols):
                    if c == 0 or c == gui.cols - 1:
                        row.append('#')
                    else:
                        if (r, c) in walls_pos:
                            row.append('#')
                        elif (r, c) in boxes_pos:
                            row.append(gui.solver.BOX_ON_TARGET if (r, c) in targets_pos else gui.solver.BOX)
                        elif (r, c) in targets_pos:
                            row.append(gui.solver.TARGET)
                        elif (r, c) == player_pos:
                            row.append(gui.solver.PLAYER_ON_TARGET if (r, c) in targets_pos else gui.solver.PLAYER)
                        else:
                            row.append(gui.solver.FLOOR)
                new_map.append(''.join(row))

        gui.initial_map = new_map
        gui.current_map = [list(row) for row in new_map]
        gui.solver = SokobanSolver(gui.initial_map, debug=getattr(gui, 'debug', False))
        gui.reset_game()
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    btn_frame = tk.Frame(dlg)
    btn_frame.grid(row=3, column=0, columnspan=4, pady=6)
    tk.Button(btn_frame, text="生成", command=on_confirm).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT, padx=6)

    gui.master.wait_window(dlg)
