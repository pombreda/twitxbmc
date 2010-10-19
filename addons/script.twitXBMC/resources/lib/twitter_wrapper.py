import sys
import os
import xbmc
import xbmcgui
import xbmcaddon
import string
import openbrowser
import time
import ConfigParser
import string
import urllib2

#from python_twitter import *
from utilities import *
from twitter import *


__settings__ = xbmcaddon.Addon(id='script.twitXBMC')
__language__ = __settings__.getLocalizedString

MEDIA_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'skins' ) )

CONSUMER_KEY = "TmSvaQBT6UEZ0k5bu2GN2w"
CONSUMER_SECRET = "bW2G8PRYzyHMxaxw7qGzjdO6fw0caOJcBT5jrhwWg"

try:
  from urlparse import parse_qsl
except:
  from cgi import parse_qsl
  
import oauth2 as oauth

REQUEST_TOKEN_URL = 'http://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'http://api.twitter.com/oauth/authorize'
SIGNIN_URL        = 'http://api.twitter.com/oauth/authenticate'

lasttweet = ""

def Twitter_Login(bWhichAccount = False):
    Debug( '::Login::' , True)
    Debug( 'Using OAuth', True)
    #OAuth login details found
    twitter_key = __settings__.getSetting('Key')
    twitter_secret = __settings__.getSetting('Secret')
    #access_token = OAuthToken(twitter_key, twitter_secret)
    #api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, access_token)
    api = twitter.Api(consumer_key=CONSUMER_KEY,
                            consumer_secret=CONSUMER_SECRET,
                            access_token_key=twitter_key,
                            access_token_secret=twitter_secret,
                            base_url=__settings__.getSetting('BaseUrl'),
                            use_gzip_compression = True)
    
    bVerified, sError = VerifyAuthentication(api)
    if (not bVerified):
                ShowMessage(40001) 
                Debug( 'get request url', True)
                api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET,base_url=__settings__.getSetting('BaseUrl')) 
                request_token = api.getRequestToken()
                redirect_url = api.getAuthorizationURL(request_token)
                Debug( 'request url - '+redirect_url, True)
                openbrowser.open(redirect_url)
                keyboard = xbmc.Keyboard('',__language__(30000))
                keyboard.doModal()
                if (keyboard.isConfirmed()):
                    password = keyboard.getText()
                    Debug( 'PIN - '+password, True)
                else:
                    #Maybe using text based browser or XBOX
                    ShowMessage(40002)
                    return False, False
                try:
                    Debug( 'get key secret', True)
                    api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, request_token,base_url=__settings__.getSetting('BaseUrl')) 
                    token = api.getAccessToken(password)
                    api = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET, token,base_url=__settings__.getSetting('BaseUrl'))
                    Debug( 'key-%s secret%s'%(token.key,token.secret), True)
                    twitter_key = token.key
                    twitter_secret = token.secret
                except Exception, ex:
                    #PIN Number incorrect
                    Debug('Error - '+str(ex), True)
                    ShowMessage(40003)
                    return False, False
                Debug( 'Writing Configuration Details...', True)
                __settings__.setSetting(id='Key', value=twitter_key)
                __settings__.setSetting(id='Secret', value=twitter_secret)
                try:
                    api = twitter.Api(consumer_key=CONSUMER_KEY,
                            consumer_secret=CONSUMER_SECRET,
                            access_token_key=twitter_key,
                            access_token_secret=twitter_secret,
                            base_url=__settings__.getSetting('BaseUrl'),
                            use_gzip_compression = True)
                    bVerified, sError = VerifyAuthentication(api)
                    if (not bVerified):
                        return False, False
                except:
                    Debug( 'Exception: Login: ' + str(sys.exc_info()[1]), True)
                    return False, False
   
    Debug( '::Login::', True) 
    return api, api
       
def VerifyAuthentication(api):
    Debug( '::VerifyAuthentication::', True)   
    bVerified = False
    sError = ""
    if (api):
        try:
            user = api.VerifyCredentials()
            if (user != None): bVerified = True
        except Exception,ex:
            sError = "Exception: Failed to verify credentials: api.verify_credentials()"
            print sError
            print str(ex)
    Debug( '::VerifyAuthentication::', True)   
    return bVerified, sError
    
def ShowMessage(MessageID):    
    import gui_auth
    message = __language__(MessageID)
    ui = gui_auth.GUI( "Message.xml" , os.getcwd(), "Default")
    ui.setParams ("message", __language__(30001), message, 0)
    ui.doModal()
    del ui

def CheckAPIRate(api):
    #check we didn't hit the api limit
    apicallsleft = 0
    try:
        count = str(api.rate_limit_status())
        apicallsleft = int(count.split(',')[1].split(':')[1])
    except:
        Debug( 'Error fetching API count: ' + str(sys.exc_info()[1]), True)
        return 0
    
    Debug ('API Count Check: ' + str(apicallsleft), True)
    return count
    
