import pyttsx3
import threading
from textblob import TextBlob
from view import DictionaryView
from model import DictionaryModel
from difflib import get_close_matches
from PyDictionary import PyDictionary



class DictionaryController:
    def __init__(self, root):
        self.model = DictionaryModel() 
        self.view = DictionaryView(root, self)
        self.is_running = False #assigning false to raise flag that program isn't searching for a word
        self.is_open=False
        self.validating()




    def on_closing(self):
        if self.view.askyesno(title="QUIT" , message="ARE YOU SURE YOU WANT TO QUIT?") :
            self.view.boolean()
            self.view.root.destroy()



    def speed_slider_change(self,event):
        try:
            self.slider=self.view.speed_slider.get()
            speed_slider_new='{: .1f}'.format(self.slider)
            self.view.speed_label.config(text=speed_slider_new)
        except AttributeError:
            pass
    

    
    def likely(self, event=None):

        
            def start(event):
                word = self.view.entry.get().lower().strip()
                likely_corrected_word=TextBlob(word).correct()
                for likely_corrected in self.model.likely_words:
                    if likely_corrected == likely_corrected_word:
                        return
                else:
                    self.model.likely_words.append(likely_corrected_word)
                

                likely_word = get_close_matches(word, self.model.likely_words , cutoff=0.6,n=6)
                if likely_word:
                    self.view.entry.config(values=likely_word)
                else:return
            start_likely = threading.Thread(target=start, args=(event,))
            start_likely.start()


    def search(self):
        try:
            if not self.is_running:
                search_thread = threading.Thread(target=self.search_synthesis)
                search_thread.start()
        except Exception as e:
            self.view.showerror(title='ERROR', message=e)


    def search_synthesis(self):
        word = self.view.entry.get().lower().strip()
        self.view.show_spinner()
        
        if word == "":
            self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            self.view.hide_spinner()
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF "{word}", PLEASE ENTER A VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
        if not self.is_running:
            
            if word == '' :
            # message box to display if the word variable is empty
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                return  # Exit the function if the word is empty
            self.is_running = True
            

            if word:
                self.view.update_preview(word)
                meanings = self.meaning(word)
                if meanings:
                    self.model.add_to_history(word)
                    # self.view.update_recent_search(self.model.full_history, self.model.search_time)
                    self.view.update_meaning_box(meanings)
                    self.view.hide_spinner()
                    self.validating()
                    self.view.save_button.pack(side="right")

                else:
                    if word==self.model.full_history[0]:
                        self.view.hide_spinner()
                        return
                    else:
                        self.view.hide_spinner()
                        self.view.showerror(title='ERROR', message='YOU HAVE SLOW OR INTERNET CONNECTTION. PLEASE CHECK IT AND TRY AGAIN!!')
                        self.correct(word)

            else:
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            self.is_running = False
            self.view.hide_spinner()


    def meaning(self, word):        
        try:
            dict_obj = PyDictionary()
            meanings = dict_obj.meaning(word)
                    
            return meanings
        except FileNotFoundError:
            self.view.showerror(title='ERROR', message=f'SOME FILES WERE NOT FOUND!!! PLEASE MAKE SURE YOU HAVE ALL REQUIRED FILES AND TRY AGAIN')
            return
        
        # catching all errors
        except KeyError:
            self.view.showerror(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!')
            return
        
        # no internet connectivity
        except ConnectionError:
            self.view.showerror(title='ERROR', message='THERE IS A PROBLEM WITH YOUR INTERNET CONNECTION! \nPLEASE CHECK IT AND THEN TRY AGAIN.')
            return
        
        # catching the rest of the exceptions
        except Exception as e:
            self.view.showerror(title='ERROR', message=f'AN ERROR OCCURRED: {str(e)}')
            return


    def correct(self, word):
        corrected_word = TextBlob(word).correct()
        correct_meaning=PyDictionary.meaning(corrected_word) 
                


        if correct_meaning:
            if self.view.askyesno(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!.\n DO YOU MEAN "{corrected_word}"?'):  
                    self.view.entry.delete(0,self.view.end)
                    self.view.entry.insert(self.view.end,corrected_word)
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
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                self.view.hide_spinner()
                return
            if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF"{word}"\n PLEASE ENTER A VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
            
            self.view.read_word_button.config(state="disabled")
            self.view.show_spinner()
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(self.view.speed_slider.get()))
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


    def read_sentence(self):
        word = self.model.full_history[0]
        if word == "":
            self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            self.view.hide_spinner()
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF"{word}"\n PLEASE ENTER A VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty        
        if word:
            try:
                read_sentence_thread = threading.Thread(target=self.read_sentence_synthesis, args=(word,))
                read_sentence_thread.start()
            except ConnectionError:
                return
                 
        else:
            self.view.showerror(title="ERROR", message="PLEASE SEARCH FOR THE WORD FIRST!!")


    def read_sentence_synthesis(self, word):
        self.view.read_button.config(state="disabled")
        self.view.show_spinner()
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', int(self.view.speed_slider.get()))
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[self.view.selected_voice.get()].id)            # creating a dictionary object
        dictionary = PyDictionary()

            # passing a word to the dictionary object
        meanings = dictionary.meaning(word)

        if meanings:
                    
                    # read_sentence the word
            engine.say(word)
                    # read_sentence each meaning
            for part_of_speech, meaning_list in meanings.items():
                    engine.say(part_of_speech)
                    for meaning in meaning_list:
                            engine.say(meaning)
            self.view.hide_spinner()
                
        else:
               
                
                self.view.hide_spinner()
                return
                
        if engine._inLoop:
            self.view.read_button.config(state="normal")
            engine.endLoop()
            self.view.hide_spinner()
            # this function processes the voice 
        else:
                self.view.read_button.config(state="normal")
                engine.runAndWait()
                self.view.hide_spinner()
        self.view.read_button.config(state="normal")

    
    def increment(self,number):

            self.view.progress["value"] = number+10
            self.view.tab4.update()

    def meaning_save(self):
        if self.view.selected_save.get()==0:
            self.meaning_read_save()
            
        else:
            self.meaning_text_save()


    def meaning_text_save(self):
         saving_txt=threading.Thread(target=self.saving_text)
         saving_txt.start()


    def saving_text(self):
        file_path=str(self.view.file_name.get().strip())
        meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
        if meanings=="":
            self.view.showerror(title="FAILD" ,message="NO MEANINGS TO BE SAVED. PLEASE SEARCH FOR THE MEANING FIRST")                
            return
        if file_path =="":
             self.view.showerror(title="SAVE AS", message="PLEASE ENTER SAVE AS NAME ")
             return
        if self.view.askyesno(title="SAVE AS", message=f"DO YOU WANT TO SAVE AUDIO AS '{file_path}'.txt "): 
            self.view.progress.start()
            self.increment(40)

            with open(f"saved_meanings/{file_path}.txt","a") as file:
                file.write(f"{self.model.full_history[0]}\n")   
                file.write(meanings)   
                file.close() 
        self.increment(90)
                    
            
        self.view.progress.stop()
        if self.view.askyesno(title="SAVING COMPLETE ", message="SAVED IN 'SAVED_MEANINGS' FOLDER.\n WOULD YOU LIKE TO OPEN fILE?"):
            self.model.open_file_txt(file_path)
            self.switch_tab(self.view.parent_tab,0)
            self.view.parent_tab.hide(3)


    def meaning_read_save(self):
        save=threading.Thread(target=self.saving)
        save.start()


    def saving(self):
        file_path=str(self.view.file_name.get().strip())
        meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
        if meanings=="":
            self.view.showerror(title="FAILD" ,message="NO MEANINGS TO BE SAVED. PLEASE SEARCH FOR THE MEANING FIRST")                
            return
        if file_path =="":
             self.view.showerror(title="SAVE AS", message="PLEASE ENTER SAVE AS NAME ")
             return
        if self.view.askyesno(title="SAVE AS", message=f"DO YOU WANT TO SAVE AUDIO AS '{file_path}'.mp3 "): 
            self.view.progress.start()
            self.increment(20)
            engine = pyttsx3.init()
            self.increment(30)
            rate = engine.getProperty('rate')
            self.increment(40)
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            self.increment(50)
            voices = engine.getProperty('voices')
            self.increment(60)
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id) 
            self.increment(70)        
            engine.save_to_file(meanings, filename=f"saved_meanings/{file_path}.mp3")
            self.increment(80)
            engine.runAndWait()
            self.increment(90)
                    
            
            self.view.progress.stop()
            if self.view.askyesno(title="SAVING COMPLETE ", message="SAVED IN 'SAVED_MEANINGS' FOLDER.\n WOULD YOU LIKE TO OPEN fILE?"):
                self.model.open_file(file_path)
                self.switch_tab(self.view.parent_tab,0)
                self.view.parent_tab.hide(3)
            

    def clear_history(self):
        self.view.tab3.bell()
        if self.view.askyesno("CLEAR", f"ARE YOU SURE YOU WANT TO CLEAR HISTORY? \n ALL SAVED DATA WILL BE LOST!!!"):
            self.model.full_history = []
            self.model.search_time = []
            self.model.save_data()
            self.validating()
            self.view.full.delete(0,self.view.end)


    
    def show_full_history(self):
        self.view.setup_history_window(self.model.full_history,self.model.search_time)


    

    def spell(self):
        word=self.view.entry.get().strip()
        if word:
            spell_thread=threading.Thread(target=self.spell_synthesis)
            spell_thread.start()
        else:
             self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SPELL!!')
             


    def spell_synthesis(self):
            word=self.view.entry.get().strip()

            if word == "":
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                self.view.hide_spinner()
                return
            if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF"{word}"\n PLEASE ENTER A VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
            
            self.view.read_word_button.config(state="disabled")
            self.view.show_spinner()
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id)  

            engine.say(word)      
            for letter in word:
                 engine.say(letter)

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
         


    def view_audiofolder(self):
        self.model.open_folder()


    def copy_meaning(self):
            
            meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
            self.view.tab1.clipboard_clear()
            self.view.tab1.clipboard_append(meanings)


    def cut(self):
         
        self.view.tab1.clipboard_clear()
        self.view.tab1.clipboard_append(self.view.entry.get())
        self.view.entry.delete(0, self.view.end)
         

    def paste(self):
        word_to_be_pasted=self.view.tab1.clipboard_get ()
        self.view.entry.insert(0, self.view.end)
        



    def switch_tab(self, notebook, tab_index):
        self.view.parent_tab.select(tab_index)


    def redirect_to_save(self):
         self.switch_tab(self.view.parent_tab,3)


    def research(self,index):
        try:
            self.view.entry.delete(0,self.view.end)
            self.view.entry.insert(self.view.end,self.model.full_history[index])
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
    
