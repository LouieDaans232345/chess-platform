###   ###   ###
###    1    ###                     
###   ###   ###

class GameState():

    def __init__(self):
        # the board is an 8x8 2d list, each element of the list has 2 characters.
        # first character represents color of the piece, 'b' or 'w'
        # second character represents type of piece, 'K', 'Q', 'R', 'B', 'N', or 'p'
        # "--" represents empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = () # coordinates where en passant caputre is possible
        self.enpassantPossibleLog = [self.enpassantPossible] # keep track of enpassant rights for undoing moves
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    #
    # ...
    ##
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move
        self.whiteToMove = not self.whiteToMove # switch turns
        # update kings position (needed for checks)
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # en passant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # capturing the pawn
        
        # update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # moves the rook
                self.board[move.endRow][move.endCol+1] = '--'  # erase old rook
            else:  # queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # moves the rook
                self.board[move.endRow][move.endCol-2] = '--'  # erase old rook
        
        self.enpassantPossibleLog.append(self.enpassantPossible)

    #
    # ...
    ##
    def undoMove(self):
        if len(self.moveLog) != 0: # there should be a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update kings position (needed for checks)
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]
            
            # undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightsLog[-1]
            
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:  # queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False
        
        # if a rook is captured
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    #
    # All moves considering checks
    ##
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0] # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol] # enemy piece causing the check
                validSquares = [] # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # once you get to piece end checks
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1): # go trough backwards list for removing
                    if moves[i].pieceMoved[1] != 'K': # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares: # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: # not in check so all moves are fine
            moves = self.getAllPossibleMoves()
        
        # Check for checkmate or stalemate
        if len(moves) == 0:  # No valid moves
            if self.inCheck:
                self.checkmate = True  # Player is in checkmate
            else:
                self.stalemate = True  # Player is in stalemate

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    #
    # All moves
    ##
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): # number of rows
            for c in range(len(self.board[r])): # number of columns
                turn = self.board[r][c][0] # 'w', 'b' or '-'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # calls appropriate move function based on piece type
        return moves

    #
    # ...
    ##     
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            allyColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            allyColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = () # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == (): # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # five possibilities here in this complex conditional
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else: # enemy piece not applying check
                            break
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N': # enemy knight attacking king
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks
    
    #
    # Get all pawn moves for the pawn located at row, col and add these moves to the list
    ##
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        
        if self.board[r+moveAmount][c] == '--': # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r+moveAmount, c), self.board))
                if r == startRow and self.board[r+2 * moveAmount][c] == '--': # 2 square moves
                    moves.append(Move((r, c), (r+2 * moveAmount, c), self.board))
        if c-1 >= 0: # capture to left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c-1), self.board))
                # handling en passant
                if (r + moveAmount, c-1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of the pawn
                            # inside between king and pawn; outside range between pawn and border
                            insideRange = range(kingCol + 1, c-1)
                            outsideRange = range(c+1, 8)
                        else: # king is right of the pawn
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c-2, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != '--': # some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1]=='R' or square[1] == 'Q'): # if treath
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c-1), self.board, isEnpassantMove=True))
        if c+1 <= 7: # capture to right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    moves.append(Move((r, c), (r+moveAmount, c+1), self.board))
                # handling en passant
                if (r + moveAmount, c+1) == self.enpassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of the pawn
                            # inside between king and pawn; outside range between pawn and border
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c+2, 8)
                        else: # king is right of the pawn
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c-1, -1, -1)
                        for i in insideRange:
                            if self.board[r][i] != '--': # some other piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1]=='R' or square[1] == 'Q'): # if treath
                                attackingPiece = True
                            elif square != '--':
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r+moveAmount, c+1), self.board, isEnpassantMove=True))

    #
    # Get all rook moves for the rook located at row, col and add these moves to the list
    ##
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # can't remove queen from pin on rook moves, only remove it on bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (1,0), (0,-1), (0,1)) # up, down, left, right
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7: # has to be on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): # or opposite direction
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': # if empty we add to moves
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # if enemy we add to moves (it can take)
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break # here we break since it captured, turn of other player
                        else: # if it is friendly piece
                            break
                else: # if off board
                    break

    #
    # Get all knight moves for the knight located at row, col and add these moves to the list
    ##
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((-2,-1), (-2,1), (2,-1), (2,1), (-1,2), (-1,-2), (1,2), (1,-2)) # 8 different L movements
        allyColor = 'w' if self.whiteToMove else 'b'
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: # not an ally piece (empty or enemy piece)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    #
    # Get all bishop moves for the bishop located at row, col and add these moves to the list
    ##
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1), (-1,1), (1,1), (1,-1)) # left-up, right-up, right-down, left-down
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7: # has to be on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--': # if empty we add to moves
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor: # if enemy piece we add to moves and break 
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # friendly piece we break
                            break
                else: # off board -> break
                    break

    #
    # Get all queen moves for the queen located at row, col and add these moves to the list
    ##
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves) # mix of rook rules
        self.getBishopMoves(r, c, moves) # and bishop rules

    #
    # Get all king moves for the king located at row, col and add these moves to the list
    ##
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        originalKingLocation = (r, c)

        for i in range(8):  # check all 8 possible directions for the king
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:  # make sure the move is on the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # king can't capture its own piece
                    # Simulate the king's new position for the check
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)

                    # Check if the king is still in check after this move
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:  # If the move does not result in the king being in check
                        moves.append(Move((r, c), (endRow, endCol), self.board))

                    # Restore the king's original position
                    if allyColor == 'w':
                        self.whiteKingLocation = originalKingLocation
                    else:
                        self.blackKingLocation = originalKingLocation

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    def getFen(self):
        fen = ''
        for r in range(8):
            empty = 0
            for c in range(8):
                piece = self.board[r][c]
                if piece == '--':
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece[1].lower() if piece[0] == 'b' else piece[1]
            if empty > 0:
                fen += str(empty)
            if r < 7:
                fen += '/'
        fen += ' w ' if self.whiteToMove else ' b '
        fen += 'KQkq - 0 1'  # Simplified castling rights and move counters
        return fen

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

###   ###   ###
###    2    ###                     
###   ###   ###
                        
class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0,}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7,}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7): # if pawn made it to the end, it is promotion
            self.isPawnPromotion = True
        # en passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCapture = self.pieceCaptured != '--'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # hash?
        self.isCastleMove = isCastleMove

    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    # Overriding the str() function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "O-O" if self.endCol == 6 else "O-O-O"
        
        endSquare = self.getRankFile(self.endRow, self.endCol)

        # paw moves
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare

            # pawn promotion (implement later using ...)
        
        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += 'x'
        return moveString + endSquare
        
        
        # check (implement later using '*')

        # checkmate (implement later using '#')

        # two pieces of same type of piece can move to same square (implementing later using 'Nbd2')

        pass
        
        
