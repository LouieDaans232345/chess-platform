import chess
import chess.engine

### (1) BEST MOVE EXAMPLE
# Yes, Stockfish can provide numerical evaluations for positions and suggest best moves.
# You can interact with Stockfish using the Universal Chess Interface (UCI) protocol.
# Here's a basic example using the Python-Chess library:

def analyze_position(fen, depth=20):
    engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")
    board = chess.Board(fen)
    
    result = engine.analyse(board, chess.engine.Limit(depth=depth))
    
    score = result["score"].relative.score(mate_score=100000)
    best_move = result["pv"][0]
    
    engine.quit()
    return score, best_move

# Usage
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"  # Starting position
score, best_move = analyze_position(fen)
print(f"Evaluation: {score/100}")  # Convert centipawns to pawns
print(f"Best move: {best_move}")

### (2) MOVE CLASSIFICATION EXAMPLE
# Stockfish itself doesn't provide a built-in classification system for moves (e.g., blunder, mistake, inaccuracy).
# However, you can implement this yourself based on the change in evaluation before and after a move. Here's a simple example:

def classify_move(eval_before, eval_after):
    diff = eval_after - eval_before
    if diff < -0.7:
        return "Blunder"
    elif diff < -0.5:
        return "Mistake"
    elif diff < -0.2:
        return "Inaccuracy"
    elif diff > 0.5:
        return "Excellent move"
    elif diff > 0.2:
        return "Good move"
    else:
        return "Normal move"

# Usage (continuing from the previous example)
eval_before = analyze_position(fen)[0]
board = chess.Board(fen)
board.push(best_move)
eval_after = analyze_position(board.fen())[0]

move_quality = classify_move(eval_before, eval_after)
print(f"Move quality: {move_quality}")

# (3) PATTERN RECOGNITION EXAMPLE
# Stockfish doesn't have a built-in system for recognizing common chess patterns, tactics, or strategic themes that you can directly access in your code.
# Stockfish is primarily an evaluation and move-searching engine.
# To implement pattern recognition, you would need to develop this system separately. This could involve:

# 1. Creating a database of common patterns and their descriptions
# 2. Implementing algorithms to detect these patterns on the board
# 3. Possibly using machine learning models trained on large datasets of chess games

# Here's a very basic example of how you might start implementing pattern recognition:

def recognize_patterns(board):
    patterns = []
    
    # Check for doubled pawns
    for file in range(8):
        pawns = [i for i in range(8, 56, 8) if board.piece_at(i + file) == chess.Piece(chess.PAWN, chess.WHITE)]
        if len(pawns) > 1:
            patterns.append("White has doubled pawns")
    
    # Check for open files
    for file in range(8):
        if all(board.piece_at(i + file) is None or board.piece_at(i + file).piece_type != chess.PAWN for i in range(8, 56, 8)):
            patterns.append(f"Open file on {chess.FILE_NAMES[file]}")
    
    # Add more pattern checks here...
    
    return patterns

# Usage
board = chess.Board(fen)
patterns = recognize_patterns(board)
for pattern in patterns:
    print(pattern)