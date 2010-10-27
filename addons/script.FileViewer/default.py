"""

 Script to view text using a xbmc skins pre-defined window

 Written by BigBellyBilly

  Like my script, why not Buy Me A Beer !?  

"""

import sys, os.path
import xbmc, xbmcgui
import xbmcaddon

# Script constants
__scriptname__ = "FileViewer"
__date__ = '27-01-2010'
__version__ = "1.0"
xbmc.output( __scriptname__ + " Version: " + __version__  + " Date: " + __date__)

__settings__ = xbmcaddon.Addon(id='script.FileViewer')
__language__ = __settings__.getLocalizedString


#################################################################################################################
class TextViewer( xbmcgui.WindowXML ):
	""" Use a skins text XML window to view text """

	XML_FILENAME = "DialogTextViewer.xml"       # xbmc skin supplied textbox viewer
	ACTION_EXIT = ( 9, 10, 247, 275, 61467, 216, 257, 61448,)

	def __init__( self, *args, **kwargs):
		pass
		
	def onInit( self ):
		try:
			self.getControl( 3 ).setLabel( self.title )		# may not have an ID assigned
		except: pass
		self.getControl( 5 ).setText( self.text )

	def onClick( self, controlId ):
		pass

	def onFocus( self, controlId ):
		pass

	def onAction( self, action ):
		if action and (action.getButtonCode() in self.ACTION_EXIT or action.getId() in self.ACTION_EXIT):
			self.close()

	def ask(self, title="", text="", fn="" ):
		if not title and fn:
			self.title = os.path.basename(fn)
		else:
			self.title = title

		# load from file as a priority
		if fn:
			try:
				self.text = file(fn).read()
			except:
				self.text = text
		else:
			self.text = text

		self.doModal()		# causes window to be drawn

#########################################################################################################
## BEGIN
#########################################################################################################
quit = False
defaultFolder = ""
mediaVideos = xbmc.getSupportedMedia('video')
mediaMusics = xbmc.getSupportedMedia('music')
mediaPictures =xbmc.getSupportedMedia('picture')
menu = [__language__(100), __language__(101), __language__(102),__language__(103)]

# Meda select loop
while not quit:
	# choose media type inorder to mask files
	selected = xbmcgui.Dialog().select(__language__(110), menu )
	print "selected=%s" % selected
	if selected < 0:
		break
	elif selected == 0:
		mask = ""
	elif selected == 1:
		mask = mediaVideos
	elif selected == 2:
		mask = mediaMusics
	elif selected == 3:
		mask = mediaPictures

	# File browse loop
	title = "(%s) %s" % ( menu[selected], __language__(111))
	while not quit:
		# Show browser, using selected file mask
		print "defaultFolder=" + defaultFolder
		fn = xbmcgui.Dialog().browse(1, title, "files", mask, False, False, defaultFolder)
		if not fn or fn == defaultFolder:
			break

		# examine file and play or view accordingly
		defaultFolder = os.path.dirname(fn)
		xbmc.output( "fn=%s" % fn )
		ext = os.path.splitext(fn)[1].lower()
		try:
			if ext in mediaVideos + mediaMusics:
				# MEDIA file
#				xbmc.executebuiltin("xbmc.PlayMedia(%s)" % fn)
				xbmc.Player().play(fn)
				if ext in mediaVideos:
					xbmc.executebuiltin("xbmc.ActivateWindow('video')")
					quit = True
			elif ext in mediaPictures:
				xbmc.executehttpapi("Stop()")
				xbmc.executehttpapi("ShowPicture(%s)" % fn)
				quit = True
			else:
				# TEXT file
				print 1
				tbd = TextViewer(TextViewer.XML_FILENAME, os.getcwd())
				tbd.ask( fn=fn )
				del tbd
		except:
			m = str( sys.exc_info()[ 1 ] )
			xbmc.output(m)
			xbmcgui.Dialog().ok(__scriptname__, "Error opening file:", fn, m)

sys.modules.clear()