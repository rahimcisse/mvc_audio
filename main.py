import tkinter as tk
from controller import DictionaryController

if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryController(root)
    root.mainloop()
