#!/usr/bin/env python
from __future__ import unicode_literals

"""
Part of a webcitation.org bot
(C) Legoktm, 2012 under the MIT License
This portion interacts Wikipedia and updates articles.
"""

import time
import datetime
import re

import pywikibot
import mwparserfromhell

#from webcite import citationdotorg
import citationdotorg
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
    orig = unicode(wikitext)
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
    if unicode(orig) != unicode(wikitext):
        return unicode(wikitext)
    #not in a cite web template :(
    
    #look for [url title]
    match = re.search('\[\w?%s\w?(.*?)\]' % url, unicode(wikitext), re.IGNORECASE)
    if match:
        cite = CITE_WEB_TEMPLATE % (
            url, match.group(1).strip(), archive_url, calculate_date())
        wikitext = unicode(wikitext).replace(match.group(0), cite)
        return wikitext
    #look for [url]
    find = '[%s]' % url
    title = citationdotorg.get_title(url)
    if find in wikitext:
        cite = CITE_WEB_TEMPLATE % (
            url, title, archive_url, calculate_date())
        wikitext = unicode(wikitext).replace(find, cite)
        return wikitext
    #look for just url
    plain_regex = '\<ref(.*?)\>\w?\[?\w?%s\w?\]?\w?\</ref\>' % url
    match = re.search(plain_regex, unicode(wikitext))
    if match:
        cite_t = CITE_WEB_TEMPLATE % (url, title, archive_url, calculate_date())
        cite = '<ref%s>%s</ref>' % (match.group(1), cite_t)
        wikitext = re.sub(plain_regex, cite, unicode(wikitext))
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
        print url
        text = add_template(text, link, url)
        if not text:
            print 'ERROR'
        text = mwparserfromhell.parse(text)
        pywikibot.showDiff(orig, unicode(text))
        time.sleep(5)
    print '-----------------------'
    pywikibot.showDiff(orig, unicode(text))
    page.put(unicode(text), 'bot: manual testing by op')


if __name__ == "__main__":
    modify_all_of_page(pywikibot.Page(pywikibot.Site(), 'User:Legoktm/Sandbox'))
    