# -*- coding: utf-8 -*-
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import re
import urllib


#
# Constants
# 
__settings__ = xbmcaddon.Addon(id='plugin.image.oboobs')
__language__ = __settings__.getLocalizedString
rootDir = os.getcwd()
if rootDir[-1] == ';':rootDir = rootDir[0:-1]
cacheDir = os.path.join(rootDir, 'cache')
resDir = os.path.join(rootDir, 'resources')
imgDir = os.path.join(resDir, 'images')

pDialog = None
enable_debug = True

def _get_keyboard( default="", heading="", hidden=False ):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard( default, heading, hidden )
    keyboard.doModal()
    if ( keyboard.isConfirmed() ):
        return unicode( keyboard.getText(), "utf-8" )
    return default

def showRoot(localpath, handle):
        ri=[
            (__language__(30411),"http://oboobs.ru/%s/d"),
            (__language__(30412),"http://oboobs.ru/%s/e"),
            (__language__(30413),"http://oboobs.ru/%s/i/"),
            ]
        for name, url in ri:
            li=xbmcgui.ListItem(name)
            u=localpath+"?mode=1&name="+name+"&url="+urllib.quote_plus(url)
            xbmcplugin.addDirectoryItem(handle,u,li,True)
        url = "http://oboobs.ru/a/1"
        li=xbmcgui.ListItem(__language__(30414))
        u=localpath+"?mode=2&name="+__language__(30414)+"&url="+urllib.quote_plus(url)
        xbmcplugin.addDirectoryItem(handle,u,li,True)
        xbmcplugin.endOfDirectory(handle)
        
def showList(localpath, handle, name, url, page):
    pageUrl = url%(str(int(page)))
    showListCommon(localpath, handle, pageUrl)
    # Next page entry...
    listitem = xbmcgui.ListItem (__language__(30401), iconImage = "DefaultFolder.png", thumbnailImage = os.path.join(imgDir, 'next-page.png'))
    next_page_url = localpath+"?mode=1&name="+__language__(30401)+"&url="+urllib.quote_plus(url)+"&page="+str(int(page)+1)
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = next_page_url, listitem = listitem, isFolder = True)
    # Label (top-right)...
    xbmcplugin.setPluginCategory( handle, category=( "%s (%s)" % ( name, ( __language__(30402) % page ) ) ) )
    # End of directory...
    xbmcplugin.endOfDirectory(handle)
    
def showNoise(localpath, handle, name, url, page):
    pageUrl = "http://oboobs.ru/a/%s"%(str(int(page)))
    showNoiseCommon(localpath, handle, pageUrl)
    # Again entry...
    listitem = xbmcgui.ListItem (__language__(30401), iconImage = "DefaultFolder.png", thumbnailImage = os.path.join(imgDir, 'next-page.png'))
    next_page_url = localpath+"?mode=2&name="+__language__(30401)+"&url="+urllib.quote_plus(url)+"&page="+str(int(page)+1)
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = next_page_url, listitem = listitem, isFolder = True)
    # End of directory...
    xbmcplugin.endOfDirectory(handle)

def showListCommon(localpath, handle, pageUrl):
        print "Opening page: " + pageUrl
        f=urllib.urlopen(pageUrl)
        a=f.read()
        f.close()
        
        thumbRE = '<div class="dimage">.+?<img src="(.+?)" alt=.+?>'
        imagesRE = '<div class="ident"><a href="(.+?)">#(.+?)</a></div>'
        rankRE = '<div id="divrank.+?">(.+?)</div>'
        
        thumbPattern,videoPattern = re.compile(thumbRE), re.compile(imagesRE)
        rankPattern = re.compile(rankRE)
        
        matchThumb=thumbPattern.findall(a)
        matchImg=videoPattern.findall(a)
        matchRank=rankPattern.findall(a)

        n = 0
        for url, name in matchImg:
            thumb = matchThumb[n]
            rank = matchRank[n]
            full_image_url = thumb.replace("boobs_preview","boobs")
            # Add directory entry...
            li=xbmcgui.ListItem("#"+name+" ("+str(rank)+")",iconImage="DefaultPicture.png",thumbnailImage = thumb )
            li.setInfo( type="pictures", infoLabels={ "Title": name, "Rating": str(rank)} )
            try:
                action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=5&url=' + full_image_url)
                action1 = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=6&url=' + name)
                action2 = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=7&url=' + name)
                li.addContextMenuItems([(__language__(30201), action),(__language__(30202), action1),(__language__(30203), action2)])
            except:
                pass

            xbmcplugin.addDirectoryItem(handle,url = full_image_url,listitem=li, isFolder=False)
            n=n+1

