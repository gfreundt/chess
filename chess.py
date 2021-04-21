#TODO: en passant
#TODO: checkmate
#TODO: castling no check on spaces travelled ny king


import chess_board_score as cbs
from time import *
from itertools import permutations
import pygame
from pygame.locals import *
import numpy as np
import os
import csv

pygame.init()


def load_init_config():
    board = np.zeros((8,8), dtype=int)
    with open('chess_config.txt', mode='r') as file:
        for p,x,y in csv.reader(file):
            board[int(x)][int(y)] = int(p)
    return board


def draw_board(moving_piece_coords = (0,0)):
    # Background
    for x in range(8):
        for y in range(8):
            if piece_picked_up and (x, y) in possible_destinations:
                screen.blit(squareSelectedImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
            elif (x + y) % 2 == 0:
                screen.blit(squareClearImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
            else:
                screen.blit(squareDarkImage, (x * SQUARE_SIZE, y * SQUARE_SIZE))
    # Fixed Pieces
    for x in range(8):
        for y in range(8):
            coords = ((x * SQUARE_SIZE) + 15, (y * SQUARE_SIZE) + 15)
            image_code = activeBoard[(x,y)]
            if image_code != 0:
                screen.blit(pieceImages[image_code], coords)

    # Moving Piece
    if moving_piece_coords != (0,0):
        moving_piece_coords = [i - SQUARE_SIZE//2 for i in moving_piece_coords]
        screen.blit(pieceImages[selected_piece], moving_piece_coords)

    
    #print(np.flip(np.rot90(activeBoard, k=-1),axis=1))
    pygame.display.update()


def player_action():
    last_mouse_pos = pygame.mouse.get_pos()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return 'ESC', None
            if event.type == MOUSEBUTTONDOWN:
                return 'MBD', get_square(pygame.mouse.get_pos())
            if event.type == MOUSEBUTTONUP:
                return 'MBU', get_square(pygame.mouse.get_pos())
        if pygame.mouse.get_pos() != last_mouse_pos:
            return 'MOV', pygame.mouse.get_pos()


def me_in_check():
    all_attacked = []
    for x in range(8):
        for y in range(8):
            piece_reviewed = activeBoard[(x,y)]
            if piece_reviewed == 1*current_turn:
                my_king_pos = (x,y)  # find where my king is
            elif piece_reviewed / current_turn < 0:
                all_attacked.append(get_destination_squares(piece_reviewed, (x,y), rev=-1))
    if my_king_pos in [item for s in all_attacked for item in s]:
        return True
    return False


def opp_in_check():
    all_attacked = []
    for x in range(8):
        for y in range(8):
            piece_reviewed = activeBoard[(x,y)]
            if piece_reviewed == -1*current_turn:
                my_king_pos = (x,y)  # find where my king is
            elif piece_reviewed / -current_turn < 0:
                all_attacked.append(get_destination_squares(piece_reviewed, (x,y)))
    if my_king_pos in [item for s in all_attacked for item in s]:
        return True
    return False


def checkmate():
    if opp_in_check():
        pass
    return False


def get_square(coords):
    return int(coords[0] / SQUARE_SIZE),int(coords[1] / SQUARE_SIZE)


def long_move(x0, y0, piece, direction): # queen, rook, bishop
    moves = []
    for a,b in [(-1, 0), (0, -1), (1, 0), (0, 1)] if direction == 'orthogonal' else [(-1, 1), (-1, -1), (1, 1), (1, -1)]:
        x,y = int(a), int(b)
        while True:
            new_coords = (x0 + x, y0 + y)
            if out_of_bounds(new_coords) or (activeBoard[new_coords] / piece) > 0:
                break
            elif (activeBoard[new_coords] / piece) < 0:
                moves.append(new_coords)
                break
            else:
                moves.append(new_coords)
                x += a
                y += b
    return moves


def knight_move(x0, y0, piece):
    moves = []
    for m in permutations((-2, -1, 1, 2), 2):
        x, y = m[0], m[1]
        if abs(x) - abs(y) != 0 and not out_of_bounds((x0 + x, y0 + y)) and (activeBoard[(x0 + x, y0 + y)] / piece) <= 0:
            moves.append((x0 + x, y0 + y))
    return moves


def king_move(x0, y0, piece, rev):
    moves=[]
    # one square
    for x,y in [(-1, 1), (-1, -1), (1, 1), (1, -1),(0, 1), (0, -1), (1, 0), (-1, 0)]:
        if not out_of_bounds((x0 + x, y0 + y)) and (activeBoard[(x0 + x, y0 + y)] / piece) <= 0:
            moves.append((x0 + x, y0 + y))
    if rev == 1: # skip when evaluating positions for check
        # castling long TODO: check for in check or attacked spaces
        line = 0 if current_turn < 0 else 7
        if castling_left[current_turn] and all([activeBoard[(x0 - i, line)] == 0 for i in range(1,4)]):
            moves.append((1, line))
        # castling short TODO: check for in check or attacked spaces
        if castling_right[current_turn] and all([activeBoard[(x0 + i, line)] == 0 for i in range(1,3)]):
            moves.append((6, line))
    return moves


def pawn_move(x0, y0, piece):
    moves=[]
    color = -int(piece / abs(piece))
    # one square forward
    new_coords = (x0, y0 + color)
    if activeBoard[new_coords] == 0:
        moves.append(new_coords)
        # two sqaures foward
        new_coords = (x0, y0 + color*2)
        if ((color == -1 and y0 == 6)  or (color == 1 and y0 == 1)) and (activeBoard[new_coords] == 0):
            moves.append(new_coords)
    # capture
    for cap in (-1, 1):
        new_coords = (x0 + cap, y0 + color)
        if not out_of_bounds(new_coords) and int(activeBoard[new_coords]/color) > 0:
            moves.append(new_coords)
    # en passant
    pass

    return moves


def out_of_bounds(coords):  # coordinates outside board boundaries
    if (coords[0] < 0) or (coords[0] > 7) or (coords[1] < 0) or (coords[1] > 7):
        return True


def get_destination_squares(piece, square, rev=1):
    x0, y0 = square
    if int(piece/abs(piece)) == current_turn * rev:
        if abs(piece) == 1:  # king
            moves = king_move(x0, y0, piece, rev)
        elif abs(piece) == 2:  # queen
            moves = long_move(x0,y0, piece, 'orthogonal') + long_move(x0, y0, piece, 'diagonal')
        elif abs(piece) == 3:  # rook
            moves = long_move(x0,y0, piece, 'orthogonal')
        elif abs(piece) == 4:  # bishop
            moves = long_move(x0, y0, piece, 'diagonal')
        elif abs(piece) == 5:  # knight
            moves = knight_move(x0, y0, piece)
        elif abs(piece) == 6:  # pawn
            moves = pawn_move(x0, y0, piece)
        return moves


def execute_move(origin, dest):
    # castling
    if abs(selected_piece) == 1:
        x,y = dest
        if x == 6 and castling_right[current_turn]:
            activeBoard[dest] = selected_piece
            activeBoard[(7,y)], activeBoard[(4,y)] = 0,0
            activeBoard[(5,y)] = 3 * current_turn
            castling_left[current_turn], castling_right[current_turn] = 0, 0
            return
        elif x == 1 and castling_left[current_turn]:
            activeBoard[dest] = selected_piece
            activeBoard[(0,y)], activeBoard[(4,y)] = 0,0
            activeBoard[(2,y)] = 3 * current_turn
            castling_left[current_turn], castling_right[current_turn] = 0, 0
            return

    # regular move or capture and turn off castling if appropriate
    activeBoard[dest] = selected_piece
    activeBoard[origin] = 0

    if abs(selected_piece) == 1:
        castling_left[current_turn], castling_right[current_turn] = 0, 0
    elif abs(selected_piece) == 3 and origin[0] == 7:
        castling_right[current_turn] = 0
    elif abs(selected_piece) == 3 and origin[0] == 0:
        castling_left[current_turn] = 0
    
    # promotion
    if abs(activeBoard[dest]) == 6 and ((current_turn == 1 and dest[1] == 0)  or (current_turn == -1 and dest[1] == 7)):
        activeBoard[dest] = 2*current_turn # queen


def end_conditions():
    if checkmate():
        return True
    return False


# Paths
FILE_PATH = r"D:\Google Drive Backup\Multi-Sync\gui games"
IMAGE_PATH = os.path.join(FILE_PATH, "Chess", "Images")

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
SCREEN_POS = (2500, 30)
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{SCREEN_POS[0]},{SCREEN_POS[1]}"

# Saved Image Paths and Sizes
squareClearImage = pygame.image.load(FILE_PATH + r"\Chess\Images\clear_empty.jpg")
squareDarkImage = pygame.image.load(FILE_PATH + r"\Chess\Images\dark_empty.jpg")
squareSelectedImage = pygame.image.load(FILE_PATH + r"\Chess\Images\selected_square.jpg")

# Game Variables
pieceCodeGuide = {1:'king', 2:'queen', 3:'rook', 4:'bishop', 5:'knight', 6:'pawn'}
pieceImages = {piece:pygame.image.load(os.path.join(IMAGE_PATH, f'{"black" if piece < 0 else "white"}_{pieceCodeGuide[abs(piece)]}.png')) for piece in [i for i in range(-6,7) if i != 0]}
activeBoard = load_init_config()


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
castling_left = {-1: 1, 1: 1} # Key = color, Value = (Left, Right) Side | -1 = Previous Turn Castle Not Available, 0 = Castle Not Available Permanently, 1 = Castle Available
castling_right = {-1: 1, 1: 1}
current_turn = 1 # white always starts
piece_picked_up = False

# Main Loop
running = True
while running:

    draw_board()

    # Action 1: Pick up piece
    possible_destinations = []
    selection = False
    while not selection:  # loops while waiting for BEGIN activity from player
        action, square_clicked = player_action()
        if action == 'ESC':
            quit()
        elif action == 'MBD':
            selected_piece = activeBoard[square_clicked]
            if selected_piece:  # clicked on piece, not empty square
                possible_destinations = get_destination_squares(selected_piece, square_clicked)
                if possible_destinations:  # piece was valid to be picked (right color / turn)
                    piece_picked_up = True
                    square_clicked_pick = square_clicked[:]
                    selection = True

    # Action 2: Move piece
    activeBoard[square_clicked] = 0   # temporarily erase piece from array
    button_down = True
    while button_down:  # loops while waiting for BEGIN activity from player
        action, moving_piece_coords = player_action()
        if action == 'ESC':
            quit()
        elif action == 'MOV':
            draw_board(moving_piece_coords = moving_piece_coords)
        elif action == 'MBU':
            print(moving_piece_coords)
            button_down = False

    # Action 3: Drop piece and validate position
    if moving_piece_coords in possible_destinations:
        previousBoard = activeBoard.copy()
        activeBoard[moving_piece_coords] = selected_piece
        execute_move(square_clicked, moving_piece_coords)
        turn_complete = True
        if me_in_check():
            activeBoard = previousBoard.copy()
            activeBoard[square_clicked] = selected_piece
            turn_complete = False
        if opp_in_check():
            pass
        piece_picked_up = False
    else:
        activeBoard[square_clicked] = selected_piece
        turn_complete = False


    # Check for end of game - if not next turn
    if turn_complete:
        if end_conditions():
            break
        current_turn *= -1
        #print(cbs.score(activeBoard, 'kaufman'))



print("The End")