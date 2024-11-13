from gui import ChessAnalyserApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = ChessAnalyserApp(root)
    print("Chess Analyser App is starting...")
    root.mainloop()


if __name__ == "__main__":
    main()