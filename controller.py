import os
import time
import threading
import pyttsx3
from textblob import TextBlob
from difflib import get_close_matches
from PyDictionary import PyDictionary
from model import DictionaryModel
from views import DictionaryView

class DictionaryController:
    def __init__(self, root):
        self.model = DictionaryModel()
        self.view = DictionaryView(root, self)
        self.view.update_recent_search(self.model.full_history, self.model.search_time)
        self.is_running = False
        self.close = False

    def on_closing(self):
        self.close = True
        self.view.root.destroy()

    def likely(self, event=None):
        word = self.view.entry.get().lower().strip()
        likely_words = get_close_matches(word, self.model.all_words)
        self.view.entry.config(values=likely_words[:6])

    def search(self):
        if not self.is_running:
            search_thread = threading.Thread(target=self.search_synthesis)
            search_thread.start()

    def search_synthesis(self):
        if not self.is_running:
            self.is_running = True
            word = self.view.entry.get().lower().strip()
            if word:
                self.view.update_preview("searching.....")
                meanings = self.meaning(word)
                if meanings:
                    self.model.full_history.append(word)
                    self.model.search_time.append(time.strftime("%I:%M %p"))
                    self.view.update_recent_search(self.model.full_history, self.model.search_time)
                    self.view.update_meaning_box(meanings)
                    self.model.save_data()
            else:
                self.view.show_error("Error", "Field is empty")
            self.is_running = False

    def meaning(self, word):
        try:
            dict_obj = PyDictionary()
            meanings = dict_obj.meaning(word)
            if meanings is None:
                self.view.update_preview("Word not found")
                return None
            return meanings
        except Exception as e:
            self.view.show_error("Error", str(e))
            return None

    def speak(self):
        word = self.view.entry.get().strip()
        if word:
            speak_thread = threading.Thread(target=self.speak_word, args=(word,))
            speak_thread.start()
        else:
            self.view.show_error("Error", "Field is empty")

    def speak_word(self, word):
        self.view.read_button.config(state="disabled")
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[self.view.selected_voice.get()].id)
        engine.say(TextBlob(word).correct())
        engine.runAndWait()
        self.view.read_button.config(state="normal")

    def theme(self):
        if self.view.selected_meaning_colour.get() == 0:
            self.view.apply_theme(bg="#ececec", fg="black")
        elif self.view.selected_meaning_colour.get() == 1:
            self.view.apply_theme(bg="black", fg="white")
        elif self.view.selected_meaning_colour.get() == 2:
            self.view.apply_theme(bg="white", fg="black")

    def clear_history(self):
        if self.view.ask_yes_no("Clear", "Are you sure you want to clear history?"):
            self.model.full_history = []
            self.model.search_time = []
            self.model.save_data()
            self.view.update_recent_search(self.model.full_history, self.model.search_time)

    def show_full_history(self):
        history = self.model.full_history[::-1]
        search_time = self.model.search_time[::-1]
        with open("documents/full_history.txt", "w") as file:
            file.write("Full History:\n\n")
            for word, time in zip(history, search_time):
                file.write(f"{word}          {time}\n\n")
        os.startfile("documents/full_history.txt")
