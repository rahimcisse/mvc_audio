import os
import time
import pyttsx3
import threading
import tkinter as tk
from textblob import TextBlob
from view import DictionaryView
from model import DictionaryModel
from difflib import get_close_matches
from PyDictionary import PyDictionary
from tkinter.messagebox import askyesno, askokcancel,showerror
from tkinter.scrolledtext import ScrolledText

class DictionaryController:
    def __init__(self, root):
        self.model = DictionaryModel()
        self.view = DictionaryView(root, self)
        self.is_running = False
        self.close = False
        self.validating()

    def on_closing(self):
        self.close = True
        if askyesno(title="QUIT" , message="ARE YOU SURE YOU WANT TO QUIT?") :
            self.view.root.destroy()
            self.show_full_history

    def speed_slider_change(self,event):
        speed_slider_new='{: .1f}'.format(self.view.speed_slider.get())
        self.view.speed_label.config(text=speed_slider_new)

    def volume_slider_change(self,event):
        volume_slider_new='{: .0f}%'.format(self.view.volume_slider.get())
        self.view.volume_label.config(text=volume_slider_new)
     
    def likely(self, event=None):
        def start(event):
            word = self.view.entry.get().lower().strip()
            likely_words = get_close_matches(word, possibilities=self.model.all_words,cutoff=0.6,n=6)
            self.view.entry.config(values=likely_words)
        start_likely = threading.Thread(target=start, args=(event,))
        start_likely.start()

    def search(self):
        if not self.is_running:
            search_thread = threading.Thread(target=self.search_synthesis)
            search_thread.start()

    def search_synthesis(self):
        word = self.view.entry.get().lower().strip()
        self.view.show_spinner()
        if word == "":
            self.view.show_error(title='Error', message='Please enter the word you want to search for!!')
            self.view.hide_spinner()
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.show_error('Error',f'Sorry, cannot search for the meaning of "{word}", Please enter a valid word.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
        if not self.is_running:
            
            if word == '' :
            # message box to display if the word variable is empty
                self.view.show_error('Error', 'Please enter the word you want to search for!!')
                return  # Exit the function if the word is empty
            self.is_running = True
            

            if word:
                self.view.update_preview(word)
                meanings = self.meaning(word)
                if meanings:
                    self.model.full_history.append(word)
                    self.model.search_time.append(time.asctime())
                    # self.view.update_recent_search(self.model.full_history, self.model.search_time)
                    self.view.update_meaning_box(meanings)
                    self.model.save_data()
                    self.view.hide_spinner()
                    self.validating()

                else:
                    self.correct(word)
            else:
                self.view.show_error("Error", "Field is empty")
            self.is_running = False
            self.view.hide_spinner()


    def meaning(self, word):        
        try:
            dict_obj = PyDictionary()
            meanings = dict_obj.meaning(word)
                    
            return meanings
        except FileNotFoundError:
            self.view.show_error(title='Error', message=f'Some files were not found!!! Please make sure you have all required files and try again')
            return
        
        # catching all errors
        except KeyError:
            self.view.show_error(title='Error', message=f'"{word}" was not found in the dictionary!')
            return
        
        # no internet connectivity
        except ConnectionError:
            self.view.show_error(title='Error', message='There is a problem with your internet connection! Please check it and then try again.')
            return
        
        # catching the rest of the exceptions
        except Exception as e:
            self.view.show_error(title='Error', message=f'An error occurred: {str(e)}')
            return
    def correct(self, word):
        corrected_word = TextBlob(word).correct()
        correct_meaning=PyDictionary.meaning(corrected_word) 
                


        if correct_meaning:
            if askyesno(title='Error', message=f'"{word}" was not found in the dictionary!. Do you mean "{corrected_word}"?'):  
                    self.view.entry.delete(0,tk.END)
                    self.view.entry.insert(tk.END,corrected_word)
                    self.is_running=False
                    self.search()
            else:
                        return

    
    def say_word(self):
        word=self.view.entry.get().strip()
        if word:
            word_thread=threading.Thread(target=self.word_synthesis)
            word_thread.start()

    def word_synthesis(self):
            word=self.view.entry.get().strip()

            if word == "":
                self.view.show_error(title='Error', message='Please enter the word you want to search for!!')
                self.view.hide_spinner()
                return
            if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.show_error('Error',f'Sorry, cannot search for the meaning of "{word}", Please enter a valid word.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
            
            self.view.read_word_button.config(state="disabled")
            self.view.show_spinner()
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            volume=engine.getProperty('volume')
            engine.setProperty('volume',int(self.view.volume_slider.get())/10)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id)        
            engine.say(word)
            if engine._inLoop:
                self.view.read_word_button.config(state="normal")
                engine.endLoop()
                self.view.hide_spinner()
           # this function processes the voice 
            else:
                    self.view.read_word_button.config(state="normal")
                    engine.runAndWait()
                    self.view.hide_spinner()
            self.view.read_button.config(state="normal")

    def speak(self):
        word = self.view.entry.get().strip()
        if word == "":
            self.view.show_error(title='Error', message='Please enter the word you want to search for!!')
            self.view.hide_spinner()
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.show_error('Error',f'Sorry, cannot search for the meaning of "{word}", Please enter a valid word.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty        
        if word:
            speak_thread = threading.Thread(target=self.speak_word, args=(word,))
            speak_thread.start()
        else:
            self.view.show_error("Error", "Field is empty")



    def speak_word(self, word):
        self.view.read_button.config(state="disabled")
        self.view.show_spinner()
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', int(self.view.speed_slider.get()))
        volume=engine.getProperty('volume')
        engine.setProperty('volume',int(self.view.volume_slider.get())/10)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[self.view.selected_voice.get()].id)            # creating a dictionary object
        dictionary = PyDictionary()

            # passing a word to the dictionary object
        meanings = dictionary.meaning(word)

        if meanings:
                    
                    # Speak the word
            engine.say(word)
                    # Speak each meaning
            for part_of_speech, meaning_list in meanings.items():
                    engine.say(part_of_speech)
                    for meaning in meaning_list:
                            engine.say(meaning)
            self.view.hide_spinner()
                
        else:
               
                engine.say("No meanings found for the word.")
                self.view.hide_spinner()
                
        if engine._inLoop:
            self.view.read_button.config(state="normal")
            engine.endLoop()
            self.view.loading.config(text="")
            self.view.hide_spinner()
            # this function processes the voice 
        else:
                self.view.read_button.config(state="normal")
                self.view.loading.config(text="Reading🔊")
                engine.runAndWait()
                self.view.hide_spinner()
                self.view.loading.config(text="")
        self.view.read_button.config(state="normal")


    def meaning_read_save(self):
        save=threading.Thread(target=self.saving)
        save.start()

    def saving(self):
        file_path=str(self.view.file_name.get().strip())
        meaning=self.view.meaning_box.get(1.0,tk.END).strip()
        meanings=self.view.meaning_box.get(1.0,tk.END).strip()
        if meaning=="":
            self.view.hide_spinner()
            showerror(title="Faild" ,message="No meanings to be saved. Please search for the meaning first")                
            return
        if file_path =="":
             showerror(title="Save As", message="Please enter Save As name")
             return
        if askyesno(title="Save As", message=f"Do you want to save mp3 file as '{file_path}'"): 
            self.view.progress.start(1)
            
            
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            volume=engine.getProperty('volume')
            engine.setProperty('volume',int(self.view.volume_slider.get())/10)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id)         
            engine.save_to_file(text=meanings, filename=f"saved_audio/{file_path}.mp3")
            self.view.hide_spinner()
            engine.runAndWait()
                    
            
            self.view.progress.stop()
            askokcancel(title="Save", message="Saving Complete. Saved audio can be found in the saved_audio folder.")
            

    def clear_history(self):
        if self.view.ask_yes_no("Clear", "Are you sure you want to clear history?"):
            self.model.full_history = []
            self.model.search_time = []
            self.model.save_data()
            self.validating()

    is_runn=False
    def show_full_history(self,tk=tk):

        def boolean():
            history_window.destroy()
            global is_runn
            is_runn=False
        
        
        
        global is_runn
        if self.is_runn == False:
            history_window=tk.Tk()
            history_window.title("History")
            history_window.geometry("540x500+1+100")
            history_window.resizable(False,False)
            self.full=ScrolledText(history_window,fg="black",state="disabled", background="#f8f0dc", bd=1,font=("Javanese Text",20),padx=12)
            self.full.pack(side="top", fill="both")

            self.full.config(state="normal")
            self.model.full_history.reverse()
            self.model.search_time.reverse()
            for line in zip(self.model.full_history,self.model.search_time):
                self.full.insert(1.0, f"{line}\n")
            self.model.full_history.reverse()
            self.model.search_time.reverse() 
            self.is_runn=True
        else:return  

        
            

        
      
                
            
      
        self.full.config(state="disabled")
        is_runn=True

        history_window.protocol("WM_DELETE_WINDOW", boolean)
    
    def switch_tab(self, notebook, tab_index):
        self.view.parent_tab.select(tab_index)

    def research1(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[0])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass


    def research2(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[1])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research3(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[2])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research4(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[3])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research5(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[4])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research6(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[5])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research7(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[6])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def research8(self):
        try:
            self.view.entry.delete(0,tk.END)
            self.view.entry.insert(tk.END,self.model.full_history[7])
            self.switch_tab(self.view.parent_tab,0)
            self.search()
        except IndexError:
            pass

    def validating(self):
        self.model.full_history.reverse()
        self.model.search_time.reverse()
        if 0 < len(self.model.full_history) and  0 < len(self.model.search_time):
            self.view.first_word.config(text=f"{self.model.full_history[0]}          {self.model.search_time[0]}")
        if  1 < len(self.model.full_history) and  1 < len(self.model.search_time):
            self.view.second_word.config(text=f"{self.model.full_history[1]}          {self.model.search_time[1]}")
        if  2 < len(self.model.full_history) and 2 < len(self.model.search_time):
            self.view.third_word.config(text=f"{self.model.full_history[2]}          {self.model.search_time[2]}")
        if  3 < len(self.model.full_history) and  3 < len(self.model.search_time):
            self.view.fourth_word.config(text=f"{self.model.full_history[3]}          {self.model.search_time[3]}")
        if  4 < len(self.model.full_history) and  4 < len(self.model.search_time):
            self.view.fifth_word.config(text=f"{self.model.full_history[4]}          {self.model.search_time[4]}")    
        if  5 < len(self.model.full_history) and  5 < len(self.model.search_time):
            self.view.sixth_word.config(text=f"{self.model.full_history[5]}          {self.model.search_time[5]}")  
        if  6 < len(self.model.full_history) and  6 < len(self.model.search_time):
            self.view.seventh_word.config(text=f"{self.model.full_history[6]}          {self.model.search_time[6]}")  
        if  7 < len(self.model.full_history) and  7 < len(self.model.search_time):
            self.view.eight_word.config(text=f"{self.model.full_history[7]}          {self.model.search_time[7]}")  
        else:
            return
    
    