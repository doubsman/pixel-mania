from tkinter import *

def mouse(event=None):
    x = win.winfo_pointerx()
    y = win.winfo_pointery()
    canvas.create_oval(x-10,y-10,x+10,y+10,fill='red')
    win.after(10,mouse)

win = Tk()
win.overrideredirect(True)
win.state("zoomed")
win.lift()
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "white")
canvas = Canvas(win,bg='white')
canvas.pack(side=TOP, expand=True, fill=BOTH)
mouse()
win.mainloop()