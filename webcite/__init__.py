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
import requests

import ceterach
#import pywikibot

from webcite import irc
from webcite import errors
from webcite import db
from webcite import bot
from webcite import citationdotorg
from webcite import regex


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
        print('Init: ArchiveThread')
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
        #verify the url actually exists and we can access it
        r = requests.get(url, headers=citationdotorg.FIREFOX_HEADERS)
        if r.status_code != 200:
            return False
        #pg = pywikibot.Page(self.Site, article)
        pg = self.api.page(article)
        url = url.strip()
        if not pg.exists:
            return False
        while pg.is_redirect:
            pg = pg.redirect_target
        links = list(pg.ext_links())
        if url in links:
            return True
        text = pg.content
        if url.lower() in text.lower():
            return True
        urls = [match.group(0) for match in regex.MATCH_URL.finditer(text)]
        return url in urls


    def run(self):
        while True:
            print('fetch_ready_links()')
            fetch = self.Database.fetch_ready_links()
            for row in fetch:
                print(row)
                url = row[2]
                article = row[1]
                if self.url_in_article(article, url):
                    print('Yippe! The url is still in %s' % article)
                    archive_url = self.archive_url(url)
                    if archive_url:
                        self.Database.move_archived_links(row, archive_url)
                    else:
                        print('Failed to archive %s' % article)
                        self.Database.delete_from_new_links(row,removed=True)
                else:
                    print('Oh noes. Url is no longer in %s' % article)
                    self.Database.delete_from_new_links(row,removed=True)
            if not fetch:
                print('No read_link rows found, sleeping')
                time.sleep(300) #let the table fill up again

class WikiBot(threading.Thread):

    def __init__(self, api):
        threading.Thread.__init__(self)
        print('Init: WikiBot')
        self.Database = db.Database()
        self.Database.connect()
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
        print(data)
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
            print('fetch_archived_links')
            fetch = self.Database.fetch_archived_links()
            for row in fetch:
                print(row)
                self.add_link(data)
            if not fetch:
                print('No archived_links found, sleeping')
                time.sleep(300) #let the table fill up again

def main():
    print('Started IRC')
    ircthread = IRCThread()
    ircthread.setDaemon(True)
    ircthread.start()
    print('Starting ArchiveThread')
    archivethread = ArchiveThread(api)
    archivethread.setDaemon(True)
    archivethread.start()
    print('Starting WikiBot')
    wikibotthread = WikiBot(api)
    wikibotthread.setDaemon(True)
    wikibotthread.start()
    ircthread.join()
    archivethread.join()
    wikibotthread.join()