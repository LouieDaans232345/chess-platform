import chess
import chess.svg
import chess.pgn
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cairosvg
import io
from stockfish import Stockfish
from datetime import datetime

class ChessGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Human vs Human Chess")
        self.master.geometry("900x600")
        self.master.configure(bg='#2c3e50')

        self.board = chess.Board()
        self.stockfish = Stockfish(path="/usr/local/bin/stockfish")
        self.stockfish.set_depth(10)  # Limit search depth
        
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.master, bg='#2c3e50')
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Board and evaluation bar frame
        board_eval_frame = tk.Frame(main_frame, bg='#2c3e50')
        board_eval_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Chess board
        self.board_svg = tk.Canvas(board_eval_frame, bg='#2c3e50', highlightthickness=0)
        self.board_svg.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.board_svg.bind("<Button-1>", self.on_square_click)

        # Evaluation bar
        self.eval_frame = tk.Frame(board_eval_frame, width=40, bg='#2c3e50')
        self.eval_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.eval_canvas = tk.Canvas(self.eval_frame, width=40, height=600, bg='#34495e', highlightthickness=0)
        self.eval_canvas.pack(expand=True, fill=tk.BOTH)

        # Right frame for move list and buttons
        right_frame = tk.Frame(main_frame, bg='#2c3e50')
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.move_list = tk.Listbox(right_frame, bg='#34495e', fg='white')
        self.move_list.pack(expand=True, fill=tk.BOTH)

        self.status_label = tk.Label(right_frame, text="White to move", bg='#2c3e50', fg='white')
        self.status_label.pack(pady=10)

        button_frame = tk.Frame(right_frame, bg='#2c3e50')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="White Resigns", command=lambda: self.resign("White")).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Black Resigns", command=lambda: self.resign("Black")).pack(side=tk.LEFT, padx=5)

        self.selected_square = None

    def update_display(self):
        board_svg = chess.svg.board(self.board, size=600)
        png_data = cairosvg.svg2png(bytestring=board_svg.encode('utf-8'))
        img = Image.open(io.BytesIO(png_data))
        self.photo = ImageTk.PhotoImage(img)
        self.board_svg.delete("all")
        self.board_svg.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.update_eval_bar()

        if self.board.is_game_over():
            self.show_game_over()
        else:
            self.status_label.config(text=f"{'White' if self.board.turn else 'Black'} to move")

    def update_eval_bar(self):
        self.eval_canvas.delete("all")
        self.stockfish.set_fen_position(self.board.fen())
        evaluation = self.stockfish.get_evaluation()

        if evaluation['type'] == 'cp':
            # Convert centipawns to a value between 0 and 1
            normalized_eval = 1 / (1 + 10**(-evaluation['value'] / 400))
        elif evaluation['type'] == 'mate':
            normalized_eval = 1 if evaluation['value'] > 0 else 0
        else:
            normalized_eval = 0.5  # Default to draw

        bar_height = int(600 * normalized_eval)
        
        # Draw the evaluation bar
        self.eval_canvas.create_rectangle(0, 0, 40, 600, fill='#34495e')  # Background
        self.eval_canvas.create_rectangle(0, 600 - bar_height, 40, 600, fill='white')  # White's advantage
        self.eval_canvas.create_rectangle(0, 0, 40, 600 - bar_height, fill='black')  # Black's advantage
        
        # Display the evaluation text
        text_color = 'black' if normalized_eval > 0.5 else 'white'
        if evaluation['type'] == 'cp':
            eval_text = f"{evaluation['value']/100:.2f}"
        else:
            eval_text = f"M{abs(evaluation['value'])}"
        self.eval_canvas.create_text(20, 300, text=eval_text, angle=90, fill=text_color, font=('Arial', 10, 'bold'))

    def on_square_click(self, event):
        if self.board.is_game_over():
            return

        x, y = event.x, event.y
        square = (7 - y // 75) * 8 + (x // 75)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.make_move(move)
            self.selected_square = None

        self.update_display()

    def make_move(self, move):
        san_move = self.board.san(move)
        self.board.push(move)
        if self.board.turn == chess.WHITE:
            self.move_list.insert(tk.END, f"{self.board.fullmove_number}. {san_move}")
        else:
            last_move = self.move_list.get(tk.END)
            self.move_list.delete(tk.END)
            self.move_list.insert(tk.END, f"{last_move} {san_move}")
        self.update_display()

    def new_game(self):
        self.board = chess.Board()
        self.move_list.delete(0, tk.END)
        self.update_display()

    def resign(self, color):
        if messagebox.askyesno("Resign", f"Are you sure {color} wants to resign?"):
            self.board.outcome(claim_draw=False)
            self.show_game_over(f"{color} resigned")

    def show_game_over(self, custom_message=None):
        if custom_message:
            message = custom_message
        else:
            result = self.board.result()
            if result == "1-0":
                message = "White wins!"
            elif result == "0-1":
                message = "Black wins!"
            else:
                message = "It's a draw!"
        
        self.status_label.config(text=f"Game Over: {message}")
        self.save_game()

    def save_game(self):
        game = chess.pgn.Game.from_board(self.board)
        game.headers["Event"] = "Human vs Human"
        game.headers["Site"] = "Local Computer"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "Human"
        game.headers["Black"] = "Human"
        
        filename = f"human_vs_human_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        with open(filename, "w") as pgn_file:
            pgn_file.write(str(game))
        
        messagebox.showinfo("Game Saved", f"Game has been saved to {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
