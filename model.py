import json 
import os
import time

class DictionaryModel: #defining model class
    def __init__(self):
        self.full_history = [] #setting all lists as empty
        self.search_time = []
        self.likely_words=[]
        self.data_path = "documents/data.json"  
        self.load_data()


    def save_data(self):
        data = {"full_history": self.full_history, "search_time": self.search_time}
        with open(self.data_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def load_data(self):#loading data into lists
        
        os.makedirs("documents", exist_ok=True)     #creats a folder which takes the name of the first arguments and returns if there's already a folder of that name 
        os.makedirs("saved_meanings", exist_ok=True)

        if os.path.isfile(self.data_path)==False:   #creates a json file inside the folder created if theres none
            file = open(self.data_path, 'a') 
        try:
            with open(self.data_path, "r") as json_file:    #reads history from json file and stores them into lists
                data = json.load(json_file)
                self.full_history = data.get("full_history", [])
                self.search_time = data.get("search_time", [])
        except (FileNotFoundError, json.JSONDecodeError):       #if the file is empty or cannot be found, it sets them as empty lists 
            self.full_history = []
            self.search_time = []


    def add_to_history(self, word): #adding to history
        current_time = time.ctime()
        self.full_history.insert(0,word)
        self.search_time.append(current_time)
        self.save_data()
        
    def open_file(self,file_path): #opening saved file
        root_path=os.getcwd()           #getting the directory of the parent folder on the users computer
        os.startfile(f"{root_path}{file_path}")     #opening a file with the inputed path 





