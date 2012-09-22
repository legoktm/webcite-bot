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
        self.operators = ['legoktm', 'SigmaWP', 'CoalBalls']
        #COMMANDS
        self.commands = ['!status', '!link', '!help', '!quit', '!list', '!last']
        self.owners = ['!quit']
        self.helptext = {'!status':'Gives current status of the bot',
                         '!link':'Provides a link to wikipedia. Usage: !link [[User:Legobot]]',
                         '!help':'Provide help for a command. Usage: !help cmd',
                         '!quit':'Force the bot to disconnect from the server.',
                         '!list':'Give a list of commands.',
                         '!last':'Display the info about the last link parsed from #wikipedia-en-spam',
        }
        self.last_link = None
    
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
            self.send_to_channel('IRC: up. Link harvester: up. Link archiver: down. On-wiki bot: down.', channel)
            return
        if command == '!last':
            if not self.last_link:
                msg = 'I have not parsed a link from #wikipedia-en-spam yet.'
            else:
                msg = self.last_link
            self.send_to_channel(msg, channel)
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
        #TODO: Move this into a webcite.db queue class
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
        if link.endswith('\x03'):
            link = link[:-1]
        
        
        self.last_link ={'user':user, 'article_name':article_name, 'oldid':oldid, 'link':link}
        print(self.last_link)
        db.NEWLINKSQUEUE.put(self.last_link)
    
    def send(self, msg):
        line = msg+'\r\n'
        self.s.send(line.encode())
    
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
                self.readbuffer = self.readbuffer + self.s.recv(1024).decode()
            except UnicodeDecodeError:
                continue
            temp = string.split(self.readbuffer, "\r\n")
            self.readbuffer = temp.pop()
            for line in temp:
                try:
                    self.parse_line(line)
                except Exception as e:
                    print(e)
                    print(line)
                
    def parse_line(self, line):
        line = string.rstrip(line)
        line = string.split(line)
        if line[0] == "PING":
            self.send("PONG %s" % line[0])
            return
        if line[1] in ["372", "376", "375"]:
            self.welcomed = True
            return
        line_data = {}
        line_data['sender'] = line[0][1:]
        line_data['authenticated'] = False
        for owner in self.owners:
            if owner in line_data['sender']:
                line_data['authenticated'] = True
        line_data['channel'] = line[2]
        line_data['text'] = ' '.join(line[3:]).strip()               
        #print line_data
        if self.welcomed and not self.joined:
            for channel in self.join_channels:
                self.send("JOIN "+channel)
        if line_data['channel'] == '#wikipedia-en-spam':
            self.check_new_link(line_data)
            return
        if len(line) > 3:
            if line[3][1:].startswith('!'):
                self.run_commands(line_data)
                return
                    
                
    def quit(self, msg=None, user=None):
        if user and not msg:
            msg = 'Quit command issued by ' + user
        if not user:
            msg = 'Unknown error...quitting.'
        self.send('QUIT '+msg)
        self.connected = False
        sys.exit(0)

if __name__ == '__main__':
    bot = IRCBot()
    bot.start()