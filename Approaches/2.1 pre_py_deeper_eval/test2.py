import chess
import chess.engine
import chess.pgn

pgn = open("mominalix_vs_rogeriosmunhoz_2024.06.29.pgn")
game = chess.pgn.read_game(pgn)

engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")

board = game.board()
game_moves_info = {}
for move in game.mainline_moves():
    board.push(move)
    fen = board.fen()
    analysis = engine.analyse(board, chess.engine.Limit(time=10.0, depth=20), multipv=3)
    
    if analysis[0]["score"].white().is_mate():
        score = analysis[0]['score'].white()
    else:
        cp = analysis[0]["score"].white().score()
        score = f"{cp / 100:.2f}"

    top_moves = {}
    for i, an in enumerate(analysis):
        top_move = an["pv"][0]  # get the move with the highest score
        move_score = an["score"].white().score() # white perspective

        if an["score"].white().is_mate():
            move_score_str = an["score"].white()
        else:
            move_score_str = f"{move_score / 100:.2f}"

        top_moves[f"Move{i + 1}"] = {
            "Move": top_move.uci(),
            "Score": f"{move_score_str}"
        }
    
    game_moves_info[fen] = {
        "Score": score,
        "Top Moves": top_moves
    }

    print(f"FEN: {fen}, Score: {score}, Best Moves: {top_moves}")

engine.quit()