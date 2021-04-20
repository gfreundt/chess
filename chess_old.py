from time import *
from itertools import permutations
import pygame
from pygame.locals import *

pygame.init()


class Piece:
    def __init__(self, config):
        self.type = config[0]  # King, Queen, Bishop, Knight, Rook, Pawn
        self.color = config[1]  # White / Black
        self.column = int(config[2]) - 1  # Column (0-7)
        self.row = int(config[3]) - 1  # Row (0-7)
        self.image = pygame.image.load(FILE_PATH + r"\Chess\Images" + config[4].strip())


def draw_board():
    # Background
    for x in range(8):
        for y in range(8):
            if piece_picked_up and (x, 7 - y) in valid_destinations:
                screen.blit(squareSelectedImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
            elif (x + y) % 2 == 0:
                screen.blit(squareClearImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
            else:
                screen.blit(squareDarkImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
    # Pieces
    for piece in allActivePieces:
        coords = ((piece.column * SQUARE_SIZE) + 15, (SQUARE_SIZE * (7 - piece.row)) + 15)
        screen.blit(piece.image, coords)
    pygame.display.update()


def get_square(coords):
    square_column = int(coords[0] / SQUARE_SIZE)
    square_row = int(8 - (coords[1] / SQUARE_SIZE))
    return square_column, square_row


def get_destination_squares(piece):

    def valid_squares(moves):
        print(allActivePieces)
        # not allow out of bounds
        moves = [i for i in moves if not (i[0] < 0 or i[0] > 7 or i[1] < 0 or i[1] > 7)]
        # not allow on top of piece of same color
        moves = [i for i in moves if True]

        return moves

    moves = []
    if piece.color == current_turn:
        if piece.type == 'king':
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    moves.append((piece.column + x, piece.row + y))
        elif piece.type == 'queen':
            for x in range(-7, 8):
                for y in range(-7, 8):
                    if abs(x) - abs(y) == 0 or (x == 0 or y == 0):
                        moves.append((piece.column + x, piece.row + y))
        elif piece.type == 'bishop':
            for x in range(-7, 8):
                for y in range(-7, 8):
                    if abs(x) - abs(y) == 0 and not (x == 0 or y == 0):
                        moves.append((piece.column + x, piece.row + y))
        elif piece.type == 'knight':
            for m in permutations((-2, -1, 1, 2), 2):
                x, y = m[0], m[1]
                if abs(x) - abs(y) != 0:
                    moves.append((piece.column + x, piece.row + y))
        elif piece.type == 'rook':
            for x in range(-7, 8):
                for y in range(-7, 8):
                    if x == 0 or y == 0:
                        moves.append((piece.column + x, piece.row + y))
        elif piece.type == 'pawn':
            if current_turn == 'white':
                add = 1
            else:
                add = -1
            moves = [(piece.column, piece.row + add)]
            if (add * piece.row) in (-6, 1):
                moves.append((piece.column, piece.row + 2 * add))
            # TODO: "al paso"

        # Clean moves
        final_moves = valid_squares(moves)

        print(final_moves)
        return final_moves



# Create Game Environment
FILE_PATH = r"D:\Google Drive Backup\Multi-Sync\gui games"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Fonts and Text Images
font24 = pygame.font.SysFont('Arial', 24, bold=True, italic=False)
font56 = pygame.font.SysFont('Arial', 56, bold=True, italic=False)
# scoreImg = font24.render("Score: 0", True, WHITE)

# Screen
SQUARE_SIZE = 108
SCREEN_SIZE = (SQUARE_SIZE * 8, SQUARE_SIZE * 8)
SCREEN_CAPTION = "Chess"
SCREEN_ICON = FILE_PATH + r"\_Resources\Images\G_logo.png"

# Saved Image Paths and Sizes
squareClearImage = pygame.image.load(FILE_PATH + r"\Chess\Images\clear_empty.jpg")
squareDarkImage = pygame.image.load(FILE_PATH + r"\Chess\Images\dark_empty.jpg")
squareSelectedImage = pygame.image.load(FILE_PATH + r"\Chess\Images\selected_square.jpg")
with open(FILE_PATH + r"\Chess\chess_config.txt") as config:
    allActivePieces = []
    for piece in config.readlines():
        allActivePieces.append(Piece(piece.split(',')))

# Sounds and Music
# pygame.mixer.music.load(FILE_PATH + r"\Sounds\background02.wav")
# collisionSound = pygame.mixer.Sound(FILE_PATH + r"\Sounds\explosion01.wav")
# ghostSound = pygame.mixer.Sound(FILE_PATH + r"\Sounds\power_up_and_down.wav")
# nextLevelSound = pygame.mixer.Sound(FILE_PATH + r"\Sounds\level_up.wav")

# Load variables

# Init Game Basics
# pygame.mixer.music.play(loops=-1)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(SCREEN_CAPTION)
pygame.display.set_icon(pygame.image.load(SCREEN_ICON))
start_time = time()
current_turn = 'white'
piece_picked_up = False

# Main Loop
running = True
while running:

    draw_board()

    action = False
    while not action:  # loops while waiting for BEGIN activity from player
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    # key_pressed = True
                    running = False  # Quit Game
                    action = True
            if event.type == MOUSEBUTTONDOWN:
                selected_piece = [i for i in allActivePieces if (i.column, i.row) == get_square(pygame.mouse.get_pos())]
                if selected_piece:  # clicked on piece, not empty square
                    valid_destinations = get_destination_squares(selected_piece[0])
                    # print(valid_destinations)
                    if valid_destinations:  # piece was valid to be picked (right color / turn)
                        piece_picked_up = True
                        action = True

    draw_board()

    while action and running:  # loops while waiting for CLOSE activity from player
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    action = False  # return to loop to wait for begin activity
            if event.type == MOUSEBUTTONDOWN:
                sq = pygame.mouse.get_pos()
                is_occupied_space = [i for i in allActivePieces if (i.column, i.row) == get_square(sq)]
                if not is_occupied_space:  # clicked on empty square
                    selected_piece[0].column, selected_piece[0].row = get_square(sq)
                    piece_picked_up = True
                    action = False
        valid_destinations = []

    current_turn = [i for i in ('white', 'black') if i is not current_turn][0]

    # Update screen, end loop
    # pygame.display.update()
