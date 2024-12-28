# Required imports for the application
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import chess  # python-chess library for chess logic
import chess.engine  # For Stockfish integration
import chess.pgn  # For PGN file parsing
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import io  # For reading PGN data
import logging
from datetime import datetime, timedelta

# Configure logging for debugging and error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Data class to structure move analysis results
@dataclass
class MoveAnalysis:
    """
    Represents the analysis of a single chess position
    score: Stockfish evaluation score
    best_moves: List of best moves found by Stockfish
    depth: Depth of analysis
    """
    score: float
    best_moves: List[str]
    depth: int

# Data class to structure move information
@dataclass
class MoveInfo:
    """
    Represents information about a chess move
    from_square: Starting square (0-63)
    to_square: Target square (0-63)
    promotion: Piece type if promotion move
    san: Standard Algebraic Notation of the move
    uci: Universal Chess Interface notation
    """
    from_square: int
    to_square: int
    promotion: Optional[str]
    san: str
    uci: str

# Data class to represent a position in the game
@dataclass
class Position:
    """
    Represents a complete position in the chess game
    fen: FEN string representation of the position
    move: Information about the move that led to this position
    analysis: Stockfish analysis of the position
    """
    fen: str
    move: Optional[MoveInfo]
    analysis: MoveAnalysis

# Class to handle chess analysis operations
class ChessAnalyzer:
    """
    Handles chess position analysis using Stockfish engine
    Manages engine lifecycle and provides analysis methods
    """
    def __init__(self, engine_path: str = '/usr/local/bin/stockfish'):
        """Initialize with path to Stockfish engine"""
        self.engine_path = engine_path
        self.engine = None

    def __enter__(self):
        """Context manager entry: starts the Stockfish engine"""
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: ensures engine is properly closed"""
        if self.engine:
            self.engine.quit()

    def analyze_position(self, board: chess.Board, depth: int = 20) -> MoveAnalysis:
        """
        Analyzes a chess position using Stockfish
        
        Args:
            board: Chess position to analyze
            depth: How deep to search for best moves
            
        Returns:
            MoveAnalysis with score and best moves
        """
        # Get engine analysis
        info = self.engine.analyse(board, chess.engine.Limit(time=1,depth=depth))
        
        # Extract score
        score = info["score"].white().score(mate_score=10000)
        if score is not None:
            score = score / 100  # Convert centipawns to pawns
        
        # Get best moves
        pv = info.get("pv", [])
        best_moves = []
        
        # Convert moves to SAN notation
        temp_board = board.copy()
        for move in pv[:3]:  # Get top 3 moves
            best_moves.append(temp_board.san(move))
            temp_board.push(move)
            
        return MoveAnalysis(score=score, best_moves=best_moves, depth=depth)

# Route to serve the main page
@app.route('/')
def index():
    """Renders the main application page"""
    return render_template('index.html')

# Route to analyze uploaded PGN files
@app.route('/analyze', methods=['POST'])
def analyze_game():
    """
    Loads a PGN game without analyzing all positions
    
    Expects:
        POST request with PGN file content
        
    Returns:
        JSON with game moves
    """
    try:
        # Get PGN content from request
        pgn_content = request.files['pgn'].read().decode('utf-8')
        
        # Parse PGN game
        pgn = chess.pgn.read_game(io.StringIO(pgn_content))
        if not pgn:
            return jsonify({'error': 'Invalid PGN file'}), 400
            
        # Initialize results
        positions = []
        board = chess.Board()
        
        # Add initial position
        positions.append({
            'fen': board.fen(),
            'move': None
        })
            
        # Add each move without analysis
        for move in pgn.mainline_moves():
            # Get move information before making it
            move_info = {
                'from': move.from_square,
                'to': move.to_square,
                'promotion': move.promotion,
                'san': board.san(move),
                'uci': move.uci()
            }
            
            # Make the move
            board.push(move)
            
            # Store position
            positions.append({
                'fen': board.fen(),
                'move': move_info
            })
        
        return jsonify(positions)
        
    except Exception as e:
        logger.error(f"Error analyzing game: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route to analyze a single position
@app.route('/analyze_position', methods=['POST'])
def analyze_position():
    """
    Analyzes a single chess position
    
    Expects:
        POST request with FEN string
        
    Returns:
        JSON with position analysis
    """
    try:
        # Get FEN from request
        data = request.get_json()
        if not data or 'fen' not in data:
            return jsonify({'error': 'FEN string required'}), 400
            
        # Create board from FEN
        board = chess.Board(data['fen'])
        
        # Analyze position
        with ChessAnalyzer() as analyzer:
            analysis = analyzer.analyze_position(board)
            
            return jsonify({
                'fen': board.fen(),
                'analysis': {
                    'score': analysis.score,
                    'best_moves': analysis.best_moves,
                    'depth': analysis.depth
                }
            })
            
    except Exception as e:
        logger.error(f"Error analyzing position: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route to serve static files with caching
@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    Serves static files with proper caching headers
    Caches images for 1 hour to prevent flickering
    """
    response = send_from_directory('static', filename)
    # Cache images for 1 hour
    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
        response.cache_control.max_age = 3600
        response.cache_control.public = True
        response.headers['Expires'] = (datetime.utcnow() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

# Run the application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)