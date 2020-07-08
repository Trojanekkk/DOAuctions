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

        self.button_login = tk.Button(master, text="Login", command=self.login)
        self.button_sync = tk.Button(master, text="Resync", command=self.sync)

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

    def login(self):
        self.nickname = self.entry_nickname.get()
        password = self.entry_password.get()
        self.session_requests = requests.session()
        login_url = 'https://www.darkorbit.pl/?lang=pl&ref_sid=b9d0df61f0c484f8c0c2b74fc19f9107&ref_pid=22&__utma=-&__utmb=-&__utmc=-&__utmx=-&__utmz=-&__utmv=-&__utmk=38294271'
        result = self.session_requests.get(login_url)

        tree = html.fromstring(result.text)
        auth_token = list(set(tree.xpath("//input[@name='reloadToken']/@value")))[0]
        login_destination = list(set(tree.xpath("//form[@name='bgcdw_login_form']/@action")))[0]

        payload = {
            'username': self.nickname,
            'password': password,
            'reloadToken': auth_token
        }

        result = self.session_requests.post(
            login_destination,
            payload,
            headers = dict(referer=login_url)
        )
    
        if result.status_code == 200:
            self.entry_nickname.config(state="disabled")

            self.entry_password.delete(0, tk.END)
            self.entry_password.insert(0, "*" * len(password))
            self.entry_password.config(state="disabled")
            
            self.button_login.config(state="disabled")

    def sync(self):
        pass

    def getAuctionState (self):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
