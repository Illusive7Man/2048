from BaseAI_3 import BaseAI
import time
import math
import random


class PlayerAI(BaseAI):
    """This function manages the behaviour of the PlayerAI, uses alpha-beta prunining and minimax algorithm
    to determine the optimal play, against an opponent who is playing optimally. It should work well
     with randomized moves from the opponent."""
    def __init__(self):
        self.time_left = True
        self.preferred_order = [0, 2, 3, 1]
        self.max_move = 0

    def maximize(self, state, a, b, depth=0):
        if time.clock() - self.start > 0.098:
            self.time_left = False
            return 1,2

        if depth == self.max_depth:
            utility = self.evaluate(state)
            return state, utility

        max_child, max_utility = None, -float('inf')

        available_moves = state.getAvailableMoves()
        available_moves = [self.preferred_order[i] for i in range(len(self.preferred_order))
                           if self.preferred_order[i] in available_moves]

        # if len(available_moves) > 1:
        #     try:
        #         for i in range(3):
        #              if state.map[i][0] == state.map[i + 1][0] or state.map[i][0] == 0 or state.map[3][0] == 0:
        #                 available_moves.remove(1)
        #                 break
        #     except ValueError:
        #         pass
        #
        #     if len(available_moves) > 1:
        #         try:
        #             for i in range(3):
        #                  if state.map[0][i] == state.map[0][i + 1] or state.map[0][i] == 0 or state.map[0][3] == 0:
        #                     available_moves.remove(3)
        #                     break
        #         except ValueError:
        #             pass

        children = []
        for i in available_moves:
            children.append(state.clone())
            children[-1].move(i)

        for child in children:
            *rest, utility = self.minimize(child, a, b, depth + 1)
            if not self.time_left:
                return 1,2

            if utility > max_utility:
                max_child, max_utility = child, utility
                if depth == 0:
                    self.max_move = available_moves[children.index(child)]

            if max_utility >= b:
                break

            if max_utility > a:
                a = max_utility

        return max_child, max_utility

    def minimize(self, state, a, b, depth):
        if time.clock() - self.start > 0.098:
            self.time_left = False
            return 1,2

        if depth == self.max_depth:
            utility = self.evaluate(state)
            return state, utility

        min_child, min_utility = None, float('inf')

        def sorting(a):
            return math.sqrt(a[0]**2 + a[1]**2)

        available = state.getAvailableCells()
        available.sort(key=sorting)

        children = []
        for position in available:
            children.append(state.clone())
            children[-1].setCellValue(position, random.choice([2,4]))
            if len(children) > 5:
                break

        for child in children:
            *rest, utility = self.maximize(child, a, b, depth + 1)
            if not self.time_left:
                return 1,2

            if utility < min_utility:
                min_child, min_utility = child, utility

            if min_utility <= a:
                break

            if min_utility < b:
                b = min_utility

        return min_child, min_utility

    def evaluate(self, state):
        available = state.getAvailableCells()
        return 10 * (self.max_tile_pos(state, available) + self.gradient(state) +
                + len(state.getAvailableCells())) + self.smoothness(state)

    # HEURISTICS
    # fix the ids with a dict

    def max_tile_pos(self, state, available):
        value = 0
        max_tile = state.getMaxTile()
        if max_tile == state.map[0][0]:
            value = max_tile * 2
        elif max_tile == state.map[0][1]:
            value = 0
        elif max_tile > 4:
            value = -100

        if len(state.getAvailableMoves()) <= 2 and (0,3) in available:
            value -= 5

        if max_tile > 1024:
            value += max_tile
        # elif max_tile > 512:
        #     value += 100

        return value

    def gradient(self, state):
        value = 0
        for x in range(3):
            for y in range(3):
                if state.map[x][y] >= state.map[x][y + 1]:
                    value += state.map[x][y + 1] * (1 / 2) ** (x + y)
                else:
                    break
        for x in range(3):
            for y in range(3):
                if state.map[y][x] >= state.map[y + 1][x]:
                    value += state.map[y+ 1][x] * (1 / 3) ** (y + x)
                else:
                    break

        return value

    def smoothness(self, state, trigger=0):
        value = 0
        explored = dict()
        cell_values = dict()

        for x in range(3):
            for y in range(3):
                cell = state.map[x][y]
                if cell == state.map[x][y + 1]:
                    if cell not in explored:
                        explored[cell] = 1
                    explored[cell] += 1
                else:
                    if cell not in cell_values:
                        cell_values[cell] = 0
                    cell_values[cell] += 1


                cell1 = state.map[y][x]
                if cell1 == state.map[y + 1][x]:
                    if cell1 not in explored:
                        explored[cell1] = 0
                    explored[cell1] += 1
                else:
                    if cell not in cell_values:
                        cell_values[cell] = 0
                    cell_values[cell] += 1

        new_smooth = 0
        for key in explored:
            new_smooth += key * self.round_down(explored[key], 2)

        solo_cell = 0
        for key in cell_values:
            solo_cell += key * cell_values[key]

        if trigger == 1:
            self.smooth = new_smooth
            self.solo = solo_cell

        if new_smooth + len(explored) == self.smooth and solo_cell == self.solo:
            value = 0
        else:
            value += 2 * new_smooth + solo_cell

        return value

    def round_down(self, num, divisor):
        return num - (num % divisor)

    def getMove(self, grid):
        """Plays a move from the optimal strategy

        Args:
            grid: A current state of the grid
        """

        self.start = time.clock()
        self.max_depth = 4
        move = 0
        _ = self.smoothness(grid, 1)
        while True:
            _ = self.maximize(grid, -float('inf'), float('inf'))
            if self.time_left is True:
                move = self.max_move
            else:
                break
            self.max_depth += 1

        print(self.max_depth)
        self.time_left = True
        self.max_move = 0

        return move
