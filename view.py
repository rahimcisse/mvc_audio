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
        self.read_word_button=tk.Button(self.entry,bd=4,text="🔊",bg="lightblue",command=self.controller.say_word)
        self.read_word_button.pack(side="right", padx=25)

        self.preview = tk.Text(self.tab1, width=10, height=1, bg="#ececec", font=("Times New Roman", 20), state="disabled")
        self.preview.pack(pady=10)

        self.search_image = tk.PhotoImage(file="images/search.png")
        tk.Button(self.tab1, bg="#f5f3ed", width=50, height=30, bd=5, image=self.search_image, command=self.controller.search).pack(side="top")

        self.meaning_image = tk.PhotoImage(file="images/meaning_image.png")
        tk.Label(self.tab1, image=self.meaning_image).pack(side="top")

        self.read_image = tk.PhotoImage(file="images/read_man.png")
        self.read_button = tk.Button(self.tab1, bg="#70c2f2", width=110, height=300, bd=5, image=self.read_image, command=self.controller.speak)
        self.read_button.pack(side="left")

        self.meaning_box = ScrolledText(self.tab1, state="disabled", bg="white", width=45, font=("Candara", 15), height=15, bd=5, blockcursor=True)
        self.meaning_box.pack(side="top", expand=1, fill="x")

    def setup_tab2(self):
        tk.Label(self.tab2, text="Save Recent Audio Meaning As", justify="left", font=("Gabriola", 35)).pack(side="top")

        self.file_name=tk.Entry(self.tab2)
        self.file_name.pack(side="top")

        self.save_audio=tk.Button(self.tab2,bd=5,bg="lightblue",command=self.controller.meaning_read_save, text="Save read meaning")
        self.save_audio.pack(side="top")

        
        self.progress=ttk.Progressbar(self.tab2)
        self.progress.pack(side="top")

        tk.Label(self.tab2, text="Choose voice", justify="left", font=("Gabriola", 35)).pack(side="top")
        self.selected_voice = tk.IntVar()
        tk.Radiobutton(self.tab2, text="Male", variable=self.selected_voice, value=0, font=10).pack(side="top")
        tk.Radiobutton(self.tab2, text="Female", variable=self.selected_voice, value=1, font=10).pack(side="top")
        self.selected_voice.set(1)

        self.style=ttk.Style()
        self.style.configure('TScale',background='lightgrey')
        self.selected_volume=tk.IntVar
        self.selected_speed=tk.IntVar

        tk.Label(self.tab2, text="Set Reading Speed", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.speed_slider=ttk.Scale(self.tab2,from_=1,to=200,style='TScale',variable=self.selected_speed ,command=self.controller.speed_slider_change, orient="horizontal")
        self.speed_slider.pack(side="top")
        
        self.speed_label=tk.Label(self.tab2, justify="left", font=("Gabriola", 15))
        self.speed_label.pack(side="top")
        self.speed_slider.set(125)

        tk.Label(self.tab2, text="Set volume", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.volume_slider=ttk.Scale(self.tab2,from_=0,to=100,style='TScale',variable=self.selected_volume,command=self.controller.volume_slider_change, orient="horizontal")
        self.volume_slider.pack(side="top")
        self.volume_label=tk.Label(self.tab2, justify="left", font=("Gabriola", 15))
        self.volume_label.pack(side="top")
        self.volume_slider.set(100)

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