def showNoiseCommon(localpath, handle, pageUrl):
        print "Opening page: " + pageUrl
        f=urllib.urlopen(pageUrl)
        a=f.read()
        f.close()
        
        numRE = '<div id="noise(.+?)" class="nimagebox">'
        thumbRE = '<div class="dimage"><img src="(.+?)" alt=.+?>'
        

        thumbPattern,numPattern = re.compile(thumbRE), re.compile(numRE)
        
        matchNum=numPattern.findall(a)
        matchThumb=thumbPattern.findall(a)
        
        n = 0
        for name in matchNum:
            thumb = matchThumb[n]
            full_image_url = thumb.replace("noise_preview","noise")
            # Add directory entry...
            li=xbmcgui.ListItem(name,iconImage="DefaultPicture.png",thumbnailImage = thumb )
            li.setInfo( type="pictures", infoLabels={ "Title": name} )
            try:
                action = 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=5&url=' + full_image_url)
                li.addContextMenuItems([(__language__(30201), action)])
            except:
                pass
            xbmcplugin.addDirectoryItem(handle,url = full_image_url,listitem=li, isFolder=False)
            n=n+1

def rating(localpath, handle, num, operation):
    pageUrl = "http://oboobs.ru/rank/"+str(operation)+"/"+str(num)+"/"
    print "Opening page: " + pageUrl
    f=urllib.urlopen(pageUrl)
    a=f.read()
    f.close()
    text = __language__(30301)+" #"+num+" - " + a
    xbmcgui.Dialog().ok(__language__(30001), text)
        
            
def get_params(args):
    param=[]
    print "Parsing arguments: " + str(args)
    paramstring=args[2]
    if len(paramstring)>=2:
        params=args[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
        return param

def download(localpath, handle, url):
    global pDialog
    pDialog = xbmcgui.DialogProgress()
    pDialog.create('Download OBoobs', __language__(30050), __language__(30051))
    pDialog.update(0)
    file = downloadFile(url)
    pDialog.close()
        
def downloadFile(url):
    if __settings__.getSetting('download_path') == '':
        try:
            dl_path = xbmcgui.Dialog().browse(0, __language__(30017),'files', '', False, False)
            __settings__.setSetting(id='download_path', value=dl_path)
            if not os.path.exists(dl_path):
                os.mkdir(dl_path)
        except:pass
    name =''
    extl = url.split('/')
    for i in extl:
        name=i
    file_path = xbmc.makeLegalFilename(os.path.join(__settings__.getSetting('download_path'), name))
    if os.path.isfile(file_path):
        return None
    try:
        urllib.urlretrieve(url, file_path, report_hook)
        if enable_debug:
            xbmc.output('Picture ' + str(url) + ' downloaded to ' + repr(file_path))
        return file_path
    except IOError:
        return None
        
    except  Exception,e:
        print e
        pass
    xbmc.sleep(500)
    return None
    
def report_hook(count, blocksize, totalsize):
    global pDialog
    percent = int(float(count * blocksize * 100) / totalsize)
    msg1 = __language__(30050)
    msg2 = __language__(30051)
    pDialog.update(percent,msg1, msg2)
    if pDialog.iscanceled():
        raise KeyboardInterrupt

def main():
            
    params=get_params(sys.argv)
    mode=None
    url=None
    name="Oboobs"
    page=1
    try:
        url=urllib.unquote_plus(params["url"])
    except:
        pass
    try:
        mode=int(params["mode"])
    except:
        pass
    try:
        page=int(params["page"])
    except:
        pass
    try:
        name=int(params["name"])
    except:
        pass
    
    if mode==None:
        showRoot(sys.argv[0], int(sys.argv[1]))
    elif mode==1:
        showList(sys.argv[0], int(sys.argv[1]), name, url, page)
    elif mode==2:
        showNoise(sys.argv[0], int(sys.argv[1]), name, url, page)
    elif mode==5:
        download(sys.argv[0], int(sys.argv[1]), url)
    elif mode==6:
        rating(sys.argv[0], int(sys.argv[1]), url,'add')
    elif mode==7:
        rating(sys.argv[0], int(sys.argv[1]), url, 'sub')

if __name__ == "__main__":
    main()

