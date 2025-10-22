import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import random
from typing import List, Tuple, Set, Optional, Any
from SokobanSolver import SokobanSolver
from SokobanDialogs import save_scene, import_scene, prompt_resize_board, prompt_random_map
from SokobanView import draw_tile, draw_board

class SokobanGUI:
    def __init__(self, master: tk.Tk, initial_map: List[str]) -> None:
        self.master = master
        master.title("Sokoban Solver")
        # 内部地图与求解器
        self.initial_map = initial_map
        self.current_map = [list(row) for row in initial_map]
        self.solver = SokobanSolver(initial_map)
        self.rows = len(initial_map)
        self.cols = len(initial_map[0])
        self.tile_size = 40

        # 求解/播放状态
        self.solution_steps = []
        self.step_index = 0
        self.playing = False

        # 画布
        self.canvas = tk.Canvas(master, width=self.cols * self.tile_size, height=self.rows * self.tile_size)
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)


        # 控件栏分为两行
        control_frame1 = tk.Frame(master)
        control_frame1.pack(pady=2)
        control_frame2 = tk.Frame(master)
        control_frame2.pack(pady=2)


        # 第一行：保存、导入、重设地图大小、随机生成地图
        self.save_button = tk.Button(control_frame1, text="保存地图", command=self.save_scene)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.import_button = tk.Button(control_frame1, text="导入地图", command=self.import_scene)
        self.import_button.pack(side=tk.LEFT, padx=5)

        self.resize_button = tk.Button(control_frame1, text="重设地图大小", command=self.prompt_resize_board)
        self.resize_button.pack(side=tk.LEFT, padx=5)

        self.random_button = tk.Button(control_frame1, text="随机生成地图", command=self.prompt_random_map)
        self.random_button.pack(side=tk.LEFT, padx=5)

        # 第二行：求解、上一步、下一步、重置、帮助
        self.solve_button = tk.Button(control_frame2, text="求解 (A*)", command=self.start_solve)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = tk.Button(control_frame2, text="上一步", command=self.prev_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(control_frame2, text="下一步", command=self.next_step, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(control_frame2, text="重置", command=self.reset_game)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.help_button = tk.Button(control_frame2, text="帮助", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(master, text="状态: 等待求解")
        self.status_label.pack(pady=5)

        self.reset_game()

    def show_help(self):
        help_text = (
            "【操作指南】\n"
            "\n"
            "1. 鼠标左键点击地图格子可编辑格子类型（墙、地板、目标、箱子、玩家）。\n"
            "2. 地图编辑完成后，点击‘求解(A*)’自动计算最优解。\n"
            "3. ‘上一步’/‘下一步’可逐步回放解题过程，‘重置’恢复初始状态。\n"
            "4. ‘保存地图’/‘导入地图’可保存和加载地图(txt格式)。\n"
            "5. ‘重设地图大小’可自定义行列数，‘随机生成地图’可生成随机地图。\n"
            "6. 目标点数量需不少于箱子数。所有箱子均位于目标点上，则游戏胜利。\n"
            "7. 求解时，括号内大写字母表示推箱子，小写字母表示仅玩家移动。\n"
            "\n"
        )
        messagebox.showinfo("操作指南", help_text)

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        处理画布点击事件，在编辑模式下切换格子类型。
    
        编辑模式由 "是否存在解" 控制：未求解时可编辑，已求解/播放期间禁用编辑。
        """
        # 只有未求解时允许编辑
        if self.solution_steps:
            return

        c = event.x // self.tile_size
        r = event.y // self.tile_size
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
            return

        # 弹出一个上下文菜单，让用户选择格子类型
        menu = tk.Menu(self.master, tearoff=0)

        # 为每个选项准备 BooleanVar（全部使用复选框）
        ch = self.current_map[r][c]
        var_wall = tk.BooleanVar(value=(ch == self.solver.WALL))
        var_floor = tk.BooleanVar(value=(ch == self.solver.FLOOR))
        var_target = tk.BooleanVar(value=(ch == self.solver.TARGET or ch == self.solver.BOX_ON_TARGET or ch == self.solver.PLAYER_ON_TARGET))
        var_box = tk.BooleanVar(value=(ch == self.solver.BOX or ch == self.solver.BOX_ON_TARGET))
        var_player = tk.BooleanVar(value=(ch == self.solver.PLAYER or ch == self.solver.PLAYER_ON_TARGET))

        # 用循环简化 checkbutton 添加逻辑
        options = [
            ("墙 (#)", var_wall, 'wall'),
            ("地板 ( )", var_floor, 'floor'),
            ("目标 (.)", var_target, 'target'),
            ("箱子 ($)", var_box, 'box'),
            ("玩家 (@)", var_player, 'player'),
        ]
        for label, var, key in options:
            menu.add_checkbutton(
                label=label, variable=var,
                command=lambda r=r, c=c, w=var_wall, f=var_floor, t=var_target, b=var_box, p=var_player, k=key:
                    self._on_menu_change(r, c, w.get(), f.get(), t.get(), b.get(), p.get(), k)
            )

        # 显示菜单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_menu_change(self, r: int, c: int, wall: bool, floor: bool, target: bool, box: bool, player: bool, last: str) -> None:
        """统一处理弹出菜单复选框变化，按优先级决定格子最终状态。

        规则：
        - 如果选择了玩家，则先移除旧玩家，玩家放置在非墙位置；若同时选择了目标，则为 PLAYER_ON_TARGET。
        - 如果选择了箱子，则在非墙位置放置箱子；若同时选择了目标，则为 BOX_ON_TARGET。
        - 如果既选择了墙又选择了其它（玩家/箱子/目标），优先移除墙（即墙与其它不共存）。
        - 地板表示没有特殊元素（非墙、非目标、非箱子、非玩家）。
        """
        # 覆盖策略：以最后点击的选项为主（last），在必要时移除墙并保证玩家唯一性
        new_ch = self.solver.FLOOR

        def fallback():
            # 其他选项都未明确指定时的回退逻辑
            if player:
                return self.solver.PLAYER_ON_TARGET if target else self.solver.PLAYER
            if box:
                return self.solver.BOX_ON_TARGET if target else self.solver.BOX
            if target:
                return self.solver.TARGET
            if wall:
                return self.solver.WALL
            return self.solver.FLOOR

        if last == 'wall':
            new_ch = self.solver.WALL if wall else fallback()
        elif last == 'floor':
            new_ch = self.solver.FLOOR if floor else fallback()
        elif last == 'target':
            # 设置或取消目标；当设置 target 并且同时选择 player/box 时，优先放置 player/box on target
            if target:
                if player:
                    new_ch = self.solver.PLAYER_ON_TARGET
                elif box:
                    new_ch = self.solver.BOX_ON_TARGET
                else:
                    # 目标优先覆盖墙
                    new_ch = self.solver.TARGET
            else:
                # 取消 target：把 on-target 转回普通
                if player:
                    new_ch = self.solver.PLAYER
                elif box:
                    new_ch = self.solver.BOX
                else:
                    new_ch = self.solver.FLOOR
        elif last == 'box':
            if box:
                # 放箱子时移除墙（直接覆盖），并考虑 target
                new_ch = self.solver.BOX_ON_TARGET if target else self.solver.BOX
            else:
                new_ch = fallback()
        elif last == 'player':
            if player:
                # 放玩家前移除其他玩家
                for rr in range(self.rows):
                    for cc in range(self.cols):
                        if self.current_map[rr][cc] == self.solver.PLAYER:
                            self.current_map[rr][cc] = self.solver.FLOOR
                        elif self.current_map[rr][cc] == self.solver.PLAYER_ON_TARGET:
                            self.current_map[rr][cc] = self.solver.TARGET
                new_ch = self.solver.PLAYER_ON_TARGET if target else self.solver.PLAYER
            else:
                new_ch = fallback()
        else:
            # 未知 last：回退到综合决策
            new_ch = fallback()

        # 写入并刷新
        self.current_map[r][c] = new_ch
        self.initial_map = ["".join(row) for row in self.current_map]
        self.solver = SokobanSolver(self.initial_map)
        self.reset_game()

    # 已移除工具栏选择逻辑，编辑通过点击格子弹出选择菜单完成。

    def prompt_resize_board(self) -> None:
        return prompt_resize_board(self)

    def save_scene(self) -> None:
        return save_scene(self)

    def import_scene(self) -> None:
        return import_scene(self)

    def prompt_random_map(self) -> None:
        return prompt_random_map(self)

    def _draw_tile(self, r: int, c: int, tile_type: str) -> None:
        return draw_tile(self.canvas, self.solver, self.tile_size, r, c, tile_type)

    def _draw_board(self) -> None:
        return draw_board(self.canvas, self.rows, self.cols, self.current_map, self.solver, self.tile_size)

    def start_solve(self) -> None:
        if self.solution_steps != []:
            return
        # 求解前验证地图合法性：必须存在玩家，且目标点数量 >= 箱子数量
        player_exists = False
        box_count = 0
        target_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                ch = self.current_map[r][c]
                if ch == self.solver.PLAYER or ch == self.solver.PLAYER_ON_TARGET:
                    player_exists = True
                if ch == self.solver.BOX or ch == self.solver.BOX_ON_TARGET:
                    box_count += 1
                if ch == self.solver.TARGET or ch == self.solver.BOX_ON_TARGET or ch == self.solver.PLAYER_ON_TARGET:
                    target_count += 1

        if not player_exists:
            messagebox.showwarning("地图不合法", "地图中没有玩家，请先放置一个玩家 (@)")
            return
        if target_count < box_count:
            messagebox.showwarning("地图不合法", "目标点数量少于箱子数量，请增加目标点或减少箱子")
            return

        self.status_label.config(text="状态: 正在求解...")
        # 进入求解/播放状态时，标记为播放中以禁止编辑
        self.playing = True
        self.solve_button.config(state=tk.DISABLED)
        self.master.update()
        try:
            solution = self.solver.solve()
        finally:
            # 无论是否求解成功，播放标志在求解结束后关闭（解存在时保持 solution_steps 控制编辑）
            self.playing = False

        if solution is None:
            self.solution_steps = solution
            self.status_label.config(text="状态: 失败 (无解)")
            # 求解失败，用户仍可编辑（通过没有 solution_steps 来允许）
            pass
        else:
            self.solution_steps = solution
            self.step_index = 0
            self.status_label.config(text=f"状态: 找到解，共 {len(solution)} 步")
            self.next_button.config(state=tk.NORMAL)

        # 如果找到了解，保持编辑禁用直到重置；否则（无解）允许编辑
        self.solve_button.config(state=tk.NORMAL)

    def _apply_move(self, current_map: List[List[str]], move: str) -> List[List[str]]:
        pr, pc = -1, -1
        for r in range(self.rows):
            for c in range(self.cols):
                if current_map[r][c] in [self.solver.PLAYER, self.solver.PLAYER_ON_TARGET]:
                    pr, pc = r, c
                    break
            if pr != -1: break
        if pr == -1:
            # 未找到玩家时直接返回原地图（保持类型为 list of lists）
            return current_map
        dr, dc = 0, 0
        if move.upper() == 'U': dr = -1
        elif move.upper() == 'D': dr = 1
        elif move.upper() == 'L': dc = -1
        elif move.upper() == 'R': dc = 1
        npr, npc = pr + dr, pc + dc
        new_map = [list(row) for row in current_map]
        if new_map[pr][pc] == self.solver.PLAYER:
            new_map[pr][pc] = self.solver.FLOOR
        elif new_map[pr][pc] == self.solver.PLAYER_ON_TARGET:
            new_map[pr][pc] = self.solver.TARGET
        if move.isupper():
            nbr, nbc = npr + dr, npc + dc
            if new_map[npr][npc] == self.solver.BOX:
                new_map[npr][npc] = self.solver.PLAYER
            elif new_map[npr][npc] == self.solver.BOX_ON_TARGET:
                new_map[npr][npc] = self.solver.PLAYER_ON_TARGET
            if new_map[nbr][nbc] == self.solver.FLOOR:
                new_map[nbr][nbc] = self.solver.BOX
            elif new_map[nbr][nbc] == self.solver.TARGET:
                new_map[nbr][nbc] = self.solver.BOX_ON_TARGET
        else:
            if new_map[npr][npc] == self.solver.FLOOR:
                new_map[npr][npc] = self.solver.PLAYER
            elif new_map[npr][npc] == self.solver.TARGET:
                new_map[npr][npc] = self.solver.PLAYER_ON_TARGET
        return new_map

    def next_step(self) -> None:
        if self.step_index < len(self.solution_steps):
            move = self.solution_steps[self.step_index]
            self.current_map = self._apply_move(self.current_map, move)
            self._draw_board()
            self.step_index += 1
            self.status_label.config(text=f"状态: 步数 {self.step_index}/{len(self.solution_steps)} ({move})")
            self.prev_button.config(state=tk.NORMAL)
            if self.step_index == len(self.solution_steps):
                self.next_button.config(state=tk.DISABLED)
    
    def prev_step(self) -> None:
        if self.step_index <= 0:
            return

        new_index = self.step_index - 1

        # 从初始地图重放 new_index 步以得到目标地图状态
        temp_map = [list(row) for row in self.initial_map]
        for i in range(new_index):
            temp_map = self._apply_move(temp_map, self.solution_steps[i])

        self.current_map = temp_map
        self.step_index = new_index
        self._draw_board()

        self.status_label.config(text=f"状态: 步数 {self.step_index}/{len(self.solution_steps)}")
        # 更新按钮状态
        self.next_button.config(state=tk.NORMAL if self.step_index < len(self.solution_steps) else tk.DISABLED)
        self.prev_button.config(state=tk.NORMAL if self.step_index > 0 else tk.DISABLED)
    
    def reset_game(self) -> None:
        self.current_map = [list(row) for row in self.initial_map]
        self._draw_board()
        self.step_index = 0
        self.solution_steps = []
        self.status_label.config(text="状态: 已重置")
    # 重置后允许编辑（编辑受 solution_steps 控制，无需 edit_button）
        self.prev_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
