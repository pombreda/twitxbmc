#
#Copyright (C) 2009  Steven J. Burch
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You may obtain a copy of this license at:
#  http://www.gnu.org/licenses/gpl-3.0.html


#Standard modules
import os
import sys
import datetime
#Third-party modules
import xbmcaddon
from pysqlite2 import dbapi2 as sqlite3
#Project modules


__scriptID__      = "script.XMPPnotify"
__settings__ = xbmcaddon.Addon(id=__scriptID__)
__language__ = __settings__.getLocalizedString
###Path handling
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
resDir = os.path.join(rootDir, 'resources')
libDir = os.path.join(resDir, 'lib')
sys.path.append (libDir)
skinsDir = os.path.join(resDir, 'skins')

addon_work_folder = os.path.join(xbmc.translatePath( "special://profile/addon_data/" ), __scriptID__)
addon_db = os.path.join(addon_work_folder, "xmpp.db")



from utilities import *

import xmpp
    
bot = None
AUTO_RESTART=0
OldAutoStatus = ''

Debug('Entering idle state...', False)
smallicon = xbmc.translatePath( os.path.join( skinsDir, 'Default', 'media', 'smallxmpp.png' ) )
xbmc.executebuiltin('Notification(XMPP notify,Load addon...,3000,' + smallicon + ')')

######################################################################
#create the addon's database
def database_setup():
        print "#  Setting Up Database"
        print "#    addon_work_path: %s" % addon_work_folder
        if not os.path.exists(addon_work_folder):
            print "#  Settings not set, aborting database creation"
            return -1
        if  os.path.exists(addon_db):
            print "#  Database find"
            return 0
        conn = sqlite3.connect(addon_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE messages(dt TIMESTAMP, jid, message)''')
        conn.commit()
        c.close()
        return 1

######################################################################
def start():
    global bot
    global LOGGEDIN
    LOGGEDIN = 0
    acc = xmpp.JID(__settings__.getSetting( "Login" )) 
    user,server=acc.getNode(),acc.getDomain()
    bot = xmpp.Client(server,debug=[])
    
    if bot.connect():
        print "Connected"
    else:
        print "Couldn't connect"
        sys.exit(1)
        return

    if bot.auth(user,__settings__.getSetting( "Password" ),__settings__.getSetting( "Resource")):
        print 'Logged In'
    else:
        print "Auth error: eek -> ", bot.lastErr, bot.lastErrCode
        time.sleep(60) # sleep for 10 seconds
        sys.exit(1)
        return
       
    bot.roster = bot.getRoster()
    
    
    
    
    bot.RegisterDisconnectHandler(bot.reconnectAndReauth)
    bot.RegisterHandler('message',message_callback)
    bot.sendInitPresence()
    print "Bot started."

    presence = xmpp.Presence(status = "", show = "online", priority = __settings__.getSetting( "priority"))
    bot.send(presence)
    
    smallicon = xbmc.translatePath( os.path.join( skinsDir, 'Default', 'media', 'smallxmpp.png' ) )
    xbmc.executebuiltin('Notification(XMPP notify,Connected ...,3000,' + smallicon + ')')
    
    LOGGEDIN = 1

    while 1:
        if (__settings__.getSetting( "AutoStatusEnable")):
            AutoStatus()
        bot.Process(10)

def message_callback(conn,mess):
    try:
        msg = mess.__str__()#.encode('utf8')
        user=mess.getFrom()
        user=str(user).split('/')
        user=user[0]
        text = mess.getBody()
        #print text
        if ( text == None ):
            return
            
        command = "insert into messages(dt, jid, message) values('%s','%s','%s')" %(datetime.datetime.now(),str(user),text)
        con = sqlite3.connect(addon_db)
        c=con.cursor() 
        try: 
            c.execute(command) 
            con.commit()
        except sqlite3.OperationalError,e: 
            print(str(e)) 
        con.close()

        smallicon = xbmc.translatePath( os.path.join( skinsDir, 'Default', 'media', 'smallxmpp.png' ) )
        xbmc.executebuiltin('Notification('+user.encode('utf-8','ignore')+',' + text.encode('utf-8','ignore') + ',5000,' + smallicon + ')')

        
    except Exception ,x:
        print "Error-"+ str(x)
        
def addPadding(number):
    if len(number) == 1:
        number = '0' + number
    return number
    
def AutoStatus():
    global bot
    global OldAutoStatus
    try:
        status = 'online'
        text = ''
        player = xbmc.Player()
        if player.isPlayingAudio():
                text = __settings__.getSetting('Music')
                text = text.replace('%ARTISTNAME%', xbmc.getInfoLabel("MusicPlayer.Artist"))
                text = text.replace('%SONGTITLE%', xbmc.getInfoLabel("MusicPlayer.Title"))
                text = text.replace('%ALBUMTITLE%', xbmc.getInfoLabel("MusicPlayer.Album"))
                status = 'away'
        elif player.isPlayingVideo():
            if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
                text = __settings__.getSetting('TVShow')   
                text = text.replace('%SHOWNAME%', xbmc.getInfoLabel("VideoPlayer.TvShowTitle"))
                text = text.replace('%EPISODENAME%', xbmc.getInfoLabel("VideoPlayer.Title"))
                text = text.replace('%EPISODENUMBER%', xbmc.getInfoLabel("VideoPlayer.Episode"))
                text = text.replace('%EPISODENUMBER_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Episode")))            
                text = text.replace('%SEASON%', xbmc.getInfoLabel("VideoPlayer.Season"))
                text = text.replace('%SEASON_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Season")))   
                status = 'away'
            elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
                text = __settings__.getSetting('Movie')    
                text = text.replace('%MOVIETITLE%', xbmc.getInfoLabel("VideoPlayer.Title"))
                text = text.replace('%MOVIEYEAR%', xbmc.getInfoLabel("VideoPlayer.Year"))
                status = 'away'
        else:
            status = 'online'
            text = ''
        if (text!=OldAutoStatus):
            presence = xmpp.Presence(status = text, show = status, priority = __settings__.getSetting( "priority"))
            bot.send(presence)        
            OldAutoStatus = text
    except Exception ,x:
        print "Error-"+ str(x) 

if __name__ == "__main__":
    try:	
        database_setup()
        start()
    except KeyboardInterrupt:
        print 'INTERRUPT'
        
        sys.exit(1)
    except:
        if AUTO_RESTART:
            if sys.exc_info()[0] is not SystemExit:
                traceback.print_exc()
            try:
                bot.disconnected()
            except IOError:
                # IOError is raised by default DisconnectHandler
                pass
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print 'INTERRUPT'
                sys.exit(1)
            print 'RESTARTING'
            os.execl(sys.executable, sys.executable, sys.argv[0])
        else:
            raise

#EOF