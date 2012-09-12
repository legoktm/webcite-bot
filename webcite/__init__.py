#!/usr/bin/env python
import threading

from webcite import irc
from webcite import errors
from webcite import db
from webcite import bot

class IRCThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.ircbot = irc.IRCBot()
    
    def run(self):
        self.ircbot.start()


def main():
    ircthread = IRCThread()
    ircthread.setDaemon(True)
    ircthread.start()
    
    