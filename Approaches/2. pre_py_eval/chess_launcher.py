import tkinter as tk
from tkinter import messagebox
import subprocess
import os

class ChessLauncher:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game Launcher")
        self.master.geometry("300x200")
        self.master.configure(bg='#2c3e50')

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.master, text="Select Game Mode", bg='#2c3e50', fg='white', font=('Arial', 14))
        title_label.pack(pady=20)

        button_frame = tk.Frame(self.master, bg='#2c3e50')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Player vs Player", command=self.launch_human_vs_human).pack(pady=5, padx=10)
        tk.Button(button_frame, text="Player vs Stockfish", command=self.launch_play_against_stockfish).pack(pady=5, padx=10)
        tk.Button(button_frame, text="Stockfish vs Stockfish", command=self.launch_stockfish_vs_stockfish).pack(pady=5, padx=10)

    def launch_human_vs_human(self):
        self.run_script("human_vs_human.py")

    def launch_play_against_stockfish(self):
        self.run_script("play_against_stockfish.py")

    def launch_stockfish_vs_stockfish(self):
        self.run_script("stockfish_vs_stockfish.py")

    def run_script(self, script_name):
        try:
            # Check if the script exists
            if os.path.exists(script_name):
                subprocess.Popen(["python", script_name])
                self.master.quit()  # Close the launcher
            else:
                messagebox.showerror("Error", f"{script_name} not found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessLauncher(root)
    root.mainloop() 