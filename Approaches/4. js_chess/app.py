import os
from flask import Flask, render_template, request, jsonify
import json
import chess
import chess.engine
import chess.pgn

engine = chess.engine.SimpleEngine.popen_uci("stockfish")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/make_move', methods=['POST'])
def make_move():
    # extract the FEN from the request, so from the JS board state
    fen = request.form.get('fen')

    # mirrors board actions
    board = chess.Board(fen)

    # find best move
    result = engine.play(board, chess.engine.Limit(time=1.0))

    # update internal chess board state
    board.push(result.move)
    
    # extract the FEN from current PY board state, so that it can be used to update the JS board
    fen = board.fen()

    return {'fen': fen, 'best_move': str(result.move)}


@app.route('/get_top_moves', methods=['POST'])
def get_top_moves():
    # extract the FEN from the request, so from the JS board state
    fen = request.form.get('fen')

    # mirrors board actions
    board = chess.Board(fen)

    # analyze the next position for the 3 best moves
    info = engine.analyse(board, chess.engine.Limit(time=1.0), multipv=3)
    top_moves = [
        {
            'move': str(entry["pv"][0]),
            'score': entry["score"].white().score(mate_score=10000)  # Handle mate scores
        }
        for entry in info
    ]
    print(top_moves)

    # extract the FEN from current PY board state, so that it can be used to update the JS board
    fen = board.fen()

    return {'fen': fen, 'top_moves': top_moves}



if __name__ == '__main__':
    app.run(debug=True, threaded=True)