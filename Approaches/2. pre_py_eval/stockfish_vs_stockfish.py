import chess
import chess.svg
import chess.pgn
import tkinter as tk
from PIL import Image, ImageTk
import cairosvg
import io
from stockfish import Stockfish
from datetime import datetime
import random

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Stockfish vs Stockfish Chess Game")
        self.master.configure(bg='#2c3e50')  # Dark blue background
        
        # Initialize the chess board
        self.board = chess.Board()
        
        # Initialize Stockfish for both players
        self.stockfish_white = Stockfish(path="/usr/local/bin/stockfish")
        self.stockfish_black = Stockfish(path="/usr/local/bin/stockfish")

        self.stockfish_white.set_skill_level(random.randint(10, 20))  # Random skill level for white
        self.stockfish_black.set_skill_level(random.randint(10, 20))  # Random skill level for black
        
        # Create the chess board display
        self.board_display = tk.Label(self.master, bg='#2c3e50')
        self.board_display.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Create the evaluation bar
        self.eval_frame = tk.Frame(self.master, width=40, height=400, bg='#2c3e50')
        self.eval_frame.pack(side=tk.LEFT, padx=10)
        self.eval_canvas = tk.Canvas(self.eval_frame, width=40, height=400, bg='#34495e', highlightthickness=0)
        self.eval_canvas.pack()
        
        # Update the display
        self.update_display()
        
        # Start the game
        self.master.after(1000, self.play_game)

    def update_display(self):
        # Generate SVG of the current board state with custom colors
        svg = chess.svg.board(
            self.board,
            size=400,
            colors={'square light': '#f0d9b5', 'square dark': '#b58863'}
        )
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
        
        # Create a PhotoImage from the PNG data
        image = Image.open(io.BytesIO(png_data))
        photo = ImageTk.PhotoImage(image)
        
        # Update the label with the new image
        self.board_display.config(image=photo)
        self.board_display.image = photo

    def update_eval_bar(self, evaluation):
        self.eval_canvas.delete("all")
        if evaluation is not None:
            # Convert centipawns to a value between 0 and 1
            normalized_eval = 1 / (1 + 10**(-evaluation / 400))
            bar_height = int(400 * normalized_eval)
            
            # Draw the evaluation bar
            self.eval_canvas.create_rectangle(0, 0, 40, 400, fill='#34495e')  # Background
            self.eval_canvas.create_rectangle(0, 400 - bar_height, 40, 400, fill='white')  # White's advantage
            self.eval_canvas.create_rectangle(0, 0, 40, 400 - bar_height, fill='black')  # Black's advantage
            
            # Display the evaluation text
            text_color = 'black' if normalized_eval > 0.5 else 'white'
            self.eval_canvas.create_text(20, 200, text=f"{evaluation/100:.2f}", angle=90, fill=text_color, font=('Arial', 10, 'bold'))

    def play_game(self):
        if not self.board.is_game_over():
            self.make_next_move()
            self.master.after(500, self.play_game)  # Schedule the next move
        else:
            self.game_over()

    def make_next_move(self):
        if self.board.turn == chess.WHITE:
            stockfish = self.stockfish_white
        else:
            stockfish = self.stockfish_black
        
        stockfish.set_fen_position(self.board.fen())
        evaluation = stockfish.get_evaluation()['value']
        self.update_eval_bar(evaluation)
        
        best_move = stockfish.get_best_move()
        self.board.push(chess.Move.from_uci(best_move))
        self.update_display()

    def game_over(self):
        result = self.board.result()
        if result == "1-0":
            message = "White (Stockfish) wins!"
        elif result == "0-1":
            message = "Black (Stockfish) wins!"
        else:
            message = "It's a draw!"
        print(message)
        
        # Save the game to a PGN file
        self.save_game_to_pgn()
        
        self.master.after(2000, self.master.quit)  # Close the window after 2 seconds

    def save_game_to_pgn(self):
        game = chess.pgn.Game()
        game.headers["Event"] = "Stockfish vs Stockfish"
        game.headers["Site"] = "Local Computer"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["White"] = "Stockfish"
        game.headers["Black"] = "Stockfish"
        game.headers["Result"] = self.board.result()

        # Reconstruct the game from the final position
        node = game.add_variation(self.board.move_stack[0])
        for move in self.board.move_stack[1:]:
            node = node.add_variation(move)

        # Save to file
        filename = f"stockfish_vs_stockfish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        with open(filename, "w") as pgn_file:
            pgn_file.write(str(game))
        
        print(f"Game saved to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
