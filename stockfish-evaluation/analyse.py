import chess
import chess.engine
import json
import os

# Importing Stockfish as our engine
engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")
EVALUATION_FILE = "evaluations.json"  # file to store evaluations

def load_evaluations():
    """Load evaluations from the JSON file."""
    if os.path.exists(EVALUATION_FILE):
        with open(EVALUATION_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_evaluation(fen, evaluation):
    """Save the evaluation for a given FEN to the JSON file."""
    evaluations = load_evaluations()
    evaluations[fen] = evaluation
    with open(EVALUATION_FILE, 'w') as f:
        json.dump(evaluations, f)

def analyze_position(fen, num_moves_to_return=1, depth_limit=None, time_limit=None):
    evaluations = load_evaluations()  # load existing evaluations
    if fen in evaluations:  # check if the FEN has already been evaluated
        print(f"Using cached evaluation for FEN: {fen}")
        return evaluations[fen]  # return the cached evaluation

    search_limit = chess.engine.Limit(depth=depth_limit, time=time_limit)
    board = chess.Board(fen)
    infos = engine.analyse(board, search_limit, multipv=num_moves_to_return)
    results = [format_info(info) for info in infos]

    # Save the new evaluation
    save_evaluation(fen, results)
    return results

def format_info(info):
    # Normalize by always looking from White's perspective
    score = info["score"].white()
    
    # Split up the score into a mate score and a centipawn score
    mate_score = score.mate()
    centipawn_score = score.score()
    return {
        "mate_score": mate_score,
        "centipawn_score": centipawn_score,
        "pv": format_moves(info["pv"]),
    }

# Convert the move class to a standard string 
def format_moves(pv):
    return [move.uci() for move in pv]

# Example usage
if __name__ == "__main__":
    results = analyze_position("8/8/6P1/4R3/8/6k1/2r5/6K1 b - - 0 1", num_moves_to_return=3, depth_limit=20)
    for move in results:
        print()
        print(move)