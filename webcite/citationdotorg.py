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
This portion interacts with webcitation.org in querying
and analyzing data.
"""

import requests
from io import StringIO
from lxml import etree
from bs4 import BeautifulSoup

import pw

#global configuation settings
WEBCITE_URL = 'http://www.webcitation.org/archive'
DEFAULT_PARAMETERS = {'email':pw.email,'returnxml':'true'}
FIREFOX_HEADERS = {'Content-Length':'',
                      'Accept-Language':'en-us,en;q=0.5',
                      'Accept-Encoding':'gzip, deflate',
                      'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                      'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0',
                      'Connection':'keep-alive',
                      'Referer':'http://en.wikipedia.org',
                      }
BOT_HEADERS = FIREFOX_HEADERS
BOT_HEADERS['User-Agent'] = 'Wikipedia Archive Bot - enwp.org/User:Lowercase_sigmabot_III'
def get_title(url):
    try:
        r = requests.get(url, headers=FIREFOX_HEADERS) #sites may reject custom headers
    except: #wtf
        return None
    if r.status_code != requests.codes.ok:
        return None
    soup = BeautifulSoup(r.text)
    title = soup.title.string.strip()
    title = title.replace('|', '{{!}}')
    return title

def archive_url(url):
    d = DEFAULT_PARAMETERS
    d['url'] = url
    r = requests.get(WEBCITE_URL, params=d, headers=BOT_HEADERS)
    if r.status_code != requests.codes.ok:
        raise errors.ArchivingFailed(url)
    soup = BeautifulSoup(r.text)
    try:
        return str(soup.archiverequest.resultset.webcite_url.string)
    except:
        return None


if __name__ == "__main__":
    d=archive_url('en.wikipedia.org')
    print(d)