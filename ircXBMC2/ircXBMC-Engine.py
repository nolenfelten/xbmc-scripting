"""
    ircXBMC Engine
    Author: Sean Donnellan (Donno)  [darkdonno@gmail.com]
    
    Notes:
        Requires: Settings
        Shouldn't require Languages or xbmcgui (maybe for toast) or Dialogs
"""

__title__ = 'IRC-XBMC Engine'

import os
import sys

scriptPath = os.getcwd().replace( ';' , '' )
sys.path.append( os.path.join( scriptPath ,'libs' ) )

import irclib
from settings import Settings
from ircdb import ircUser
from ircdb import ircServer
from ircdb import ircChannel
irclib.DEBUG = 0

irc = irclib.IRC()

DEBUG = 1

defSettingsForAServer = { 'Auto Connect': ["false","boolean"], 'Address': ["irc.freenode.net","text"],'Port': ["6667","text"],'Channels': [['#xbmc'],'simplelist']}
defServerSettings = Settings("",__title__,defSettingsForAServer,2)

defSettings = {
    "Username": ["donno","text"],
    "Nickname": ["donno","text"],
    "Secondary Nickname": ["donnoII","text"],
    "Real Name": ["Donno", "text"],
    "Show TimeStamp": ["true","boolean"],
    "Quit Message": ["Quitting","text"],
    "Away Message": ["I'm busy","text"],
    "Auto Connect": ["true","boolean"],
    "Servers": [['server',[["FreeNode",defServerSettings,"settings"]]],"list"]
    }
settingsManager = Settings("ircxbmc.xml",__title__,defSettings)

def dP(text):
    if DEBUG: print "<DEBUG>: " + text

class ircClient:
    """
        One per Server
    """
    _clientNo = 1
    def __init__(self, server, port, ircUser, serverPassword=None, eventManger=None):
        dP("starting ircClient class")
        dP("using User Profile:\n %s" % ircUser.toString() )
        dP("connected to %s on port %i" % (server, port))

        self.server =   server
        self.port   =   port
        self.user   =   ircUser
        self.clientNo = self._clientNo
        self.eventManger = eventManger
        
        self._clientNo += 1
        self.server = irc.server()
        self.channels = {}
        self.connection = self.server.connect(server, port, ircUser.nickname, serverPassword, ircUser.username, ircUser.realname)
        self.hookEventManger()
        
    def toString(self):
        print "<ircClient> Server: %s\tPort: %s" % (self.server, self.port)

    def joinChannel(self, channel):
        dP("joinning channel: %s" % channel)
        self.connection.join(channel)
        # Wait for the onJoin event to add the channels

    def sendMessage(self, destName, message):
        self.server.privmsg(destName, message)

    def hookEventManger(self):
        self.connection.add_global_handler("welcome", self.eventManger.on_Connect)
        self.connection.add_global_handler("join", self.eventManger.on_Join)
        self.connection.add_global_handler("motd", self.eventManger.on_Motd)
        self.connection.add_global_handler("endofmotd",self.eventManger.on_Motdend)
        self.connection.add_global_handler("currenttopic", self.eventManger.on_Curtopic)
        self.connection.add_global_handler("topic", self.eventManger.on_Topic)
        self.connection.add_global_handler("privmsg", self.eventManger.on_Privmsg)
        self.connection.add_global_handler("ctcp", self.eventManger.on_Ctcpmsg)
        self.connection.add_global_handler("pubmsg", self.eventManger.on_Pubmsg)
        #self.connection.add_global_handler("namreply", self.eventManger.on_getnicklist) #not quite working
        self.connection.add_global_handler("kick", self.eventManger.on_Kick) #not quite working
        self.eventManger.addIrcClient(self)

class ircEventManger:
    def __init__(self):
        dP("<ircEventManger> Started")
        self.icClients = []

    def addIrcClient(self, Client):
        self.icClients.append(Client)

    def on_Connect(self, connection, event):
        dP("<ircEventManger> onConnect()")
    def on_Kick(self, connection, event):
        dP("<ircEventManger> onKick()")
    def on_Join(self, connection, event):
        for iC in self.icClients:
            if (iC.connection == connection):
                if (irclib.nm_to_n(event.source()) == iC.user.nickname):
                    dP("<ircEventManger> onJoin(): You have joined the channel %s" + event.target())
                    #|donno|!n=donno@ppp230-121.static.internode.on.net
                    iC.channels[event.target()] = ircChannel(event.target())
                    print iC.channels
                else:
                    dP("<ircEventManger> onJoin(): Some User %s" + event.source())

        
    def on_Privmsg (self, connection, event):
        dP("<ircEventManger> onPrivMsg()")
        print event
    def on_Motd (self, connection, event):
        dP("<ircEventManger> onConnect()")
    def on_Motdend (self, connection, event):
        dP("<ircEventManger> onConnect()")
    def on_Ctcpmsg (self, connection, event):
        dP("<ircEventManger> onConnect()")
    def on_Pubmsg (self, connection, event):
        dP("<ircEventManger> on_Pubmsg()")
        #event.eventtype() == Should be pubmsg
        nickName = irclib.nm_to_n(event.source())
        userName = irclib.nm_to_h(event.source())
        hostName = irclib.nm_to_u(event.source())
        srcUser = ircUser(nickName,userName,None,hostName)
        print srcUser.toString()
                
        channel =  event.target()
        message = event.arguments()[0]
        print "%s | <%s>\t%s" % (channel, sourceNickName, message)

    def on_Topic (self, connection, e):
        dP("<ircEventManger> onConnect()")
    def on_Curtopic(self, connection,e):
        pass

def main():
    print "Starting " + __title__
    # Startup Event Manager
    eM = ircEventManger()
    # Create User to use    
    dP("getting User Infomation")
    theUser = ircUser(settingsManager.getSetting("Nickname"),settingsManager.getSetting("Username"),settingsManager.getSetting("Real Name"),"")
    theUser.secondarynick = settingsManager.getSetting("Secondary Nickname")
    print theUser.toString()

    theServers = []
    
    # Get Servers, Address Ports
    dP("getting Server list")
    if (settingsManager.getSettingType("Servers") == "list"):
        servers = settingsManager.getSetting("Servers")[1]
        for server in servers:
            if (server[2] == "settings"):
                serverName = server[0]                
                nfo1 = server[1].getSetting("Address")
                nfo2 = server[1].getSetting("Port")
                nfo3 = server[1].getSetting("Auto Connect")
                channels = server[1].getSetting("Channels")
                theServer = ircServer(serverName,nfo1,nfo2,nfo3,channels)
                theServers.append(theServer)

    # Create the ircClient 
    dP("creating ircClients")
    icClients = []
    for server in theServers:
        if (server.autoConnect == "true"):
            print "ok port=|%s|" % server.port
            iC = ircClient(server.address, int(server.port), theUser,eventManger=eM)    
            icClients.append(iC)     
            if (len(server.channels) > 0):
                for chan in server.channels:
                    iC.joinChannel(chan)
    if len(icClients) > 0:
        irc.process_forever() 
    else:
        dP("didn't join any servers")
    
    # Do Stuff here 

    print __title__ + " has been exited"

if __name__ == "__main__":    main()
    