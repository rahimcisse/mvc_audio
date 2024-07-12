import json
import os

class DictionaryModel:
    def __init__(self):
        self.full_history = []
        self.search_time = []
        self.all_words = []
        self.load_all_words()
        self.load_data()

    def load_all_words(self):
        try:
            with open("documents/all_words.json", "r") as json_file:
                data = json.load(json_file)
                self.all_words.extend(data)
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
