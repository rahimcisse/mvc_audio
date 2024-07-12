import json
import os
from difflib import get_close_matches
from textblob import TextBlob
from PyDictionary import PyDictionary
import time

class DataModel:
    def __init__(self):
        self.full_history = []
        self.search_time = []
        self.all_words = []
        self.load_all_words()
        self.load_data()
        self.dictionary = PyDictionary()

    def load_all_words(self):
        try:
            with open("documents/all_words.json", "r") as json_file:
                data = json.load(json_file)
                for item in data:
                    self.all_words.append(item)
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_words = []

    def save_data(self):
        data = {"full_history": self.full_history, "search_time": self.search_time}
        with open("documents/data.json", "w") as json_file:
            json.dump(data, json_file)

    def load_data(self):
        try:
            with open("documents/data.json", "r") as json_file:
                data = json.load(json_file)
                self.full_history = data["full_history"]
                self.search_time = data["search_time"]
        except (FileNotFoundError, json.JSONDecodeError):
            self.full_history = []
            self.search_time = []

    def search_word(self, word):
        corrected_word = TextBlob(word).correct()
        meanings = self.dictionary.meaning(word)
        return meanings, corrected_word

    def add_to_history(self, word):
        current_time = time.ctime()
        self.full_history.append(word)
        self.search_time.append(current_time)
        self.save_data()

    def get_history(self):
        return self.full_history, self.search_time
