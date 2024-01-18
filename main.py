
#pip install numpy
#pip install pygame
#pip install easygui
#pip install PyQt5


import numpy as np
import random
import pygame
import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

SQUARESIZE = 100

RADIUS = int(SQUARESIZE / 2 - 5)

width = COLUMN_COUNT * SQUARESIZE

height = (ROW_COUNT + 1) * SQUARESIZE





def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r][c + 1] == piece
                and board[r][c + 2] == piece
                and board[r][c + 3] == piece
            ):
                return True

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c] == piece
                and board[r + 2][c] == piece
                and board[r + 3][c] == piece
            ):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if (
                board[r][c] == piece
                and board[r + 1][c + 1] == piece
                and board[r + 2][c + 2] == piece
                and board[r + 3][c + 3] == piece
            ):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if (
                board[r][c] == piece
                and board[r - 1][c + 1] == piece
                and board[r - 2][c + 2] == piece
                and board[r - 3][c + 3] == piece
            ):
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def score_position(board, piece):
    score = 0

    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c : c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r : r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(
        board, AI_PIECE
    ) or len(get_valid_locations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]

            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]

            if new_score < value:
                value = new_score
                column = col

            beta = min(beta, value)

            if alpha >= beta:
                break

        return column, value

def get_valid_locations(board):
    valid_locations = []

    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)

    return valid_locations

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)

    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)

        if score > best_score:
            best_score = score
            best_col = col

    return best_col

# Ajoutez ces fonctions à votre code

def draw_text(text, x, y, color):
    font = pygame.font.SysFont(None, 55)
    text = font.render(text, True, color)
    screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE)
            )
            pygame.draw.circle(
                screen,
                BLACK,
                (
                    int(c * SQUARESIZE + SQUARESIZE / 2),
                    int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                ),
                RADIUS,
            )

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        height - int(r * SQUARESIZE + SQUARESIZE / 2),
                    ),
                    RADIUS,
                )

    pygame.display.update()


