import json, codecs
import time
import tkinter as tk

import requests
from lxml import html
import getpass

def isEmpty (clanAttrArr):
    if (len(clanAttrArr) > 0):
        return clanAttrArr[0]
    return False

class MainApp:
    def __init__ (self, master):  
        # Define elements
        self.master = master
        self.master.title("DOAuction Tool by MaksimGBV")

        self.entry_nickname = tk.Entry(master, text="Nickname")
        self.entry_password = tk.Entry(master, text="Password")

        self.button_login = tk.Button(master, text="Login")
        self.button_sync = tk.Button(master, text="Resync")

        self.listbox_items = tk.Listbox(master, selectmode=tk.SINGLE, width="80")

        # Put elements in the window
        self.entry_nickname.grid(row=0, column=0)
        self.entry_password.grid(row=0, column=1)
        
        self.button_login.grid(row=0, column=2, sticky=tk.W+tk.E)
        self.button_sync.grid(row=0, column=3, sticky=tk.W+tk.E)

        self.listbox_items.grid(row=1, column=0, columnspan=4)

        # Set initial state
        self.entry_nickname.insert(0, "Nickname")
        self.entry_password.insert(0, "Password")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
