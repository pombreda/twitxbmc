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

 #xTweet, an XBMC script to interface with Twitter

#Standard modules
import os
import sys
#Third-party modules
import xbmcaddon
#Project modules


__settings__ = xbmcaddon.Addon(id='script.twitXBMC')
__language__ = __settings__.getLocalizedString
###Path handling
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
resDir = os.path.join(rootDir, 'resources')
libDir = os.path.join(resDir, 'lib')
skinsDir = os.path.join(resDir, 'skins')

sys.path.append (libDir)


from twitter_wrapper import *

def ShowMessage(MessageID):    
    import gui_auth
    message = __language__(MessageID)
    ui = gui_auth.GUI( "Message.xml" , os.getcwd(), "Default")
    ui.setParams ("message", __language__(30001), message, 0)
    ui.doModal()
    del ui
    
###Initial checks
#API Validation
api, auth = Twitter_Login()
if not api:
    ShowMessage(40004) #OAuth starts
else:
#Only start the gui if this module is executed directly
#if __name__ == "__main__":
    #xbmc.executebuiltin('Notification(twitXBMC,' + __language__(30000).encode( "utf-8", "ignore" ) + ',3000)')
    import gui
    ui = gui.GUI("Generic.xml" , os.getcwd(), "Default")
    ui.doModal()
    del ui
    