from tkinter import *

window = Tk()
# window.geometry("1000x500") #Width x Height

logo = PhotoImage(file="xxx")
Label (window, image=logo, bg="#f0f0f0") .grid(row=0, column=0)

T = Text(window, height=2, width=30)
T.insert(END, "Just a text Widget\nin two lines\n")
T.grid(row=1, column=0, sticky=S)

window.grid_rowconfigure(1,weight=1)

window.mainloop()