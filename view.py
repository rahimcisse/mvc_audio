import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror, askyesno
import os
import time
import threading
import pyttsx3
from textblob import TextBlob
from PIL import Image, ImageTk, ImageSequence
from difflib import get_close_matches
from PyDictionary import PyDictionary
from model import DictionaryModel

class DictionaryView:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.root.title("Audio Dictionary With Spell Checks")
        self.root.config(bg="grey")
        self.root.geometry("650x700+400+1")
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)

        self.parent_tab = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.parent_tab)
        self.tab2 = ttk.Frame(self.parent_tab)
        self.tab3 = ttk.Frame(self.parent_tab)
        self.parent_tab.add(self.tab1, text="Audio-Dictionary")
        self.parent_tab.add(self.tab3, text="Recent")
        self.parent_tab.add(self.tab2, text="Settings")
        self.parent_tab.pack(expand=1, fill="both")

        

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()

    def setup_tab1(self):
        self.audio_image = tk.PhotoImage(file="images/audio.png")
        tk.Label(self.tab1, image=self.audio_image).pack(side="top", fill="x")
        tk.Label(self.tab1, text="Input Word:", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.loading=ttk.Label(self.tab1)
        self.loading.pack()

        self.spinner = SpinnerLabel(self.loading, "images/loading1.gif", size=(20, 20))
        self.spinner.pack()
        self.spinner.pack_forget()

        self.entry = ttk.Combobox(self.tab1, width=45, font=("Cambria", 15))
        self.entry.pack(side="top", expand=1, fill="x")
        self.entry.bind('<KeyRelease>', self.controller.likely)

        self.preview = tk.Text(self.tab1, width=10, height=1, bg="#ececec", font=("Times New Roman", 20), state="disabled")
        self.preview.pack(pady=10)

        self.search_image = tk.PhotoImage(file="images/search.png")
        tk.Button(self.tab1, bg="#f5f3ed", width=50, height=30, bd=5, image=self.search_image, command=self.controller.search).pack(side="top")

        self.meaning_image = tk.PhotoImage(file="images/meaning_image.png")
        tk.Label(self.tab1, image=self.meaning_image).pack(side="top")

        self.read_image = tk.PhotoImage(file="images/read_man.png")
        self.read_button = tk.Button(self.tab1, bg="#70c2f2", width=110, height=300, bd=5, image=self.read_image, command=self.controller.speak)
        self.read_button.pack(side="left")

        self.meaning_box = ScrolledText(self.tab1, state="disabled", bg="lightgrey", width=45, font=("Candara", 15), height=15, bd=5, blockcursor=True)
        self.meaning_box.pack(side="top", expand=1, fill="x")

    def setup_tab2(self):
        tk.Label(self.tab2, text="Choose meaning theme", justify="left", font=("Gabriola", 35)).pack(side="top")
        self.selected_meaning_colour = tk.IntVar()
        tk.Radiobutton(self.tab2, text="default", variable=self.selected_meaning_colour, value=0, font=10).pack(side="top")
        tk.Radiobutton(self.tab2, text="dark", variable=self.selected_meaning_colour, value=1, font=10).pack(side="top")
        tk.Radiobutton(self.tab2, text="light", variable=self.selected_meaning_colour, value=2, font=10).pack(side="top")
        tk.Button(self.tab2, text="Apply", command=self.controller.theme, bd=5, bg="lightblue").pack(side="top")

        tk.Label(self.tab2, text="Choose voice", justify="left", font=("Gabriola", 35)).pack(side="top")
        self.selected_voice = tk.IntVar()
        tk.Radiobutton(self.tab2, text="Male", variable=self.selected_voice, value=0, font=10).pack(side="top")
        tk.Radiobutton(self.tab2, text="Female", variable=self.selected_voice, value=1, font=10).pack(side="top")
        self.selected_voice.set(1)

    def setup_tab3(self):
        self.recent_image = tk.PhotoImage(file="images/recent.png")
        tk.Label(self.tab3, image=self.recent_image, bd=40).pack(side="top", fill="x")
        tk.Label(self.tab3, text="Most Recent Search:", justify="left", font=("Ink Free", 20)).pack(side="top")

        self.recent_box = tk.Text(self.tab3, state="disabled", bg="lightgrey", width=45, font=("Candara", 25), height=8, bd=5, blockcursor=True)
        self.recent_box.pack(side="top", expand=1, fill="x")

        self.first_word=tk.Button(self.recent_box,text="" ,command=self.controller.research1,bg="lightgrey", font=("Ariel",15))
        self.first_word.pack (side="top",fill="x")

        self.second_word=tk.Button(self.recent_box,text="",command=self.controller.research2,bg="lightgrey", font=("Ariel",15))
        self.second_word.pack (side="top",fill="x")

        self.third_word=tk.Button(self.recent_box,text="",command=self.controller.research3,bg="lightgrey", font=("Ariel",15))
        self.third_word.pack (side="top",fill="x")
        self.fourth_word=tk.Button(self.recent_box ,text="",command=self.controller.research4,bg="lightgrey", font=("Ariel",15))
        self.fourth_word.pack (side="top",fill="x")
        self.fifth_word=tk.Button(self.recent_box,text="",command=self.controller.research5,bg="lightgrey", font=("Ariel",15))
        self.fifth_word.pack (side="top",fill="x")
        self.sixth_word=tk.Button(self.recent_box,text="",command=self.controller.research6,bg="lightgrey", font=("Ariel",15))
        self.sixth_word.pack (side="top",fill="x")
        self.seventh_word=tk.Button(self.recent_box,text="",command=self.controller.research7,bg="lightgrey", font=("Ariel",15))
        self.seventh_word.pack (side="top",fill="x")
        self.eight_word=tk.Button(self.recent_box,text="",command=self.controller.research8,bg="lightgrey", font=("Ariel",15))
        self.eight_word.pack (side="top",fill="x")

        self.clear=tk.Button(self.tab3,width=10, height=1 ,bd=5,bg="#ff6060",text="Clear History" ,command=self.controller.clear_history)
        self.clear.pack(side="left")
        self.show_button=tk.Button(self.tab3,width=15,bg="lightblue", height=1 ,bd=5,text="View Full History", command=self.controller.show_full_history)    
        self.show_button.pack(side="left")
    def update_preview(self, word):
        self.preview.config(state="normal")
        self.preview.delete(1.0, tk.END)
        self.preview.insert(1.0, word)
        self.preview.config(state="disabled")

    def update_meaning_box(self, meanings):
        self.meaning_box.config(state="normal")
        self.meaning_box.delete('1.0', tk.END)
        for pos, meaning in enumerate(meanings, start=1):
            self.meaning_box.insert(tk.END, f"{pos}. {meaning.capitalize()}:\n")
            self.meaning_box.insert(tk.END, f"{', '.join(meanings[meaning])}\n\n")
        self.meaning_box.config(state="disabled")


    def apply_theme(self, bg, fg):
        
        self.meaning_box.config(bg=bg, fg=fg)

    def show_error(self, title, message):
        showerror(title=title, message=message)  

    def show_spinner(self):
        self.spinner.pack()

    def hide_spinner(self):
        self.spinner.pack_forget()

class SpinnerLabel(tk.Label):
    def __init__(self, master, gif_path, size, *args, **kwargs):
        tk.Label.__init__(self, master, *args, **kwargs)
        self.size = size
        self.frames = [ImageTk.PhotoImage(img.resize(self.size, Image.Resampling.LANCZOS)) 
                       for img in ImageSequence.Iterator(Image.open(gif_path))]
        self.index = 0
        self.update_label()

    def update_label(self):
        self.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(100, self.update_label)  # Adjust the delay as necessary



if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryView(root, None)
    root.mainloop()
