import chess
import chess.engine
import chess.pgn

pgn = open("mominalix_vs_rogeriosmunhoz_2024.06.29.pgn")
game = chess.pgn.read_game(pgn)

engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")

board = game.board()
score_list = []
for move in game.mainline_moves():
    board.push(move)
    fen = board.fen()
    analysis = engine.analyse(board, chess.engine.Limit(time=10.0, depth=20))["score"].white() # white perspective
    analysis2 = engine.analyse(board, chess.engine.Limit(time=10.0, depth=20), multipv=3)
    for i, an2 in enumerate(analysis2):
        top_move = an2["pv"][0]  # Get the move with the highest score
        score = an2["score"].relative.score()
        
        if score is None:
            score_str = "0.00"  # Draw situation or unclear evaluation
        elif score > 0:
            score_str = f"{score / 100:.2f}"  # Positive score (advantage for white)
        else:
            score_str = f"{score / 100:.2f}"  # Negative score (advantage for black)

        print(f"  {i + 1}. Move: {top_move} with Score: {score_str}")

    score_list.append((fen, [an2["pv"][0] for an2 in analysis2]))
    
    if analysis.is_mate():
        score = f"Mate in {analysis}"
    else:
        cp = analysis.score()
        score = f"{cp / 100:.2f}" if cp else 0.00
    
    print(f"FEN: {fen}, Score: {score}")
    score_list.append(score)

engine.quit()
print(score_list)
