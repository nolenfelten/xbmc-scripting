"""
    ircdb
    
    Classes and Tools for storing infomation about irc objects.
    
    Author: Sean Donnellan (Donno)  [darkdonno@gmail.com]
    
"""
class ircUser:
    def __init__(self, nickname, username, realname, hostname):
        self.username = username
        self.nickname = nickname
        self.realname = realname
        self.hostname = hostname
        self.secondarynick = ""

    def toString(self):
        return "<User> Username: %s\tNickName: %s\tRealname: %s\tHostName: %s" % ( self.username , self.nickname , self.realname, self.hostname )

        
class ircServer:
    def __init__(self, name, address, port, autoConnect, channels=[]):
        self.name = name
        self.address = address
        self.port = port
        self.autoConnect = autoConnect
        self.channels = channels

    def toString(self):
        #return "Username: %s\tNickName: %s\tRealname: %s" % ( self.username , self.nickname , self.realname )
        return "<Server> Name: %s\tAddress: %s\tPort: %s\tAutoConenct: %s" % ( self.name , self.address , self.port,  self.autoConnect)
        
class ircChannel:
    def __init__(self, channelName, topic, modes):
        self.channelName = channelName
        self.topic = topic
        self.modes = modes
        self.users = []

    def toString(self):
        #return "<User> Username: %s\tNickName: %s\tRealname: %s\tHostName: %s" % ( self.username , self.nickname , self.realname, self.hostname )
        pass
