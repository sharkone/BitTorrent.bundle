################################################################################
import anime_menu
import movies_menu
import tvshows_menu
import yts_menu

import tracking

################################################################################
TITLE  = 'BitTorrent'
ART    = 'art-default.jpg'
ICON   = 'icon-default.png'

################################################################################
def Start():
    DirectoryObject.thumb  = R(ICON)
    ObjectContainer.art    = R(ART)
    ObjectContainer.title1 = TITLE
    VideoClipObject.art    = R(ART)
    VideoClipObject.thumb  = R(ICON)

################################################################################
@handler(SharedCodeService.common.PREFIX, TITLE, thumb=ICON, art=ART)
def Main():
    tracking.track('Started channel')

    Log.Info('Server Platform: {0} ({1})'.format(Platform.OS, Platform.CPU))
    Log.Info('Client Product: {0} ({1})'.format(Client.Product, Client.Platform))

    object_container = ObjectContainer(title2=TITLE)

    if Platform.OS not in ('Linux', 'MacOSX', 'Windows'):
        object_container.header  = 'Not supported'
        object_container.message = 'The {0} channel is not supported on {1} servers.'.format(TITLE, Platform.OS)
    else:
        object_container.add(DirectoryObject(key=Callback(anime_menu.menu), title='Anime'))
        object_container.add(DirectoryObject(key=Callback(movies_menu.menu), title='Movies'))
        object_container.add(DirectoryObject(key=Callback(tvshows_menu.menu), title='TV Shows'))
        
        if Prefs['USE_YTS_PROVIDER']:
            object_container.add(DirectoryObject(key=Callback(yts_menu.menu), title="YTS", thumb=R('yts.png')))
            
        object_container.add(PrefsObject(title='Preferences'))

    return object_container
