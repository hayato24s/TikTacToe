import numpy as np
import pygame
import sys
from cp import CpRandom, CpAI

BOARD_LENGTH = 3
CIRCLE = 1 # first
CROSS = -1 # second
EMPTY = 0
LENGTH = 80
DEBUG = True
bx, by = 30, 70

# グローバル変数
idx = 1

class Board:
    def __init__(self, mark="first"):
        self.state = np.zeros((BOARD_LENGTH, BOARD_LENGTH))
        self.turn = CIRCLE
        self.turn_cnt = 0
        self.result = None
        if mark == "first":
            self.pl_mark = CIRCLE
        elif mark == "second":
            self.pl_mark = CROSS
        self.cp_mark = -self.pl_mark

    def put(self, x, y):
        if self.state[y, x] != EMPTY:
            if DEBUG:
                print("そこには置けません。")
            return False

        self.turn_cnt += 1
        self.state[y, x] = self.turn
        self.turn = -self.turn
        return True

    def judge(self):
        total1, total2 = 0, 0 # 斜めの判定
        for i in range(BOARD_LENGTH):
            total1 += self.state[i, i]
            total2 += self.state[i, BOARD_LENGTH-1-i]
        if np.any(np.sum(self.state, axis=0) == 3*self.pl_mark) \
           or np.any(np.sum(self.state, axis=1) == 3*self.pl_mark) \
           or total1 == 3*self.pl_mark \
           or total2 == 3*self.pl_mark:
            self.result = 'win'
            return True
        elif  np.any(np.sum(self.state, axis=0) == 3*self.cp_mark) \
              or np.any(np.sum(self.state, axis=1) == 3*self.cp_mark) \
              or total1 == 3*self.cp_mark \
              or total2 == 3*self.cp_mark:
            self.result = 'lose'
            return True
        elif np.all(self.state != EMPTY):
            self.result = 'draw'
            return True
        else:
            return False

class Interface:
    def __init__(self):
        self.input_x = None
        self.input_y = None
        self.mark = None

    def choose_mark(self):
        self.mark = None
        key = pygame.key.get_pressed()
        if key[pygame.K_f]:
            self.mark = "first"
        elif key[pygame.K_s]:
            self.mark = "second"
        if self.mark:
            if DEBUG:
                print("you're {}".format(self.mark))
            return True
        else:
            return False

    def input_data(self):
        mBtn1, _, _ = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (mBtn1 == True) and (0 + bx <= mouse_x < BOARD_LENGTH * LENGTH + bx) and  (0 +by <= mouse_y < BOARD_LENGTH * LENGTH + by):
            self.input_x = (mouse_x - bx) // LENGTH
            self.input_y = (mouse_y - by) // LENGTH
            return True
        else:
            return False

    def next_game(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            if DEBUG:
                print("next game")
            return True
        else:
            return False

class Display:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("./assets/ipaexg.ttf", 30)

    def draw_display(self, board):
        self.screen.fill((0, 0, 0))
        if idx == 1:
            txt1 = self.font.render("Press", True, (255, 255, 255))
            txt2 = self.font.render("[F]irst or [S]econd", True, (255, 255, 255))
            self.screen.blits([(txt1, [290, 100]), (txt2, [290, 150])])
        if 2 <= idx <= 5:
            self.draw_board(board.state)
        if idx == 5:
            txt1 = self.font.render("result: {}".format(board.result), True, (255, 255, 255))
            txt2 = self.font.render("next game: SpaceKey", True, (255, 255, 255))
            self.screen.blits([(txt1, [290, 100]), (txt2, [290, 150])])
        pygame.display.update()

    def draw_board(self, board_state):
        for i in range(BOARD_LENGTH + 1):
            pygame.draw.line(self.screen, (255, 255, 255), [0 + bx, LENGTH*i + by], [LENGTH*3 + bx, LENGTH*i + by], 2)
            pygame.draw.line(self.screen, (255, 255, 255), [LENGTH*i + bx, 0 + by], [LENGTH*i + bx, LENGTH*3 + by], 2)
        for j in range(BOARD_LENGTH):
            for i in range(BOARD_LENGTH):
                if board_state[j, i] == CIRCLE:
                    txt = self.font.render("○", True, (255, 255, 255))
                    x = int(i * LENGTH + LENGTH / 2 - txt.get_width() / 2 + bx)
                    y = int(j * LENGTH + LENGTH / 2 - txt.get_height() / 2 + by)
                    self.screen.blit(txt, [x, y])
                elif board_state[j, i] == CROSS:
                    txt = self.font.render("×", True, (255, 255, 255))
                    x = int(i * LENGTH + LENGTH / 2 - txt.get_width() / 2 + bx)
                    y = int(j * LENGTH + LENGTH / 2 - txt.get_height() / 2 + by)
                    self.screen.blit(txt, [x, y])

def main():
    global idx

    pygame.init()
    pygame.display.set_caption("TikTacToe")
    screen = pygame.display.set_mode((600, 400))
    clock = pygame.time.Clock()

    board = None
    interface = Interface()
    display = Display(screen)
    cp = CpAI()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if idx == 1:
            if interface.choose_mark():
                board = Board(interface.mark)
                if board.pl_mark == CIRCLE:
                    idx = 2
                elif board.pl_mark == CROSS:
                    idx = 4

        if idx == 2:
            if interface.input_data():
                idx = 3

        if idx == 3:
            if not board.put(interface.input_x, interface.input_y):
                idx = 2
                continue
            if DEBUG:
                print("pl: ({}, {})".format(interface.input_x, interface.input_y))
            if board.judge():
                idx = 5
                if DEBUG:
                    print(board.result)
                continue
            idx = 4

        elif idx == 4:
            cp_x, cp_y = cp.choice(board.state, board.turn, board.turn_cnt)
            while not board.put(cp_x, cp_y):
                cp_x, cp_y = cp.choice(board.state, board.turn, board.turn_cnt)
            if DEBUG:
                print("cp: ({}, {})".format(cp_x, cp_y))
            if board.judge():
                idx = 5
                if DEBUG:
                    print(board.result)
                continue
            idx = 2

        elif idx == 5:
            if interface.next_game():
                idx = 1

        display.draw_display(board)
        clock.tick(5)

if __name__ == '__main__':
    main()
