import random
import numpy as np

EMPTY = 0
CIRCLE = 1
CROSS = -1
BOARD_LENGTH = 3
DEBUG = True

class CpRandom:
    def choice(self, board_state, mark, init_depth):
        tpl = np.where(board_state == EMPTY)
        tpl_idx = random.randint(0, len(tpl[0])-1)
        return tpl[1][tpl_idx], tpl[0][tpl_idx]


class CpAI:
    def choice(self, board_state, mark, init_depth):
        # 先手の時、初手はランダム
        if init_depth == 0:
            a = np.arange(0, 9)
            prob = [0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]
            b = np.random.choice(a, size=1, p=prob)[0]
            y = b // 3
            x = b % 3
            return x, y
        self.model = AlphaBeta(mark, init_depth)
        x, y = self.model.choice(board_state)
        return x, y

class MiniMax:
    def __init__(self, mark, depth):
        self.mark = mark # 呼び出し元のmark => board.cp_mark
        self.depth = depth

    def choice(self, board_state):
        best_score, best_trace = self.maxlevel(board_state.copy(), self.mark, self.depth)
        best_trace.reverse()
        if DEBUG:
            print("score:", best_score, "trace:", best_trace)
        return best_trace[0]

    def maxlevel(self, board_state, current_mark, depth):
        best_score = -10
        best_trace = []
        depth += 1
        can_put_tpl = np.where(board_state == EMPTY)
        for y, x in zip(*can_put_tpl):
            board_state[y, x] = current_mark
            result = self.judge(board_state, current_mark)
            if result == "continue":
                score, trace = self.minlevel(board_state.copy(), -current_mark, depth)
                trace.append((x, y))
                # scoreを最大化する
                if (best_score < score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = trace
            else:
                score = self.evaluate(result, current_mark, depth)
                # scoreを最大化する
                if (best_score < score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = [(x, y)]
            board_state[y, x] = EMPTY

        return best_score, best_trace

    def minlevel(self, board_state, current_mark, depth):
        best_score = 10
        best_trace = []
        depth += 1
        can_put_tpl = np.where(board_state == EMPTY)
        for y, x in zip(*can_put_tpl):
            board_state[y, x] = current_mark
            result = self.judge(board_state, current_mark)
            if result == "continue":
                score, trace = self.maxlevel(board_state.copy(), -current_mark, depth)
                trace.append((x, y))
                # scoreを最小化する
                if (best_score > score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = trace
            else:
                score = self.evaluate(result, current_mark, depth)
                # scoreを最小化する
                if (best_score > score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = [(x, y)]
            board_state[y, x] = EMPTY

        return best_score, best_trace

    # self.markのscore
    def evaluate(self, result, current_mark, depth):
        if result == 'win':
            score = 10 - depth
        elif result == "lose":
            score = -10 + depth
        elif result == "draw":
            score = 0
        if self.mark == current_mark:
            return score
        else:
            return -score

    # mark側の判定
    def judge(self, board_state, mark):
        total1, total2 = 0, 0 # 斜めの判定
        for i in range(BOARD_LENGTH):
            total1 += board_state[i, i]
            total2 += board_state[i, BOARD_LENGTH-1-i]
        # win
        if np.any(np.sum(board_state, axis=0) == 3*mark) \
           or np.any(np.sum(board_state, axis=1) == 3*mark) \
           or total1 == 3*mark \
           or total2 == 3*mark:
            return 'win'
        # lose
        elif  np.any(np.sum(board_state, axis=0) == -3*mark) \
              or np.any(np.sum(board_state, axis=1) == -3*mark) \
              or total1 == -3*mark \
              or total2 == -3*mark:
            return 'lose'
        # draw
        elif np.all(board_state != EMPTY):
            return 'draw'
        # continue
        else:
            return 'continue'

class AlphaBeta:
    def __init__(self, mark, depth):
        self.mark = mark # 呼び出し元のmark => board.cp_mark
        self.depth = depth

    def choice(self, board_state):
        best_score, best_trace = self.maxlevel(board_state.copy(), self.mark, self.depth)
        best_trace.reverse()
        if DEBUG:
            print("score:", best_score, "trace:", best_trace)
        return best_trace[0]

    def maxlevel(self, board_state, current_mark, depth, beta=10):
        best_score = -10
        best_trace = []
        depth += 1
        can_put_tpl = np.where(board_state == EMPTY)
        for y, x in zip(*can_put_tpl):
            board_state[y, x] = current_mark
            result = self.judge(board_state, current_mark)
            if result == "continue":
                score, trace = self.minlevel(board_state.copy(), -current_mark, depth, alpha=best_score)
                trace.append((x, y))
                # scoreを最大化する
                if (best_score < score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = trace
            else:
                score = self.evaluate(result, current_mark, depth)
                # scoreを最大化する
                if (best_score < score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = [(x, y)]
            if best_score > beta:
                return best_score, best_trace
            board_state[y, x] = EMPTY

        return best_score, best_trace

    def minlevel(self, board_state, current_mark, depth, alpha=-10):
        best_score = 10
        best_trace = []
        depth += 1
        can_put_tpl = np.where(board_state == EMPTY)
        for y, x in zip(*can_put_tpl):
            board_state[y, x] = current_mark
            result = self.judge(board_state, current_mark)
            if result == "continue":
                score, trace = self.maxlevel(board_state.copy(), -current_mark, depth, beta=best_score)
                trace.append((x, y))
                # scoreを最小化する
                if (best_score > score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = trace
            else:
                score = self.evaluate(result, current_mark, depth)
                # scoreを最小化する
                if (best_score > score) or (best_score == score and random.randint(0, 99) >= 50):
                    best_score = score
                    best_trace = [(x, y)]
            if best_score < alpha:
                return best_score, best_trace
            board_state[y, x] = EMPTY

        return best_score, best_trace

    # self.markのscore
    def evaluate(self, result, current_mark, depth):
        if result == 'win':
            score = 10 - depth
        elif result == "lose":
            score = -10 + depth
        elif result == "draw":
            score = 0
        if self.mark == current_mark:
            return score
        else:
            return -score

    # mark側の判定
    def judge(self, board_state, mark):
        total1, total2 = 0, 0 # 斜めの判定
        for i in range(BOARD_LENGTH):
            total1 += board_state[i, i]
            total2 += board_state[i, BOARD_LENGTH-1-i]
        # win
        if np.any(np.sum(board_state, axis=0) == 3*mark) \
           or np.any(np.sum(board_state, axis=1) == 3*mark) \
           or total1 == 3*mark \
           or total2 == 3*mark:
            return 'win'
        # lose
        elif  np.any(np.sum(board_state, axis=0) == -3*mark) \
              or np.any(np.sum(board_state, axis=1) == -3*mark) \
              or total1 == -3*mark \
              or total2 == -3*mark:
            return 'lose'
        # draw
        elif np.all(board_state != EMPTY):
            return 'draw'
        # continue
        else:
            return 'continue'
