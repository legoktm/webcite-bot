#!/usr/bin/env python
"""
Copyright (C) 2012 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import threading
import time

import ceterach
#import pywikibot

from webcite import irc
from webcite import errors
from webcite import db
from webcite import bot
from webcite import citationdotorg


api = ceterach.apir.MediaWiki("http://en.wikipedia.org/w/api.php")
api.login("Lowercase sigmabot III", ceterach.passwords.lcsb3)


class IRCThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ircbot = irc.IRCBot()
    
    def run(self):
        self.ircbot.start()

class ArchiveThread(threading.Thread):
    def __init__(self, api):
        threading.Thread.__init__(self)
        self.Database = db.Database()
        self.Database.connect()
        self.time = 0
        #self.Site = pywikibot.Site()
        self.api = api
    
    def archive_url(self, url):
        """Implements a 5 second time delay"""
        delay = time.time() - self.time
        if delay < 5:
            time.sleep(5-delay)
        self.time = time.time()
        return citationdotorg.archive_url(url)
    
    def url_in_article(self, article, url):
        #pg = pywikibot.Page(self.Site, article)
        pg = self.api.page(article)
        if not pg.exists:
            return False
        while pg.is_redirect:
            pg = pg.redirect_target
        links = list(pg.extlinks())
        if url in links:
            return True
        text = pg.content
        return url.lower().strip() in text.lower()

    
    def run(self):
        while True:
            fetch = self.Database.fetch_ready_links()
            for row in fetch:
                url = row[1]
                article = row[0]
                if self.url_in_article(article, url):
                    archive_url = self.archive_url(url)
                    self.Database.move_archived_links(row, archive_url)
                else:
                    self.Database.delete_from_new_links(row)
            if not fetch:
                time.sleep(300) #let the table fill up again

class WikiBot(threading.Thread):
    
    def __init__(self, api):
        threading.Thread.__init__(self)
        self.Database = db.Database()
        #self.Site = pywikibot.Site()
        #self.error_page = pywikibot.Page(self.Site, 'User:Legobot/WebCite Errors')
        self.api = api
        self.error_page = self.api.page("User:Lowercase sigmabot III/WebCite Errors")


    def report_error(self, article, url, archive_url):
        if self.error_page.exists:
            old = self.error_page.content
        else:
            old = ''
        new = '* [[:%s]] -- [%s Original], [%s Archive]. ~~~~~' % (article, url, archive_url)
        text = old + '\n' + new
        self.error_page.edit(text, 'BOT: Logging error',minor=True,bot=True)
    
    def add_link(self, data):
        article = data[1]
        url = data[3]
        archive_url = data[2]
        #page = pywikibot.Page(self.site, article)
        page = self.api.page(article)
        text = page.content
        new_text = bot.add_template(text, url, archive_url)
        if new_text:
            page.edit(new_text, 'BOT: adding webcitation.org link to %s' % url, minor=True, bot=True)
            #TODO: Implement page.latest_revision
            page.load() #force it to load new info
            #new_oldid = page.latestRevision() #pywikibot
            #new_oldid = page.latest_revision #ceterach
            new_oldid = 00000
            self.Database.move_processed_links(data, new_oldid)
        else:
            self.report_error(article, url, archive_url)
            self.Database.move_processed_links(data, 0)
    
    def run(self):
        while True:
            fetch = self.Database.fetch_archived_links()
            for row in fetch:
                self.add_link(data)
            if not fetch:
                time.sleep(300) #let the table fill up again

def main():
    ircthread = IRCThread()
    ircthread.setDaemon(True)
    ircthread.start()
    #archivethread = ArchiveThread(api)
    #archivethread.setDaemon(True)
    #archivethread.start()
    #wikibotthread = WikiBot(api)
    #wikibotthread.setDaemon(True)
    #wikibotthread.start()
    ircthread.join()
    #archivethread.join()
    #wikibotthread.join()