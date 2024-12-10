import pygame
from random import randint
from copy import deepcopy
import sys

# Inicialização de variáveis globais relacionadas à janela e gráficos
w_width = 700
w_height = 800
win = pygame.display.set_mode((w_width, w_height))
pygame.display.set_caption('Shimodle')
pygame.init()
pygame.font.init()
text_font = 'arial'

# Inicialização de variáveis relacionadas aos quadrados (squares)
s_width = 50
s_height = 50
s_space = 7
s_margin = 2

# Inicialização de variáveis relacionadas aos botões
b_margin = 20
b_font = 15
b_letters = 37

# Quantidade de tentativas até perder a rodada
tries = 6

# Definição de cores em RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 150, 0)
GRAY = (128, 128, 128)
YELLOW = (128, 128, 0)
DARKGRAY = (50, 50, 50)

"""Abre o arquivo com a lista de palavras e salva as palavras na lista "words".
    OBS: a lista contém apenas palavras com 5 letras.
"""
with open('wordlist.txt', 'r', encoding='utf-8') as file:
    words = []
    s = file.readline()
    while s:
        words.append(s.rstrip().upper())
        s = file.readline()


class Board:
    """Classe que define os atributos e métodos do tabuleiro de 6 linhas x 5 colunas.
    Ela recebe a palavra da rodada, tem uma lista com as tentativas do jogador,
    grava o número da linha atual, grava o chute correspondente a cada quadrado do tabuleiro (30 no total),
    quais letras estão verdes, amarelas ou cinzas, e se o jogo já acabou.
    """

    def __init__(self, correct_word):
        self.word = correct_word
        self.player_word = ['' for _ in range(tries)]
        self.row = 0
        self.guess = ['NONE' for _ in range(30)]
        self.yellow_letters = ''
        self.green_letters = ''
        self.gray_letters = ''
        self.game_end = False

    def check(self, word_guess, check_letters):
        """Método usado para avaliar o chute atual do jogador, letra a letra.
        Recebe a string do chute e um dict com cada letra da palavra correta como suas chaves, e
        quantas vezes as letras aparecem como seus valores. Caso a letra do chute esteja no lugar
        correto, o "guess" do quadrado de número correspondente, ou seja,
        o quandrado de número = índice da iteração + a linha * 5 (quantidade de colunas)
        será marcado como "CORRECT" e a letra entrará na string de letras verdes.
        Se a letra não estiver na palavra, o número do quadrado ficará marcado como "INCORRECT",
        e a letra entrará na string de letras cinzas.
        """
        for i in range(len(word_guess)):
            if word_guess[i] == self.word[i]:
                self.guess[i + self.row * 5] = 'CORRECT'
                self.green_letters += word_guess[i]
                check_letters[word_guess[i]] -= 1
            elif word_guess[i] not in self.word:
                self.guess[i + self.row * 5] = 'INCORRECT'
                self.gray_letters += word_guess[i]
        """Depois de checar as letras certas e erradas, é necessário checar de novo
        se há letras na posição errada. Isso não pode ser feito no primeiro loop 
        porque antes é necessário ter certeza que todas as letras na posição certa
        tenham sido subtraídas do dict "used", para o programa não pintar de amarelo
        letras que foram usadas na posição certa depois.
        Aqui, as letras que existem na palavra mas não estão na posição certa entram na string 
        das amarelas se não foi esgotada a quantidade de letras iguais à que está sendo checada 
        atualmente. Se foi esgotada, então ela está "INCORRECT".
        """
        for i in range(len(word_guess)):
            if word_guess[i] != self.word[i] and word_guess[i] in self.word:
                if check_letters[word_guess[i]] > 0:
                    self.guess[i + self.row * 5] = 'WRONG POSITION'
                    self.yellow_letters += word_guess[i]
                    check_letters[word_guess[i]] -= 1
                else:
                    self.guess[i + self.row * 5] = 'INCORRECT'

    def reset(self, other_word):
        # Método que reinicia os atributos quando um novo jogo é iniciado.
        self.word = other_word
        self.player_word = ['' for _ in range(tries)]
        self.row = 0
        self.guess = ['NONE' for _ in range(30)]
        self.yellow_letters = ''
        self.green_letters = ''
        self.gray_letters = ''
        self.game_end = False


