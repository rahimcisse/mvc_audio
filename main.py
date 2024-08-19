import tkinter as tk
from view import DictionaryView
from controller import DictionaryController

     
if __name__ == "__main__":
    root = tk.Tk()
    icon=tk.PhotoImage(file="images/icon.png")
    root.iconphoto(True,icon)
    controller = DictionaryController(root)  
    view = DictionaryView(root, controller)  
    root.mainloop()
