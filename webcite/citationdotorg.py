#!/usr/bin/env python
from __future__ import unicode_literals

"""
Part of a webcitation.org bot
(C) Legoktm, 2012 under the MIT License
This portion interacts with webcitation.org in querying
and analyzing data.
"""

import requests
from lxml import etree
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO

#from webcite import errors

#global configuation settings
WEBCITE_URL = 'http://www.webcitation.org/archive'
DEFAULT_PARAMETERS = {'email':'legoktm.wikipedia@gmail.com','returnxml':'true'}
FIREFOX_HEADERS = {'Content-Length':'',
                      'Accept-Language':'en-us,en;q=0.5',
                      'Accept-Encoding':'gzip, deflate',
                      'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0',
                      'Connection':'keep-alive',
                      'Referer':'http://en.wikipedia.org',
                      }
BOT_HEADERS = FIREFOX_HEADERS
BOT_HEADERS['User-Agent'] = 'Wikipedia LegoCITEBot - enwp.org/User:Legobot'
def get_title(url):
    r = requests.get(url, headers=FIREFOX_HEADERS)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text)
    title = soup.title.string  
    title = title.replace('|', '{{!}}')
    title = title.strip()
    return title  

def archive_url(url):
    d = DEFAULT_PARAMETERS
    d['url'] = url
    r = requests.get(WEBCITE_URL, params=d, headers=BOT_HEADERS)
    if r.status_code != 200:
        raise errors.ArchivingFailed, url
    obj = StringIO(str(r.text))
    data = {}
    try:
        for event, element in etree.iterparse(obj):
            data[element.tag] = element.text
    except:
        print r.text
    return data

if __name__ == "__main__":
    d=archive_url('en.wikipedia.org')
    print d