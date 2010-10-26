#Standard modules
import os
import sys
#Third-party modules
import xbmcaddon
#Project modules


__settings__ = xbmcaddon.Addon(id='script.Screensaver.Clock')
__language__ = __settings__.getLocalizedString
###Path handling
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
resDir = os.path.join(rootDir, 'resources')
libDir = os.path.join(resDir, 'lib')
skinsDir = os.path.join(resDir, 'skins')

sys.path.append (libDir)

import gui
ui = gui.GUI("Generic.xml" , os.getcwd(), "Default")
ui.doModal()
    