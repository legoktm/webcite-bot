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
This portion interacts Wikipedia and updates articles.
"""

import time
import datetime
import re
import ceterach
#import pywikibot
import mwparserfromhell

from webcite import citationdotorg
CITE_WEB = ['cite web', 'web', 'web reference', 'web-reference', 'weblink', 'c web', 'cit web', 'cita web', 'citar web', 'cite blog', 'cite tweet',
            'cite url,', 'cite web.', 'cite webpage', 'cite website', 'cite website article', 'cite-web', 'citeweb', 'cw', 'lien web',
            'web citation', 'web cite',]
CITE_NEWS = ['cite news', 'cit news', 'cite article', 'citenewsauthor', 'cite new', 'cite news-q', 'cite news2', 'cite newspaper', 'cite-news',
              'citenews', 'cute news']
CITE_TEMPLATES = CITE_WEB
CITE_TEMPLATES.extend(CITE_NEWS)
CITE_WEB_TEMPLATE = '{{cite web|url=%s|title=%s|archiveurl=%s|archivedate=%s|deadurl=no}}'

def calculate_date(delay=None):
    #format of 31 June 2012
    now = datetime.datetime.utcnow()
    return now.strftime('%d %B %Y')



def add_template(wikitext, url, archive_url):
    orig = str(wikitext)
    wikitext = mwparserfromhell.parse(wikitext)
    for template in wikitext.filter_templates():
        lower = template.name.lower()
        if lower in CITE_TEMPLATES:
            if not template.has_param('url'): #cite news may not have this
                continue
            if template.has_param('archiveurl'):
                continue #already archived
            if template.get('url').value.strip() != url:
                continue
            template.add('archiveurl', archive_url)
            template.add('archivedate', calculate_date())
            template.add('deadurl', 'no')
            break
    if str(orig) != str(wikitext):
        return str(wikitext)
    #not in a cite web template :(
    
    #look for [url title]
    match = re.search('\[\w?%s\w?(.*?)\]' % url, str(wikitext), re.IGNORECASE)
    if match:
        cite = CITE_WEB_TEMPLATE % (
            url, match.group(1).strip(), archive_url, calculate_date())
        wikitext = str(wikitext).replace(match.group(0), cite)
        return wikitext
    #look for [url]
    find = '[%s]' % url
    title = citationdotorg.get_title(url)
    if find in wikitext:
        cite = CITE_WEB_TEMPLATE % (
            url, title, archive_url, calculate_date())
        wikitext = str(wikitext).replace(find, cite)
        return wikitext
    #look for just url
    plain_regex = '\<ref(.*?)\>\w?\[?\w?%s\w?\]?\w?\</ref\>' % url
    match = re.search(plain_regex, str(wikitext))
    if match:
        cite_t = CITE_WEB_TEMPLATE % (url, title, archive_url, calculate_date())
        cite = '<ref%s>%s</ref>' % (match.group(1), cite_t)
        wikitext = re.sub(plain_regex, cite, str(wikitext))
        return wikitext
    #un-successful in adding the cite
    return None

def modify_all_of_page(page):
    links = page.extlinks()
    orig = page.get()
    text = mwparserfromhell.parse(orig)
    for link in links:
        if 'wiki' in link:
            continue
        if not link.startswith(('http', 'ftp', 'https')):
            continue
        url = citationdotorg.archive_url(link)['webcite_url']
        print(url)
        text = add_template(text, link, url)
        if not text:
            print('ERROR')
        text = mwparserfromhell.parse(text)
        #pywikibot.showDiff(orig, str(text))
        time.sleep(5)
    print('-----------------------')
    #pywikibot.showDiff(orig, str(text))
    page.put(str(text), 'bot: manual testing by op')


if __name__ == "__main__":
    #modify_all_of_page(pywikibot.Page(pywikibot.Site(), 'User:Legoktm/Sandbox'))
    pass