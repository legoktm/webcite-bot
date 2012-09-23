A [webcitaton.org](http://webcitation.org) bot for [en.wikipedia.org](http://en.wikipedia.org)
===================
* Written by [Legoktm](http://en.wikipedia.org/wiki/User:Legoktm)
* Source code released under the MIT License

Implementation
---------
* An IRC bot sits in [#wikipedia-en-spam](irc://irc.freenode.net/#wikipedia-en-spam) (webcite/irc.py)
* Stores new links in `new_links` (webcite/db.py)
* Verifies that the link still exists after 48 hours (webcite/bot.py)
* Archives the link with webcitation.org (webcite/citationdotorg.py)
* Updates the article page with a link to the archive (webcite/bot.py)

Dependencies
---------
* Ceterach - by [Riamse](https://github.com/Riamse)
* mwparserfromhell - [Github repo](https://github.com/earwig/mwparserfromhell)
* Requests - [Homepage](http://docs.python-requests.org/en/latest/index.html)
* lxml - [Homepage](http://lxml.de/)
* BeautifulSoup4 - [Homepage](http://www.crummy.com/software/BeautifulSoup/)

Thanks
---------
* [rmdashrf](https://github.com/rmdashrf) for assistance with MySQL and other matters
* [nosklo](http://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python) for an amazing URL matching regex