def player_vs_player(player1_name, player2_name):
    board = create_board()
    print_board(board)
    game_over = False
    turn = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == 0:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                else:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1 if turn == 0 else 2)

                    if winning_move(board, 1) or winning_move(board, 2):
                        winner = player1_name if turn == 0 else player2_name
                        label = myfont.render(f"{winner} Bravo!!", 1, RED if turn == 0 else YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

                    if game_over:
                        pygame.time.wait(3000)

def player_vs_ai(myfont, player_name):
    board = create_board()
    print_board(board)
    game_over = False
    turn = random.randint(PLAYER, AI)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION and turn == PLAYER:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = myfont.render(f"{player_name} wins!!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

            if turn == AI and not game_over:
                col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)

                    if winning_move(board, AI_PIECE):
                        label = myfont.render(f"AI vous a gagné {player_name}!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn += 1
                    turn = turn % 2

                if game_over:
                    pygame.time.wait(3000)


 # Classe qui gère le dialog pour entrer le nom des deux players
class PlayerNamesDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Entrez les noms des joueurs')
        self.setGeometry(200, 200, 400, 200)

        # Couleur de fond de l'écran
        self.setStyleSheet("background-color: #3498db;")

        # Police et style du texte
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        self.player1_label = QLabel('Nom du Joueur 1:')
        self.player1_label.setStyleSheet("color: #ecf0f1;")
        self.player1_label.setFont(font)

        self.player1_input = QLineEdit(self)
        self.player1_input.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-family: 'Arial'; font-size: 14px;")
        self.player1_input.setPlaceholderText("Entrez votre nom...")

        self.player2_label = QLabel('Nom du Joueur 2:')
        self.player2_label.setStyleSheet("color: #ecf0f1;")
        self.player2_label.setFont(font)

        self.player2_input = QLineEdit(self)
        self.player2_input.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-family: 'Arial'; font-size: 14px;")
        self.player2_input.setPlaceholderText("Entrez votre nom...")

        self.ok_button = QPushButton('OK', self)
        self.ok_button.setStyleSheet("background-color: #2ecc71; color: #ecf0f1; font-family: 'Arial'; font-size: 16px; border: none;")
        self.ok_button.clicked.connect(self.accept_names)

        layout = QVBoxLayout()
        layout.addWidget(self.player1_label)
        layout.addWidget(self.player1_input)
        layout.addWidget(self.player2_label)
        layout.addWidget(self.player2_input)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # Ajout d'une animation
        self.fade_in_animation()

    def fade_in_animation(self):
        # Animation de fondu pour l'ensemble du widget
        self.setWindowOpacity(0.0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def accept_names(self):
        # Animation de fondu avant de fermer la fenêtre
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

        player1_name = self.player1_input.text()
        player2_name = self.player2_input.text()
        player_vs_player(player1_name, player2_name)

def get_player_names():
    app = QApplication(sys.argv)
    dialog = PlayerNamesDialog()
    dialog.show()
    sys.exit(app.exec_())


 # Classe qui gère le dialog pour entrer le nom d'un joueur
    
class SinglePlayerNameDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Entrez votre nom')
        self.setGeometry(100, 100, 400, 100)

        # Couleur de fond de l'écran
        self.setStyleSheet("background-color: #3498db;")

        # Police et style du texte
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)

        self.player_label = QLabel('Nom du Joueur:')
        self.player_label.setStyleSheet("color: #ecf0f1;")
        self.player_label.setFont(font)

        self.player_input = QLineEdit(self)
        self.player_input.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-family: 'Arial'; font-size: 14px;")
        self.player_input.setPlaceholderText("Entrez votre nom...")

        self.ok_button = QPushButton('OK', self)
        self.ok_button.setStyleSheet("background-color: #2ecc71; color: #ecf0f1; font-family: 'Arial'; font-size: 16px; border: none;")
        self.ok_button.clicked.connect(self.accept_name)

        layout = QVBoxLayout()
        layout.addWidget(self.player_label)
        layout.addWidget(self.player_input)
        layout.addWidget(self.ok_button)
        layout.setSpacing(15)  # Ajustez cet espace selon vos préférences

        self.setLayout(layout)

        # Ajout d'une animation
        self.fade_in_animation()

    def fade_in_animation(self):
        # Animation de fondu pour l'ensemble du widget
        self.setWindowOpacity(0.0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def accept_name(self):
        # Animation de fondu avant de fermer la fenêtre
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

        player_name = self.player_input.text()
        player_vs_ai(myfont, player_name)

def get_single_player_name():
    app = QApplication(sys.argv)
    dialog = SinglePlayerNameDialog()
    dialog.show()
    sys.exit(app.exec_())


def game_mode_menu():
    screen.fill(BLACK)
    draw_board(create_board())

    # Ajoutez des boutons pour les options de jeu
    draw_text("Choisissez le mode de jeu:", width // 2, height // 4, (255, 255, 255))
    draw_text("1. Joueur contre Joueur", width // 2, height // 2 - 30, (255, 255, 255))
    draw_text("2. Joueur contre AI", width // 2, height // 2 + 30, (255, 255, 255))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

                # Vérifie si l'événement est un clic de souris (BUTTONDOWN) avec le bouton gauche (button == 1)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Récupère les coordonnées (x, y) de la souris au moment du clic
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Vérifie si le clic de souris est dans la zone du bouton "1. Joueur contre Joueur"
            if width // 2 - 100 < mouse_x < width // 2 + 100:
                if height // 2 - 50 < mouse_y < height // 2 - 10:
                    pygame.event.clear()  # Efface les événements de souris pour éviter la répétition
                    screen.fill(BLACK)  # Remplit l'écran avec la couleur noire
                    draw_board(create_board())  # Redessine le plateau de jeu vide
                    return "1", *get_player_names()

            # Vérifie si le clic de souris est dans la zone du bouton "2. Joueur contre AI"
            elif height // 2 + 10 < mouse_y < height // 2 + 50:
                pygame.event.clear()  # Efface les événements de souris pour éviter la répétition
                screen.fill(BLACK)  # Remplit l'écran avec la couleur noire
                draw_board(create_board())  # Redessine le plateau de jeu vide
                return "2", get_single_player_name()


        pygame.display.update()



def main():
    global screen, SQUARESIZE, RADIUS, width, height, myfont
    pygame.init()

    SQUARESIZE = 100

    width = COLUMN_COUNT * SQUARESIZE
    height = (ROW_COUNT + 1) * SQUARESIZE

    size = (width, height)

    RADIUS = int(SQUARESIZE / 2 - 5)

    screen = pygame.display.set_mode(size)
    myfont = pygame.font.SysFont(None, 55)

    user_choice, *player_names = game_mode_menu()

    if user_choice == "1":
        player_vs_player(*player_names)
    elif user_choice == "2":
        player_vs_ai(myfont, player_names[0])



if __name__ == "__main__":
    main()

