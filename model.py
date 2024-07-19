import json
import os
import time
from difflib import get_close_matches
from textblob import TextBlob
from PyDictionary import PyDictionary

class DictionaryModel:
    def __init__(self):
        self.full_history = []
        self.search_time = []
        self.all_words = []
        self.data_path = "documents/data.json"
        self.words_path = "documents/all_words.json"
        self.load_all_words()
        self.load_data()

    def load_all_words(self):
        try:
            with open(self.words_path, "r") as json_file:
                data = json.load(json_file)
                self.all_words = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.all_words = []

    def save_data(self):
        data = {"full_history": self.full_history, "search_time": self.search_time}
        with open(self.data_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def load_data(self):
        try:
            with open(self.data_path, "r") as json_file:
                data = json.load(json_file)
                self.full_history = data.get("full_history", [])
                self.search_time = data.get("search_time", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.full_history = []
            self.search_time = []

    def get_closest_matches(self, word):
        return get_close_matches(word, self.all_words, n=6, cutoff=0.6)

    def get_meaning(self, word):
        dictionary = PyDictionary()
        return dictionary.meaning(word)

    def correct_word(self, word):
        return TextBlob(word).correct()

    def add_to_history(self, word):
        current_time = time.ctime()
        self.full_history.append(word)
        self.search_time.append(current_time)
        self.save_data()
