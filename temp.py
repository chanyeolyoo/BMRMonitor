import tkinter as tk
from tkinter import ttk
# from random import choice
import numpy as np


root = tk.Tk()

root.tk.eval ("" "ttk :: style map Treeview -foreground {disabled SystemGrayText selected SystemHighlightText} -background {disabled SystemButtonFace selected System Highlight}"" ")


tree=ttk.Treeview(root)

# s = ttk.Style()
# s.theme_use('clam')

# colors = ['#008001', '#FFFF00', '#000000']
colors = ["#E8E8E8", "#DFDFDF", "white"]


tree["columns"]=("one","two","three")
tree.column("#0", width=60, minwidth=30, stretch=tk.NO)
tree.column("one", width=120, minwidth=30, stretch=tk.NO)

tree.heading("#0",text="0",anchor=tk.W)
tree.heading("one", text="1",anchor=tk.W)

for i in range(10):
    tree.insert("", i, text="Elem"+str(i), values=("none"))

tree.pack(side=tk.TOP,fill=tk.X)


for c in colors:
    tree.tag_configure(c, background=c)  
def recolor():
    for child in tree.get_children():
        idx = np.random.randint(len(colors))
        tree.item(child, tags=(colors[idx],), values=(colors[idx]))




b = tk.Button(root, text="Change", command=recolor)
b.pack()


root.mainloop()