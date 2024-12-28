import chess
import chess.pgn
import chess.engine
import chess.svg
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cairosvg
import io

class ChessAnalyzer:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game Analyzer")
        self.master.geometry("1200x600")
        self.master.configure(bg='#2c3e50')
        
        # Make the window resizable
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

        self.board = chess.Board()
        self.game = None
        self.current_node = None
        self.engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")
        self.eval_cache = {}  # Cache for evaluations

        self.create_widgets()

    def create_widgets(self):
        # Board and evaluation bar frame
        board_eval_frame = tk.Frame(self.master, bg='#2c3e50')
        board_eval_frame.grid(row=0, column=0, rowspan=2, padx=20, pady=20, sticky="nsew")

        # Board display
        self.board_frame = tk.Frame(board_eval_frame, bg='#2c3e50')
        self.board_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.board_display = tk.Label(self.board_frame, bg='#2c3e50')
        self.board_display.pack(expand=True, fill=tk.BOTH)

        # Evaluation bar
        self.eval_frame = tk.Frame(board_eval_frame, width=40, bg='#2c3e50')
        self.eval_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.eval_canvas = tk.Canvas(self.eval_frame, width=40, height=400, bg='#34495e', highlightthickness=0)
        self.eval_canvas.pack(expand=True, fill=tk.BOTH)

        # Move list and Analysis in a PanedWindow
        self.paned_window = ttk.PanedWindow(self.master, orient=tk.VERTICAL)
        self.paned_window.grid(row=0, column=1, rowspan=2, padx=20, pady=20, sticky="nsew")

        # Move list
        move_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(move_frame, weight=1)

        self.move_list = ttk.Treeview(move_frame, columns=("White", "Black"), show="headings")
        self.move_list.heading("White", text="White")
        self.move_list.heading("Black", text="Black")
        self.move_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(move_frame, orient=tk.VERTICAL, command=self.move_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.move_list.configure(yscrollcommand=scrollbar.set)

        self.move_list.bind("<<TreeviewSelect>>", self.on_move_select)

        # Analysis display
        analysis_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(analysis_frame, weight=1)

        self.analysis_text = tk.Text(analysis_frame, wrap=tk.WORD, bg='#34495e', fg='white')
        self.analysis_text.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        button_frame = tk.Frame(self.master, bg='#2c3e50')
        button_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Button(button_frame, text="Load PGN", command=self.load_pgn).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Previous", command=self.previous_move).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Next", command=self.next_move).pack(side=tk.LEFT, padx=5)

    def load_pgn(self):
        file_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn")])
        if file_path:
            with open(file_path) as pgn_file:
                self.game = chess.pgn.read_game(pgn_file)
            self.current_node = self.game
            self.board = self.game.board()
            self.eval_cache = {}  # Clear the evaluation cache
            self.calculate_all_evaluations()  # Pre-calculate evaluations for all positions
            self.update_display()
            self.populate_move_list()

    def calculate_all_evaluations(self):
        node = self.game
        while not node.is_end():
            fen = node.board().fen()
            if fen not in self.eval_cache:
                result = self.engine.analyse(node.board(), chess.engine.Limit(depth=20))
                score = result["score"].relative.score(mate_score=100000)
                self.eval_cache[fen] = score
            node = node.next()

    def update_display(self):
        # Update board display
        svg = chess.svg.board(self.board, size=400)
        png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
        image = Image.open(io.BytesIO(png_data))
        photo = ImageTk.PhotoImage(image)
        self.board_display.config(image=photo)
        self.board_display.image = photo

        # Update evaluation bar
        self.update_eval_bar()

        # Update analysis
        self.update_analysis()

    def update_eval_bar(self):
        self.eval_canvas.delete("all")
        fen = self.board.fen()
        
        if fen in self.eval_cache:
            score = self.eval_cache[fen]
        else:
            result = self.engine.analyse(self.board, chess.engine.Limit(depth=20))
            score = result["score"].relative.score(mate_score=100000)
            self.eval_cache[fen] = score

        if score is not None:
            # Convert score to a value between 0 and 1
            normalized_score = 1 / (1 + 10**(-score / 400))
        else:
            normalized_score = 0.5  # Default to draw

        bar_height = int(400 * normalized_score)
        
        # Draw the evaluation bar
        self.eval_canvas.create_rectangle(0, 0, 40, 400, fill='#34495e')  # Background
        self.eval_canvas.create_rectangle(0, 400 - bar_height, 40, 400, fill='white')  # White's advantage
        self.eval_canvas.create_rectangle(0, 0, 40, 400 - bar_height, fill='black')  # Black's advantage
        
        # Display the evaluation text
        text_color = 'black' if normalized_score > 0.5 else 'white'
        eval_text = f"{score/100:.2f}" if score is not None else "0.00"
        self.eval_canvas.create_text(20, 200, text=eval_text, angle=90, fill=text_color, font=('Arial', 10, 'bold'))

    def update_analysis(self):
        if self.current_node.parent:
            move = self.current_node.move
            fen = self.current_node.board().fen()
            prev_fen = self.current_node.parent.board().fen()
            
            score = self.eval_cache.get(fen)
            prev_score = self.eval_cache.get(prev_fen)
            
            if score is None:
                result = self.engine.analyse(self.current_node.board(), chess.engine.Limit(depth=20))
                score = result["score"].relative.score(mate_score=100000)
                self.eval_cache[fen] = score
            
            if prev_score is None:
                result = self.engine.analyse(self.current_node.parent.board(), chess.engine.Limit(depth=20))
                prev_score = result["score"].relative.score(mate_score=100000)
                self.eval_cache[prev_fen] = prev_score
            
            move_quality = self.classify_move(prev_score, score)
            patterns = self.recognize_patterns(self.board)

            analysis = f"Move: {self.current_node.parent.board().san(move)}\n"
            analysis += f"Evaluation: {score/100:.2f}\n"
            analysis += f"Move quality: {move_quality}\n"
            if patterns:
                analysis += "Patterns recognized:\n"
                for pattern in patterns:
                    analysis += f"- {pattern}\n"

            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, analysis)

    def populate_move_list(self):
        self.move_list.delete(*self.move_list.get_children())
        node = self.game
        move_num = 1
        current_row = ""
        while not node.is_end():
            node = node.next()
            if node.turn() == chess.BLACK:
                current_row = self.move_list.insert("", "end", values=(f"{move_num}. {node.parent.board().san(node.move)}", ""))
            else:
                if current_row:
                    self.move_list.set(current_row, "Black", node.parent.board().san(node.move))
                else:
                    self.move_list.insert("", "end", values=(f"{move_num}. ...", node.parent.board().san(node.move)))
                move_num += 1
                current_row = ""

    def on_move_select(self, event):
        selected_items = self.move_list.selection()
        if selected_items:
            selected_item = selected_items[0]
            move_num = self.move_list.index(selected_item)
            self.current_node = self.game
            self.board = self.game.board()
            for _ in range(move_num * 2 + 1):
                if not self.current_node.is_end():
                    self.current_node = self.current_node.next()
                    self.board.push(self.current_node.move)
            self.update_display()

    def previous_move(self):
        if self.current_node.parent:
            self.current_node = self.current_node.parent
            self.board.pop()
            self.update_display()

    def next_move(self):
        if not self.current_node.is_end():
            self.current_node = self.current_node.next()
            self.board.push(self.current_node.move)
            self.update_display()

    def classify_move(self, eval_before, eval_after):
        diff = eval_after - eval_before
        diff_pawns = diff / 100

        if diff_pawns <= -1.5:
            return "Blunder"
        elif diff_pawns <= -0.8:
            return "Mistake"
        elif diff_pawns <= -0.3:
            return "Inaccuracy"
        elif diff_pawns >= 1.0:
            return "Excellent move"
        elif diff_pawns >= 0.5:
            return "Good move"
        else:
            return "Normal move"

    def recognize_patterns(self, board):
        patterns = []
        
        # Check for doubled pawns
        for color in [chess.WHITE, chess.BLACK]:
            for file in range(8):
                pawns = [i for i in range(8, 56, 8) if board.piece_at(i + file) == chess.Piece(chess.PAWN, color)]
                if len(pawns) > 1:
                    patterns.append(f"{'White' if color == chess.WHITE else 'Black'} has doubled pawns on file {chess.FILE_NAMES[file]}")
        
        # Check for open files
        for file in range(8):
            if all(board.piece_at(i + file) is None or board.piece_at(i + file).piece_type != chess.PAWN for i in range(8, 56, 8)):
                patterns.append(f"Open file on {chess.FILE_NAMES[file]}")
        
        # Check for isolated pawns
        for color in [chess.WHITE, chess.BLACK]:
            for file in range(8):
                if any(board.piece_at(i + file) == chess.Piece(chess.PAWN, color) for i in range(8, 56, 8)):
                    adjacent_files = [f for f in [file-1, file+1] if 0 <= f < 8]
                    if all(board.piece_at(i + f) != chess.Piece(chess.PAWN, color) for f in adjacent_files for i in range(8, 56, 8)):
                        patterns.append(f"{'White' if color == chess.WHITE else 'Black'} has an isolated pawn on file {chess.FILE_NAMES[file]}")
        
        return patterns

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessAnalyzer(root)
    root.mainloop()