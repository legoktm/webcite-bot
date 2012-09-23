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

"""
Part of a webcitation.org bot
This portion interacts with the database storing and reading links.
"""

import os
import threading
import queue

import mysql.connector
from webcite import errors
import pw
class Database:
    
    def connect(self):
        self.db = mysql.connector.connect(database='u_sigma_webcite_p',
                                          host="sql-user-l.toolserver.org",
                                          user="sigma",
                                          password=pw.mysql)

    def add_link(self, table, wikipage, url, author, oldid, **kwargs):
        timestamp = None
        id = None
        if table in ['new_links', 'removed_links']:
            data = (id, wikipage, url, author, timestamp, oldid)
        elif table == 'archived_links':
            data = (id, wikipage, kwargs['archive_url'], url, author, timestamp, oldid)
        elif table == 'processed_links':
            data = (id, wikipage, kwargs['archive_url'], url, author, timestamp, oldid, kwargs['added_oldid'])
        else:
            raise errors.NoTableError(table)
        values = '(' + ', '.join(['%s' for i in range(0,len(data))]) + ')'
        print(data)
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO `'+table+'` VALUES '+values, data)
        self.db.commit()
        cursor.close()
    
    def fetch_ready_links(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM `new_links` WHERE `timestamp` < (NOW() - INTERVAL 48 HOUR)")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
    def delete_from_new_links(self, orig_row, removed=False):
        if removed:
            self.add_link('removed_links', orig_row[1], orig_row[2], orig_row[3], orig_row[5])
        self.delete_from_table('new_links', orig_row)
    def delete_from_table(self, table, orig_row):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM `"+table+"` WHERE `id` = %s", (orig_row[0],))
        self.db.commit()
        cursor.close()


    def move_archived_links(self, orig_row, archive_url):
        self.add_link('archived_links', orig_row[1], orig_row[2], orig_row[3], orig_row[5], archive_url = archive_url)
        self.delete_from_new_links(orig_row)
    
    def move_processed_links(self, orig_row, new_oldid):
        self.add_link('processed_links', orig_row[1], orig_row[2], orig_row[3], orig_row[5], archive_url = archive_url, added_oldid=new_oldid)
        self.delete_from_table('archived_links', orig_row)
    
    def fetch_archived_links(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM `archived_links` LIMIT 10")
        rows = cursor.fetchall()
        cursor.close()
        return rows



class NewLinksThread(threading.Thread):
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.Database = Database()
        self.Database.connect()
    
    def parse(self, data):
        #data ={'user':user, 'article_name':article_name, 'oldid':oldid, 'link':link}
        table = 'new_links'
        self.Database.add_link(table, data['article_name'], data['link'], data['user'], data['oldid'])
    
    def run(self):
        while True:
            data = self.queue.get()
            self.parse(data)
            self.queue.task_done()

NEWLINKSQUEUE = queue.Queue()
NEWLINKSTHREAD = NewLinksThread(NEWLINKSQUEUE)
NEWLINKSTHREAD.setDaemon(True)
NEWLINKSTHREAD.start()