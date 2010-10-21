import sys
import os
import time
import xbmc
import xbmcgui
import xbmcaddon
import urllib
#import threading
import twitter
#from python_twitter import *
from utilities import *
from act import *

__settings__ = xbmcaddon.Addon(id='script.twitXBMC')
__language__ = __settings__.getLocalizedString

rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
resDir = os.path.join(rootDir, 'resources')

cacheDir = xbmc.translatePath('special://profile/addon_data/script.twitXBMC/cache/')
if not os.path.exists(cacheDir): os.makedirs(cacheDir)


STATUS_LABEL = 133
LIST = 2000


BASE_PATH = xbmc.translatePath( os.getcwd() )

KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

ACTION_CONTEXT_MENU   = 117

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
        self.pageTimeline = 1;
        self.userTimeline = None
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
        #access_token = OAuthToken(twitter_key, twitter_secret)
        #self.api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
        self.api = twitter.Api(consumer_key=CONSUMER_KEY,
                            consumer_secret=CONSUMER_SECRET,
                            access_token_key=twitter_key,
                            access_token_secret=twitter_secret,
                            base_url=__settings__.getSetting('BaseUrl'),
                            use_gzip_compression = True)
        
        user = self.api.VerifyCredentials()
        self.getControl( 100 ).setLabel(__language__(30100)+' ('+str(user.statuses_count)+')')
        self.getControl( 102 ).setLabel(__language__(30102)+' ('+str(user.friends_count)+')')
        self.getControl( 103 ).setLabel(__language__(30103)+' ('+str(user.followers_count)+')')
        img_url = self.image_cache(user.id,user.profile_image_url)
        self.getControl( 222 ).setImage(img_url)
        self.getControl( 223 ).setLabel(user.name.encode('utf-8'))
        self.getControl( 224 ).setLabel(user.location.encode('utf-8'))
        self.getControl( 225 ).setLabel(user.status.text.encode('utf-8'))
        
        self.getControl( STATUS_LABEL ).setLabel(__language__(30101))
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
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        if (self.pageTimeline==1):
            self.getControl( LIST ).reset()
        pos = self.getControl( LIST ).getSelectedPosition()
        
        retw = __settings__.getSetting('view_retweet')
        
        if (self.userTimeline is None): 
            statuses = self.api.GetFriendsTimeline(page=self.pageTimeline,retweets=retw)
        else:
            statuses = self.api.GetUserTimeline(id = self.userTimeline,page=self.pageTimeline)
        for s in statuses:
            img_url = self.image_cache(s.user.id,s.user.profile_image_url)
            listitem = xbmcgui.ListItem(label=s.user.name.encode('utf-8'),\
                                        label2=s.text.encode('utf-8'),\
                                        thumbnailImage=img_url)
            created = time.localtime( s.GetCreatedAtInSeconds() )
            timestamp = time.strftime( '%Y-%m-%d %H:%M', created )
            listitem.setProperty( "created_at", timestamp )
            listitem.setProperty( "source", s.source )
            listitem.setProperty( "idUser", str(s.user.id) )
            listitem.setProperty( "nickUser", str(s.user.screen_name) )
            listitem.setProperty( "idStatus", str(s.id) )
            self.getControl( LIST ).addItem( listitem )                
        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem(pos)
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        self.pageTimeline = self.pageTimeline + 1
    
    def getFollowing(self):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        self.getControl( LIST ).reset()
        users = self.api.GetFriends(user=self.userTimeline)
        for u in users:
            img_url = self.image_cache(u.id,u.profile_image_url)
            s=u.status
            text = ''
            if u.status != None:
                text = s.text.encode('utf-8')
            listitem = xbmcgui.ListItem(label=u.name.encode('utf-8'),\
                                        label2=text,\
                                        thumbnailImage=img_url)
            listitem.setProperty( "idUser", str(u.id) )
            self.getControl( LIST ).addItem( listitem )                

        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    
    def getFollowers(self):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        self.getControl( LIST ).reset()
        users = self.api.GetFollowers()
        for u in users:
            img_url = self.image_cache(u.id,u.profile_image_url)
            s=u.status
            text = ''
            if u.status != None:
                text = s.text.encode('utf-8')
            listitem = xbmcgui.ListItem(label=u.name.encode('utf-8'),\
                                        label2=text,\
                                        thumbnailImage=img_url)
            listitem.setProperty( "idUser", str(u.id) )
            self.getControl( LIST ).addItem( listitem )                

        self.setFocus( self.getControl( LIST ) )
        self.getControl( LIST ).selectItem( 0 )
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    
    def getDirectMessages(self):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
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
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    
    def tweetWhatImDoing( self ):
        if self.player.isPlayingAudio():
            return self.tweetWhatImListeningTo()
        elif self.player.isPlayingVideo():
            return self.tweetWhatImWatching()
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(  "Success" , "No playing"  )
            return False
            
    def tweetWhatImListeningTo( self ):
        try:
            title = __settings__.getSetting('MusicTweet')
            title = title.replace('%ARTISTNAME%', xbmc.getInfoLabel("MusicPlayer.Artist"))
            title = title.replace('%SONGTITLE%', xbmc.getInfoLabel("MusicPlayer.Title"))
            title = title.replace('%ALBUMTITLE%', xbmc.getInfoLabel("MusicPlayer.Album"))
            message = appendFooterToStatus( title, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
            return self.tweet( message)    
        except Exception, ex:
            Debug('Error tweetWhatImListeningTo - '+str(ex),True)
            return False
        

    def tweetWhatImWatching( self ):
        try:
            if len(xbmc.getInfoLabel("VideoPlayer.TVshowtitle")) >= 1: # TvShow
                title = __settings__.getSetting('TVShowTweet')   
                title = title.replace('%SHOWNAME%', xbmc.getInfoLabel("VideoPlayer.TvShowTitle"))
                title = title.replace('%EPISODENAME%', xbmc.getInfoLabel("VideoPlayer.Title"))
                title = title.replace('%EPISODENUMBER%', xbmc.getInfoLabel("VideoPlayer.Episode"))
                title = title.replace('%EPISODENUMBER_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Episode")))            
                title = title.replace('%SEASON%', xbmc.getInfoLabel("VideoPlayer.Season"))
                title = title.replace('%SEASON_PADDED%', addPadding(xbmc.getInfoLabel("VideoPlayer.Season")))            
                message = appendFooterToStatus( title, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
                return self.tweet( message )
            elif len(xbmc.getInfoLabel("VideoPlayer.Title")) >= 1: #Movie
                info = __settings__.getSetting('MovieTweet')    
                info = info.replace('%MOVIETITLE%', xbmc.getInfoLabel("VideoPlayer.Title"))
                info = info.replace('%MOVIEYEAR%', xbmc.getInfoLabel("VideoPlayer.Year"))
                message = appendFooterToStatus( info, twitter.CHARACTER_LIMIT, __settings__.getSetting('TagsTweet') )
                return self.tweet( message )
        except Exception, ex:
            Debug('Error tweetWhatImWatching - '+str(ex),True)
            return False
    
    def onClick( self, controlId ):
        if controlId == 100 : 
           self.tweetManually()
        if controlId == 101 :
            self.pageTimeline = 1;
            self.userTimeline = None;
            self.getControl( STATUS_LABEL ).setLabel(__language__(30101))
            self.getTimeline()
        if controlId == 102 : 
            self.getControl( STATUS_LABEL ).setLabel(__language__(30102))
            self.pageTimeline = 0;
            self.userTimeline = None;
            self.getFollowing()
        if controlId == 103 : 
            self.getControl( STATUS_LABEL ).setLabel(__language__(30103))
            self.pageTimeline = 0;
            self.userTimeline = None;
            self.getFollowers()
        if controlId == 104 : 
            self.getControl( STATUS_LABEL ).setLabel(__language__(30104))
            self.userTimeline = None;
            self.getDirectMessages()
        if controlId == 105 : #Settings
            __settings__.openSettings()
        if controlId == 106 : #Exit
            self.close()
        
        if controlId == 111 : #Auto post
            self.tweetWhatImDoing()
        
        # if controlId == 2000 : 
            # item = self.getControl( LIST ).getSelectedItem()
            # import notification
            # import datetime
            # ui = notification.GUI( "Notification.xml" , BASE_PATH, "Default")
            # ui.setTwitterText (item.getLabel2(), "mention", item.getLabel(), '', datetime.datetime.now(), '')
            # ui.doModal()
            # del ui
        
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
        dialog.ok( "Warning" , __language__(30013)%(twitter.CHARACTER_LIMIT)  )
        
    def tweet( self, message, reply_id=None ):
        Debug( message, True)   
        try:
            self.api.PostUpdate( message, reply_id )
            self.alertStatusSuccessfullyUpdated()
            self.getControl( 225 ).setLabel(message)
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

    def doMenu(self):
        item = self.getControl( LIST ).getSelectedItem()
        user=item.getProperty("idUser")
        status = item.getProperty("idStatus")
        #print status
        dialog = xbmcgui.Dialog()
        if (status !=""):
            idx = dialog.select(__language__(30200),[__language__(30201),__language__(30202),__language__(30203),__language__(30204),])
        else:
            idx = dialog.select(__language__(30200),[__language__(30201),__language__(30202),])

        self.userTimeline = user
        if idx == 0: 
            self.pageTimeline = 1
            self.getControl( STATUS_LABEL ).setLabel(__language__(30101)+" "+item.getLabel().decode('utf-8'))
            self.getTimeline()
        elif idx == 1: 
            self.pageTimeline = 0
            self.getControl( STATUS_LABEL ).setLabel(__language__(30102)+" "+item.getLabel().decode('utf-8'))
            self.getFollowing()
        elif idx == 2: 
            message = "RT: @%s %s"%(item.getLabel(),item.getLabel2(),)
            self.tweet("", status)
        elif idx == 3: 
            keyboard = xbmc.Keyboard( "", __language__(30014) )
            keyboard.doModal()
            if keyboard.isConfirmed():
                message = keyboard.getText().strip()
                if message == "":
                    self.alertStatusEmpty()
                elif len( message ) > twitter.CHARACTER_LIMIT:
                    self.alertStatusTooLong()
                else:
                    nickUser = item.getProperty("nickUser")
                    message = "@%s %s"%(nickUser,message)
                    self.tweet(message, status)
            

    def onAction( self, action ):
        if action == ACTION_CONTEXT_MENU:
            self.doMenu()
            pass
        if (self.pageTimeline == 0):
            pass
        count = self.getControl( LIST ).size()
        pos = self.getControl( LIST ).getSelectedPosition()
        if (count > 1):
            if (pos==count-1):
                self.getTimeline()
        pass

def onAction( self, action ):
    if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC):
            self.close()
    if ( action.getButtonCode() in CANCEL_DIALOG ):
        print "# Closing"
        self.close()