from tkinter import ttk 
import tkinter as tk
import numpy as np

import time

import requests
from tkinter.ttk import Frame, Label, Button
import webbrowser

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]
VERSION = 1.20
IS_TEST = False

class Screen():
    def __init__(self, monitor=None):
        self.check_update()
        if monitor:
            self.monitor = monitor
            self.tgs = monitor.tgs
        else:
            self.monitor = None
            self.tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]

        self.root = tk.Tk() 
        self.root.title('DMR Korean Talkgroup Monitor by VK2CYO')
        self.root.resizable(width=False, height=False)
        # self.root.config(bg='red')
        self.root.attributes('-topmost', True)

        '''Overall structure'''
        info_frame = Frame(self.root)
        list_frame = Frame(self.root)
        author_frame = Frame(self.root)
        status_frame = Frame(self.root)
        setting_frame = Frame(self.root)
        
        # info_frame.grid(row=0, column=0, padx=5, pady=5, columnspan=2)
        list_frame.grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        setting_frame.grid(row=2, column=0, padx=5, pady=5, columnspan=2, sticky='ew')
        author_frame.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        status_frame.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        '''Setting frame'''
        istop = tk.IntVar(value=1)
        def change_top():
            print(f'pressed: {istop.get()}')
            if istop.get() == 1:
                self.root.attributes('-topmost', True)
            else:
                self.root.attributes('-topmost', False)
        check_button = tk.Checkbutton(setting_frame, 
            text='항상 위에', variable=istop, onvalue=1, offvalue=0, command=change_top, anchor='w'
            )
        check_button.select()
        check_button.grid(row=0, column=0, sticky='ew')

        '''Active info'''
        # SourceID, SourceCall, SourceName, DestinationName, SourceID
        Label(info_frame, text='asdf').grid(row=0, column=0, padx=5, pady=5)
        Label(info_frame, text='asdf').grid(row=1, column=0, padx=5, pady=5)
        Label(info_frame, text='asdf').grid(row=2, column=0, padx=5, pady=5)
        ttk.Treeview(info_frame, selectmode ='browse', height=self.monitor.num_history, pad=3).grid(row=0, column=1, rowspan=3)

        '''Author info'''
        Label(author_frame, text=f'Developed by Chanyeol Yoo (VK2CYO)\nv{VERSION}', justify=tk.LEFT).grid(row=3, column=0, padx=5, pady=5, sticky='ew')

        '''Status'''
        def openGit():
            webbrowser.open_new(self.url_git)
        if self.is_update_available:
            button = Button(status_frame, text='업데이트 가능', command=openGit)
        else:
            button = Button(status_frame, text="Github", command=openGit)
        button.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        button.config(width=20)

        '''List Frame'''
        # style = ttk.Style()
        # style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('arial', 11)) # Modify the font of the body
        # style.configure("mystyle.Treeview", font=('segoe', 12)) # Modify the font of the body
        # style.configure("mystyle.Treeview.Heading", font=('Calibri', 13,'bold')) # Modify the font of the headings
        
        # self.treev = ttk.Treeview(list_frame, style='mystyle.Treeview', selectmode ='browse', height=len(tgs), pad=3)
        self.treev = ttk.Treeview(list_frame, selectmode ='browse', height=len(tgs), pad=3)
        self.treev.pack(fill='x')

        self.treev.bind("<<TreeviewSelect>>", self.onClick)

        self.treev["columns"] = (0, 1, 2) 
        self.treev['show'] = 'headings'
        self.treev.column(0, width = 50, anchor ='e') 
        self.treev.column(1, width = 200, anchor ='w') 
        self.treev.column(2, width = 500, anchor ='w') 
        self.treev.heading(0, text ="TG") 
        self.treev.heading(1, text ="Active") 
        self.treev.heading(2, text ="Inactive") 


        if self.monitor:
            for tg in self.monitor.tgs:
                self.treev.insert("", 'end', text ="", values=[str(tg), "", ""])
        else:
            for tg in self.tgs:
                self.treev.insert("", 'end', text ="", values=[str(tg), "VK2CYO Chanyeol (180s)", "VK2CNN (30s), HL2XXX (10s), HL2XXX (10s), "])

    def onClick(self, event):
        item = self.treev.identify('item',event.x,event.y)
        # print("you clicked on", self.treev.item(item, "text"))

    def check_update(self):
        try:
            text_release = requests.get('https://api.github.com/repos/chanyeolyoo/BMRMonitor/releases/latest').text
            text_release = text_release.replace('false', 'False')
            text_release = text_release.replace('true', 'True')
            text_release = text_release.replace('null', 'None')
            resp_release = eval(text_release)
            tag_release = float(resp_release['tag_name'])

            if (tag_release > VERSION) or (tag_release >= VERSION and IS_TEST):
                is_update_available = True
            else:
                is_update_available = False
            self.url_git = resp_release['html_url']
        except:
            is_update_available = False
            self.url_git = 'https://github.com/chanyeolyoo/BMRMonitor'
        self.is_update_available = is_update_available

    def start(self):
        self.refresh()
        self.root.mainloop()

    def refresh(self, data=None):
        if not self.monitor.is_alive():
            for idx, node in enumerate(self.treev.get_children()):
                self.treev.item(node, tags=('red'), values=[self.tgs[idx], str(np.random.rand()), str(np.random.rand())])
            # return
        else:
            now = time.time()
            for node, tg in zip(self.treev.get_children(), self.monitor.history_tgs):
                text_active = ''
                text_inactive = ''

                history_tg = self.monitor.history_tgs[tg]
                try:
                    text_inactive = ''
                    for d in history_tg:
                        if now - d['Stop'] < self.monitor.timeout:
                            text_inactive = text_inactive + ('%s (%ds), ' % (d['SourceCall'], now - d['Stop']))
                    text_inactive = text_inactive

                    if history_tg[0]['Stop'] == 0:
                        elapsed = now-history_tg[0]['Start']
                        text_active = '%s, %s (%ds) ' % (history_tg[0]['SourceCall'], history_tg[0]['SourceName'], elapsed)
                except Exception as e:
                    pass

                self.treev.item(node, values=[str(tg), text_active, text_inactive])

        self.root.after(100, self.refresh)
        
if __name__ == "__main__":
    from monitor import Monitor
    monitor = Monitor(tgs)
    monitor.start()

    # monitor = None
    

    screen = Screen(monitor)
    screen.start()