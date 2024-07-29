import json
import os
import time

class DictionaryModel:
    def __init__(self):
        self.full_history = []
        self.search_time = []
        self.likely_words=[]
        self.data_path = "documents/data.json"
        self.load_data()


    def save_data(self):
        data = {"full_history": self.full_history, "search_time": self.search_time}
        with open(self.data_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def load_data(self):
        
        os.makedirs("documents", exist_ok=True)
        os.makedirs("saved_audio", exist_ok=True)

        if os.path.isfile("documents/data.json")==False:
            file = open("documents/data.json", 'a') 
        try:
            with open(self.data_path, "r") as json_file:
                data = json.load(json_file)
                self.full_history = data.get("full_history", [])
                self.search_time = data.get("search_time", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.full_history = []
            self.search_time = []


    def add_to_history(self, word):
        current_time = time.ctime()
        self.full_history.append(word)
        self.search_time.append(current_time)
        self.save_data()
        
    def open_file(self,file_path):
        root_path=os.getcwd()
        os.startfile(f"{root_path}/saved_audio/{file_path}.mp3")

    def open_folder(self):
        root_path=os.getcwd()
        os.startfile(f"{root_path}/saved_audio")
