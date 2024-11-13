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

# Function to load the PGN and analyze the game
def analyze_game(pgn_file):
    global game_moves_info_cache

    if game_moves_info_cache: # check if analysis already done
        return game_moves_info_cache

    pgn = open(pgn_file)
    game = chess.pgn.read_game(pgn)

    engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
    board = game.board()
    game_moves_info = []

    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()
        analysis = engine.analyse(board, chess.engine.Limit(time=0.1, depth=20), multipv=3)
        
        score = analysis[0]['score'].white().score() / 100 if not analysis[0]['score'].white().is_mate() else f'M{analysis[0]["score"].white().mate()}'

        top_moves = []
        for i, an in enumerate(analysis):
            top_move = an["pv"][0]  # get the move with the highest score
            move_score = an["score"].white().score() / 100 if not an["score"].white().is_mate() else f'M{an["score"].white().mate()}' # white perspective
            top_moves.append({
                'Move': top_move.uci(),
                'Score': move_score
            })
        
        game_moves_info.append({
            'FEN': fen,
            'Score': score,
            'Top Moves': top_moves
        })

    engine.quit()
    game_moves_info_cache = game_moves_info
    return game_moves_info_cache

# Flask route to serve the game analysis
@app.route('/')
def index():
    return render_template('index.html') # rendering in html

# Flask route to analyse game info into json
@app.route('/analyze', methods=['POST'])
def analyze():
    global game_moves_info_cache
    file = request.files['pgn']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.filename.endswith('.pgn'):
        return jsonify({'error': 'Invalid file type, must be a PGN file'}), 400
    
    file.save('game.pgn') # save the uploaded pgn file

    game_moves_info_cache = []
    game_moves_info = analyze_game('game.pgn')
    for index, move_info in enumerate(game_moves_info):
        try:
            json_str = json.dumps(move_info)  # Try serializing each item individually
        except TypeError as e:
            print(f"Error serializing item at index {index}: {move_info}")
            print(f"Exception: {e}")
    return jsonify(game_moves_info)

# Flask route enabling naviagtion trough moves
@app.route('/get_board/<int:move_index>', methods=['GET'])
def get_board(move_index):
    if move_index < len(game_moves_info_cache):
        return jsonify(game_moves_info_cache[move_index])
    else:
        return jsonify({'error': 'Move index out of range'}), 404


if __name__ == '__main__':
    app.run(debug=True)