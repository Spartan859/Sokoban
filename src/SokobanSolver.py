import heapq

class SokobanSolver:
    """
    Sokoban 问题的 A* 搜索求解器。
    状态 (State): (玩家位置, 箱子位置集合)
    """

    WALL = '#'
    FLOOR = ' '
    BOX = '$'
    TARGET = '.'
    PLAYER = '@'
    BOX_ON_TARGET = '!'
    PLAYER_ON_TARGET = '+'

    def __init__(self, board_map):
        self.board_map = board_map
        self.rows = len(board_map)
        self.cols = len(board_map[0])
        self.targets = self._find_elements(self.TARGET)
        self.targets.update(self._find_elements(self.PLAYER_ON_TARGET))
        self.targets.update(self._find_elements(self.BOX_ON_TARGET))

    def _find_elements(self, symbol):
        positions = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.board_map[r][c] == symbol:
                    positions.add((r, c))
        return positions

    def _get_initial_state(self):
        player_pos = next(iter(self._find_elements(self.PLAYER) or self._find_elements(self.PLAYER_ON_TARGET)))
        boxes = self._find_elements(self.BOX)
        boxes.update(self._find_elements(self.BOX_ON_TARGET))
        return (player_pos, frozenset(boxes))

    def _is_goal(self, state):
        _, boxes = state
        # 当目标点数量 >= 箱子数量时，只需保证所有箱子位置都在某个目标点上
        return set(boxes).issubset(self.targets)
    
    def _manhattan_distance(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _heuristic(self, state):
        _, boxes = state
        h_score = 0
        available_targets = list(self.targets)
        for box_r, box_c in boxes:
            if (box_r, box_c) in self.targets:
                continue
            min_dist = float('inf')
            best_target_index = -1
            for i, (target_r, target_c) in enumerate(available_targets):
                dist = self._manhattan_distance((box_r, box_c), (target_r, target_c))
                if dist < min_dist:
                    min_dist = dist
                    best_target_index = i
            if best_target_index != -1:
                h_score += min_dist
                available_targets.pop(best_target_index) 
        return h_score

    def _get_next_states(self, state):
        (pr, pc), boxes = state
        next_states = []
        moves = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}

        def is_deadlock(r, c):
            # 死角判定：上下或左右均为墙，且不是目标点
            if (r, c) in self.targets:
                return False
            wall_up = r - 1 < 0 or self.board_map[r - 1][c] == self.WALL
            wall_down = r + 1 >= self.rows or self.board_map[r + 1][c] == self.WALL
            wall_left = c - 1 < 0 or self.board_map[r][c - 1] == self.WALL
            wall_right = c + 1 >= self.cols or self.board_map[r][c + 1] == self.WALL
            # 角落死角（上下或左右均为墙）
            if (wall_up and wall_left) or (wall_up and wall_right) or (wall_down and wall_left) or (wall_down and wall_right):
                return True
            return False

        for move, (dr, dc) in moves.items():
            npr, npc = pr + dr, pc + dc
            # 判断边界和墙壁
            if npr < 0 or npr >= self.rows or npc < 0 or npc >= self.cols:
                continue
            if self.board_map[npr][npc] == self.WALL:
                continue
            if (npr, npc) in boxes:
                nbr, nbc = npr + dr, npc + dc
                if self.board_map[nbr][nbc] != self.WALL and (nbr, nbc) not in boxes:
                    # 死角剪枝：箱子被推到死角且不是目标点，直接跳过
                    if is_deadlock(nbr, nbc):
                        continue
                    new_boxes = set(boxes)
                    new_boxes.remove((npr, npc))
                    new_boxes.add((nbr, nbc))
                    next_state = ((npr, npc), frozenset(new_boxes))
                    next_states.append((next_state, move.upper()))
            else:
                next_state = ((npr, npc), boxes)
                next_states.append((next_state, move.lower()))
        return next_states

    def solve(self):
        start_state = self._get_initial_state()
        priority_queue = [(self._heuristic(start_state), 0, start_state, None, None)]  # (f, g, state, parent, move)
        visited = {start_state: 0}
        parent_map = {}  # state -> (parent_state, move)
        goal_state = None
        while priority_queue:
            f_score, g_score, current_state, parent_state, move = heapq.heappop(priority_queue)
            if parent_state is not None:
                parent_map[current_state] = (parent_state, move)
            if self._is_goal(current_state):
                goal_state = current_state
                break
            for next_state, next_move in self._get_next_states(current_state):
                new_g_score = g_score + 1
                if next_state not in visited or new_g_score < visited[next_state]:
                    visited[next_state] = new_g_score
                    h_score = self._heuristic(next_state)
                    f_score = new_g_score + h_score
                    heapq.heappush(priority_queue, (f_score, new_g_score, next_state, current_state, next_move))
        if goal_state is None:
            return None
        # 回溯路径
        path = []
        state = goal_state
        while state in parent_map:
            parent, move = parent_map[state]
            path.append(move)
            state = parent
        path.reverse()
        return path
