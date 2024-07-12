import threading
from model import DataModel
from views import DictionaryView
import tkinter as tk

class DictionaryController:
    def __init__(self, root):
        self.model = DataModel()
        self.view = DictionaryView(root)
        self.view.search_button.config(command=self.on_search)

    def on_search(self):
        word = self.view.entry.get().strip().lower()
        if not word:
            self.view.display_error('Please enter the word you want to search for!')
            return

        if not word.isalpha():
            self.view.display_error(f'Sorry, cannot search for the meaning of "{word}", Please enter a valid word.')
            return

        search_thread = threading.Thread(target=self.search_word, args=(word,))
        search_thread.start()

    def search_word(self, word):
        meanings, corrected_word = self.model.search_word(word)
        if meanings:
            self.model.add_to_history(word)
            self.view.display_meaning(meanings)
        else:
            self.view.display_error(f'"{word}" was not found in the dictionary!')

if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryController(root)
    root.mainloop()
