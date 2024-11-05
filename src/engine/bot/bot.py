import random  # import the random module to generate random numbers
import src.engine.engine as engine  # import the engine module which contains the game logic

# Define the score values for each piece type
pieceScore = {'K': 0, 'Q': 9.5, 'R': 5.63, 'B': 3.33, 'N': 3.05, 'p': 1}
CHECKMATE = 1000  # constant value representing checkmate score
STALEMATE = 0  # constant value representing stalemate score
DEPTH = 3

def findRandomMove(validMoves):
    """ 
    FIND RANDOM MOVE 
    This function selects a random move from the list of valid moves.
    """
    return validMoves[random.randint(0, len(validMoves)-1)]  # return a random move from validMoves

def findBestMove(gs, validMoves):
    """ 
    FIND BEST MOVE 
    This function evaluates all possible moves and selects the best one based on the minimax algorithm.
    """
    turnMultiplier = 1 if gs.whiteToMove else -1  # determine the multiplier based on whose turn it is
    opponentMinMaxScore = CHECKMATE  # initialize the opponent's minimum score to checkmate
    bestPlayerMove = None  # variable to store the best move for the player
    random.shuffle(validMoves)

    # Iterate through all valid moves for the player
    for playerMove in validMoves:
        gs.makeMove(playerMove)  # make the player's move
        opponentsMoves = gs.getValidMoves()  # get all valid moves for the opponent
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            # Evaluate each move the opponent can make
            for move in opponentsMoves:
                gs.makeMove(move)  # make the opponent's move
                gs.getValidMoves()
                if gs.checkmate:  # check if the opponent has checkmated the player
                    score = CHECKMATE  # assign a high negative score for checkmate
                elif gs.stalemate:  # check if the game is in stalemate
                    score = STALEMATE  # assign a score of zero for stalemate
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)  # evaluate the board score based on material

                if score > opponentMaxScore:  # if the current score is better than the opponent's max score
                    opponentMaxScore = score  # update the opponent's max score
                gs.undoMove()  # undo the opponent's move to evaluate the next one

        # If the opponent's max score is better than the current minimum score
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore  # update the minimum score for the opponent
            bestPlayerMove = playerMove  # update the best move for the player
        gs.undoMove()  # undo the player's move to evaluate the next one

    return bestPlayerMove  # return the best move found for the player


def findBestMoveMinMax(gs, validMoves): # helper method
    global nextMove
    nextMove = None
    findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    return nextMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0: # if terminal node (deepest)
        return scoreMaterial(gs.board)
    
    if whiteToMove: # trying to MAXimise
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else: # trying to MINimise
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore
    


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
    elif gs.stalemate:
        return STALEMATE   

    score = 0
    # Iterate through each row of the board
    for row in gs.board:
        # Iterate through each square in the row
        for square in row:
            if square[0] == 'w':  # if the piece is white
                score += pieceScore[square[1]]  # add the piece's score to the total
            elif square[0] == 'b':  # if the piece is black
                score -= pieceScore[square[1]]  # subtract the piece's score from the total
    return score  # return the total score of the board



def scoreMaterial(board):
    """ 
    SCORE MATERIAL 
    This function calculates the total material score of the board.
    """
    score = 0  # initialize the score to zero
    # Iterate through each row of the board
    for row in board:
        # Iterate through each square in the row
        for square in row:
            if square[0] == 'w':  # if the piece is white
                score += pieceScore[square[1]]  # add the piece's score to the total
            elif square[0] == 'b':  # if the piece is black
                score -= pieceScore[square[1]]  # subtract the piece's score from the total
    return score  # return the total score of the board