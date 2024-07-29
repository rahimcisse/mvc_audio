import tkinter as tk  #importing tkinter module into file as tk to prevent conflicting
from tkinter import ttk 
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror, askyesno ,askokcancel
from PIL import Image, ImageTk, ImageSequence #importing pillow to be used for the spinner 
from model import DictionaryModel
from idlelib.tooltip import Hovertip



class DictionaryView:
    def __init__(self, root, controller):
        self.controller = controller
        self.root = root
        self.end=tk.END
        self.askyesno=askyesno
        self.askokcancel=askokcancel
        self.showerror=showerror


        
        self.root.title("Audio Dictionary With Spell Checks")
        self.root.config(bg="grey")
        self.root.geometry("650x700+400+1")
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)
        

        self.parent_tab = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.parent_tab)
        self.tab2 = ttk.Frame(self.parent_tab)
        self.tab3 = ttk.Frame(self.parent_tab)
        self.tab4 = ttk.Frame(self.parent_tab)


        self.parent_tab.add(self.tab1, text="Home")
        self.parent_tab.add(self.tab3, text="Recent")
        self.parent_tab.add(self.tab2, text="Settings")
        self.parent_tab.add(self.tab4, text="Save As")
        self.parent_tab.pack(expand=1, fill="both")
        self.parent_tab.hide(3)

        
        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()


        self.menu = tk.Menu(root,bg="lightblue", tearoff=0)
        self.menu.add_command(label="Spell word",command=self.controller.spell)
        self.menu.add_command(label="Read meaning",command=self.controller.read_sentence)
        self.menu.add_separator()
        self.menu.add_command(label="Search", command=self.controller.search)
        self.menu.add_separator()
        self.menu.add_command(label="Save audio", command=lambda:(self.parent_tab.add(self.tab4),self.controller.switch_tab(self.parent_tab,3)))
        self.menu.add_separator()
        self.menu.add_command(label="Copy meanings", command=self.controller.copy_meaning)
        self.menu.add_command(label="Cut", command=self.controller.cut)
        self.menu.add_command(label="Paste", command=self.controller.paste)
    

        def do_popup(event):
            try:
                self.menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu.grab_release()



        self.tab1.bind("<Button-3>", do_popup)    
        self.meaning_box.bind("<Button-3>", do_popup)
        self.entry.bind("<Button-3>", do_popup)
        


    def setup_tab1(self):
        self.audio_image = tk.PhotoImage(file="images/audio.png")
        self.audio_label=tk.Label(self.tab1, image=self.audio_image).pack(side="top", fill="x")
        tk.Label(self.tab1, text="Input Word:", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.loading=ttk.Label(self.tab1)
        self.loading.pack()

        self.spinner = SpinnerLabel(self.loading, "images/loading1.gif", size=(20, 20))
        self.spinner.pack()
        self.spinner.pack_forget()
        
        self.entry = ttk.Combobox(self.tab1, width=45, font=("Cambria", 15))
        self.entry.pack(side="top", expand=1, fill="x")
        self.entry.bind('<KeyRelease>', self.controller.likely)

        self.read_word_button=tk.Button(self.entry,bd=4,text="🔊",bg="lightblue",command=self.controller.say_word)
        self.read_word_button.pack(side="right", padx=25)
        self.hover_popup(self.read_word_button, "Pronounce word")

        self.preview = tk.Text(self.tab1, width=10, height=1, bg="#ececec", font=("Times New Roman", 20), state="disabled")
        self.preview.pack(pady=10)

        self.search_image = tk.PhotoImage(file="images/search.png")
        self.search_button=tk.Button(self.tab1, bg="#f5f3ed", width=50, height=30, bd=5, image=self.search_image, command=self.controller.search)
        self.search_button.pack(side="top")
        self.hover_popup(self.search_button, "Search for meanings")

        self.meaning_image = tk.PhotoImage(file="images/meaning_image.png")
        tk.Label(self.tab1, image=self.meaning_image).pack(side="top")

        self.read_image = tk.PhotoImage(file="images/read_man.png")
        self.read_button = tk.Button(self.tab1, bg="#70c2f2", width=110, height=300, bd=5, image=self.read_image, command=self.controller.read_sentence)
        self.read_button.pack(side="left")
        self.hover_popup(self.read_button, "Read meaning")
        

        self.meaning_box = ScrolledText(self.tab1, state="disabled", bg="white", width=45, font=("Candara", 15), height=15, bd=5, blockcursor=True)
        self.meaning_box.pack(side="top", expand=1, fill="x")


    def setup_tab2(self):
        
        self.settings_image = tk.PhotoImage(file="images/settings.png")
        tk.Label(self.tab2, image=self.settings_image, justify="left").pack(side="top")

        tk.Label(self.tab2, text="Choose voice", justify="left", font=("Gabriola", 35)).pack(side="top")
        self.selected_voice = tk.IntVar()
        tk.Radiobutton(self.tab2, text="Male", variable=self.selected_voice, value=0, font=10).pack(side="top")
        tk.Radiobutton(self.tab2, text="Female", variable=self.selected_voice, value=1, font=10).pack(side="top")
        self.selected_voice.set(1)

        self.style=ttk.Style()
        self.style.configure('TScale',background='lightgrey')
        self.selected_speed=tk.IntVar

        tk.Label(self.tab2, text="Set Reading Speed", justify="left", font=("Gabriola", 25)).pack(side="top")
        self.speed_slider=ttk.Scale(self.tab2,from_=1,to=200,style='TScale',variable=self.selected_speed ,command=self.controller.speed_slider_change, orient="horizontal")
        self.speed_slider.pack(side="top")
        self.hover_popup(self.speed_slider, "Increase or decrease speed of reading")
        
        self.speed_label=tk.Label(self.tab2, justify="left", font=("Gabriola", 15))
        self.speed_label.pack(side="top")
        self.speed_slider.set(125)
        

    def setup_tab3(self):

        
        self.recent_image = tk.PhotoImage(file="images/recent.png")
        tk.Label(self.tab3, image=self.recent_image, bd=40).pack(side="top", fill="x")
        tk.Label(self.tab3, text="Most Recent Search:", justify="left", font=("Ink Free", 20)).pack(side="top")

        self.recent_box = tk.Text(self.tab3, state="disabled", bg="lightgrey", width=45, font=("Candara", 25), height=8, bd=5, blockcursor=True)
        self.recent_box.pack(side="top", expand=1, fill="x")

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


        self.clear=tk.Button(self.tab3,width=10, height=1 ,bd=5,bg="#ff6060",text="Clear History" ,command=self.controller.clear_history)
        self.clear.pack(side="left")
        self.hover_popup(self.clear, "Clear all history")

        self.show_button=tk.Button(self.tab3,width=15,bg="lightblue", height=1 ,bd=5,text="View Full History", command=self.controller.show_full_history)    
        self.show_button.pack(side="left")
        self.hover_popup(self.show_button, "Display full history")

        self.save_button=tk.Button(self.tab3,width=15,bg="lightblue", height=1 ,bd=5,text="Save Audio", command=lambda:(self.parent_tab.add(self.tab4),self.controller.switch_tab(self.parent_tab,3)))    ##############
        self.save_button.pack(side="right")
        self.hover_popup(self.save_button, "Save audio")


    def setup_tab4(self):
        
        tk.Label(self.tab4, text="Save Recent Audio Meaning As", justify="left", font=("Gabriola", 35)).pack(side="top",pady=50)
        tk.Label(self.tab4, text="Input Save As Name", justify="left", font=("Gabriola", 25)).pack(side="top")

        self.file_name=tk.Entry(self.tab4, font=30)
        self.file_name.pack(side="top",pady=20)

        self.save_audio=tk.Button(self.tab4,bd=5,bg="lightblue",font=40, command=self.controller.meaning_read_save, text="Save read meaning")
        self.save_audio.pack(side="top",pady=10)


        self.openfolder=tk.Button(self.tab4,bd=5,bg="lightblue",font=20, text="Downloads",  command=self.controller.view_audiofolder)
        self.openfolder.pack(side="top")
        
        self.progress=ttk.Progressbar(self.tab4, length=200)
        self.progress.step(100)
        self.progress.pack(side="top",pady=50)

        self.done=tk.Button(self.tab4,bd=5,bg="lightblue",font=20, text="Done",  command=lambda:(self.controller.switch_tab(self.parent_tab,0),self.parent_tab.hide(3)))
        self.done.pack(side="bottom",pady=20)

    is_open=False
    def boolean(self):
        if self.is_open:
            self.history_window.destroy()
            global is_open
            self.is_open=False
        else:
            return
        

    def setup_history_window(self,word_model,time_model):
            global is_open
            if self.is_open == False:
                self.history_window=tk.Tk()
                self.history_window.title("History")
                self.history_window.geometry("540x500+1+100")
                self.history_window.resizable(False,False)
                tk.Label(self.history_window, text="(  Word   , Date Time Year )", justify="left" ,background="#f2ffff", font=("Segoe Script", 25)).pack(side="top",fill="x")
                self.full=ScrolledText(self.history_window,fg="black",state="disabled", background="#f2ffff", bd=1,font=("Javanese Text",20),padx=12)
                self.full.pack(side="top", fill="both")

                self.full.config(state="normal")
                word_model.reverse()
                time_model.reverse()
                
                for line in zip(word_model,time_model):
                    self.full.insert(1.0, f"{line}\n")
                word_model.reverse()
                time_model.reverse()

                self.full.config(state="disabled")
                self.is_open=True

                self.history_window.protocol("WM_DELETE_WINDOW", self.boolean)
                    
            else:
                    return


    def update_preview(self, word):
        self.preview.config(state="normal")
        self.preview.delete(1.0, tk.END)
        self.preview.insert(1.0, word)
        self.preview.config(state="disabled")


    def update_meaning_box(self, meanings):
        self.meaning_box.config(state="normal")
        self.meaning_box.delete('1.0', tk.END)
        for pos, meaning in enumerate(meanings, start=1):
            self.meaning_box.insert(tk.END, f"{pos}. {meaning.capitalize()}:\n")
            self.meaning_box.insert(tk.END, f"{', '.join(meanings[meaning])}\n\n")
        self.meaning_box.config(state="disabled")


    def show_spinner(self):
        self.spinner.pack()


    def hide_spinner(self):
        self.spinner.pack_forget()


    def hover_popup(self, widget, message):
        Hovertip(widget, message)




class SpinnerLabel(tk.Label):
    def __init__(self, master, gif_path, size, *args, **kwargs):
        tk.Label.__init__(self, master, *args, **kwargs)
        self.size = size
        self.frames = [ImageTk.PhotoImage(img.resize(self.size, Image.Resampling.LANCZOS)) 
                       for img in ImageSequence.Iterator(Image.open(gif_path))]
        self.index = 0
        self.update_label()

    def update_label(self):
        self.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.after(100, self.update_label)  # Adjust the delay as necessary



if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryView(root, None)
    root.mainloop()
