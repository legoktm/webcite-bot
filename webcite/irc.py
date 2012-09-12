#!/usr/bin/env python
from __future__ import unicode_literals

"""
Part of a webcitation.org bot
(C) Legoktm, 2012 under the MIT License
This portion reads from #wikipedia-en-spam, and updates the database.
"""

import sys
import socket
import string

from webcite import db
            
class IRCBot:
    def __init__(self):
        self.HOST = "irc.freenode.net"
        self.PORT = 6667
        self.NICK = "Legobot"
        self.readbuffer = ""
        self.join_channels = ['##legoktm','#wikipedia-en-spam']
        self.write_channels = ['##legoktm', 'legoktm']
        self.error_channel = 'legoktm'
        self.owners = ['legoktm!~legoktm@wikipedia/Legoktm']
        #COMMANDS
        self.commands = ['!status', '!isup', '!link', '!help', '!quit', '!list', '!last']
        self.owners = ['!quit']
        self.helptext = {'!status':'Gives current status of the bot',
                         '!isup':'Whether the bot is up.',
                         '!link':'Provides a link to wikipedia. Usage: !link [[User:Legobot]]',
                         '!help':'Provide help for a command. Usage: !help cmd',
                         '!quit':'Force the bot to disconnect from the server.',
                         '!list':'Give a list of commands.',
                         '!last':'Display the info about the last link',
        }
    
    def run_commands(self, line_data):
        if line_data['channel'] == 'Legobot':
            line_data['channel'] = 'legoktm'
        channel = line_data['channel']
        split = line_data['text'].split(' ')
        command = split[0][1:].strip().lower()
        text = ' '.join(split[1:])
        text = text.strip()
        if (command in self.owners) and (not line_data['authenticated']):
            self.send_to_channel('Sorry, %s, you can\'t run that command. Please talk to legoktm for permission.' % operator,
                                 channel)
            return
        if command == '!list':
            self.send_to_channel('!list: %s' % (', '.join(self.commands)), channel)
            return
        if command == '!help':
            if not text.startswith('!'):
                text = '!'+text
            if text in self.commands:
                if self.helptext.has_key(text):
                    msg = '%s: %s' % (text, self.helptext[text])
                    if text in self.owners:
                        msg += ' This command can only be run by owners.'
                    self.send_to_channel(msg, channel)
                    return
                else:
                    self.send_to_channel('Sorry, help isn\'t availible for this command. Please let legoktm know.', channel)
                    return
            else:
                self.send_to_channel('Sorry, thats not a valid command.', channel)
                return
        if command == '!quit':
            self.quit(msg=text, user=line_data['sender'])
            return
        if command == '!status':
            self.send_to_channel('The IRC bot is currently running.', channel)
            return
        if command == '!isup':
            self.send_to_channel('The cite-web bot is currently not running.', channel)
            return
        if command == '!last':
            self.send_to_channel(self.last_link, channel)
            return
        if command == '!link':
            if text.startswith('[[') and text.endswith(']]'):
                article = text[2:-2]
                link = 'http://enwp.org/' + article.strip().replace(' ','_')
                self.send_to_channel('%s: %s' %(line_data['sender'], link), channel)
                return
            else:
                self.send_to_channel("Sorry, I couldn't parse that link.", channel)
                return
        
        self.send_to_channel('Sorry %s, I didn\'t recognize that. Here is a list of my commands:', channel)
        self.send_to_channel('Type !help cmd to get more info: %s' % (', '.join(self.commands)), channel)
    
    def check_new_link(self, line_data):
        if not line_data['sender'].startswith('LiWa3'):
            #not a new link
            return
        text = line_data['text']
        start = text.find('[[en:')
        end = text.find(']]')
        article_name = text[start+5:end]
        if article_name.startswith('User:'):
            #skip articles not in mainspace
            return
        oldid_key = text.find('?diff=') + 6
        if oldid_key == (-1 + 6):
            oldid_key = text.find('?oldid=') + 7
        oldid = text[oldid_key:oldid_key+9]
        user_key = text.find('[[en:User') + 10
        user_end_key = user_key + text[user_key:].find(']]')
        user = text[user_key:user_end_key]
        link_part = text[user_end_key:]
        link_start = link_part.find('http')
        if link_start == -1:
            link_start = link_part.find('www')
            if link_start == -1:
                #wtf
                return
        link_end = link_part.find(' (')
        link = link_part[link_start:link_end]
        
        
        self.last_link ={'user':user, 'article_name':article_name, 'oldid':oldid, 'link':link}
        print self.last_link
        db.NEWLINKSQUEUE.put(self.last_link)
    
    def send(self, msg):
        self.s.send(msg+'\r\n')
    
    def send_to_channel(self, msg, channel):
        #if not (channel in self.write_channels):
        #    self.send_to_channel('Unable to send the following message to: '+channel, self.error_channel)
        #    self.send_to_channel(msg, self.error_channel)
        #    return
        self.send("PRIVMSG %s :%s" % (channel, unicode(msg)))
    
    def connect(self):
        self.s = socket.socket()
        self.s.connect((self.HOST, self.PORT))
        self.send("USER %s %s bla :%s" % (self.NICK, self.HOST, self.NICK))
        self.send("NICK %s" % self.NICK)
        self.connected = True
    
    def start(self):
        self.connect()
        self.welcomed = False
        self.joined = False
        while self.connected:
            try:
                self.readbuffer = self.readbuffer + self.s.recv(1024)
            except UnicodeDecodeError:
                continue
            temp = string.split(self.readbuffer, "\r\n")
            self.readbuffer = temp.pop()
            for line in temp:
                line = string.rstrip(line)
                line = string.split(line)
                line_data = {}
                line_data['sender'] = line[0][1:]
                line_data['authenticated'] = line_data['sender'] in self.owners
                line_data['channel'] = line[2]
                line_data['text'] = ' '.join(line[3:]).strip()               
                #print line_data
                if line[1] in ["372", "376", "375"]:
                    self.welcomed = True
                    continue
                if line[0] == "PING":
                    self.send("PONG %s" % line[0])
                    continue
                if self.welcomed and not self.joined:
                    for channel in self.join_channels:
                        self.send("JOIN "+channel)
                if line_data['channel'] == '#wikipedia-en-spam':
                    self.check_new_link(line_data)
                    continue
                if len(line) > 3:
                    if line[3][1:].startswith('!'):
                        self.run_commands(line_data)
                        continue
                    
                
    def quit(self, msg=None, user=None):
        if user and not msg:
            msg = 'Quit command issued by ' + user
        if not user:
            msg = 'Unknown error...quitting.'
        self.send('QUIT '+msg)
        self.connected = False

if __name__ == '__main__':
    bot = IRCBot()
    bot.start()