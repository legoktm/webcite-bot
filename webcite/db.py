#!/usr/bin/env python
from __future__ import unicode_literals

"""
Part of a webcitation.org bot
(C) Legoktm, 2012 under the MIT License
This portion interacts with the database storing and reading links.
"""

import os
import threading
import Queue

import oursql

from webcite import errors

class Database:
    
    def connect(self):
        self.db = oursql.connect(db='u_legoktm_webcite_p',
                            host="sql-user-l.toolserver.org",
                            read_default_file=os.path.expanduser("~/.my.cnf"),
                            charset=None,
                            use_unicode=False
                            )

    def add_link(self, table, wikipage, url, author, oldid, **kwargs):
        timestamp = 'CURRENT_TIMESTAMP'
        if table in ['new_links', 'removed_links']:
            data = (table, wikipage, url, author, timestamp, oldid)
        elif table == 'archived_links':
            data = (table, wikipage, kwargs['archive_url'], url, author, timestamp, oldid)
        elif table == 'processed_links':
            data = (table, wikipage, kwargs['archive_url'], url, author, timestamp, oldid, kwargs['added_oldid'])
        else:
            raise errors.NoTableError, table
        values = '(' + ', '.join('?' for i in len(data)-1) + ')'
        print data
        with self.db.cursor() as cursor:
            cursor.execute('INSERT INTO ? VALUES %s' % (values), data)

class NewLinksThread(threading.Thread):
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def parse(self, data):
        #data ={'user':user, 'article_name':article_name, 'oldid':oldid, 'link':link}
        table = 'new_links'
        self.add_link(table, data['article_name'], data['link'], data['user'], data['oldid'])
    
    def run(self):
        while True:
            data = self.queue.get()
            self.parse(data)
            self.queue.task_done()

NEWLINKSQUEUE = Queue.Queue()
NEWLINKSTHREAD = NewLinksThread(NEWLINKSQUEUE)
NEWLINKSTHREAD.setDaemon(True)
NEWLINKSTHREAD.start()