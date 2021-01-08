import subprocess
import os
import tkinter as tk

root= tk.Tk() 
   
canvas1 = tk.Canvas(root, width = 400, height = 250) 
canvas1.pack()

def start_windows(): 
     os.system('cmd /c "pip install --upgrade pip"')
     os.system('cmd /c "pip install pylint pyqt5 "')
def start_Linux():
    os.system("pip install --upgrade pip")
    os.system("pip install pylint pyqt5") 
 

button1 = tk.Button (root, text='Windows',command=start_windows,bg='green',fg='white')
canvas1.create_window(50, 130, window=button1)
button2 = tk.Button (root, text='Linux base systems',command=start_Linux,bg='green',fg='white')
canvas1.create_window(166, 130, window=button2)
root.mainloop()
