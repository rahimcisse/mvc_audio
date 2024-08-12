import tkinter as tk  #importing tkinter module into file as tk to prevent conflicting
from tkinter import ttk #importing ttk from tkinter
from tkinter.scrolledtext import ScrolledText #importing a scrollable text box or feild
from tkinter.messagebox import showerror, askyesno ,askokcancel
from PIL import Image, ImageTk, ImageSequence #importing pillow to be used for the spinner 
from idlelib.tooltip import Hovertip #importing built-in module for displaying information when the mouse is delayed on a widget



class DictionaryView: #defining the dictionary view
    def __init__(self, root, controller): #defining the init function with two positional arguments root and controller
        self.controller = controller #storing the controller class into self.controller since the object is self and the same for the root
        self.root = root    
        self.end=tk.END  #since controller does not need tkinter imported into it because it is the functionality of the program,                                       
        self.askyesno=askyesno  #it stores tk.end into self.end variable so that i can use it inside my controller when i need to insert into a widget 
        self.askokcancel=askokcancel #Same appplies with the dialog boxes
        self.showerror=showerror


        
        self.root.title("Audio Dictionary With Spell Checks")  #setting the title,background and geometry or size of the window
        self.root.config(bg="grey")     
        self.root.geometry("600x650+400+1")
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing) #This calls on_closing in the controlller class whenever the user wants to close the window
        
        self.show_welcome_page()


        self.parent_tab = ttk.Notebook(self.root) # defining the parent window that manages all tabs in the program
        self.tab1 = ttk.Frame(self.parent_tab)  #creating frames to be added to the main notebook as tabs and storing them in variables 
        self.tab2 = ttk.Frame(self.parent_tab)
        self.tab3 = ttk.Frame(self.parent_tab)
        
        self.home_tab = tk.PhotoImage(file="images/home_image.png")
        self.recent_tab = tk.PhotoImage(file="images/recent_image.png")
        self.settings_tab = tk.PhotoImage(file="images/settings_image.png")
        self.welcome_image = tk.PhotoImage(file="images/welcome_image.gif")
    
        self.parent_tab.add(self.tab1, image=self.home_tab) #adding all those tabs into the main noebook and assigning them names
        self.parent_tab.add(self.tab3, image=self.recent_tab) 
        self.parent_tab.add(self.tab2, image=self.settings_tab)
       
        self.parent_tab.pack(expand=1, fill="both") #packing the notebook on the main window 


        self.setup_tab1()   #calling the functions defined under to setup the window
        self.setup_tab2()
        self.setup_tab3()
    


        self.menu = tk.Menu(self.root,bg="lightblue", tearoff=0) #defining menu to have its parent as the main window and storing menu into self.menu since that is the object
        self.menu.add_command(label="Search selected", command=self.controller.search_selected)  #and also tearoff by deefault is 1 which means the user can turn this menu into another window
        self.menu.add_separator()                                                             #adding commands to the menu andsepetators        self.menu.add_command(label="Pronounce word",command=self.controller.say_word)
        self.menu.add_command(label="Spell word",command=self.controller.spell)
        self.menu.add_command(label="Read meaning",command=self.controller.read_sentence)
        self.menu.add_separator()
        self.menu.add_command(label="Save meanings", command=lambda:self.setup_saving_window(root))
        self.menu.add_command(label="Copy meanings", command=self.controller.copy_meaning)
        self.menu.add_separator()
        self.menu.add_command(label="Cut", command=self.controller.cut)
        self.menu.add_command(label="Copy", command=self.controller.copy)
        self.menu.add_command(label="Paste", command=self.controller.paste)
    

        def do_popup(event):    #defining a funtion to show the popup menu
            try:
                self.menu.tk_popup(event.x_root, event.y_root) #showing the menu at the x and y positions of where the right button was clicked
            finally:
                self.menu.grab_release()    #release the popup after the user has chosen the functionality



        self.tab1.bind("<Button-3>", do_popup) #binding each of these widgets to the popup menu whenever the right mouse buttn is pressed with in them    
        self.meaning_box.bind("<Button-3>", do_popup)
        self.entry.bind("<Button-3>", do_popup)
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_focus_out)

    def on_entry_click(self,event):
        if self.entry.get() == "Enter Word Here":
            self.entry.delete(0, tk.END)
            self.entry.configure(foreground="black")

    def on_focus_out(self,event):
        if self.entry.get() == "":
            self.entry.insert(0, "Enter Word Here")
            self.entry.configure(foreground="gray") 


    
    def show_welcome_page(self):
        

        self.welcome_frame = tk.Frame(self.root, bg='#fdfafe')
        self.welcome_frame.place(relwidth=1, relheight=1)

        self.welcome2 = SpinnerLabel(self.welcome_frame, 'images/welcome_image.gif', size=(650,700)) #calling the spinnerclass defined at the bottom of the code
        self.welcome2.config(bg='white')

        self.welcome2.pack(fill="both")

        self.root.after(2600, self.welcome_frame.destroy)


    def setup_tab1(self): #defining a function to set up tab1
        self.audio_image = tk.PhotoImage(file="images/audio.png") #processing the audio image throught tkinter photoimage and storing it in self.audio_image variable
        self.audio_label=tk.Label(self.tab1, image=self.audio_image).pack(side="top", fill="x") #creating a label with the image defined on top

        tk.Label(self.tab1, text="Input Word:", justify="left", font=("Gabriola", 25)).pack(side="top") #creating an ""input word" label
        
        self.loading=ttk.Label(self.tab1) #setting the label in which the spinner will be placed on
        self.loading.pack() #packing the label uder the "input word" label

        self.spinner = SpinnerLabel(self.loading, "images/loading1.gif", size=(20, 20)) #calling the spinnerclass defined at the bottom of the code
        self.spinner.pack()    #packing iton the loading label and ttaing two positiona arguments directory and size
        self.spinner.pack_forget()  #making the spinner disappear from the label. We only want to show it when there's a search ongoing 
        
        self.entry = ttk.Combobox(self.tab1, width=45, font=("Cambria", 15), foreground="grey")    #creating our combobox entry 
        self.entry.pack(side="top", expand=1, fill="x")                         #packing it into tab1
        self.entry.insert(0, "Enter Word Here")
        self.entry.bind('<Return>', lambda event: self.controller.search())              #bingingg the entry so that whenever a key is released, it should calll the "likely" fuction inside the contoller
        self.entry.bind('<KeyRelease>', self.controller.likely)              #bingingg the entry so that whenever a key is released, it should calll the "likely" fuction inside the contoller


        self.read_word_button=tk.Button(self.entry,bd=4,text="🔊",bg="lightblue",command=self.controller.say_word,cursor="hand2") #crreatng the read button
        self.read_word_button.pack(side="right", padx=25)   #packing it into the window
        self.hover_popup(self.read_word_button, "Pronounce word") #when the mouse is delayed on the read button,it should show "pronounce word"


        self.search_image = tk.PhotoImage(file="images/search.png")
        self.search_button=tk.Button(self.tab1, bg="#f5f5f5", width=50, height=30, bd=5, image=self.search_image, command=self.controller.search,cursor="hand2")
        self.search_button.pack(side="top") #using an image on the button and also packing it on the window to be used for searching for word 
        self.hover_popup(self.search_button, "Search for meanings")
 
        self.meaning_label=tk.Label(self.tab1, text="Meanings", font=("Gabriola", 30))
        self.meaning_label.pack(side="top") 


        self.save_button=tk.Button(self.tab1,cursor="hand2",bg="#4ec3f8", height=1 ,bd=5,text="Save", command=lambda:self.setup_saving_window(self.root))   
        self.save_button.place(x=0,y=325) 
        self.hover_popup(self.save_button, "Save meanings of words in audio or text")

        self.copy_label=tk.Label(self.tab1,bg="#f0f0f0",font=("Segoe Script", 10),fg="#4ec3f8")   
        self.copy_label.place(x=50,y=330) 
      

        self.read_image = tk.PhotoImage(file="images/read.png")
        self.read_button = tk.Button(self.tab1, bg="#4ec3f8", width=110, height=350, bd=5,cursor="hand2", image=self.read_image, command=self.controller.read_sentence)
        self.read_button.pack(side="left")
        self.hover_popup(self.read_button, "Read meaning")
        
        self.meaning_box = ScrolledText(self.tab1, state="disabled", bg="white", width=45, font=("Candara", 15), height=15, bd=5, blockcursor=True)
        self.meaning_box.pack(side="top", expand=1, fill="x") #using the scrolled text from tkinter to preview meanings
        


    def setup_tab2(self):
        
        self.settings_image = tk.PhotoImage(file="images/settings.png")
        tk.Label(self.tab2, image=self.settings_image, justify="left").pack(side="top")

        tk.Label(self.tab2, text="Choose voice", justify="left", font=("Gabriola", 35)).pack(side="top")
        self.selected_voice = tk.IntVar()   #setting the variable to return an integar value
        tk.Radiobutton(self.tab2, text="Male", variable=self.selected_voice, value=0, font=10,cursor="hand2").pack(side="top")
        tk.Radiobutton(self.tab2, text="Female", variable=self.selected_voice, value=1, font=10,cursor="hand2").pack(side="top")
        self.selected_voice.set(1) #setting default as Female

        self.style=ttk.Style()
        self.style.configure('TScale',background='#f0f0f0') #configuring the slider to have a lightgrey background
        self.selected_speed=tk.IntVar 

        tk.Label(self.tab2, text="Set Reading Speed", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.speed_slider=ttk.Scale(self.tab2,from_=1,to=200,length=150, style='TScale',variable=self.selected_speed ,command=self.controller.speed_slider_change, orient="horizontal",cursor="hand2")
        self.speed_slider.pack(side="top", padx=10)
        self.hover_popup(self.speed_slider, "Increase or decrease speed of reading")
        
        self.speed_label=tk.Label(self.tab2, justify="left", font=("Gabriola", 15))
        self.speed_label.pack(side="top")
        self.speed_slider.set(125) #setting default speed as 125
        

    def setup_tab3(self):

        
        self.recent_image = tk.PhotoImage(file="images/recent.png")
        tk.Label(self.tab3, image=self.recent_image, bd=40).pack(side="top", fill="x")
        tk.Label(self.tab3, text="Most Recent Search:", justify="left", font=("Ink Free", 20)).pack(side="top")

        self.recent_box = tk.Text(self.tab3, state="disabled", bg="lightgrey", width=45, font=("Candara", 25), height=8, bd=5, blockcursor=True)
        self.recent_box.pack(side="top", expand=1, fill="x") #creating a textbox to house buttons to help search the history that has been clicked

        self.first_word=tk.Button(self.recent_box,text="" ,command=lambda: self.controller.research(0),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.first_word.pack (side="top",fill="x")
        self.hover_popup(self.first_word, "Research")

        self.second_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(1),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.second_word.pack (side="top",fill="x")
        self.hover_popup(self.second_word, "Research")

        self.third_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(2),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.third_word.pack (side="top",fill="x")
        self.hover_popup(self.third_word, "Research")

        self.fourth_word=tk.Button(self.recent_box ,text="",command=lambda: self.controller.research(3),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.fourth_word.pack (side="top",fill="x")
        self.hover_popup(self.fourth_word, "Research")

        self.fifth_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(4),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.fifth_word.pack (side="top",fill="x")
        self.hover_popup(self.fifth_word, "Research")

        self.sixth_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(5),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.sixth_word.pack (side="top",fill="x")
        self.hover_popup(self.sixth_word, "Research")

        self.seventh_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(6),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.seventh_word.pack (side="top",fill="x")
        self.hover_popup(self.seventh_word, "Research")

        self.eight_word=tk.Button(self.recent_box,text="",command=lambda: self.controller.research(7),bg="lightgrey", font=("Ariel",15),cursor="circle")
        self.eight_word.pack (side="top",fill="x")
        self.hover_popup(self.eight_word, "Research")


        self.clear=tk.Button(self.tab3,width=10, height=1 ,cursor="hand2",bd=5,bg="#ff6060",text="Clear History" ,command=self.controller.clear_history)
        self.clear.pack(side="left") #button for clearing all history
        self.hover_popup(self.clear, "Clear all history")

        self.show_button=tk.Button(self.tab3,width=15,bg="lightblue",cursor="hand2", height=1 ,bd=5,text="View Full History", command=self.controller.show_full_history)    
        self.show_button.pack(side="left") #button for showing all history
        self.hover_popup(self.show_button, "Display full history")


    is_saving=False #showing that the history window is closed
    def is_saving_boolean(self): #definig a function for closing the histor window
        if self.is_saving:
            self.saving_window.destroy()
            global is_open
            self.is_saving=False
        else:
            return
        

    def setup_saving_window(self,root):
        global is_saving
        if self.is_saving == False:
                self.saving_window=tk.Toplevel(root)
                
                tk.Label(self.saving_window, text="Save Recent Audio Meaning ", justify="left", font=("Gabriola", 35)).pack(side="top",pady=15)
                tk.Label(self.saving_window, text="Enter the name you want to save the file as", justify="left", font=("Gabriola", 25)).pack(side="top")

                self.selected_save = tk.IntVar()
                tk.Radiobutton(self.saving_window, text="Audio", variable=self.selected_save, value=0,cursor="hand2", font=3).pack(side="top")
                tk.Radiobutton(self.saving_window, text="Text", variable=self.selected_save, value=1,cursor="hand2", font=3).pack(side="top")
        
                self.file_name=tk.Entry(self.saving_window, font=30,bd=10,bg="lightgrey",border=5)
                self.file_name.pack(side="top",pady=20) #save as name
                self.file_name.focus_set()
                

                self.save_audio=tk.Button(self.saving_window,bd=5,bg="lightblue",font=30, command=self.controller.meaning_save,cursor="hand2", text="Save meanings")
                self.save_audio.pack(side="top",pady=10) #button for saving


                self.openfolder=tk.Button(self.saving_window,bd=5,bg="lightblue",font=10, text="Downloads",cursor="hand2",  command=self.controller.view_audiofolder)
                self.openfolder.pack(side="top") #opening the folder which the saved meanings are
                self.hover_popup(self.save_button, "View all saved audio")

                self.progress=ttk.Progressbar(self.saving_window, length=200) #creating progressbar 
                self.progress.pack(side="top",pady=50) 
                self.progress.pack_forget()

                self.done=tk.Button(self.saving_window,bd=5,bg="lightblue",font=20, text="Done",cursor="hand2",  command=lambda:self.saving_window.destroy())
                self.done.pack(side="bottom",pady=20) #button for finishing the saves

                self.is_saving=True #raising a flag that the history window is open
                self.saving_window.protocol("WM_DELETE_WINDOW", self.is_saving_boolean)
                

    is_open=False #showing that the history window is closed
    def boolean(self): #definig a function for closing the histor window
        if self.is_open:
            self.history_window.destroy()
            global is_open
            self.is_open=False
        else:
            return
        

    def setup_history_window(self,word_model,time_model):
            global is_open
            if self.is_open == False:
                self.history_window=tk.Toplevel(self.root) #creating history window
                self.history_window.title("History")
                self.history_window.geometry("540x500+1+100")
                self.history_window.resizable(False,False)

                tk.Label(self.history_window, text="(  Word   , Date Time Year )", justify="left" ,background="#f2ffff", font=("Segoe Script", 20)).pack(side="top",fill="x")
                self.full=ScrolledText(self.history_window,fg="black",state="disabled", background="#f2ffff", bd=1,font=("Javanese Text",20),padx=12)
                self.full.pack(side="top", fill="both")

                self.full.config(state="normal")
                word_model.reverse() #reversing both lists
                time_model.reverse()
                
                for line in zip(word_model,time_model): #inserting into scrolled text
                    self.full.insert(1.0, f"{line}\n")
                word_model.reverse()
                time_model.reverse()

                self.full.config(state="disabled")
                self.is_open=True #raising a flag that the history window is open

                self.history_window.protocol("WM_DELETE_WINDOW", self.boolean)
                    
            else:
                    return




    def update_meaning_box(self, meanings): #inserting into meaningbox
        self.meaning_box.config(state="normal")
        self.meaning_box.delete('1.0', tk.END)

    # Clear the ScrolledText widget first
        if meanings:
                self.my_list=[]
                for entry in meanings:
                    self.meaning_box.insert(tk.END, f"Word: {entry.get('word')}\n")
                    self.my_list.append(f"Word: {entry.get('word')}\n")
                    self.meaning_box.insert(tk.END, f"Phonetic: {entry.get('phonetic')}\n")
                    self.my_list.append(f"Phonetic: {entry.get('phonetic')}\n")
                    if 'phonetics' in entry:
                        for phonetic in entry['phonetics']:
                            self.meaning_box.insert(tk.END, f" - Text: {phonetic.get('text')}\n")
                            self.my_list.append(f" - Text: {phonetic.get('text')}\n")
                    if 'meanings' in entry:
                        for meaning in entry['meanings']:
                            self.meaning_box.insert(tk.END, f"Part of Speech: {meaning.get('partOfSpeech')}\n")
                            self.my_list.append(f"Part of Speech: {meaning.get('partOfSpeech')}\n")
                            self.meaning_box.insert(tk.END, f" - Definition: \n")
                            self.my_list.append(f" - Definition: \n")
                            for definition in meaning['definitions']:
                                self.meaning_box.insert(tk.END, f"{definition.get('definition')}\n")
                                self.my_list.append(f"{definition.get('definition')}\n")
                                if 'example' in definition:
                                    self.meaning_box.insert(tk.END, f"   Example: {definition.get('example')}\n")
                                    self.my_list.append(f"   Example: {definition.get('example')}\n")
                            if meaning.get('synonyms'):
                                self.meaning_box.insert(tk.END, f"Synonyms: {', '.join(meaning.get('synonyms'))}\n")
                                self.my_list.append(f"Synonyms: {', '.join(meaning.get('synonyms'))}\n")
                            if meaning.get('antonyms'):
                                self.meaning_box.insert(tk.END, f"Antonyms: {', '.join(meaning.get('antonyms'))}\n")
                                self.my_list.append(f"Antonyms: {', '.join(meaning.get('antonyms'))}\n")
                
        else:
            return
        self.meaning_box.config(state="disabled")


    def show_spinner(self):#function for showing spinner
        self.spinner.pack()


    def hide_spinner(self):
        self.spinner.pack_forget()


    def hover_popup(self, widget, message):
        Hovertip(widget, message) 


    def while_reading_image(self):
        self.stop_image = tk.PhotoImage(file="images/stop.png")
        self.read_button.config(bg='red', image=self.stop_image)

    
    def while_end_image(self):
        self.stop_image = tk.PhotoImage(file="images/read.png")
        self.read_button.config(bg="#4ec3f8", image=self.stop_image)


class SpinnerLabel(tk.Label):
    def __init__(self, master, gif_path, size):
        tk.Label.__init__(self, master)
        self.size = size
        self.frames = [ImageTk.PhotoImage(img.resize(self.size, Image.Resampling.LANCZOS)) 
                       for img in ImageSequence.Iterator(Image.open(gif_path))]
        self.index = 0
        self.update_label()

    def update_label(self):
        self.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(100, self.update_label)  # Adjust the delay as necessary



