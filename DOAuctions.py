import json, codecs
import time
import hashlib
import tkinter as tk
import re
import random
import datetime 

import requests
from lxml import html

def isEmpty (clanAttrArr):
    if (len(clanAttrArr) > 0):
        return clanAttrArr[0]
    return False

class MainApp:
    def __init__ (self, master): 
        self.actions_list = [
            "Manual resync", 
            "Show SID", 
            "Clear tracked"
        ]
        
        self.tracked_auction_type = []
        self.tracked_item_name = []
        self.tracked_loot_id = []
        self.tracked_credits = []

        # Define elements
        self.master = master
        self.master.title("DOAuction Tool by MaksimGBV")

        self.var_countdown_hour = tk.StringVar()
        self.var_other = tk.StringVar()
        self.var_price = tk.IntVar()

        self.label_countdown = tk.Label(master, textvariable=self.var_countdown_hour)

        self.entry_nickname = tk.Entry(master)
        self.entry_password = tk.Entry(master)
        self.entry_price = tk.Entry(master, textvariable=self.var_price)
        self.entry_interval = tk.Entry(master)

        self.button_login = tk.Button(master, text="Login", command=self.login)
        self.button_sync = tk.OptionMenu(self.master, self.var_other, *self.actions_list)
        self.button_bid = tk.Button(master, text="Bid once at the end", command=self.addTracked)
        self.button_zombie = tk.Button(master, text="Zombie bidding", command=self.zombie)

        self.scrlbar_auction = tk.Scrollbar(master)

        self.listbox_items = tk.Listbox(master, selectmode=tk.SINGLE, width="90", height="13", yscrollcommand=self.scrlbar_auction.set)
        self.listbox_status = tk.Listbox(master, height="3")
        self.listbox_tracked = tk.Listbox(master, height="3")

        # Set initial state
        self.var_countdown_hour.set("Left: 00:00")
        self.var_other.set("More")
        self.var_other.trace("w", self.other_actions)
        self.entry_nickname.insert(0, "Nickname")
        self.entry_nickname.focus_set()
        self.entry_password.insert(0, "Password")
        self.var_price.set("Price in cr")
        # self.entry_price.insert(0, "Price in cr")
        self.entry_interval.insert(0, "Interval in s")
        self.listbox_items.configure(font=("Consolas", 10))
        self.scrlbar_auction.config(command=self.listbox_items.yview)
        self.log("STATUS: Initialization... DONE")

        # Put elements into the window
        self.label_countdown.grid(row=0, column=2)

        self.entry_nickname.grid(row=0, column=0)
        self.entry_password.grid(row=0, column=1)
        self.entry_price.grid(row=2, column=0)
        self.entry_interval.grid(row=2, column=1)
        
        self.button_login.grid(row=0, column=3, sticky=tk.W+tk.E)
        self.button_sync.grid(row=0, column=4, columnspan=2, sticky=tk.W+tk.E)
        self.button_bid.grid(row=2, column=2, columnspan=2, sticky=tk.W+tk.E)
        self.button_zombie.grid(row=2, column=4, columnspan=2, sticky=tk.W+tk.E)

        self.scrlbar_auction.grid(row=1, column=5, sticky=tk.N+tk.S)

        self.listbox_items.grid(row=1, column=0, columnspan=5)
        self.listbox_status.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E)
        self.listbox_tracked.grid(row=3, column=2, columnspan=4, sticky=tk.W+tk.E)

    def login(self):
        self.nickname = self.entry_nickname.get()
        password = self.entry_password.get()

        if self.auth():
            self.log("STATUS: Checking license DONE")
            self.session_requests = requests.session()
            self.login_url = 'https://www.darkorbit.pl/'
            result = self.session_requests.get(self.login_url)
            self.log("STATUS: Collecting login info & tokens DONE")

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

            self.log("STATUS: Logging in DONE")
        
            if result.status_code == 200:
                self.entry_nickname.config(state="disabled")

                self.entry_password.delete(0, tk.END)
                self.entry_password.insert(0, "*" * len(password))
                self.entry_password.config(state="disabled")
                
                self.button_login.config(state="disabled")

                

                self.getAuctionState()
        else:
            self.log("ATTENTION: Checking license FAILED")

    def sync(self):
        self.master.after_cancel(self.timer)
        self.getAuctionState()

    def getAuctionState(self):
        self.listbox_items.delete(0, tk.END)

        self.auction_url = "https://pl2.darkorbit.com/indexInternal.es?action=internalAuction"
        result = self.session_requests.get(
            self.auction_url,
            headers = dict(referer=self.login_url)
        )
        self.log("STATUS: Getting auction status DONE")
        self.tic = time.perf_counter()

        tree = html.fromstring(result.text)

        cd = re.findall(r'\d+', re.findall(r'counterWeek.*myBidCount', result.text, re.DOTALL)[0])
        countdown = {
            "seconds" : int(cd[0]),
            "minutes" : int(cd[1]),
            "hours" : int(cd[2]),
            "days" : int(cd[3])
        }

        self.hour_left = 0
        self.hour_countdown_interval = random.randint(90, 180)
        self.processCountdown(countdown)

        self.sid = re.findall(r"'dosid=.*'", result.text)[0][7:-1]

        self.auction_item = ['ITEM NAME'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_name_col']/text()")]
        self.auction_winner = ['WINNER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_highest']/text()")]
        self.auction_current = ['CURRENT OFFER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_current']/text()")]
        self.auction_you = ['YOUR OFFER'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_you']/text()")]
        self.item_loot_id = ['LOOT ID'] + [x.strip() for x in tree.xpath("//td[@class='auction_item_instant']/input[5]/@value")]
        self.bid_destination = tree.xpath("//form[@name='placeBid']/@action")[0]

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

    def addTracked(self):
        if not self.listbox_items.curselection():
            self.log("ATTENTION: Do not selected any item")
            return 0

        if self.listbox_items.curselection()[0] == 0:
            self.log("ATTENTION: It's not an item")
            return 0

        if not isinstance(self.var_price.get(), int):
            self.log("ATTENTION: Price is not an integer")
            return 0

        item_name = self.auction_item[self.listbox_items.curselection()[0]]
        loot_id = self.item_loot_id[self.listbox_items.curselection()[0]]
        credit = self.var_price.get()
        if loot_id in self.tracked_loot_id:
            if credit == self.tracked_credits[self.tracked_loot_id.index(loot_id)]:
                self.log("ATTENTION: Item is already tracked")
                return 0
            else:
                itemIndex = self.tracked_loot_id.index(loot_id)
                self.tracked_auction_type.pop(itemIndex)
                self.tracked_item_name.pop(itemIndex)
                self.tracked_loot_id.pop(itemIndex)
                self.tracked_credits.pop(itemIndex)

        if len(self.tracked_auction_type) >= 3:
            self.tracked_auction_type.pop(0)
            self.tracked_item_name.pop(0)
            self.tracked_loot_id.pop(0)
            self.tracked_credits.pop(0)

        self.tracked_auction_type.append("hour")
        self.tracked_item_name.append(item_name)
        self.tracked_loot_id.append(loot_id)
        self.tracked_credits.append(credit)

        self.updateTracked()

    def updateTracked(self):
        self.listbox_tracked.delete(0, tk.END)

        if len(self.tracked_loot_id) < 1:
            return 0

        column_auction_type = self.createColumn(self.tracked_auction_type)
        column_item_name = self.createColumn(self.tracked_item_name, True)
        column_credits = self.tracked_credits

        self.listbox_tracked.delete(0, tk.END)

        for i, item in enumerate(self.tracked_auction_type):
            self.listbox_tracked.insert(
                tk.END, 
                "{}  {}  {}".format(
                    column_auction_type[i],
                    column_item_name[i],
                    column_credits[i]
                )
            )

    def clearTracked(self):
        self.tracked_auction_type = []
        self.tracked_item_name = []
        self.tracked_loot_id = []
        self.tracked_credits = []

        self.updateTracked()

    def bid(self):
        payload = {
            "auctionType" : "hour",
            "subAction" : "bid",
            "lootId" : self.item_loot_id[self.listbox_items.curselection()[0]],
            "credits" : int(self.var_price.get())
        }

        result = self.session_requests.post(
            "https://pl2.darkorbit.com" + self.bid_destination,
            payload,
            headers = dict(referer=self.auction_url)
        )

        self.log("STATUS: Auto syncing")
        self.getAuctionState()

    def zombie(self):
        pass

    def processCountdown(self, countdown):
        self.hour_left += 1
        if self.hour_left == self.hour_countdown_interval:
            self.log("STATUS: Auto syncing")
            self.sync()
            return

        self.hour_remeaning = countdown['seconds'] + countdown['minutes'] * 60
        if countdown['minutes'] == 0 and countdown['seconds'] < 10 and self.hour_left > 10:
            self.log("STATUS: Auto syncing")
            self.sync()
            return

        if countdown['minutes'] == 0 and countdown['seconds'] < 30 and self.hour_left > 30:
            self.log("STATUS: Auto syncing")
            self.sync()
            return
            
        if countdown['seconds'] > 0:
            countdown['seconds'] -= 1
        else:
            countdown['seconds'] = 59
            countdown['minutes'] -= 1
        self.toc = time.perf_counter()
        # print(str("{:7.4f}".format(self.toc - self.tic)))
        self.updateCountdown(countdown)
        self.timer = self.master.after(1000, self.processCountdown, countdown)

    def updateCountdown(self, countdown):
        self.var_countdown_hour.set("Left: {:02d}:{:02d}".format(countdown['minutes'], countdown['seconds']))

    def other_actions(self, *args):
        action = self.actions_list.index(self.var_other.get())

        if action == 0:
            self.var_other.set("More")
            self.log("STATUS: Manual syncing")
            self.sync()

        elif action == 1:
            self.var_other.set("More")
            self.log("SID: " + self.sid)

        elif action == 2:
            self.var_other.set("More")
            self.log("STATUS: Tracked items removed")
            self.clearTracked()

        else:
            self.var_other.set("More")

    def log(self, message):
        datetime.datetime.now()
        self.listbox_status.insert(0, str(datetime.datetime.now().strftime('%H:%M:%S')) + " " + message)

    def auth(self):
        auth_link = 'https://auth_server'
        result = requests.get(
            auth_link,
            { 'req' : hashlib.md5(b'salt_req' + self.nickname.encode()).hexdigest() }
        )
        if result.status_code == 200 and json.loads(result.text)['res'] == hashlib.md5(b'salt_res' + self.nickname.encode()).hexdigest():
            return True
        return False
    
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
