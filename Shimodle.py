import pygame
from random import randint
from copy import deepcopy


w_width = 700
w_height = 800
win = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption('Shimodle')
pygame.init()
pygame.font.init()

s_width = 50
s_height = 50
s_space = 7
s_margin = 2

b_margin = 20
b_font = 15
b_letters = 37

tries = 6

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
GRAY = (128, 128, 128)
YELLOW = (128, 128, 0)
DARKGRAY = (50, 50, 50)

with open('wordlist.txt', 'r', encoding='utf-8') as file:
    words = file.readlines()
for c_word in range(len(words)):
    words[c_word] = words[c_word][:-1]
    words[c_word] = words[c_word].upper()

word = ''
used = []


def new_word():

    global word
    global used

    while True:
        n = randint(121, (len(words) - 1))
        if words[n][4] != 'Á' and words[n][4] != 'Ê':
            word = words[n].upper()
            break

    for let in word:
        found = False
        while not found:
            for i in range(len(used)):
                if let == used[i][0]:
                    used[i][1] += 1
                    found = True
            if not found:
                used.append([let, 0])


new_word()


class Board:

    def __init__(self, correct_word):
        self.word = correct_word
        self.player_word = ['' for i in range(tries)]
        self.row = 0
        self.guess = [0 for i in range(30)]
        self.yellow_letters = ''
        self.green_letters = ''
        self.gray_letters = ''
        self.game_end = False

    def check(self, word_guess, check_letters):
        c_l_copy = deepcopy(check_letters)
        for i in range(len(word_guess)):
            if word_guess[i] == self.word[i]:
                self.guess[i + self.row * 5] = 2
                self.green_letters += word_guess[i]
                for j in range(len(c_l_copy)):
                    if word_guess[i] == c_l_copy[j][0]:
                        c_l_copy[j][1] -= 1
            elif word_guess[i] not in self.word:
                self.guess[i + self.row * 5] = 3
                self.gray_letters += word_guess[i]
        for i in range(len(word_guess)):
            if word_guess[i] != self.word[i] and word_guess[i] in self.word:
                for j in range(len(c_l_copy)):
                    if word_guess[i] == c_l_copy[j][0]:
                        if c_l_copy[j][1] > 0:
                            self.guess[i + self.row * 5] = 1
                            self.yellow_letters += word_guess[i]
                            c_l_copy[j][1] -= 1
                        else:
                            self.guess[i + self.row * 5] = 3

    def reset(self, other_word):
        self.word = other_word
        self.player_word = ['' for i in range(tries)]
        self.row = 0
        self.guess = [0 for i in range(30)]
        self.yellow_letters = ''
        self.green_letters = ''
        self.gray_letters = ''
        self.game_end = False


