import pygame as p
import src.engine.engine as engine
import src.engine.bot.bot as bot
import time

BOARD_WIDTH = BOARD_HEIGHT = 512 #512x512
MOVE_LOG_PANEL_WIDTH = 256
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  #8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
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
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('White'))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # flag variable for when a move is made

    loadImages() # only once before the while loop
    running = True
    sqSelected = () # no square selected initially, keeps track of last click of the user (tuple)
    playerClicks = [] # keep track of players clicks (two tuples: [(6, 4), (4, 4)])
    possibleMoves = []  # list to store possible moves for the selected piece
    gameOver = False
    playerOne = True # if a human is playing white, then this will be True, if an AI is playing, then false
    playerTwo = False # same as above but for black
    
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT: # option to quit 
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN: # option to click
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # (x,y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8: # user clicked the same square twice or user clicked mouse log
                        sqSelected = () # deselect
                        playerClicks = [] # clear player clicks
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
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_LEFT: # undo when left arrow is pressed
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                if e.key == p.K_r: # reset the board when 'r' is pressed
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
        
        # BOT move logic
        if not gameOver and not humanTurn:
            botMove = bot.findBestMove(gs, validMoves)
            if botMove is None:
                print('check bot move logic, this shouldnt be none')
                botMove = bot.findRandomMove(validMoves)
            time.sleep(1)
            print(botMove.getChessNotation())
            gs.makeMove(botMove)
            moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            
        drawGameState(screen, gs, validMoves, sqSelected, possibleMoves, moveLogFont)
        clock.tick(MAX_FPS)
        p.display.flip()

        if gs.checkmate or gs.stalemate:
            gameOver = True
            text = 'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate'
            drawEndGameText(screen, text)
            

        # Ensure the screen is updated after drawing the text
        p.display.flip()

#
# Responsible for all graphics within current game state
#
def drawGameState(screen, gs, validMoves, sqSelected, possibleMoves, moveLogFont):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, possibleMoves)
    drawPieces(screen, gs.board) # draw pieces on top of squares
    drawMoveLog(screen, gs, moveLogFont)


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
            
            # Create a surface for highlighting moves
            highlight_surface = p.Surface(screen.get_size(), p.SRCALPHA)  # Create a surface with alpha
            highlight_surface.fill((0, 0, 0, 0))  # Fill with transparent color
            
            # Highlight possible move squares
            for move in possibleMoves:
                # Draw a slightly transparent yellow square for possible moves
                yellow_square = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)
                yellow_square.fill((255, 255, 0, 20))  # Yellow with alpha for transparency
                highlight_surface.blit(yellow_square, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                
                # Draw circles for the moves
                if move.pieceCaptured == '--':
                    p.draw.circle(highlight_surface, (105, 105, 105, 80),  # More transparent for move dots
                                  (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2), 
                                  SQ_SIZE // 8)  # Slightly larger circles
                else:
                    p.draw.circle(highlight_surface, (105, 105, 105, 80),  # More transparent for capture circles
                                  (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2), 
                                  SQ_SIZE // 2, 4)  # Outline circle for captures
            
            # Blit the highlight surface onto the main screen
            screen.blit(highlight_surface, (0, 0))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("antiquewhite3"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i+1 < len(moveLog): # make sure black made a move
            moveString += str(moveLog[i+1]) + "  "
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('black'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing
    pass


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2,
                                                    BOARD_HEIGHT/2 - textObject.get_height()/2) # center the text
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()