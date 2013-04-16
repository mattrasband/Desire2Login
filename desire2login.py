#!/usr/bin/env python

import urllib2, urllib, cookielib, json
from HTMLParser import HTMLParser

URLS = json.load( open("urls.json") )

class d2l():
    def __init__(self, username, password):
        
        self.url = URLS["BaseUrl"] + URLS["LoginUrl"]
        self.redir = URLS["BaseUrl"] + URLS["RedirUrl"]

        self.data = urllib.urlencode({"Username" : username, "Password" : password})

        self.cookies = cookielib.CookieJar()

        self.opener = urllib2.build_opener(
            urllib2.HTTPRedirectHandler(),
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(self.cookies)
        )

        self.response = None

        self.Connect(self.url, self.data)
        self.Connect(self.redir)

    def Connect(self, url, data=None):
        self.response = self.opener.open(url, data)

    def GoHome(self):
        self.Connect(URLS["BaseUrl"] + URLS["HomeUrl"])

class MainPage(HTMLParser):
    wanted = {'Classes' : False, 'Email' : False}
    classes = {}
    link = '' # Temp holder to load classes dict
    email = {'Unread' : 0, 'Link' : ''}

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and '/d2l/lp/ouHome/home.d2l?ou=' in attrs[0][1]:
            self.link = attrs[0][1]
            self.wanted['Classes'] = True
        if tag == 'a' and '/d2l/lms/email/frame.d2l?ou=' in attrs[0][1]:
            try:
                if 'New Emails for Regis University' in attrs[1][1]:
                    self.email['Link'] = URLS["BaseUrl"] + attrs[0][1]
                    self.wanted['Email'] = True
            except:
                pass

    def handle_data(self, data):
        if (self.wanted['Classes']):
            self.classes[data.split(' ')[0].split('_')[0]] = URLS["BaseUrl"] + self.link
            del self.link
            self.wanted['Classes'] = False
        if (self.wanted['Email']):
            self.email['Unread'] = data
            self.wanted['Email'] = False

class ClassPage(HTMLParser):
    wanted = {'Dropbox' : False, 'Discussion' : False}
    info = {
        'Dropbox' : {'Unread' : 0, 'Link' : ''},
        'Discussion' : {'Unread' : 0, 'Link' : ''}
    }

    def handle_starttag(self, tag, attrs):
        try:
            if tag == 'a' and 'Unread Discussions Messages for ' in attrs[1][1]:
                self.info['Discussion']['Link'] = URLS["BaseUrl"] + attrs[0][1]
                self.wanted['Discussion'] = True
        except:
            pass

        try:
            if tag == 'a' and 'Dropboxes With Unread Feedback for ' in attrs[1][1]:
                self.info['Dropbox']['Link'] = URLS["BaseUrl"] + attrs[0][1]
                self.wanted['Dropbox'] = True
        except:
            pass

    def handle_data(self, data):
        if (self.wanted['Discussion']):
            self.info['Discussion']['Unread'] = data
            self.wanted['Discussion'] = False
        if (self.wanted['Dropbox']):
            self.info['Dropbox']['Unread'] = data
            self.wanted['Dropbox'] = False

