import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno
from tkinter.scrolledtext import ScrolledText

class DictionaryView:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Dictionary With Spell Checks")
        self.root.config(bg="grey")
        self.root.geometry("650x700+400+1")
        self.create_widgets()

    def create_widgets(self):
        self.parent_tab = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.parent_tab)
        self.tab2 = ttk.Frame(self.parent_tab)
        self.tab3 = ttk.Frame(self.parent_tab)
        self.parent_tab.add(self.tab1, text="Audio-Dictionary")
        self.parent_tab.add(self.tab3, text="Recent")
        self.parent_tab.add(self.tab2, text="Settings")
        self.parent_tab.pack(expand=1, fill="both")

        # Tab 1
        audio_image = tk.PhotoImage(file="images/audio.png")
        tk.Label(self.tab1, image=audio_image).pack(side="top", fill="x")
        tk.Label(self.tab1, text="Input Word:", justify="left", font=("Gabriola", 25)).pack(side="top")

        self.entry = ttk.Combobox(self.tab1, width=45, font=("Cambria", 15))
        self.entry.pack(side="top", expand=1, fill="x")

        self.search_button = tk.Button(self.tab1, text="Search", command=self.on_search)
        self.search_button.pack(side="top")

        self.meaning_box = ScrolledText(self.tab1, state="disabled", bg="lightgrey", width=45, font=("Candara", 15), height=15, bd=5, blockcursor=True)
        self.meaning_box.pack(side="top", expand=1, fill="x")

        # Tab 3
        self.recent_box = tk.Text(self.tab3, state="disabled", bg="lightgrey", width=45, font=("Candara", 25), height=8, bd=5, blockcursor=True)
        self.recent_box.pack(side="top", expand=1, fill="x")

    def display_meaning(self, meanings):
        self.meaning_box.config(state="normal")
        self.meaning_box.delete('1.0', tk.END)
        for pos, meaning in enumerate(meanings, start=1):
            self.meaning_box.insert(tk.END, f"{pos}. {meaning.capitalize()}:\n")
            self.meaning_box.insert(tk.END, f"{', '.join(meanings[meaning])}\n\n")
        self.meaning_box.config(state="disabled")

    def display_error(self, message):
        showerror(title='Error', message=message)

    def on_search(self):
        pass
