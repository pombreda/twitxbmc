import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import urllib
#import threading
from python_twitter import *
from utilities import *
from act import *

__settings__ = xbmcaddon.Addon(id='script.twitXBMC')
__language__ = __settings__.getLocalizedString

rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
resDir = os.path.join(rootDir, 'resources')
cacheDir = os.path.join(resDir, 'cache')

STATUS_LABEL = 100
LIST = 2000

BASE_PATH = xbmc.translatePath( os.getcwd() )

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

CONSUMER_KEY = "TmSvaQBT6UEZ0k5bu2GN2w"
CONSUMER_SECRET = "bW2G8PRYzyHMxaxw7qGzjdO6fw0caOJcBT5jrhwWg"

def addPadding(number):
    if len(number) == 1:
        number = '0' + number
    return number

class GUI( xbmcgui.WindowXMLDialog ):
    
    def __init__( self, *args, **kwargs ):
    
        pass


    def onInit( self ):
        self.player = xbmc.Player()
        audioIsPlaying = self.player.isPlayingAudio()
        videoIsPlaying = self.player.isPlayingVideo()
        if audioIsPlaying:
            self.getControl( 111 ).setVisible(True)
            self.getControl( 111 ).setLabel(__language__(30111))
        elif videoIsPlaying:
            self.getControl( 111 ).setVisible(True)
            self.getControl( 111 ).setLabel(__language__(30110))
        else:
            self.getControl( 111 ).setVisible(False)
        
        twitter_key = __settings__.getSetting('Key')
        twitter_secret = __settings__.getSetting('Secret')
        access_token = OAuthToken(twitter_key, twitter_secret)
        self.api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
        
        user = self.api.GetUserInfo()
        self.getControl( 102 ).setLabel(__language__(30102)+' ('+str(user.friends_count)+')')
        self.getControl( 103 ).setLabel(__language__(30103)+' ('+str(user.followers_count)+')')

        self.getTimeline()
        pass
    
    def image_cache(self,id,image_url):
        ext =''
        extl = image_url.split('.')
        for i in extl:
            ext=i
        img_path = os.path.join(cacheDir,str(id)+"."+ext)
        if os.path.isfile(img_path)==False:
            urllib.urlretrieve(image_url, img_path)    
        return img_path

    def getTimeline(self):
        self.getControl( LIST ).reset()
        statuses = self.api.GetFriendsTimeline()
        for s in statuses:
            img_url = self.image_cache(s.user.id,s.user.profile_image_url)
            listitem = xbmcgui.ListItem(label=s.user.name.encode('utf-8'),\
                                        label2=s.text.encode('utf-8'),\
                                        thumbnailImage=img_url)
            self.getControl( LIST ).addItem( listitem )                
        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
    
    def getFollowing(self):
        self.getControl( LIST ).reset()
        users = self.api.GetFriends()
        for u in users:
            img_url = self.image_cache(u.id,u.profile_image_url)
            s=u.status
            text = ''
            if u.status != None:
                print s
                text = s.text.encode('utf-8')
            listitem = xbmcgui.ListItem(label=u.name.encode('utf-8'),\
                                        label2=text,\
                                        thumbnailImage=img_url)
            self.getControl( LIST ).addItem( listitem )                

        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
    
    def getFollowers(self):
        self.getControl( LIST ).reset()
        users = self.api.GetFollowers()
        for u in users:
            img_url = self.image_cache(u.id,u.profile_image_url)
            s=u.status
            text = ''
            if u.status != None:
                print s
                text = s.text.encode('utf-8')
            listitem = xbmcgui.ListItem(label=u.name.encode('utf-8'),\
                                        label2=text,\
                                        thumbnailImage=img_url)
            self.getControl( LIST ).addItem( listitem )                

        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
    
    def getDirectMessages(self):
        self.getControl( LIST ).reset()
        dirmess = self.api.GetDirectMessages()
        for dm in dirmess:
            img_url =''
            text = dm.text.encode('utf-8')
            listitem = xbmcgui.ListItem(label=dm.sender_screen_name.encode('utf-8'),\
                                        label2=text,\
                                        thumbnailImage=img_url)
            self.getControl( LIST ).addItem( listitem )                
        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
    
    def tweetWhatImDoing( self ):
        if self.player.isPlayingAudio():
            return self.tweetWhatImListeningTo()
        elif self.player.isPlayingVideo():
            return self.tweetWhatImWatching()
        else:
            return False
            
    def tweetWhatImListeningTo( self ):
        try:
            title = __settings__.getSetting('MusicTweet').encode("utf-8",'ignore')
            title = title.replace('%ARTISTNAME%', xbmc.getInfoLabel("MusicPlayer.Artist").decode('utf-8'))
            title = title.replace('%SONGTITLE%', xbmc.getInfoLabel("MusicPlayer.Title").decode('utf-8'))
            title = title.replace('%ALBUMTITLE%', xbmc.getInfoLabel("MusicPlayer.Album").decode('utf-8'))
        except:
            return False
        message = appendFooterToStatus( title, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
        return self.tweet( message )

    def tweetWhatImWatching( self ):
        try:
            video = self.player.getVideoInfoTag()
        except:
            return False
            
        if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
            title = __settings__.getSetting('TVShowTweet').encode("utf-8",'ignore')    
            title = title.replace('%SHOWNAME%', xbmc.getInfoLabel("VideoPlayer.TvShowTitle").decode('utf-8'))
            title = title.replace('%EPISODENAME%', xbmc.getInfoLabel("VideoPlayer.Title").decode('utf-8'))
            title = title.replace('%EPISODENUMBER%', xbmc.getInfoLabel("VideoPlayer.Episode").decode('utf-8'))
            title = title.replace('%EPISODENUMBER_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Episode")).decode('utf-8'))            
            title = title.replace('%SEASON%', xbmc.getInfoLabel("VideoPlayer.Season").decode('utf-8'))
            title = title.replace('%SEASON_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Season")).decode('utf-8'))            
            message = appendFooterToStatus( title, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
            return self.tweet( message.encode('utf-8') )
        elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
            info = __settings__.getSetting('MovieTweet').encode("utf-8",'ignore')    
            info = info.replace('%MOVIETITLE%', xbmc.getInfoLabel("VideoPlayer.Title").decode('utf-8'))
            info = info.replace('%MOVIEYEAR%', xbmc.getInfoLabel("VideoPlayer.Year").decode('utf-8'))
            message = appendFooterToStatus( info, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
            return self.tweet( message.encode('utf-8') )
    
    def onClick( self, controlId ):
        if controlId == 100 : 
           self.tweetManually()
        if controlId == 101 : 
           self.getTimeline()
        if controlId == 102 : 
           self.getFollowing()
        if controlId == 103 : 
           self.getFollowers()
        if controlId == 104 : 
           self.getDirectMessages()
        if controlId == 105 : #Settings
            __settings__.openSettings()
        if controlId == 106 : #Exit
            self.close()
        
        if controlId == 111 : #Auto post
            self.tweetWhatImDoing()
        
        if controlId == 2000 : 
            item = self.getControl( LIST ).getSelectedItem()
            import notification
            import datetime
            ui = notification.GUI( "Notification.xml" , BASE_PATH, "Default")
            ui.setTwitterText (item.getLabel2().encode( "utf-8", "ignore" ), "mention", item.getLabel().encode( "utf-8", "ignore" ), '', datetime.datetime.now(), '')
            ui.doModal()
            del ui
        
        pass	

    def alertStatusEmpty( self ):
        dialog = xbmcgui.Dialog()
        dialog.ok( "Warning", __language__(30011)  )
        
    
    def alertStatusSuccessfullyUpdated( self ):
        dialog = xbmcgui.Dialog()
        dialog.ok(  "Success" , __language__(30012)  )
        
    def alertServerConnectionFailed( self ):
        dialog = xbmcgui.Dialog()
        dialog.ok( "Warning",  "Server_ConnectionFailed_Line1","Server_ConnectionFailed_Line2",  "Server_ConnectionFailed_Line3" )

    def alertStatusTooLong( self ):
        dialog = xbmcgui.Dialog()
        dialog.ok( "Warning" , __language__(30013)  )
        
    def tweet( self, message ):
        Debug( message, True)   
        try:
            self.api.PostUpdate( message )
            self.alertStatusSuccessfullyUpdated()
            return True
        except:
            self.alertServerConnectionFailed()
            return False
        
    def tweetManually( self ):
        keyboard = xbmc.Keyboard( "", __language__(30010) )
        while True:
            keyboard.doModal()
            if keyboard.isConfirmed():
                message = keyboard.getText().strip()
                if message == "":
                    self.alertStatusEmpty()
                elif len( message ) > twitter.CHARACTER_LIMIT:
                    self.alertStatusTooLong()
                else:
                    return self.tweet( message )
            else:
                return False
        
    def onFocus( self, controlId ):

        self.controlId = controlId


    def onAction( self, action ):
        #if ( action.getButtonCode() in CANCEL_DIALOG ):
        #    print "Closing"
        #    self.close()
        pass

def onAction( self, action ):
    if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.close()
    if ( action.getButtonCode() in CANCEL_DIALOG ):
	print "# Closing"
	self.close()