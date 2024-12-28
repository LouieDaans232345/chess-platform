import tkinter as tk  # import the tkinter module for GUI

class MoveLog:
    def __init__(self, parent):
        # initialize the move log frame and listbox
        self.frame = tk.Frame(parent)  # create a frame for the move log
        self.frame.grid(row=0, column=2, rowspan=8, padx=10, pady=5)  # position the frame in the grid
        self.history_area = tk.Listbox(self.frame, width=30)  # create a listbox to display move history
        self.history_area.pack(fill=tk.BOTH, expand=True)  # pack the listbox to fill the frame

    def update(self, move_stack):
        # update the listbox with the current move stack
        self.history_area.delete(0, tk.END)  # clear the current listbox entries
        for move in move_stack:
            self.history_area.insert(tk.END, move.uci())  # insert each move in UCI format