class Square:

    def __init__(self, color, letter, x, y):
        self.width = s_width
        self.height = s_height
        self.font = 30
        self.color = color
        self.letter = letter
        self.x = x
        self.y = y

    def draw(self, window):
        pygame.draw.rect(window, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(window, self.color, (self.x + s_margin, self.y + s_margin, self.width - 2*s_margin,
                                              self.height - 2*s_margin))
        font = pygame.font.SysFont("comicsans", self.font)
        if len(self.letter) > 0:
            text = font.render(self.letter, 1, WHITE)
            window.blit(text, (self.x + s_margin + round((self.width - 2*s_margin) / 2) - round(text.get_width() / 2),
                        self.y + s_margin + round((self.height - 2*s_margin) / 2) - round(text.get_height() / 2)))


class Button:

    def __init__(self, window, text, x, y, width, height):
        self.window = window
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = b_font

    def draw(self, color):
        pygame.draw.rect(win, color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("comicsans", self.font)
        text = font.render(self.text, 1, WHITE)
        win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            return True
        return False


def redraw_window(window, board, buttons, message):

    window.fill(BLACK)

    def draw_squares():

        x = round(w_width / 2) - round((5 * s_width + 4 * s_space) / 2)
        y = 20

        for i in range(tries):
            for j in range(5):
                color = BLACK
                if len(board.player_word[i]) > j and len(board.player_word[i]) > 0:
                    letter = board.player_word[i][j]
                    if i == board.row:
                        color = GRAY
                else:
                    letter = ''
                if board.guess[i*5 + j] == 1:
                    color = YELLOW
                elif board.guess[i*5 + j] == 2:
                    color = GREEN
                square = Square(color, letter, x, y)
                square.draw(window)
                if j < 4:
                    x += s_width + s_space
                else:
                    x = round(w_width / 2) - round((5 * s_width + 4 * s_space) / 2)
                    y += s_height + s_space

    def draw_buttons():

        for i in range(len(buttons)):
            color = GRAY
            if i < b_letters:
                if buttons[i].text in board.gray_letters:
                    color = DARKGRAY
                elif buttons[i].text in board.green_letters:
                    color = GREEN
                elif buttons[i].text in board.yellow_letters:
                    color = YELLOW

            buttons[i].draw(color)

    def write_message(mess):
        font = pygame.font.SysFont("comicsans", 30)
        text = font.render(mess, 1, WHITE)
        win.blit(text, (round(w_width / 2) - round(text.get_width() / 2), 370))

    draw_squares()
    draw_buttons()
    write_message(message)
    pygame.display.update()
    if message == 'A palavra não está na lista de palavras!':
        pygame.time.wait(1000)
        pygame.display.update()


b = Board(word)
btns = []
letters = 'QWERTYUIOPASDFGHJKLÇZXCVBNMÁÃÂÓÕÔÉÊÍÚ'
rows = (10, 10, 7, 10, 2)
b_x = 0
jind = 0
f = pygame.font.SysFont("comicsans", b_font)
t = f.render('W', 1, WHITE)
w1 = t.get_width() + b_margin
h1 = t.get_height() + 2 * b_margin
t = f.render('ENTER', 1, WHITE)
w2 = t.get_width() + b_margin
h2 = t.get_height() + 2 * b_margin
t = f.render('DEL', 1, WHITE)
w3 = t.get_width() + b_margin
h3 = t.get_height() + 2 * b_margin
for ind in range(b_letters + 2):
    if ind < b_letters:
        content = letters[ind]
        w = w1
        h = h1
    elif ind == b_letters:
        content = 'ENTER'
        w = w2
        h = h2
    else:
        content = 'DEL'
        w = w3
        h = h3
    if ind == 0 or ind == rows[0] or ind == rows[0] + rows[1] \
            or ind == rows[0] + rows[1] + rows[2] or ind == b_letters:
        b_x = round(w_width / 2) - round((rows[jind] * w + (rows[jind] - 1) * s_space) / 2)
    b_y = 410 + jind * (h + s_space)
    btns.append(Button(win, content, b_x, b_y, w, h))
    b_x += w + s_space
    if ind == rows[0] - 1 or ind == rows[0] + rows[1] - 1 or ind == rows[0] + rows[1] + rows[2] - 1 \
            or ind == b_letters - 1:
        jind += 1


def main():

    run = True

    while run:
        m = ''
        global used
        global word
        if b.row > 0 and b.player_word[b.row - 1] == b.word:
            b.game_end = True
            m = 'Parabéns! Clique para reiniciar'
        elif b.row > 5:
            m = f'Palavra: "{word}". Clique para reiniciar'
            b.game_end = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                pygame.quit()
                return 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not b.game_end:
                    pos = pygame.mouse.get_pos()
                    for i in range(b_letters + 2):
                        if btns[i].click(pos):
                            if btns[i].text == 'ENTER' and len(b.player_word[b.row]) == 5:
                                if b.player_word[b.row] in words:
                                    b.check(b.player_word[b.row], used)
                                    b.row += 1
                                else:
                                    m = 'A palavra não está na lista de palavras!'
                            elif btns[i].text == 'DEL' and len(b.player_word[b.row]) > 0:
                                b.player_word[b.row] = b.player_word[b.row][:-1]
                            elif len(b.player_word[b.row]) < 5 and len(btns[i].text) == 1:
                                b.player_word[b.row] += btns[i].text
                else:
                    used = []
                    word = ''
                    new_word()
                    b.reset(word)
            elif event.type == pygame.KEYDOWN:
                if not b.game_end:
                    if event.key == pygame.K_RETURN and len(b.player_word[b.row]) == 5:
                        if b.player_word[b.row] in words:
                            b.check(b.player_word[b.row], used)
                            b.row += 1
                        else:
                            m = 'A palavra não está na lista de palavras!'
                    elif event.key == pygame.K_BACKSPACE and len(b.player_word[b.row]) > 0:
                        b.player_word[b.row] = b.player_word[b.row][:-1]
                    elif len(b.player_word[b.row]) < 5 and event.unicode.isalpha():
                        b.player_word[b.row] += event.unicode.upper()
                else:
                    used = []
                    word = ''
                    new_word()
                    b.reset(word)

        redraw_window(win, b, btns, m)


main()