class Square:
    # Classe que define os quadrados que representarão cada letra em cada linha do tabuleiro
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
        font = pygame.font.SysFont(text_font, self.font)
        if len(self.letter) > 0:
            text = font.render(self.letter, 1, WHITE)
            window.blit(text, (self.x + s_margin + round((self.width - 2*s_margin) / 2) - round(text.get_width() / 2),
                        self.y + s_margin + round((self.height - 2*s_margin) / 2) - round(text.get_height() / 2)))


class Button:
    # Classe que define os botões das letras que podem ser pressionados
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
        font = pygame.font.SysFont(text_font, self.font)
        text = font.render(self.text, 1, WHITE)
        win.blit(text, (self.x + round(self.width / 2) - round(text.get_width() / 2),
                        self.y + round(self.height / 2) - round(text.get_height() / 2)))

    def click(self, pos):
        if self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height:
            return True
        return False


class Game:

    def __init__(self):
        self.game_started = False
        self.word = ''
        self.used = {}
        self.b = Board(self.word)
        self.btns = []
        self.letters = 'QWERTYUIOPASDFGHJKLÇZXCVBNMÁÃÂÓÕÔÉÊÍÚ'
        self.rows = (10, 10, 7, 10, 2)
        self.m = ''

    def new_word(self):
        # Método que define uma nova palavra aleatória para a rodada atual
        while True:
            """OBS: Aqui a função seleciona palavras com algumas restrições.
            Não pode terminar com "Á" nem "Ê" (ou seja, a quinta letra não pode ser nenhuma dessas), 
            porque as palavras terminadas assim geralmente são verbos que precedem um pronome, 
            por exemplo: "ABATÊ-LO". Essas palavras acabam sendo inconvenientes para o jogo, 
            porém elas ficam na lista "words" porque a cada tentativa do jogador
            o jogo checa se a palavra é válida (ou seja, se está na lista), caso
            não seja a tentativa não é válida. O jogo aceita essas palavras como
            tentativas válidas, mesmo que elas nunca sejam escolhidas como a palavra certa,
            porque isso facilita para o jogador na descoberta de novas letras. O mesmo
            vale para nomes próprios: a função randint é chamada com o mínimo de 121,
            porque essa é a linha da lista de palavras em que todos os nomes próprios já terminaram.
            """
            n = randint(121, (len(words) - 1))
            if words[n][4] != 'Á' and words[n][4] != 'Ê':
                self.word = words[n].upper()
                break

        """Criar ou atualizar a chave do dicionário "used" que corresponde a cada letra da palavra,
        com o valor de quantas vezes a letra é usada."""
        for let in self.word:
            if let in self.used:
                self.used[let] += 1
            else:
                self.used[let] = 1

    def init_widgets(self):
        b_x = 0
        jind = 0
        f = pygame.font.SysFont(text_font, b_font)
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
                content = self.letters[ind]
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
            if (ind == 0 or ind == self.rows[0] or ind == self.rows[0] + self.rows[1]
                    or ind == self.rows[0] + self.rows[1] + self.rows[2] or ind == b_letters):
                b_x = round(w_width / 2) - round((self.rows[jind] * w + (self.rows[jind] - 1) * s_space) / 2)
            b_y = 410 + jind * (h + s_space)
            self.btns.append(Button(win, content, b_x, b_y, w, h))
            b_x += w + s_space
            if (ind == self.rows[0] - 1 or ind == self.rows[0] + self.rows[1] - 1 or
                    ind == self.rows[0] + self.rows[1] + self.rows[2] - 1
                    or ind == b_letters - 1):
                jind += 1

    def draw_squares(self):
        x = round(w_width / 2) - round((5 * s_width + 4 * s_space) / 2)
        y = 20

        for i in range(tries):
            for j in range(5):
                color = BLACK
                if len(self.b.player_word[i]) > j and len(self.b.player_word[i]) > 0:
                    letter = self.b.player_word[i][j]
                    if i == self.b.row:
                        color = GRAY
                else:
                    letter = ''
                if self.b.guess[i*5 + j] == 'WRONG POSITION':
                    color = YELLOW
                elif self.b.guess[i*5 + j] == 'CORRECT':
                    color = GREEN
                square = Square(color, letter, x, y)
                square.draw(win)
                if j < 4:
                    x += s_width + s_space
                else:
                    x = round(w_width / 2) - round((5 * s_width + 4 * s_space) / 2)
                    y += s_height + s_space

    def draw_buttons(self):
        for i in range(len(self.btns)):
            color = GRAY
            if i < b_letters:
                if self.btns[i].text in self.b.gray_letters:
                    color = DARKGRAY
                elif self.btns[i].text in self.b.green_letters:
                    color = GREEN
                elif self.btns[i].text in self.b.yellow_letters:
                    color = YELLOW

            self.btns[i].draw(color)

    def write_message(self):
        font = pygame.font.SysFont(text_font, 30)
        text = font.render(self.m, 1, WHITE)
        win.blit(text, (round(w_width / 2) - round(text.get_width() / 2), 370))

    def redraw_window(self):
        # Método que desenha a janela a cada frame
        win.fill(BLACK)
        self.draw_squares()
        self.draw_buttons()
        if self.m:
            self.write_message()
        pygame.display.update()
        if self.m == 'A palavra não está na lista de palavras!':
            pygame.time.wait(1000)
            pygame.display.update()

    def send_guess(self):
        if self.b.player_word[self.b.row] in words:
            used_copy = deepcopy(self.used)
            self.b.check(self.b.player_word[self.b.row], used_copy)
            self.b.row += 1
        else:
            self.m = 'A palavra não está na lista de palavras!'

    def delete_letter(self):
        self.b.player_word[self.b.row] = self.b.player_word[self.b.row][:-1]

    def add_letter(self, letter):
        self.b.player_word[self.b.row] += letter

    def new_game(self):
        self.used = {}
        self.new_word()
        self.b.reset(self.word)

    def main(self):
        self.m = ''
        if not self.game_started:
            self.new_game()
            self.init_widgets()
            self.game_started = True
        if self.b.row > 0 and self.b.player_word[self.b.row - 1] == self.b.word:
            self.b.game_end = True
            self.m = 'Parabéns! Clique para reiniciar'
        elif self.b.row > 5:
            self.m = f'Palavra: "{self.word}". Clique para reiniciar'
            self.b.game_end = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.b.game_end:
                    pos = pygame.mouse.get_pos()
                    for i in range(b_letters + 2):
                        if self.btns[i].click(pos):
                            if self.btns[i].text == 'ENTER' and len(self.b.player_word[self.b.row]) == 5:
                                self.send_guess()
                            elif self.btns[i].text == 'DEL' and len(self.b.player_word[self.b.row]) > 0:
                                self.delete_letter()
                            elif len(self.b.player_word[self.b.row]) < 5:
                                to_add = self.btns[i].text
                                if len(to_add) == 1:
                                    self.add_letter(to_add)
                else:
                    self.new_game()
            elif event.type == pygame.KEYDOWN:
                if not self.b.game_end:
                    if event.key == pygame.K_RETURN and len(self.b.player_word[self.b.row]) == 5:
                        self.send_guess()
                    elif event.key == pygame.K_BACKSPACE and len(self.b.player_word[self.b.row]) > 0:
                        self.delete_letter()
                    elif len(self.b.player_word[self.b.row]) < 5:
                        to_add = event.unicode
                        if to_add.isalpha():
                            self.add_letter(to_add.upper())
                else:
                    self.new_game()

        self.redraw_window()


game = Game()

while True:
    game.main()
