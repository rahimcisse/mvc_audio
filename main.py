import tkinter as tk
from views import DictionaryView
from controller import DictionaryController

if __name__ == "__main__":
    root = tk.Tk()
    controller = DictionaryController(root)  # Assuming you have a Controller class defined
    view = DictionaryView(root, controller)  # Pass root and controller to DictionaryView
    root.mainloop()
