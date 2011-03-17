
#Modules General
import os
from sys import argv

# Modules XBMC
import xbmc, xbmcgui
from xbmcaddon import Addon

ADDON = Addon(id='script.ambilight')
__language__ = ADDON.getLocalizedString

def setSDK(status):
	LF = open(ADDON.getSetting('status_path'), 'w')
	LF.write(status)
	LF.close()

#########################################################################################################
## BEGIN
#########################################################################################################
quit = False
menu = [__language__(32060), __language__(32061), __language__(32062),__language__(32063)]

# Meda select loop
while not quit:
	# choose media type inorder to mask files
	selected = xbmcgui.Dialog().select(__language__(32064), menu )
	print "selected=%s" % selected
	if selected < 0:
		break
	elif selected == 0:
		setSDK("ambilight")
	elif selected == 1:
		setSDK("backlight")
	elif selected == 2:
		setSDK("moodlamp")
	elif selected == 3:
		setSDK("off")
	quit = True
