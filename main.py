import tkinter as tk

root = tk.Tk()
tk.Label(root, text='Hello World').pack()
tk.Label(root, text='Hello World2').pack()

root.title("Sample Grid")

root.geometry("640x400")

root.mainloop()