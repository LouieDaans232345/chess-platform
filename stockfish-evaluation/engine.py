import chess.engine


class ChessEngine:
    def __init__(self, stockfish_path):
        # Initialize the chess engine with the given stockfish path
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

    def analyze(self, board, num_moves_to_return=1, depth_limit=None, time_limit=None):
        # Analyze the given board state and return the best moves
        info_list = self.engine.analyse(board, chess.engine.Limit(depth=depth_limit, time=time_limit), multipv=num_moves_to_return)
        
        # Prepare the results
        results = []
        for info in info_list:
            result = {
                "score": info["score"].relative.score(mate_score=10000),  # get the score of the position
                "pv": info.get("pv"),  # get the principal variation (best moves)
                "mate_score": info["score"].relative.mate() if info["score"].relative.is_mate() else None,  # get the mate score if applicable
            }
            results.append(result)

        return results  # Return the list of results

    def quit(self):
        # Quit the chess engine
        self.engine.quit()