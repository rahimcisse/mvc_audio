import pyttsx3
import threading
from textblob import TextBlob
from view import DictionaryView
from model import DictionaryModel
from difflib import get_close_matches
from PyDictionary import PyDictionary
import requests



class DictionaryController:
    def __init__(self, root):
        self.model = DictionaryModel() 
        self.view = DictionaryView(root, self)
        self.is_running = False #assigning false to raise flag that program isn't searching for a word
        self.is_open=False #raising a flag that full history widow isn't open
        self.validating() #this function helps the user to search a word that has been searched recently by clicking on it 




    def on_closing(self):
        if self.view.askyesno(title="QUIT" , message="ARE YOU SURE YOU WANT TO QUIT?") : #for closing window
            self.view.boolean()
            self.view.is_saving_boolean()
            self.view.root.destroy()



    def speed_slider_change(self,event): #configuring the slider and slider label
        try:
            self.slider=self.view.speed_slider.get()
            speed_slider_new='{: .1f}'.format(self.slider)
            self.view.speed_label.config(text=f"🐢          {speed_slider_new}          🐇")
        except AttributeError:
            pass
    

    
    def likely(self,event): #gtting likely words

        
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
            start_likely.daemon=True
            start_likely.start()


    def search(self): #searching for word
        try:
            if not self.is_running:
                search_thread = threading.Thread(target=self.search_synthesis)
                search_thread.daemon=True
                search_thread.start()
        except Exception as e:
            self.view.showerror(title='ERROR', message=e)


    def search_synthesis(self):
        word = self.view.entry.get().lower().strip()
        self.view.show_spinner()
        
        if word == "" or word=="enter word here":
            self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            self.view.hide_spinner()
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF "{word}", PLEASE ENTER A SINGLE AND VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
        if not self.is_running:
            
            if word == '' :
            # message box to display if the word variable is empty
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                return  # Exit the function if the word is empty
            self.is_running = True
            

            if word:
                meanings = self.meaning(word)
                if meanings:
                    self.model.add_to_history(word)
                    self.view.meaning_label.config(text=f"Meaning({word})")
                    self.view.update_meaning_box(meanings)
                    self.view.hide_spinner()
                    self.validating()

                else:
                    
                        if meanings is None:
                            self.view.hide_spinner()
                            self.correct(word)

            else:
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            self.is_running = False
            self.view.hide_spinner()


    def meaning(self, word):        #getting meanings
        try:
            url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
            response = requests.get(url)
            if response.status_code == 200:
                meanings = response.json()
                return meanings
            else: return None
        
        except requests.exceptions.RequestException:
            self.is_running = False
            self.view.showerror(title='ERROR', message='THERE IS A PROBLEM WITH YOUR INTERNET CONNECTION! \nPLEASE CHECK IT AND THEN TRY AGAIN.')
            return
        except FileNotFoundError:
            self.is_running = False
            self.view.showerror(title='ERROR', message=f'SOME FILES WERE NOT FOUND!!! PLEASE MAKE SURE YOU HAVE ALL REQUIRED FILES AND TRY AGAIN')
            return
        
        # catching all errors
        except KeyError:
            self.is_running = False
            self.view.showerror(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!')
            return
        
        # no internet connectivity
        except ConnectionError:
            self.is_running = False
            self.view.showerror(title='ERROR', message='THERE IS A PROBLEM WITH YOUR INTERNET CONNECTION! \nPLEASE CHECK IT AND THEN TRY AGAIN.')
            return
        
        # catching the rest of the exceptions
        except Exception as e:
            self.is_running = False
            self.view.showerror(title='ERROR', message=f'AN ERROR OCCURRED: {str(e)}')
            return


    def correct(self, word): #correcting words
        corrected_word = TextBlob(word).correct()
        if word==corrected_word:
            return
        correct_meaning=self.meaning(corrected_word) 
                


        if correct_meaning:
            if self.view.askyesno(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!.\n DO YOU MEAN "{corrected_word}"?'):  
                    self.view.entry.delete(0,self.view.end)
                    self.view.entry.insert(self.view.end,corrected_word)
                    self.is_running=False
                    self.search()
            else:
                        return

    
    def say_word(self): #pronouncing word
        word=self.view.entry.get().strip()
        if word:
            word_thread=threading.Thread(target=self.word_synthesis)
            word_thread.daemon=True
            word_thread.start()


    def word_synthesis(self):
            word=self.view.entry.get().strip()

            if word == "" or word=="enter word here":
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                self.view.hide_spinner()
                return
            if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.showerror('ERROR',f'SORRY, PRONOUNCE "{word}"\n PLEASE ENTER A VALID WORD.')
                self.view.hide_spinner()
                return  # Exit the function if the word is empty
            
            self.view.read_word_button.config(state="disabled",bg="red")
            self.view.show_spinner()
            engine = pyttsx3.init()
            rate = engine.getProperty('rate')
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id)        
            engine.say(word)
            if engine._inLoop:
                self.view.read_word_button.config(state="normal",bg="lightblue")
                engine.endLoop()
                self.view.hide_spinner()
           # this function processes the voice 
            else:
                    self.view.read_word_button.config(state="normal")
                    engine.runAndWait()
                    self.view.hide_spinner()
            self.view.read_word_button.config(state="normal",bg="lightblue")
            self.view.hide_spinner()


    def read_sentence(self): #reading meanings
        word = str(self.model.full_history[0])
        meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
        if word == ""or meanings=="":
            return   
        if word:
            try:
                read_sentence_thread = threading.Thread(target=self.read_sentence_synthesis, args=(word,))
                read_sentence_thread.daemon=True
                read_sentence_thread.start()
            except ConnectionError:
                return
                 
        else:
            self.view.showerror(title="ERROR", message="PLEASE SEARCH FOR THE WORD FIRST!!")


    def read_sentence_synthesis(self, word):
        self.view.save_button.config(state="disabled")
        self.view.read_button.config(state="disabled")
        self.view.show_spinner()
        meanings = self.meaning(word)
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', int(self.view.speed_slider.get()))
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[self.view.selected_voice.get()].id)            
        # creating a dictionary object


        if meanings:
            for entry in meanings:
                engine.say( f"Word: {entry.get('word')}")
                engine.say( f"Phonetic: {entry.get('phonetic')}")
                if 'phonetics' in entry:
                    for phonetic in entry['phonetics']:
                        engine.say( f" - Text: {phonetic.get('text')}")
                if 'meanings' in entry:
                    for meaning in entry['meanings']:
                        engine.say( f"Part of Speech: {meaning.get('partOfSpeech')}")
                        engine.say( f" - Definition: \n")
                        for definition in meaning['definitions']:
                            engine.say( f"{definition.get('definition')}\n")
                            if 'example' in definition:
                                engine.say( f"   Example: {definition.get('example')}")
                        if meaning.get('synonyms'):
                            engine.say( f"Synonyms: {', '.join(meaning.get('synonyms'))}")
                        if meaning.get('antonyms'):
                            engine.say( f"Antonyms: {', '.join(meaning.get('antonyms'))}")
                        
            self.view.hide_spinner()
                
        else:
                self.view.read_button.config(state="normal")
                self.view.hide_spinner()
                
                return
                
        if engine._inLoop:
            engine.endLoop()
            self.view.while_end_image()
            self.view.read_button.config(state="normal")
            self.view.save_button.config(state="normal")
            self.view.hide_spinner()
            self.is_running=False
            # this function processes the voice 
        else:
                
                self.view.while_reading_image()
                self.view.read_button.config(state="normal")
                engine.runAndWait()
                self.view.hide_spinner()
                self.is_reading=True
        self.view.while_end_image()
        self.view.read_button.config(state="normal")
        self.view.save_button.config(state="normal")

    
    def increment(self,number): #increasing the progressbar

            self.view.progress["value"] = number+10
            self.view.saving_window.update()


    def meaning_save(self): #saving meaning
        if self.view.selected_save.get()==0:
            self.meaning_read_save()
            
        else:
            self.meaning_text_save()


    def meaning_text_save(self):
         saving_txt=threading.Thread(target=self.saving_text)
         saving_txt.daemon=True
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
            self.view.progress.pack() 
            self.view.progress.start()
            self.increment(40)
            with open(f"saved_meanings/{file_path}.txt","a",encoding='utf-8') as file:
                file.write(f"{self.model.full_history[0]}\n")  
                file.write(meanings)
                file.close() 
        self.increment(90)
                    
            
        self.view.progress.stop()
        self.view.progress.pack_forget()
        if self.view.askyesno(title="SAVING COMPLETE ", message="SAVED IN 'SAVED_MEANINGS' FOLDER.\n WOULD YOU LIKE TO OPEN fILE?"):
            self.model.open_file_txt(file_path)



    def meaning_read_save(self):
        save=threading.Thread(target=self.saving)
        save.daemon=True
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
            self.view.progress.pack() 
            self.view.progress.start()
            self.increment(2)
            engine = pyttsx3.init()
            self.increment(5)
            rate = engine.getProperty('rate')
            self.increment(10)
            engine.setProperty('rate', int(self.view.speed_slider.get()))
            self.increment(15)
            voices = engine.getProperty('voices')
            self.increment(20)
            engine.setProperty('voice', voices[self.view.selected_voice.get()].id) 
            self.increment(25)        
            engine.save_to_file(meanings, filename=f"saved_meanings/{file_path}.mp3")
            self.increment(25)        
            engine.runAndWait()
            self.increment(30)
            self.view.progress.stop()
            self.view.progress.pack_forget()
            if self.view.askyesno(title="SAVING COMPLETE ", message="SAVED IN 'SAVED_MEANINGS' FOLDER.\n WOULD YOU LIKE TO OPEN fILE?"):
                self.model.open_file(file_path)
            

    def clear_history(self): #function for clearing history
        self.view.tab3.bell()
        if self.view.askyesno("CLEAR", f"ARE YOU SURE YOU WANT TO CLEAR HISTORY? \n ALL SAVED DATA WILL BE LOST!!!"):
            self.model.full_history = []
            self.model.search_time = []
            self.model.save_data()
            self.validating()
            self.view.full.delete(0,self.view.end)


    
    def show_full_history(self): #displaying full history
        self.view.setup_history_window(self.model.full_history,self.model.search_time)


    

    def spell(self): #spelling word
        word=self.view.entry.get().strip()
        if word:
            spell_thread=threading.Thread(target=self.spell_synthesis)
            spell_thread.daemon==True
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
         


    def view_audiofolder(self): #opening saved_meanings folder
        self.model.open_folder()

    def copy(self):
            try:
                to_be_copied=self.view.tab1.selection_get()
                self.view.tab1.clipboard_clear()
                self.view.tab1.clipboard_append(to_be_copied)
                self.view.copy_label.config(text="Copied 📋")
            except Exception:
                 return
            self.view.tab1.after(5000, lambda:self.view.copy_label.config(text=""))

    def copy_meaning(self): #copying meanings into clipboard
            self.view.copy_label.config(text="Copied 📋")
            meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
            self.view.tab1.clipboard_clear()
            self.view.tab1.clipboard_append(meanings)
            self.view.tab1.after(5000, lambda:self.view.copy_label.config(text=""))

    def search_selected(self):
        try:
            new_word=self.view.meaning_box.selection_get()
            self.view.entry.delete(0, self.view.end)
            self.view.entry.insert(0, new_word)
            self.search()
        except Exception:
            return




    def cut(self): 
        if self.view.entry.get()=="" or self.view.entry.get()=="Enter Word Here":
                return
        else:
            self.view.tab1.clipboard_clear()
            self.view.tab1.clipboard_append(self.view.entry.get())
            self.view.entry.delete(0, self.view.end)
         

    def paste(self):
        if self.view.entry.get()=="" or self.view.entry.get()=="Enter Word Here":
            self.view.entry.delete(0, self.view.end)
            self.view.entry.configure(foreground="black")
        word_to_be_pasted=self.view.tab1.clipboard_get()
        self.view.entry.insert(0, word_to_be_pasted)
        

        
    def switch_tab(self, notebook, tab_index): #switching from one tab to another using index
        self.view.parent_tab.select(tab_index)



    def research(self,index):
        try:
            self.view.entry.configure(foreground="black")
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
    
