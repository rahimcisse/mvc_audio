import pyttsx3
import threading
from textblob import TextBlob
from view import DictionaryView
from model import DictionaryModel
from difflib import get_close_matches
import requests
from PyDictionary import PyDictionary



class DictionaryController:
    def __init__(self, root):
        self.model = DictionaryModel()    
        self.view = DictionaryView(root, self)  
        self.is_running = False      #assigning false to raise flag that program isn't searching for a word
        self.is_open=False      #raising a flag that full history widow isn't open
        self.displaying_researchable_words()      #this function helps the user to search a word that has been searched recently by clicking on it 




    def on_closing(self):
        if self.view.askyesno(title="QUIT" , message="ARE YOU SURE YOU WANT TO QUIT?") :
            self.view.close_history_window()   
            self.view.close_saving_window()    
            self.view.root.destroy()           



    def speed_slider_change(self,event):       #configuring the slider and slider label
        try:
            self.slider=self.view.speed_slider.get()    
            new_value='{: .1f}'.format(self.slider)     # formating the value from the slider into 1 decimal place
            self.view.speed_label.config(text=f"🐢          {new_value}          🐇")       #displaying the new value of the slider on the label
        except AttributeError:
            pass
    

    


    def likely(self, event):  # getting likely words

        def start(event):
            word = self.view.entry.get().lower().strip()  
            
            corrected_blob = TextBlob(word).correct()  # Correcting the word
            likely_corrected_word = str(corrected_blob)  # Converting the corrected word to a string

            if word != likely_corrected_word and likely_corrected_word not in self.model.likely_words:
                self.model.likely_words.append(likely_corrected_word)  # Append the corrected word

            # Get close matches from the likely words
            likely_word = get_close_matches(word, self.model.likely_words, cutoff=0.6, n=6)
            
            if likely_word:
                self.view.entry.config(values=likely_word)  # Update the combobox suggestions
            else:
                return

        # Start the process in a new thread
        start_likely = threading.Thread(target=start, args=(event,))
        start_likely.daemon = True  # Ensure the thread closes with the program
        start_likely.start()



    def search(self): #searching for word
        try:
            if not self.is_running:        #checking if the program is already searching for a meaning
                search_thread = threading.Thread(target=self.search_synthesis)      #passing the functionality into a thread
                search_thread.daemon=True           #exiting the thread if the program is closed
                search_thread.start()               #starting thread
        except Exception as e:
            self.view.showerror(title='ERROR', message=e)   

    server=0
    def search_synthesis(self):   
        global server  
        word = self.view.entry.get().lower().strip()    #getting the word 
        self.view.show_spinner()            

        
        if word == "" or word=="enter word here":       #checking if the entry is either empty . if yes, do nothing
            self.view.hide_spinner()
            self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
            return
        if word.isalpha()==False :
            # message box to display if the word variable has symbols and digits
                self.view.hide_spinner()
                self.view.showerror('ERROR',f'SORRY, CANNOT SEARCH FOR THE MEANING OF "{word}", PLEASE ENTER A SINGLE AND VALID WORD.')
                return  # Exit the function if the word is empty
        
        # corrected_word = TextBlob(word).correct()  
        # if corrected_word != word:
             
        if not self.is_running:
                    if self.view.selected_server.get()==0:
                        server=0
                    else:server=1
                    meanings = self.meaning(word)
                    if meanings:
                        self.model.add_to_history(word)     #adding to the history and saving it
                        self.view.meaning_label.config(text=f"Meaning({word})")     #displaying the word along next to the meaning label
                        if self.view.selected_server.get()==0:
                            self.view.update_meaning_box1(meanings)      #displaying the meanings in the meaning box
                            server=0
                        else:
                            self.view.update_meaning_box2(meanings)
                            server=1
                        
                        self.view.hide_spinner()    
                        self.displaying_researchable_words()        #reassembling the words displayed in the buttons that can be researchable
                    else:
                        self.view.hide_spinner()
                        self.correct(word)

                
                    
                     #if there are no meanings, it calls the correct function 
                            

                    self.is_running = False
                    self.view.hide_spinner()

    error=False
    
    def meaning(self, word):        #getting meanings
        global error
        global server
        try:
            if server==0:
                url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'     #storing the api into a variable
                response = requests.get(url)                #using requests to get the meanings from the url
                if response.status_code == 200:             #checking if there was a response or the meanings were found
                    meanings = response.json()              #reading it in the json format and storing it in a variable to be returned the user
                    
                
                    return meanings
                elif response.status_code==526:  
                        self.is_running = False
                        self.view.showerror(title='ERROR', message='SOMETHING WENT WRONG! \n PLEASE TRY AGAIN LATER')
                        error=True

                        return
                else:
                    print('Response', response)
            elif server==1:
                dict_obj = PyDictionary()
                meanings = dict_obj.meaning(word)

            

                return meanings


        
        except requests.exceptions.RequestException:    #catching   all errors
            self.is_running = False
            self.view.showerror(title='ERROR', message='THERE IS A PROBLEM WITH YOUR INTERNET CONNECTION! \nPLEASE CHECK IT AND THEN TRY AGAIN.')
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
        corrected_word = TextBlob(word).correct()       #using textblob to correct the word
        if self.view.selected_server.get()==0:
            global error

            #check if the corrected word is not equal to the word and also there is no ssl certificate error
            if corrected_word != word  and self.error==False:
                    if self.view.askyesno(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!.\n DO YOU MEAN "{corrected_word}"?'):  #showing the dialogbox with a suggested word
                            self.view.entry.delete(0,self.view.end)     
                            self.view.entry.insert(self.view.end,corrected_word)        
                            self.is_running=False           #assigning false to the is_running showing that it is no longer searching
                            self.search()
                            return
        else:
            if corrected_word != word:
                if self.view.askyesno(title='ERROR', message=f'"{word}" WAS NOT FOUND IN THE DICTIONARY!.\n DO YOU MEAN "{corrected_word}"?'):  #showing the dialogbox with a suggested word
                        self.view.entry.delete(0,self.view.end)     
                        self.view.entry.insert(self.view.end,corrected_word)        
                        self.is_running=False           #assigning false to the is_running showing that it is no longer searching
                        self.search()
            else:
                    self.view.showerror(title='ERROR', message='THERE IS A PROBLEM WITH YOUR INTERNET CONNECTION! \nPLEASE CHECK IT AND THEN TRY AGAIN.')
                    self.is_running = False
                    return
   


    
    def say_word(self): #pronouncing word
        word=self.view.entry.get().strip()
        if word:
            say_word_thread=threading.Thread(target=self.word_synthesis, args=(word,))
            say_word_thread.daemon=True
            say_word_thread.start()


    def word_synthesis(self,word):
        

            if word == "" or word=="Enter Word Here":
                self.view.showerror(title='ERROR', message='PLEASE ENTER THE WORD YOU WANT TO SEARCH FOR!!')
                self.view.hide_spinner()
                return
            
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
        meanings=self.view.meaning_box.get(1.0,self.view.end).strip()
        if meanings=="":
            return   
        word = str(self.model.full_history[0])
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
        global server
        self.view.save_button.config(state="disabled")
        self.view.read_button.config(state="disabled")
        self.view.show_spinner()
        
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', int(self.view.speed_slider.get()))
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[self.view.selected_voice.get()].id)            
        # creating a dictionary object



                
        if engine._inLoop:
            engine.endLoop()
            self.view.while_end_image()
            self.view.read_button.config(state="normal")
            self.view.save_button.config(state="normal")
            self.view.hide_spinner()
            self.is_running=False
            # this function processes the voice 
        else: 
            meanings = self.meaning(word)
            if meanings:
                if server==0 :
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
                    engine.say(word)
                        # read_sentence each meaning
                    for part_of_speech, meaning_list in meanings.items():
                        engine.say(part_of_speech)
                        for meaning in meaning_list:
                                engine.say(meaning)
                    self.view.hide_spinner()  

                    
                                
                    

            else:
                    self.view.read_button.config(state="normal")
                    self.view.hide_spinner()
                    
                    return
                
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
            self.read_meaning_save()
            
        else:
            self.text_meaning_save()


    def text_meaning_save(self):
         saving_text_thread=threading.Thread(target=self.saving_text)
         saving_text_thread.daemon=True
         saving_text_thread.start()


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
            self.model.open_file(f"/saved_meanings/{file_path}.txt")



    def read_meaning_save(self):
        save=threading.Thread(target=self.saving_audio)
        save.daemon=True
        save.start()


    def saving_audio(self):
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
                self.model.open_file(f"/saved_meanings/{file_path}.mp3")
            

    def clear_history(self): #function for clearing history
        self.view.tab3.bell()
        if self.view.askyesno("CLEAR", f"ARE YOU SURE YOU WANT TO CLEAR HISTORY? \n ALL SAVED DATA WILL BE LOST!!!"):
            try:
                self.model.full_history = []
                self.model.search_time = []
                self.model.save_data()
                self.displaying_researchable_words()
                self.view.full.delete(0,self.view.end)
            except Exception:
                 return


    
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

            if word == "" or word=="Enter Word Here":
                return

            
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
         


    def view_savedfolder(self): #opening saved_meanings folder
        self.model.open_file("/saved_meanings")


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



    def displaying_researchable_words(self):
            buttons = [ self.view.first_word,  self.view.second_word,  self.view.third_word,  self.view.fourth_word,  self.view.fifth_word,  self.view.sixth_word,  self.view.seventh_word,   self.view.eight_word]
            for i in range(8):
                if i < len(self.model.full_history) and  i < len(self.model.search_time):
                    buttons[i].config(text=f"{self.model.full_history[i]}          {self.model.search_time[i]}")
                else:
                     buttons[i].config(text=f"")

        
