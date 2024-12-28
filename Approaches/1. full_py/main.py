import pygame as p
import engine

WIDTH = HEIGHT = 512 #512x512
DIMENSION = 8  #8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

#
# Initialize a global dictionary of images. Will only be called once in the main
#
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("pngs/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        #Note: we can access an image by saying 'IMAGES['wp']'

#
# The main driver of our code, handles user input and updates the graphicps.
#
def main():
    p.init()
    p.display.set_caption('test chess')
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('White'))
    gs = engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made

    loadImages() # only once before the while loop
    running = True
    sqSelected = () # no square selected initially, keeps track of last click of the user (tuple)
    playerClicks = [] # keep track of players clicks (two tuples: [(6, 4), (4, 4)])
    possibleMoves = []  # List to store possible moves for the selected piece
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT: # option to quit
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: # option to click
                location = p.mouse.get_pos() # (x,y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): # user clicked the same square twice
                    sqSelected = ()
                    playerClicks = []
                    possibleMoves = []  # Clear possible moves
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # append first and second click
                    if len(playerClicks) == 1:
                        possibleMoves = [move for move in validMoves if move.startRow == row and move.startCol == col]
                if len(playerClicks) == 2: # after second click
                    move = engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            print(move.getChessNotation())
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = () # reset
                            playerClicks = [] # reset
                            possibleMoves = []  # Clear possible moves
                    if not moveMade:
                        playerClicks = [sqSelected]
                        possibleMoves = [move for move in validMoves if move.startRow == row and move.startCol == col]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT: # undo when left arrow is pressed
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            
        drawGameState(screen, gs, validMoves, sqSelected, possibleMoves)
        clock.tick(MAX_FPS)
        p.display.flip()

#
# Responsible for all graphics within current game state
#
def drawGameState(screen, gs, validMoves, sqSelected, possibleMoves):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, possibleMoves)
    drawPieces(screen, gs.board) # draw pieces on top of squares

#
# Draw squares on board
#
def drawBoard(screen):
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION): # r for row
        for c in range(DIMENSION): # c for column
            color = colors[( (r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

#
# Draw pieces on top of squares using current GameState.board
#
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # if not empty, draw piece
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected, possibleMoves):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Increased alpha for better visibility
            s.fill(p.Color('darkgray'))  # Darker gray for selected square
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # Highlight moves
            for move in possibleMoves:
                if move.pieceCaptured == '--':
                    p.draw.circle(screen, p.Color('dimgray'),  # Slightly darker gray for move dots
                                  (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2), 
                                  SQ_SIZE // 8)  # Slightly larger circles
                else:
                    p.draw.circle(screen, p.Color('dimgray'),  # Use circles for captures
                                  (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2), 
                                  SQ_SIZE // 2, 4)  # Outline circle for captures

if __name__ == "__main__":
    main()