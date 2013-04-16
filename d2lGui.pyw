#!/usr/bin/env python

import threading, json, keyring
from time import strftime, gmtime
from Tkinter import *
from desire2login import *

CONFIG = None

class GUI(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.InitUi()
        self.BuildKeybindings()
        self.refresh()

    def InitUi(self):
        '''
        Initialize the main frame, build the elements
        '''
        self.parent.title("D2L Check")      # Window Title
        self.parent.resizable(0, 0)         # Disable Resize

        self.numClasses = int(CONFIG["NumClasses"])

        self.CreateMenubar()

        # User Info
        Label(self.parent, text=CONFIG["Username"], fg="#777777").grid(row=0, column=2)

        # Email Info
        self.emails = IntVar()
        Label(self.parent, text="Email:").grid(row=1, column=0, sticky=E)
        Label(self.parent, textvariable=self.emails).grid(row=1, column=1, sticky=W)
        self.emails.set(0)

        # Labels
        Label(self.parent, text="Discussion:").grid(row=3, sticky=E)
        Label(self.parent, text="Dropbox:").grid(row=4, sticky=E)

        # Classes - Scale with various class loads
        self.classes = []
        self.clsColumn = 1
        for i in range(self.numClasses):
            self.classes.append([StringVar(), IntVar(), IntVar()])
            Label(self.parent, textvariable=(self.classes[i][0]), relief=GROOVE, width=10, anchor=CENTER).grid(row=2, column=self.clsColumn)
            Label(self.parent, textvariable=(self.classes[i][1]), width=10, anchor=CENTER).grid(row=3, column=self.clsColumn)
            Label(self.parent, textvariable=(self.classes[i][2]), width=10, anchor=CENTER).grid(row=4, column=self.clsColumn)
            self.clsColumn += 1

        # Buttons!
        b_kill = Button(self.parent, text="Close", command=self.kill)
        b_kill.grid(row=8, column=0, columnspan=(self.numClasses + 1), sticky=E, pady=5, padx=(0, 5))

        b_refresh = Button(self.parent, text="Refresh", command=self.refresh)
        b_refresh.grid(row=8, column=0, columnspan=self.numClasses, sticky=W, pady=5, padx=(5, 0))

        # Status bar
        self.status = StringVar()
        statusbar = Label(self.parent, borderwidth=1, relief="sunken", textvariable=self.status, anchor=W)
        statusbar.grid(row=10, columnspan=(self.numClasses + 1), sticky=N+E+S+W)

    def CreateMenubar(self):
        '''
        Create the menu bar (File, Edit, About, etc.)
        '''
        menubar = Menu(self.parent)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Refresh", command=self.refresh)
        filemenu.add_separator()
        filemenu.add_command(label="Close", command=self.kill)

        menubar.add_cascade(label="File", menu=filemenu)

        #menubar.add_command(label="About", command=self.about)

        self.parent.config(menu=menubar)

    def BuildKeybindings(self):
        '''
        Bind keys (when the window is in focus), uncomment the <Key> option and open the program
        from IDLE to see a print out of what key Tkinter is registering.
        '''
        self.parent.bind(CONFIG["Preferences"]["RefreshKey"], self.refresh)
        self.parent.bind(CONFIG["Preferences"]["CloseKey"], self.kill)
        #self.parent.bind("<Key>", self.key) # Use this to determine keycodes for key bindings (printed to python console)

    def key(self, event):
        '''
        Print the key that Tkinter receives to the console
        '''
        print "Pressed: {}".format(event.keysym)

    def kill(self, e=None):
        '''
        Destroy the windows and exit the main loop
        '''
        self.parent.destroy()

    def refresh(self, e=None):
        '''
        Thread the update process to allow the window to remain active
        during refresh.
        '''
        t = threading.Thread(target=self.update)
        t.start()

    def update(self):
        info = []
        
        self.status.set(">> Logging into D2L...")
        conn = d2l(CONFIG["Username"], CONFIG["Password"])

        mp = MainPage()
        cp = ClassPage()

        self.status.set(">> Checking email...")
        mp.feed( conn.response.read() )
        email = {
            'Unread' : mp.email['Unread'],
            'Link' : mp.email['Link']
        }

        self.status.set(">> Checking Discussions & Dropbox...")
        for key, val in mp.classes.iteritems():
            conn.Connect(val)
            cp.feed( conn.response.read() )
            key = {
                'Class' : key,
                'Discussion' : {
                    'Unread' : cp.info['Discussion']['Unread'],
                    'Link' : cp.info['Discussion']['Link']
                },
                'Dropbox' : {
                    'Unread' : cp.info['Dropbox']['Unread'],
                    'Link' : cp.info['Dropbox']['Link']
                }
            }
            info.append( key.copy() )
            cp.info['Discussion']['Unread'] = 0; cp.info['Discussion']['Link'] = ''
            cp.info['Dropbox']['Unread'] = 0; cp.info['Dropbox']['Link'] = ''
            del key

        self.status.set(">> Done! ({})".format(strftime("@%H:%M:%S on %m/%d"), gmtime()))

        self.showResults(info, email)

        mp.email['Unread'] = 0; mp.email['Link'] = ''
        cp.info['Dropbox']['Unread'] = 0; cp.info['Dropbox']['Link'] = ''
        cp.info['Discussion']['Unread'] = 0; cp.info['Discussion']['Link'] = ''
        del info, conn, mp, cp, email
        return

    def showResults(self, info, email):
        self.emails.set(int(email["Unread"]))

        for i in range(len(info)):
            c = info[i]
            self.classes[i][0].set(str(c["Class"]))
            self.classes[i][1].set(int(c["Discussion"]["Unread"]))
            self.classes[i][2].set(int(c["Dropbox"]["Unread"]))

    def updateConfig(self):
        th = threading.Thread(target=establishConfig())
        th.start()

class CreateConfig(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.InitUi()

    def InitUi(self):
        self.parent.title("config.json")
        self.parent.resizable(0, 0)
        #self.parent.protocol('WM_DELETE_WINDOW', 0) #Disables 'x' button
        try:
            self.parent.iconbitmap("regis-university.ico")
        except:
            pass

        Label(self.parent, text="Create config.json:").grid(row=0, columnspan=2)
        
        Label(self.parent, text="").grid(row=1, columnspan=2)

        self.uname = StringVar()
        Label(self.parent, text="Username:").grid(row=2, column=0)
        Entry(self.parent, textvariable=self.uname).grid(row=2, column=1)

        self.pwd = StringVar()
        Label(self.parent, text="*Password:").grid(row=3, column=0)
        Entry(self.parent, show="*", textvariable=self.pwd).grid(row=3, column=1)

        self.cls = StringVar()
        Label(self.parent, text="NumClasses:").grid(row=4, column=0)
        Entry(self.parent, textvariable=self.cls).grid(row=4, column=1)

        # School Portability (possibly)
        self.portability = [
            #[NAME, TkVARIABLETYPE, DEFAULTVALUE]
            ["Icon:", StringVar(), "regis-university.ico"]
            #["Main Url:", StringVar(), "https://worldclass.regis.edu"],
            #["Login Url:", StringVar(), "/d2l/lp/auth/login/login.d2l"],
            #["Redir Url:", StringVar(), "/d2l/lp/auth/login/ProcessLoginActions.d2l"],
            #["Home Url:", StringVar(), "/d2l/lp/homepage/home.d2l?ou=6066"]
        ]

        b_submit = Button(self.parent, text="Submit", command=self.submit)
        b_submit.grid(row=6, column=0, columnspan=2, sticky=E, pady=5, padx=(0, 5))

        self.parent.bind("<Return>", self.submit)

    def submit(self, e=None):
        with open("config.json", "w") as cfg:
            cfg.write("{\n")
            cfg.write("\t\"Username\" : \"{}\",\n".format(self.uname.get()))
            cfg.write("\t\"NumClasses\" : \"{}\",\n".format(self.cls.get()))
            cfg.write("\t\"SchoolInfo\" : {\n")
            cfg.write("\t\t\"Icon\" : \"{}\"\n".format(self.portability[0][2]))
            cfg.write("\t},\n")
            cfg.write("\t\"Preferences\" : {\n")
            cfg.write("\t\t\"RefreshKey\" : \"{}\",\n".format("<F5>"))
            cfg.write("\t\t\"CloseKey\" : \"{}\"\n".format("<Escape>"))
            cfg.write("\t}\n")
            cfg.write("}")
        keyring.set_password("d2l", self.uname.get(), self.pwd.get())
        self.parent.destroy()

def checkConfig():
    try:
        open("config.json")
    except:
        establishConfig()

def establishConfig():
    root = Tk()
    cfg = CreateConfig(root)
    root.mainloop()

def main():
    global CONFIG
    checkConfig()
    CONFIG = json.load( open("config.json") )
    CONFIG["Password"] = keyring.get_password("d2l", CONFIG["Username"])
    
    root = Tk()
    img = PhotoImage(file="regis-university.gif")
    root.tk.call("wm", "iconphoto", root._w, img)
    app = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
