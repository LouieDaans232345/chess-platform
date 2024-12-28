import chess
import chess.pgn
import sys

def pgn_to_fen(pgn_file):
    with open(pgn_file) as f:
        game = chess.pgn.read_game(f)  # read the game from the PGN file
        if not game:
            print("No game found in PGN file.")
            return
        
        board = game.board()  # initialize board
        fen_positions = []  # list to store FEN strings

        for move in game.mainline_moves():  # iterate through the moves in the game
            fen_positions.append(board.fen())  # append the current FEN to the list
            board.push(move)  # make the move on the board

        fen_positions.append(board.fen())  # append the final position's FEN
        return fen_positions

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pgn_to_fen.py <pgn_file>")
        sys.exit(1)

    pgn_file = sys.argv[1]
    fen_list = pgn_to_fen(pgn_file)
    
    for fen in fen_list:
        print(fen)  # Print each FEN string