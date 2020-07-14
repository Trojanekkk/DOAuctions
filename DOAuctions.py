import json, codecs
import time
import tkinter as tk
import re

import requests
from lxml import html

def isEmpty (clanAttrArr):
    if (len(clanAttrArr) > 0):
        return clanAttrArr[0]
    return False

class MainApp:
    def __init__ (self, master):  
        # Define elements
        self.master = master
        self.master.title("DOAuction Tool by MaksimGBV")

        self.var_countdown_hour = tk.StringVar()

        self.label_countdown = tk.Label(master, textvariable=self.var_countdown_hour)

        self.entry_nickname = tk.Entry(master)
        self.entry_password = tk.Entry(master)
        self.entry_price = tk.Entry(master)
        self.entry_interval = tk.Entry(master)

        self.button_login = tk.Button(master, text="Login", command=self.login)
        self.button_sync = tk.Button(master, text="Resync", command=self.sync)
        self.button_bid = tk.Button(master, text="Bid once at the end", command=self.bid)
        self.button_zombie = tk.Button(master, text="Zombie bidding", command=self.zombie)

        self.listbox_items = tk.Listbox(master, selectmode=tk.SINGLE, width="90", height="15")

        # Put elements in the window
        self.label_countdown.grid(row=0, column=2)

        self.entry_nickname.grid(row=0, column=0)
        self.entry_password.grid(row=0, column=1)
        self.entry_price.grid(row=2, column=0)
        self.entry_interval.grid(row=2, column=1)
        
        self.button_login.grid(row=0, column=3, sticky=tk.W+tk.E)
        self.button_sync.grid(row=0, column=4, sticky=tk.W+tk.E)
        self.button_bid.grid(row=2, column=2, columnspan=2, sticky=tk.W+tk.E)
        self.button_zombie.grid(row=2, column=4, sticky=tk.W+tk.E)

        self.listbox_items.grid(row=1, column=0, columnspan=5)

        # Set initial state
        self.var_countdown_hour.set("Left: 00:00")
        self.entry_nickname.insert(0, "Nickname")
        self.entry_password.insert(0, "Password")
        self.entry_price.insert(0, "Price in cr")
        self.entry_interval.insert(0, "Interval in s")
        self.listbox_items.configure(font=("Consolas", 10))

    def login(self):
        self.nickname = self.entry_nickname.get()
        password = self.entry_password.get()
        self.session_requests = requests.session()
        self.login_url = 'https://www.darkorbit.pl/?lang=pl&ref_sid=b9d0df61f0c484f8c0c2b74fc19f9107&ref_pid=22&__utma=-&__utmb=-&__utmc=-&__utmx=-&__utmz=-&__utmv=-&__utmk=38294271'
        result = self.session_requests.get(self.login_url)

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
            headers = dict(referer=self.login_url)
        )
    
        if result.status_code == 200:
            self.entry_nickname.config(state="disabled")

            self.entry_password.delete(0, tk.END)
            self.entry_password.insert(0, "*" * len(password))
            self.entry_password.config(state="disabled")
            
            self.button_login.config(state="disabled")

            self.getAuctionState()

    def sync(self):
        self.getAuctionState()

    def getAuctionState (self):
        self.listbox_items.delete(0, tk.END)

        result = self.session_requests.get(
            "https://pl2.darkorbit.com/indexInternal.es?action=internalAuction",
            headers = dict(referer=self.login_url)
        )

        tree = html.fromstring(result.text)

        cd = re.findall(r'\d+', re.findall(r'counterWeek.*myBidCount', result.text, re.DOTALL)[0])
        countdown = {
            "seconds" : cd[0],
            "minutes" : cd[1],
            "hours" : cd[2],
            "days" : cd[3]
        }

        self.var_countdown_hour.set("Left: {}:{}".format(countdown['minutes'], countdown['seconds']))

        self.auction_item = ['ITEM NAME'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_name_col']/text()")]
        self.auction_winner = ['WINNER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_highest']/text()")]
        self.auction_current = ['CURRENT OFFER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_current']/text()")]
        self.auction_you = ['YOUR OFFER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_you']/text()")]

        column_item = self.createColumn(self.auction_item)
        column_winner = self.createColumn(self.auction_winner, True)
        column_current = self.createColumn(self.auction_current, True)
        column_you = self.createColumn(self.auction_you, True)

        for i, item in enumerate(self.auction_item):
            self.listbox_items.insert(
                tk.END, 
                "{}  {}  {}  {}".format(
                    column_item[i], 
                    column_current[i], 
                    column_you[i],
                    column_winner[i]
                )
            )

    def bid(self):
        pass

    def zombie(self):
        pass
    
    def createColumn (self, arr, justifyRight = False):
        longest = len(max(arr, key=len))
        
        tmp = []
        for element in arr:
            whitespace = ' ' * (longest - len(element) + 1)
            if justifyRight:
                tmp.append(whitespace + element)
            else:
                tmp.append(element + whitespace)
            
        return tmp

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
