import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import chess
import chess.pgn
from PIL import Image, ImageTk

from engine import ChessEngine
from movelog import MoveLog
from navigation import Navigation
from analyse import load_evaluations, save_evaluation


class ChessAnalyserApp:
    DEPTH_LIMIT = 20  # 20
    TIME_LIMIT = 1   # time limit 1

    def __init__(self, root):
        self.root = root
        self.root.title("Chess Analyser Test")

        self.engine = ChessEngine("/usr/local/bin/stockfish")
        self.board = chess.Board()
        self.selected_square = None
        self.piece_images = self.load_piece_images()
        self.move_stack = []
        self.fen_positions = []  # List to store FEN strings
        self.setup_gui()
        self.cumulative_score = 0
        
    def setup_gui(self):
        self.frame = tk.Frame(self.root)  # create a frame to hold all GUI elements
        self.frame.pack(padx=10, pady=10)  # add padding around the frame for aesthetics

        self.board_canvas = tk.Canvas(self.frame, width=400, height=400)  # create a canvas for the chess board
        self.board_canvas.grid(row=0, column=1, rowspan=8, padx=5)  # position the board canvas in the grid

        self.analysis_area = scrolledtext.ScrolledText(self.frame, width=50, height=20)  # create a text area for analysis output
        self.analysis_area.grid(row=0, column=2, rowspan=8, padx=10, pady=5)  # position the analysis area in the grid

        self.analysis_bar = tk.Canvas(self.frame, width=20, height=400, bg="#FFFFFF")  # create a vertical analysis bar
        self.analysis_bar.grid(row=0, column=0, rowspan=8, padx=5)  # position the analysis bar in the grid

        self.load_pgn_button = tk.Button(
            self.frame, text="Load PGN", command=self.load_pgn
        )  # button to load PGN files
        self.load_pgn_button.grid(row=8, column=1, columnspan=2, pady=5)  # position the load button in the grid

        self.reset_board_button = tk.Button(
            self.frame, text="Reset Board", command=self.reset_board
        )  # button to reset the chess board
        self.reset_board_button.grid(row=8, column=3, columnspan=2, pady=5)  # position the reset button in the grid

        self.board_canvas.bind("<Button-1>", self.on_board_click)  # bind mouse click event to the board canvas

        self.navigation = Navigation(self.frame, self.next_move, self.prev_move)  # create navigation buttons for moves
        self.navigation.frame.grid(row=9, column=1, columnspan=4, pady=5)  # position the navigation frame in the grid

        self.move_history = MoveLog(self.frame)  # create a move log to display move history
        self.move_history.frame.grid(row=0, column=3, rowspan=8, padx=5, pady=5)  # position the move log in the grid

        self.refresh_board()  # refresh the board to display the initial state

    def load_pgn(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
        )  # open a file dialog to select a PGN file
        if not file_path:
            return  # exit if no file is selected
        
        self.analysis_area.insert(tk.END, "Loading PGN file...\n")  # Indicate loading
        self.analysis_area.update()  # Update the GUI to show the loading message

        with open(file_path) as f:
            game = chess.pgn.read_game(f)  # read the game from the PGN file
            if game:
                self.board = game.board()  # set the board to the initial position of the game
                self.move_stack = list(game.mainline_moves())  # store the moves in the move stack
                
                # Store FEN for each position
                self.fen_positions = [self.board.fen()]  # Initialize with the starting position
                for move in self.move_stack:
                    self.board.push(move)  # Make the move on the board
                    self.fen_positions.append(self.board.fen())  # Store the FEN after each move
            else:
                messagebox.showerror("Error", "Failed to load PGN file.")  # show an error if the game could not be read
                return

        self.analysis_area.delete(1.0, tk.END)  # clear the analysis area
        self.refresh_board()  # refresh the board to display the loaded game state
        self.analyze_current_position()  # analyze the current position of the board
        self.move_history.update(self.move_stack)  # update the move history display
        self.update_analysis_bar()  # update the analysis bar with new data
    
    def reset_board(self):
        self.board.reset()  # reset the chess board to its initial state
        self.move_stack = []  # clear the move stack
        self.analysis_area.delete(1.0, tk.END)  # clear the analysis area
        self.cumulative_score = 0  # reset cumulative score
        self.refresh_board()  # refresh the board to display the initial state
        self.move_history.update(self.move_stack)  # update the move history display
        self.update_analysis_bar()  # update the analysis bar with new data

    def on_board_click(self, event):
        x, y = event.x, event.y  # get the x and y coordinates of the mouse click
        col = x // 50  # determine the column based on the x coordinate
        row = 7 - (y // 50)  # determine the row based on the y coordinate
        square = chess.square(col, row)  # convert the column and row to a square index

        if self.selected_square is None:  # check if no square is currently selected
            if self.board.piece_at(square):  # check if there is a piece at the clicked square
                self.selected_square = square  # select the square if it contains a piece
        else:
            move = chess.Move(self.selected_square, square)  # create a move from the selected square to the clicked square
            if move in self.board.legal_moves:  # check if the move is legal
                self.board.push(move)  # make the move on the board
                self.selected_square = None  # reset the selected square
                self.refresh_board()  # update the board display
                self.analyze_current_position()  # analyze the new position
                self.move_history.update(self.board.move_stack)  # update the move history display
                self.update_analysis_bar()  # update the analysis bar with new data
            else:
                self.selected_square = None  # reset the selected square if the move is illegal
    
    def analyze_current_position(self):
        print("Starting analysis of the current position...")  # debug statement
        current_fen = self.board.fen()  # get the current FEN
        analysis_results = self.engine.analyze(
            chess.Board(current_fen),  # use the current FEN for analysis
            num_moves_to_return=3,
            depth_limit=self.DEPTH_LIMIT,  # use the defined depth limit
            time_limit=self.TIME_LIMIT       # use the defined time limit
        )
        print("Analysis completed.")  # debug statement
        print(analysis_results)

        self.analysis_area.delete(1.0, tk.END)  # clear the analysis area
        if self.board.move_stack:  # check if there are any moves made
            self.analysis_area.insert(tk.END, f"Move: {self.board.peek()}\n")  # display the last move

        for i, analysis in enumerate(analysis_results):  # Iterate through the analysis results
            self.analysis_area.insert(tk.END, f"Score {i + 1}: {analysis['score']}\n")  # display the score of each position
            if "pv" in analysis:  # check if there is a principal variation
                for j, move in enumerate(analysis['pv'][:3]):  # display the top 3 best moves
                    self.analysis_area.insert(tk.END, f"Best Move {i + 1}.{j + 1}: {move}\n")  # display each best move
        
        # Save the evaluation for the current FEN
        print(analysis_results)
        save_evaluation(current_fen, analysis_results)  # Save the analysis results to evaluations.json
        print("Analysis results displayed.")  # Debug statement

    def refresh_board(self):
        self.board_canvas.delete("all")  # clear the canvas to redraw the board
        for square in chess.SQUARES:  # iterate through all squares on the chess board
            col, row = chess.square_file(square), chess.square_rank(square)  # get the column and row of the square
            x1, y1 = col * 50, (7 - row) * 50  # calculate the top-left corner coordinates of the square
            x2, y2 = x1 + 50, y1 + 50  # calculate the bottom-right corner coordinates of the square
            color = "#B58863" if (col + row) % 2 == 0 else "#F0D9B5"  # Adjusted color logic
            self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color)  # draw the square on the canvas
            piece = self.board.piece_at(square)  # get the piece at the current square
            if piece:  # check if there is a piece
                piece_image = self.piece_images[piece.symbol()]  # get the image for the piece
                self.board_canvas.create_image(x1, y1, anchor=tk.NW, image=piece_image)  # place the piece image on the canvas

    def load_piece_images(self):
        piece_symbols = {  # dictionary mapping piece symbols to their image filenames
            "P": "wp.png",  # white pawn
            "N": "wN.png",  # white knight
            "B": "wB.png",  # white bishop
            "R": "wR.png",  # white rook
            "Q": "wQ.png",  # white queen
            "K": "wK.png",  # white king
            "p": "bp.png",  # black pawn
            "n": "bN.png",  # black knight
            "b": "bB.png",  # black bishop
            "r": "bR.png",  # black rook
            "q": "bQ.png",  # black queen
            "k": "bK.png",  # black king
        }
        piece_images = {}  # dictionary to store loaded piece images
        for symbol, filename in piece_symbols.items():  # iterate through each piece symbol and its filename
            image = Image.open(f"pngs/{filename}")  # open the image file for the piece
            piece_images[symbol] = ImageTk.PhotoImage(image.resize((50, 50)))  # resize and store the image in the dictionary
        return piece_images  # return the dictionary of piece images
    
    def on_quit(self):
        self.engine.quit()  # quit the chess engine to free resources
        self.root.destroy()  # close the main application window

    def next_move(self):
        if self.move_stack:  # check if there are moves in the stack
            move = self.move_stack.pop(0)  # get the next move from the stack
            self.board.push(move)  # make the move on the board
            self.refresh_board()  # update the board display
            self.analyze_current_position()  # analyze the new position
            self.move_history.update(self.board.move_stack)  # update the move history display
            self.update_analysis_bar()  # refresh the analysis bar with new data

    def prev_move(self):
        if self.board.move_stack:  # check if there are moves made on the board
            move = self.board.pop()  # get the last move made
            self.move_stack.insert(0, move)  # add the move back to the stack
            self.refresh_board()  # update the board display
            self.analyze_current_position()  # analyze the new position
            self.move_history.update(self.board.move_stack)  # update the move history display
            self.update_analysis_bar()  # refresh the analysis bar with new data

    def update_analysis_bar(self):
        print("Updating analysis bar...")  # Debug statement
        analysis = self.engine.analyze(
            self.board,
            num_moves_to_return=3,
            depth_limit=self.DEPTH_LIMIT,  # Use the defined depth limit
            time_limit=self.TIME_LIMIT       # Use the defined time limit
        )  
        print("Analysis completed for analysis bar.")  # Debug statement

        if analysis:  # Check if analysis returned results
            score = analysis[0]["score"]  # Get the score from the first analysis result
            print(f"Score from analysis: {score}")  # Debug statement

            if isinstance(score, int):
                normalized_score = score / 100  # adjust score for display
            else:
                normalized_score = score.relative.score()  # get score from score object

            max_score = 10  # set maximum score for display
            if normalized_score > 1:
                normalized_score = 1  # cap score at 1
            elif normalized_score < -1:
                normalized_score = -1  # cap score at -1

            white_percentage = (normalized_score + 1) * 50  # calculate white's advantage percentage
            black_percentage = 100 - white_percentage  # calculate black's advantage percentage

            self.analysis_bar.delete("all")  # clear existing bar

            # draw white and black sections of the bar
            self.analysis_bar.create_rectangle(
                0, 0, 20, white_percentage * 4, fill="#FFFFFF", outline=""
            )
            self.analysis_bar.create_rectangle(
                0, white_percentage * 4, 20, 400, fill="#000000", outline=""
            )

            self.analysis_bar.update()  # refresh the analysis bar display
            print("Analysis bar updated successfully.")  # Debug statement
        else:
            print("No analysis results to update the analysis bar.")  # Debug statement
    
def save_evaluation(fen, evaluation):
    """Save the evaluation for a given FEN to the JSON file."""
    EVALUATION_FILE = 'evaluations.json'
    evaluations = load_evaluations()
    evaluations[fen] = evaluation
    with open(EVALUATION_FILE, 'w') as f:
        json.dump(evaluations, f)

if __name__ == "__main__":  # check if the script is being run directly
    root = tk.Tk()  # create the main application window
    app = ChessAnalyserApp(root)  # instantiate the chess analysis application
    root.protocol("WM_DELETE_WINDOW", app.on_quit)  # set the protocol for closing the window to call the on_quit method
    root.mainloop()  # start the main event loop to run the application