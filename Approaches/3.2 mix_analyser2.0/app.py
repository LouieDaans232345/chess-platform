import os
from flask import Flask, render_template, request, jsonify
import json
import chess
import chess.engine
import chess.pgn

class Mate:
    def __init__(self, move, position):
        self.move = move
        self.position = position

    def to_dict(self):
        return {"move": self.move, "position": self.position}

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Mate):
            return obj.to_dict()
        return super().default(obj)

app = Flask(__name__)
app.debug = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # disable caching for static files
app.json_encoder = CustomJSONEncoder

stockfish_path = "/usr/local/bin/stockfish"

game_moves_info_cache = []
current_game = None
free_moves_cache = []
branches_cache = [[]]

# Function to load the PGN and return the game object
def load_game(pgn_file):
    """
    Loads the PGN file and returns the game object.
    """
    pgn = open(pgn_file)
    game = chess.pgn.read_game(pgn)
    return game

# Function to analyze the current position on the board
def analyze_position(board):
    """
    Analyzes the current position on the board and returns the analysis.
    """
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    analysis = engine.analyse(board, chess.engine.Limit(time=0.1, depth=20), multipv=3)
    engine.quit()

    score = analysis[0]['score'].white().score() / 100 if not analysis[0]['score'].white().is_mate() else f'M{analysis[0]["score"].white().mate()}'

    top_moves = []
    for i, an in enumerate(analysis):
        top_move = an["pv"][0]  # get the move with the highest score
        move_score = an["score"].white().score() / 100 if not an["score"].white().is_mate() else f'M{an["score"].white().mate()}' # white perspective
        top_moves.append({
            'Move': top_move.uci(),
            'Score': move_score
        })

    return {
        'Score': score,
        'Top Moves': top_moves
    }

# Function to load the PGN and store game moves
def store_game_moves(game):
    board = game.board()
    game_moves_info_cache.clear()
    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()
        game_moves_info_cache.append({
            'FEN': fen
        })

# Flask route to serve the game analysis
@app.route('/')
def index():
    return render_template('index.html') # rendering in html

# Flask route to analyse game info into json
@app.route('/analyze', methods=['POST'])
def analyze():
    global current_game

    file = request.files['pgn']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.pgn'):
        return jsonify({'error': 'Invalid file type, must be a PGN file'}), 400
    
    file.save('game.pgn') # save the uploaded pgn file

    current_game = load_game('game.pgn')
    store_game_moves(current_game)
    return jsonify(game_moves_info_cache)

# Flask route enabling navigation through moves
@app.route('/get_board/<int:move_index>', methods=['GET'])
def get_board(move_index):
    if move_index < len(game_moves_info_cache):
        board = chess.Board(game_moves_info_cache[move_index]['FEN'])
        analysis = analyze_position(board)
        return jsonify({
            'FEN': game_moves_info_cache[move_index]['FEN'],
            'Score': analysis['Score'],
            'Top Moves': analysis['Top Moves']
        })
    else:
        return jsonify({'error': 'Move index out of range'}), 404

# Flask route to handle free moves
@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    fen = data.get('fen')
    branch_index = data.get('branch_index', 0)

    # Ensure the branch exists
    while len(branches_cache) <= branch_index:
        branches_cache.append([])

    # If a move is made from a position that is not the latest in the branch, create a new branch
    if len(branches_cache[branch_index]) != data.get('move_index', len(branches_cache[branch_index])):
        original_branch_index = data.get('branch_index', 0)
        move_index = data.get('move_index', len(branches_cache[original_branch_index]))
        branch_index = len(branches_cache)
        branches_cache.append(branches_cache[original_branch_index][:move_index])

    print(f"Branch Index: {branch_index}, Move Index: {len(branches_cache[branch_index])}")

    # Check if the position has already been evaluated in this branch
    for move in branches_cache[branch_index]:
        if move['FEN'] == fen:
            return jsonify(move)

    # Evaluate the new position
    board = chess.Board(fen)
    analysis = analyze_position(board)
    move_data = {
        'FEN': fen,
        'Score': analysis['Score'],
        'Top Moves': analysis['Top Moves']
    }
    branches_cache[branch_index].append(move_data)
    return jsonify(move_data)
 
if __name__ == '__main__':
    app.run(debug=True)